// Utility Functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1000';
        document.body.appendChild(container);
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.getElementById('alert-container').appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// People Management
async function loadPeople() {
    try {
        const response = await fetch('/api/people');
        const people = await response.json();
        const peopleContainer = document.getElementById('people-list');
        
        if (peopleContainer) {
            peopleContainer.innerHTML = '';
            people.forEach(person => {
                const personCard = document.createElement('div');
                personCard.className = 'col-md-4 person-card';
                personCard.innerHTML = `
                    <img src="/uploads/${person.image_path}" alt="${person.name}" class="person-image">
                    <h5>${person.name}</h5>
                    <p>${person.relation || 'Unknown Relation'}</p>
                    <p>${person.description || ''}</p>
                `;
                peopleContainer.appendChild(personCard);
            });
        }
    } catch (error) {
        showAlert('Error loading people', 'danger');
        console.error('Error:', error);
    }
}

// Task Management
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        const tasksContainer = document.getElementById('tasks-list');
        
        if (tasksContainer) {
            tasksContainer.innerHTML = '';
            tasks.forEach(task => {
                const taskItem = document.createElement('div');
                taskItem.className = `task-list-item ${task.is_completed ? 'task-completed' : ''}`;
                taskItem.innerHTML = `
                    <div>
                        <input type="checkbox" 
                               class="form-check-input task-complete-checkbox" 
                               data-task-id="${task.id}"
                               ${task.is_completed ? 'checked' : ''}>
                        <span>${task.name}</span>
                        ${task.description ? `<small class="text-muted"> - ${task.description}</small>` : ''}
                    </div>
                    <small class="text-muted">
                        ${task.reminder_time ? new Date(task.reminder_time).toLocaleTimeString() : ''}
                        ${task.repeat_type !== 'none' ? `(${task.repeat_type})` : ''}
                    </small>
                `;
                tasksContainer.appendChild(taskItem);
            });

            // Add event listeners for task completion
            document.querySelectorAll('.task-complete-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', async (e) => {
                    const taskId = e.target.dataset.taskId;
                    try {
                        const response = await fetch(`/api/tasks/${taskId}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ is_completed: e.target.checked })
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to update task');
                        }
                        
                        // Update visual state
                        e.target.closest('.task-list-item').classList.toggle('task-completed');
                        showAlert('Task updated successfully', 'success');
                    } catch (error) {
                        showAlert('Error updating task', 'danger');
                        console.error('Error:', error);
                        e.target.checked = !e.target.checked;
                    }
                });
            });
        }
    } catch (error) {
        showAlert('Error loading tasks', 'danger');
        console.error('Error:', error);
    }
}

// Memory Logs
async function loadMemories() {
    try {
        const response = await fetch('/api/memories');
        const memories = await response.json();
        const memoriesContainer = document.getElementById('memories-list');
        
        if (memoriesContainer) {
            memoriesContainer.innerHTML = '';
            memories.forEach(memory => {
                const memoryEntry = document.createElement('div');
                memoryEntry.className = 'memory-log-entry';
                memoryEntry.innerHTML = `
                    <h5>${memory.title}</h5>
                    <p>${memory.content}</p>
                    <small class="text-muted">${new Date(memory.timestamp).toLocaleString()}</small>
                `;
                memoriesContainer.appendChild(memoryEntry);
            });
        }
    } catch (error) {
        showAlert('Error loading memories', 'danger');
        console.error('Error:', error);
    }
}

// Memory Chat
async function sendChatMessage() {
    const messageInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-messages');
    
    if (!messageInput || !chatContainer || !messageInput.value.trim()) return;
    
    const userMessage = messageInput.value;
    
    // Display user message
    const userMessageEl = document.createElement('div');
    userMessageEl.className = 'chat-message user-message';
    userMessageEl.textContent = userMessage;
    chatContainer.appendChild(userMessageEl);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        });
        
        const data = await response.json();
        
        // Display bot response
        const botMessageEl = document.createElement('div');
        botMessageEl.className = 'chat-message bot-message';
        botMessageEl.textContent = data.response;
        chatContainer.appendChild(botMessageEl);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Clear input
        messageInput.value = '';
    } catch (error) {
        showAlert('Error sending message', 'danger');
        console.error('Error:', error);
    }
}

// Camera and Photo Capture
function setupCamera() {
    const videoElement = document.getElementById('camera-preview');
    const captureButton = document.getElementById('capture-photo');
    const photoPreview = document.getElementById('photo-preview');
    
    if (!videoElement || !captureButton || !photoPreview) return;
    
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;
            
            captureButton.addEventListener('click', () => {
                const canvas = document.createElement('canvas');
                canvas.width = videoElement.videoWidth;
                canvas.height = videoElement.videoHeight;
                canvas.getContext('2d').drawImage(videoElement, 0, 0);
                
                const dataUrl = canvas.toDataURL('image/jpeg');
                photoPreview.src = dataUrl;
                
                // Convert data URL to blob for upload
                canvas.toBlob(blob => {
                    const file = new File([blob], 'captured-photo.jpg', { type: 'image/jpeg' });
                    // You can now use this file for upload
                });
            });
        })
        .catch(error => {
            showAlert('Error accessing camera', 'danger');
            console.error('Camera error:', error);
        });
}

// Form Submission Handlers
function setupFormHandlers() {
    // Person Form
    const personForm = document.getElementById('person-form');
    if (personForm) {
        personForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Check if a photo is selected or captured
            const photoInput = document.getElementById('photo');
            const photoPreview = document.getElementById('photo-preview');
            
            const formData = new FormData(personForm);
            
            // If photo preview is visible, convert it to a file
            if (photoPreview.style.display !== 'none' && photoPreview.src) {
                try {
                    const response = await fetch(photoPreview.src);
                    const blob = await response.blob();
                    formData.set('photo', blob, 'captured_photo.jpg');
                } catch (error) {
                    showAlert('Error processing captured photo', 'danger');
                    return;
                }
            }
            
            // Validate form data
            const name = formData.get('name').trim();
            if (!name) {
                showAlert('Name is required', 'danger');
                return;
            }
            
            if (!formData.get('photo') || formData.get('photo').size === 0) {
                showAlert('Photo is required', 'danger');
                return;
            }
            
            try {
                const response = await fetch('/api/people', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showAlert('Person added successfully', 'success');
                    personForm.reset();
                    photoPreview.style.display = 'none';
                    loadPeople();
                } else {
                    showAlert(result.error || 'Error adding person', 'danger');
                }
            } catch (error) {
                showAlert('Error submitting form', 'danger');
                console.error('Error:', error);
            }
        });
    }

    // Task Form
    const taskForm = document.getElementById('task-form');
    if (taskForm) {
        // Repeat options toggle
        const repeatCheckbox = document.getElementById('task-repeat-enable');
        const repeatOptions = document.getElementById('repeat-options');
        const repeatTypeRadios = document.querySelectorAll('input[name="repeat_type"]');
        const repeatTimeInput = document.getElementById('repeat-time');
        const repeatDaysCheckboxes = document.querySelectorAll('input[name="repeat_days"]');
        
        // Function to toggle repeat options visibility
        function toggleRepeatOptions() {
            const isRepeating = repeatCheckbox.checked;
            
            // Show/hide entire repeat options section
            repeatOptions.classList.toggle('d-none', !isRepeating);
            
            // Disable/enable inputs when not repeating
            repeatTimeInput.disabled = !isRepeating;
            repeatTypeRadios.forEach(radio => {
                radio.disabled = !isRepeating;
            });
            repeatDaysCheckboxes.forEach(checkbox => {
                checkbox.disabled = !isRepeating;
            });
            
            // If not repeating, reset to default state
            if (!isRepeating) {
                document.querySelector('input[name="repeat_type"][value="none"]').checked = true;
                repeatTimeInput.value = '';
                document.getElementById('repeat-until').value = '';
                repeatDaysCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
            }
        }
        
        // Initial setup
        repeatCheckbox.addEventListener('change', toggleRepeatOptions);
        repeatTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                // Ensure repeat checkbox is checked when changing repeat type
                if (!repeatCheckbox.checked) {
                    repeatCheckbox.checked = true;
                }
                toggleRepeatOptions();
            });
        });
        
        // Trigger initial state
        toggleRepeatOptions();
        
        taskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(taskForm);
            const taskData = {};
            
            // Standard fields
            taskData.name = formData.get('name');
            taskData.description = formData.get('description') || '';
            taskData.reminder_time = formData.get('reminder_time') || null;
            
            // Repeat fields
            if (repeatCheckbox.checked) {
                taskData.repeat_type = formData.get('repeat_type') || 'none';
                taskData.repeat_time = formData.get('repeat_time') || '';
                
                // Validate repeat type
                const validRepeatTypes = ['none', 'daily', 'weekly', 'monthly'];
                if (!validRepeatTypes.includes(taskData.repeat_type)) {
                    showAlert('Invalid repeat type', 'danger');
                    return;
                }
                
                // Handle checkbox-based repeat days
                const repeatDaysCheckboxes = document.querySelectorAll('input[name="repeat_days"]:checked');
                const selectedDays = Array.from(repeatDaysCheckboxes)
                    .map(checkbox => checkbox.value);
                
                // Validate repeat days based on repeat type
                if (taskData.repeat_type === 'weekly' && selectedDays.length === 0) {
                    showAlert('Please select at least one day for weekly repeat', 'danger');
                    return;
                }
                
                taskData.repeat_days = selectedDays.join(',');
                taskData.repeat_until = formData.get('repeat-until') || null;
                
                // Validate repeat until date if set
                if (taskData.repeat_until) {
                    const repeatUntilDate = new Date(taskData.repeat_until);
                    const today = new Date();
                    if (repeatUntilDate < today) {
                        showAlert('Repeat until date must be in the future', 'danger');
                        return;
                    }
                }
            } else {
                // Ensure default values when repeat is not enabled
                taskData.repeat_type = 'none';
                taskData.repeat_time = '';
                taskData.repeat_days = '';
                taskData.repeat_until = null;
            }
            
            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(taskData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showAlert('Task added successfully', 'success');
                    taskForm.reset();
                    repeatOptions.classList.add('d-none');
                    loadTasks();
                } else {
                    showAlert(result.error || 'Error adding task', 'danger');
                }
            } catch (error) {
                showAlert('Error submitting form', 'danger');
                console.error('Error:', error);
            }
        });
    }

    // Memory Log Form
    const memoryForm = document.getElementById('memory-form');
    if (memoryForm) {
        memoryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(memoryForm);
            const memoryData = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch('/api/memories', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(memoryData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showAlert('Memory log added successfully', 'success');
                    memoryForm.reset();
                    loadMemories();
                } else {
                    showAlert(result.error || 'Error adding memory', 'danger');
                }
            } catch (error) {
                showAlert('Error submitting form', 'danger');
                console.error('Error:', error);
            }
        });
    }
}

// Page-specific Initialization
function initializePage() {
    // Detect and run page-specific functions
    if (document.getElementById('people-list')) {
        loadPeople();
    }
    
    if (document.getElementById('tasks-list')) {
        loadTasks();
    }
    
    if (document.getElementById('memories-list')) {
        loadMemories();
    }
    
    if (document.getElementById('camera-preview')) {
        setupCamera();
    }
    
    setupFormHandlers();

    // Chat message send handler
    const chatSendButton = document.getElementById('chat-send');
    if (chatSendButton) {
        chatSendButton.addEventListener('click', sendChatMessage);
    }

    // Repeat options toggle
    const repeatCheckbox = document.getElementById('task-repeat-enable');
    const repeatOptions = document.getElementById('repeat-options');
    
    if (repeatCheckbox && repeatOptions) {
        repeatCheckbox.addEventListener('change', () => {
            repeatOptions.classList.toggle('d-none', !repeatCheckbox.checked);
        });
    }
}

// Run initialization when DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializePage);
