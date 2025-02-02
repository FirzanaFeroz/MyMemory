import os
import logging
import face_recognition
import numpy as np
from PIL import Image
import io

class FaceRecognitionHandler:
    def __init__(self, known_people_dir='known_faces'):
        """
        Initialize face recognition handler
        
        :param known_people_dir: Directory to store known face encodings
        """
        self.known_people_dir = known_people_dir
        os.makedirs(known_people_dir, exist_ok=True)
        
        # Dictionary to store known face encodings
        self.known_faces = {}
        self.load_known_faces()
    
    def load_known_faces(self):
        """
        Load known face encodings from saved files
        """
        for filename in os.listdir(self.known_people_dir):
            if filename.endswith('.npy'):
                name = os.path.splitext(filename)[0]
                encoding_path = os.path.join(self.known_people_dir, filename)
                self.known_faces[name] = np.load(encoding_path)
    
    def add_person(self, image_path, name, relation='Unknown', description=''):
        """
        Add a new person's face to known faces
        
        :param image_path: Path to the person's image
        :param name: Name of the person
        :param relation: Relation to the user
        :param description: Additional description
        :return: Dictionary with result of face recognition
        """
        try:
            # Load the image
            image = face_recognition.load_image_file(image_path)
            
            # Find face encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return {'error': 'No face detected in the image'}
            
            # Take the first face encoding
            face_encoding = face_encodings[0]
            
            # Save face encoding
            encoding_filename = os.path.join(self.known_people_dir, f'{name}.npy')
            np.save(encoding_filename, face_encoding)
            
            # Update known faces
            self.known_faces[name] = face_encoding
            
            return {
                'message': 'Person added successfully',
                'name': name,
                'relation': relation,
                'description': description
            }
        
        except Exception as e:
            logging.error(f"Error adding person: {e}")
            return {'error': str(e)}
    
    def identify_person(self, image_path, tolerance=0.6):
        """
        Identify a person from an image
        
        :param image_path: Path to the image to identify
        :param tolerance: How much distance between faces to consider it a match
        :return: Dictionary with identified person or error
        """
        try:
            # Load the image to identify
            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if not unknown_encodings:
                return {'error': 'No face detected in the image'}
            
            # Compare with known faces
            for name, known_encoding in self.known_faces.items():
                matches = face_recognition.compare_faces(
                    [known_encoding], 
                    unknown_encodings[0], 
                    tolerance=tolerance
                )
                
                if matches[0]:
                    return {
                        'name': name,
                        'match_confidence': 1 - tolerance
                    }
            
            return {'error': 'Person not recognized'}
        
        except Exception as e:
            logging.error(f"Error identifying person: {e}")
            return {'error': str(e)}

class MemoryChatbot:
    def __init__(self, memory_log_db):
        """
        Initialize memory chatbot with access to memory logs
        
        :param memory_log_db: Database of memory logs
        """
        self.memory_log_db = memory_log_db
        self.predefined_responses = {
            "hello": "Hi there! How can I help you with your memories today?",
            "help": "I can help you recall memories, find past tasks, or discuss people you know.",
            "how are you": "I'm functioning well and ready to assist you with your memory needs!",
        }
    
    def generate_response(self, user_message):
        """
        Generate a response based on memory logs and predefined rules
        
        :param user_message: User's input message
        :return: Generated response
        """
        # Convert message to lowercase for easier matching
        user_message = user_message.lower().strip()
        
        # Check predefined responses first
        for key, response in self.predefined_responses.items():
            if key in user_message:
                return response
        
        # Find relevant memories
        relevant_memories = self._find_relevant_memories(user_message)
        
        # If memories found, summarize them
        if relevant_memories:
            memory_summary = "I found some relevant memories:\n"
            for memory in relevant_memories:
                memory_summary += f"- {memory.title}: {memory.content[:100]}...\n"
            return memory_summary
        
        # Default response
        return "I couldn't find a specific memory for that. Could you be more specific?"
    
    def _find_relevant_memories(self, query, top_n=3):
        """
        Find memories relevant to the query
        
        :param query: Search query
        :param top_n: Number of top memories to return
        :return: List of relevant memories
        """
        try:
            # Simple text search in memory logs
            memories = self.memory_log_db.query.filter(
                self.memory_log_db.title.contains(query) | 
                self.memory_log_db.content.contains(query)
            ).order_by(
                self.memory_log_db.timestamp.desc()
            ).limit(top_n).all()
            
            return memories
        except Exception as e:
            logging.error(f"Error finding memories: {e}")
            return []

def configure_logging(log_dir='logs'):
    """
    Configure logging for the application
    
    :param log_dir: Directory to store log files
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'memory_assist.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validate_image(file, max_size_mb=5):
    """
    Validate uploaded image file
    
    :param file: File object
    :param max_size_mb: Maximum allowed file size in MB
    :return: Tuple (is_valid, error_message)
    """
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell() / (1024 * 1024)  # Convert to MB
    file.seek(0)
    
    if file_size > max_size_mb:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check file type
    try:
        img = Image.open(file)
        img.verify()  # Verify that it's a valid image
        
        # Additional checks can be added here
        allowed_formats = ['JPEG', 'PNG', 'GIF']
        if img.format not in allowed_formats:
            return False, f"Unsupported image format. Allowed: {', '.join(allowed_formats)}"
        
        return True, None
    
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"
