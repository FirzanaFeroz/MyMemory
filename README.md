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
  - Face recognition (placeholder)

- Task and Reminder Management
  - Create tasks with reminder times
  - Repeating reminders (daily, weekly, monthly)
  - Mark tasks as completed
  - Set repeat end date

- Memory Logs
  - Create and store memory entries
  - Timestamp each memory

- Memory Chatbot
  - Conversational AI for memory recall (placeholder)

## Setup

### Backend Setup
1. Navigate to the `backend` directory
2. Create a virtual environment
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Run the application
   ```
   python app.py
   ```

### Frontend Setup (Coming Soon)
Frontend will be developed using modern web technologies.

## Git Repository Management

### Initial Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/MemoryAssist.git
   cd MemoryAssist
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Git Workflow
- Create a new branch for features
  ```bash
  git checkout -b feature/your-feature-name
  ```
- Commit changes
  ```bash
  git add .
  git commit -m "Description of changes"
  ```
- Push to remote repository
  ```bash
  git push origin feature/your-feature-name
  ```

### Deployment
- Set environment variables in `.env` file
- Use Flask-Migrate for database migrations
  ```bash
  flask db upgrade
  ```
- Run the application
  ```bash
  python app.py
  ```

### Recommended Workflow
1. Always pull latest changes before starting work
2. Create a new branch for each feature
3. Write tests for new features
4. Submit pull requests for code review

## Technologies
- Backend: Flask, SQLAlchemy
- Database: SQLite
- Face Recognition: face_recognition library (placeholder)
- Chatbot: OpenAI API (future implementation)

## Contributing
Contributions are welcome! Please submit pull requests or open issues.

## License
[Specify your license]
