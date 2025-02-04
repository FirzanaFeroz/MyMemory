
# MyMemory

## Basic Details

### Team Members
Firzana Feroz - CUSAT, Kalamassery

### Hosted Project Link
-

### Project Description
MyMemory is an application designed to help elderly users and individuals with memory issues. Simply put, it is a memory assistant.
It helps users by providing reminders, identifying forgotten faces, and logging and recollecting memories via a chatbot. 

### The Problem Statement
Elderly individuals and those with memory impairments often struggle to remember faces and important tasks.
There is a need for a system that not only reminds them of tasks but also helps them recall memories and identify people they may forget.

### The Solution
MyMemory offers a solution by allowing users to store information about people and tasks. The app uses face recognition to identify people from images and smart reminders to help users with their daily activities like taking medications or appointments or events. Additionally, a memory chatbot aids in logging their memories and recalling previously stored memories.

## Technical Details
### Technologies/Components Used
For Software:
- **Languages used**: Python, HTML, CSS, JavaScript
- **Frameworks used**: Flask
- **Libraries used**: SQLite, PIL (for image recognition), Flask-SQLAlchemy
- **Tools used**: Git, GitHub, Vscode, ChatGpt

For Hardware:
- Currently, the application does not require specific hardware components but may be integrated with devices in the future for features like fall detection.

### Implementation
For Software:

# Installation
1. Clone the repository:
   
   git clone [https://github.com/FirzanaFeroz/remote] cd [remote/backend]
  
2. Set up a virtual environment:
   
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
 
3. Install required dependencies:

   pip install -r requirements.txt
   

# Run
1. Initialize the SQLite database:
  
   flask db init
   flask db migrate
   flask db upgrade
 
2. Run the Flask app:
  
   flask run

## Features
- Person Management
  - Add people with photos
  - Store names, relationships, and descriptions
  - Face recognition

- Task and Reminder Management
  - Create tasks with reminder times
  - Repeating reminders (daily, weekly, monthly)
  - Mark tasks as completed
  - Set repeat end date

- Memory Logs
  - Create and store memory entries
  - Timestamp each memory

- Memory Chatbot
  - Conversational AI for memory recall

### Project Documentation
For Software:

# Screenshots
![image](https://github.com/user-attachments/assets/2277c0fc-d06e-4864-b162-e473d7ce6827)
Image Home page

![image](https://github.com/user-attachments/assets/e80ea839-a0f0-485d-81bf-ed3cda44f25e)
Dashboard

![image](https://github.com/user-attachments/assets/24c01f30-de9c-4e72-9acb-9440ffb9f648)
Adding a person

![image](https://github.com/user-attachments/assets/093a6208-e748-492e-bec9-e588e2c9e2d1)
Memory gallery of people

![image](https://github.com/user-attachments/assets/b4de1487-c297-4b72-8f39-bc785bc70e75)
Adding tasks

![image](https://github.com/user-attachments/assets/523a8fee-454a-4c37-a71a-50e1bf0b7e62)
Memory Log

![image](https://github.com/user-attachments/assets/bea9c22c-dbee-42d5-8816-d5c16c4937dd)
Memory Chatbot



---
Made with ❤️ at TinkerHub
```
