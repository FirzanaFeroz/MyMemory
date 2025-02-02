# MemoryAssist

## Overview
MemoryAssist is an application designed to help elderly users and individuals with memory issues. It provides features to:
- Add and manage people with their images, names, relationships, and descriptions
- Create and track tasks and reminders with repeat options
- Create memory logs
- Use a memory chatbot for memory recall

## Features
- Person Management
  - Add people with photos
  - Store names, relationships, and descriptions
  - Face recognition using advanced computer vision

- Task and Reminder Management
  - Create tasks with reminder times
  - Repeating reminders (daily, weekly, monthly)
  - Mark tasks as completed
  - Set repeat end date

- Memory Logs
  - Create and store memory entries
  - Timestamp each memory

- Memory Chatbot
  - AI-powered conversational interface for memory recall

## Prerequisites
- Python 3.9+
- pip
- Virtual environment support

## Local Development Setup

### Backend Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/MemoryAssist.git
   cd MemoryAssist
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment
   - Copy `.env.example` to `.env`
   - Update configuration as needed

5. Initialize the database
   ```bash
   flask db upgrade
   ```

6. Run the application
   ```bash
   flask run
   ```

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: Directory for file uploads
- `LOG_LEVEL`: Logging verbosity

### Database
Supports SQLite (default) and PostgreSQL

## Security Considerations
- Use strong, unique `SECRET_KEY`
- Set appropriate file upload size limits
- Use HTTPS in production
- Regularly update dependencies

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Specify your license]

## Support
For issues or questions, please open a GitHub issue.
