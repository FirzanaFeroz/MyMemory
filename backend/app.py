import os
import time
import datetime
import pytz
import logging
import socket
from flask import Flask, request, jsonify, send_from_directory, render_template, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_migrate import Migrate

# Import custom utilities
from utils import (
    FaceRecognitionHandler, 
    MemoryChatbot, 
    configure_logging, 
    validate_image
)

# Load environment variables
load_dotenv()

# Render environment configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///memoryassist.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Configure logging
logger = configure_logging()

# Enhanced logging configuration
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app_debug.log')

# Initialize app and configurations
app = Flask(__name__)
CORS(app)

# Update app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

# Update upload folder configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
logger.debug(f'Upload folder configured to: {app.config["UPLOAD_FOLDER"]}')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Initialize database migration
migrate = Migrate(app, db)

# Timezone setup
IST = pytz.timezone('Asia/Kolkata')

# Initialize face recognition
face_recognition_handler = FaceRecognitionHandler()

# Models (same as before, but with added logging)
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    relation = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(IST))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'relation': self.relation,
            'description': self.description,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat()
        }

class TaskRepeatDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)  # monday, tuesday, etc.
    
    task = db.relationship('Task', backref=db.backref('repeat_days_rel', cascade='all, delete-orphan'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reminder_time = db.Column(db.DateTime, nullable=True)
    repeat_type = db.Column(db.String(20), nullable=True)
    repeat_time = db.Column(db.String(100), nullable=True)
    repeat_days_str = db.Column('repeat_days', db.String(100), nullable=True)  # Keep for backwards compatibility
    repeat_until = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
    version = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {    
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'repeat_type': self.repeat_type,
            'repeat_time': self.repeat_time,
            'repeat_days': [day.day_of_week for day in self.repeat_days_rel],
            'repeat_until': self.repeat_until.isoformat() if self.repeat_until else None,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat()
        }

class MemoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(IST))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

# Initialize memory chatbot
memory_chatbot = MemoryChatbot(MemoryLog)

# Log request information
@app.before_request
def log_request_info():
    # Get hostname and IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Log detailed request information
    logging.debug(f"Hostname: {hostname}")
    logging.debug(f"Local IP: {local_ip}")
    logging.debug(f"Request IP: {request.remote_addr}")
    logging.debug(f"Request Host: {request.host}")
    logging.debug(f"Request URL: {request.url}")
    logging.debug(f"Request Method: {request.method}")
    logging.debug(f"Request Headers: {dict(request.headers)}")

# Debug route to help diagnose network issues
@app.route('/debug-info')
def debug_info():
    return jsonify({
        'hostname': socket.gethostname(),
        'local_ip': socket.gethostbyname(socket.gethostname()),
        'request_ip': request.remote_addr,
        'request_host': request.host,
        'request_url': request.url
    })

# Routes for People with Enhanced Error Handling
@app.route('/api/people', methods=['POST'])
def add_person():
    try:
        logger.debug('Starting person addition process')
        logger.debug(f'Request method: {request.method}')
        logger.debug(f'Request content type: {request.content_type}')
        logger.debug(f'Request form data: {dict(request.form)}')
        logger.debug(f'Request files: {list(request.files.keys())}')
        
        if 'photo' not in request.files:
            logger.warning('No photo provided in person addition request')
            return jsonify({'error': 'No photo provided'}), 400
        
        photo = request.files['photo']
        logger.debug(f'Photo filename: {photo.filename}')
        
        # Validate image
        is_valid, error_msg = validate_image(photo)
        if not is_valid:
            logger.warning(f'Invalid image upload: {error_msg}')
            return jsonify({'error': error_msg}), 400
        
        name = request.form.get('name', '').strip()
        relation = request.form.get('relation', '').strip() or 'Unknown'
        description = request.form.get('description', '').strip()
        
        logger.debug(f'Extracted form data - Name: {name}, Relation: {relation}, Description: {description}')
        
        if not name:
            logger.warning('Name is required for person addition')
            return jsonify({'error': 'Name is required'}), 400
        
        filename = secure_filename(f"{name}_{int(time.time())}_{photo.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload directory exists and is writable
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Check directory permissions
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            logger.error(f'Upload directory is not writable: {app.config["UPLOAD_FOLDER"]}')
            return jsonify({'error': 'Server configuration error: Upload directory not writable'}), 500
        
        logger.debug(f'Attempting to save uploaded file: {filename}')
        logger.debug(f'Upload folder: {app.config["UPLOAD_FOLDER"]}')
        logger.debug(f'Full file path: {filepath}')
        
        try:
            photo.save(filepath)
            logger.debug(f'Successfully saved photo to: {filepath}')
        except PermissionError:
            logger.error(f'Permission denied when saving file: {filepath}')
            return jsonify({'error': 'Server permission error: Cannot save uploaded file'}), 500
        except Exception as save_error:
            logger.error(f'Unexpected error saving file: {save_error}')
            return jsonify({'error': f'File upload failed: {str(save_error)}'}), 500
        
        try:
            # Add person to database and perform face recognition
            logger.debug('Attempting face recognition')
            face_result = face_recognition_handler.add_person(
                filepath, name, relation, description
            )
            
            if 'error' in face_result:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.error(f'Face recognition error: {face_result["error"]}')
                    return jsonify(face_result), 400
            
            logger.debug('Creating new Person object')
            new_person = Person(
                name=name, 
                relation=relation, 
                description=description, 
                image_path=filename
            )
            
            db.session.add(new_person)
            
            try:
                db.session.commit()
                logger.info(f'Successfully added person: {name}')
                return jsonify(new_person.to_dict()), 201
            except Exception as commit_error:
                db.session.rollback()
                logger.error(f'Database commit error: {commit_error}')
                return jsonify({'error': 'Failed to save person to database'}), 500
        
        except Exception as face_error:
            logger.error(f'Face recognition or database error: {face_error}')
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(face_error)}), 500
    
    except Exception as e:
        logger.error(f'Unexpected error in add_person: {e}')
        return jsonify({'error': 'Unexpected server error'}), 500

@app.route('/api/people', methods=['GET'])
def get_people():
    try:
        people = Person.query.order_by(Person.created_at.desc()).all()
        return jsonify([person.to_dict() for person in people]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/people/<int:person_id>', methods=['GET'])
def get_person_details(person_id):
    try:
        person = Person.query.get(person_id)
        
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        return jsonify(person.to_dict()), 200
    except Exception as e:
        logger.error(f'Error fetching person details: {e}')
        return jsonify({'error': 'Error fetching person details'}), 500

@app.route('/api/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    try:
        person = Person.query.get(person_id)
        
        if not person:
            return jsonify({'error': 'Person not found'}), 404
        
        # Remove the associated image file
        if person.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], person.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Remove from known faces if applicable
        known_faces_dir = 'known_faces'
        face_encoding_path = os.path.join(known_faces_dir, f'{person.name}.npy')
        if os.path.exists(face_encoding_path):
            os.remove(face_encoding_path)
        
        # Delete from database
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({'message': 'Person deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting person: {e}')
        return jsonify({'error': 'Error deleting person'}), 500

# Face Recognition Route
@app.route('/api/identify', methods=['POST'])
def identify_person():
    try:
        if 'photo' not in request.files:
            logger.warning('No photo provided for identification')
            return jsonify({'error': 'No photo provided'}), 400
        
        photo = request.files['photo']
        
        # Validate image
        is_valid, error_msg = validate_image(photo)
        if not is_valid:
            logger.warning(f'Invalid image for identification: {error_msg}')
            return jsonify({'error': error_msg}), 400
        
        filename = secure_filename(f"identify_{int(time.time())}_{photo.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)
        
        try:
            # Identify person
            identification_result = face_recognition_handler.identify_person(filepath)
            
            if 'error' in identification_result:
                logger.warning(f'Person identification failed: {identification_result["error"]}')
                return jsonify(identification_result), 404
            
            # Find additional details about the identified person
            person = Person.query.filter_by(name=identification_result['name']).first()
            
            if person:
                result = {
                    **identification_result,
                    'relation': person.relation,
                    'description': person.description
                }
            else:
                result = identification_result
            
            logger.info(f'Person identified: {result["name"]}')
            return jsonify(result), 200
        
        except Exception as e:
            logger.error(f'Error in person identification: {e}')
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up temporary file
            os.remove(filepath)
    
    except Exception as e:
        logger.critical(f'Unexpected error in person identification: {e}')
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Task Management with Enhanced Logging
@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.json or {}
        
        if not data.get('name'):
            logger.warning('Task name is required')
            return jsonify({'error': 'Task name is required'}), 400
        
        # Parse reminder time with more robust handling
        reminder_time = None
        reminder_str = data.get('reminder_time')
        if reminder_str:
            try:
                reminder_time = datetime.datetime.strptime(reminder_str, '%H:%M')
                reminder_time = IST.localize(reminder_time)
            except ValueError:
                logger.warning(f'Invalid reminder time format: {reminder_str}')
                return jsonify({'error': 'Invalid reminder time format'}), 400
        
        # Parse repeat until date
        repeat_until = None
        repeat_until_str = data.get('repeat_until')
        if repeat_until_str:
            try:
                repeat_until = datetime.datetime.strptime(repeat_until_str, '%Y-%m-%d')
                repeat_until = IST.localize(repeat_until)
            except ValueError:
                logger.warning(f'Invalid repeat until date: {repeat_until_str}')
                return jsonify({'error': 'Invalid repeat until date format'}), 400
        
        # Validate repeat type
        repeat_type = data.get('repeat_type', 'none')
        valid_repeat_types = ['none', 'daily', 'weekly', 'monthly']
        if repeat_type not in valid_repeat_types:
            logger.warning(f'Invalid repeat type: {repeat_type}')
            return jsonify({'error': 'Invalid repeat type'}), 400
        
        new_task = Task(
            name=data['name'],
            description=data.get('description', ''),
            reminder_time=reminder_time,
            repeat_type=repeat_type,
            repeat_time=data.get('repeat_time'),
            repeat_days_str=data.get('repeat_days'),  # Keep for backwards compatibility
            repeat_until=repeat_until,
            is_completed=False
        )
        
        db.session.add(new_task)
        db.session.flush()  # Get the task ID before commit
        
        # Add repeat days
        repeat_days = data.get('repeat_days', '').split(',')
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in repeat_days:
            if day.lower() in valid_days:
                repeat_day = TaskRepeatDay(task_id=new_task.id, day_of_week=day.lower())
                db.session.add(repeat_day)
        
        db.session.commit()
        
        logger.info(f'Task added: {new_task.name}')
        return jsonify(new_task.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error adding task: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = Task.query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.json or {}
        
        if 'is_completed' in data:
            task.is_completed = data['is_completed']
        
        db.session.commit()
        return jsonify(task.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Routes for Memory Logs
@app.route('/api/memories', methods=['POST'])
def add_memory():
    try:
        data = request.json or {}
        
        if not data.get('title') or not data.get('content'):
            return jsonify({'error': 'Title and content are required'}), 400
        
        new_memory = MemoryLog(
            title=data['title'],
            content=data['content']
        )
        
        db.session.add(new_memory)
        db.session.commit()
        
        return jsonify(new_memory.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/memories', methods=['GET'])
def get_memories():
    try:
        memories = MemoryLog.query.order_by(MemoryLog.timestamp.desc()).all()
        return jsonify([memory.to_dict() for memory in memories]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Memory Chatbot Route
@app.route('/api/chat', methods=['POST'])
def memory_chat():
    try:
        data = request.json or {}
        
        if not data.get('message'):
            logger.warning('No message provided for chat')
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate response
        response = memory_chatbot.generate_response(data['message'])
        
        logger.info('Chat response generated')
        return jsonify({
            'response': response
        }), 200
    
    except Exception as e:
        logger.critical(f'Unexpected error in memory chat: {e}')
        return jsonify({'error': str(e)}), 500

# Person Identification Route
@app.route('/api/identify-person', methods=['POST'])
def identify_person_api():
    try:
        logger.debug('Starting person identification process')
        
        if 'identify-photo' not in request.files:
            logger.warning('No photo provided for identification')
            return jsonify({'error': 'No photo provided'}), 400
        
        photo = request.files['identify-photo']
        
        # Validate image
        is_valid, error_msg = validate_image(photo)
        if not is_valid:
            logger.warning(f'Invalid image upload: {error_msg}')
            return jsonify({'error': error_msg}), 400
        
        # Save the uploaded image temporarily
        filename = secure_filename(f"identify_{int(time.time())}_{photo.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload directory exists and is writable
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Check directory permissions
        if not os.access(app.config['UPLOAD_FOLDER'], os.W_OK):
            logger.error(f'Upload directory is not writable: {app.config["UPLOAD_FOLDER"]}')
            return jsonify({'error': 'Server configuration error: Upload directory not writable'}), 500
        
        logger.debug(f'Attempting to save uploaded file: {filename}')
        logger.debug(f'Upload folder: {app.config["UPLOAD_FOLDER"]}')
        logger.debug(f'Full file path: {filepath}')
        
        try:
            photo.save(filepath)
            logger.debug(f'Successfully saved photo to: {filepath}')
        except PermissionError:
            logger.error(f'Permission denied when saving file: {filepath}')
            return jsonify({'error': 'Server permission error: Cannot save uploaded file'}), 500
        except Exception as save_error:
            logger.error(f'Unexpected error saving file: {save_error}')
            return jsonify({'error': f'File upload failed: {str(save_error)}'}), 500
        
        try:
            # Attempt to identify the person
            identification_result = face_recognition_handler.identify_person(filepath)
            
            # Remove the temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Check identification result
            if 'error' in identification_result:
                return jsonify({'error': identification_result['error']}), 404
            
            return jsonify({
                'name': identification_result['name'],
                'confidence': identification_result.get('match_confidence')
            }), 200
        
        except Exception as e:
            logger.error(f'Error in person identification: {e}')
            
            # Remove the temporary file if it exists
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({'error': 'Unable to identify person'}), 500
    
    except Exception as e:
        logger.error(f'Unexpected error in person identification: {e}')
        return jsonify({'error': 'Unexpected server error'}), 500

# Template Rendering Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/people')
def people():
    return render_template('people.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/memories')
def memories():
    return render_template('memories.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/reminders')
def reminders():
    return render_template('reminders.html')

@app.route('/people-view')
def people_view():
    return render_template('people_view.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Serve uploaded files safely
    
    :param filename: Name of the file to serve
    :return: File or 404 error
    """
    try:
        # Ensure the file is within the uploads directory
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        file_path = os.path.abspath(os.path.join(upload_dir, filename))
        
        # Security check: ensure the file is within the upload directory
        if not file_path.startswith(upload_dir):
            logger.warning(f'Attempted to access file outside upload directory: {filename}')
            abort(403)  # Forbidden
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f'Requested file not found: {filename}')
            abort(404)
        
        return send_file(file_path)
    except Exception as e:
        logger.error(f'Error serving uploaded file: {e}')
        return jsonify({'error': 'Error serving file'}), 500

# Port Configuration
port = int(os.environ.get('PORT', 5000))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
