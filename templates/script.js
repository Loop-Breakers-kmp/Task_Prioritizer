// For handling login screen transitions
function login() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('task-input-screen').classList.remove('hidden');
}

// Handle submitting the task form
function submitTask() {
    const taskName = document.getElementById('task-name').value;
    const deadline = document.getElementById('deadline').value;
    const estimatedEffort = document.getElementById('time').value;
    const category = document.getElementById('category').value;
    const isPersonal = category === 'personal';

    const taskData = {
        name: taskName,
        deadline: deadline,
        estimated_effort: estimatedEffort,
        project_related: category === 'professional',
        is_personal: isPersonal
    };

    // Send the task data to the backend to add the task
    fetch('http://127.0.0.1:5000/add_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData),
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('task-name').value = '';
        document.getElementById('deadline').value = '';
        document.getElementById('time').value = '';
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to add task.');
    });
}

// Handle generating and displaying the schedule
function generateSchedule() {
    fetch('http://127.0.0.1:5000/get_tasks')
        .then(response => response.json())
        .then(data => {
            const scheduleOutput = document.getElementById('schedule-output');
            scheduleOutput.innerHTML = '';  // Clear the existing schedule
            const tasks = data.tasks;

            // Loop through tasks and display each task
            tasks.forEach(task => {
                const taskDiv = document.createElement('div');
                taskDiv.classList.add('task');

                const taskName = document.createElement('h3');
                taskName.textContent = task.name;
                taskDiv.appendChild(taskName);

                const taskDeadline = document.createElement('p');
                taskDeadline.textContent = `Deadline: ${task.deadline}`;
                taskDiv.appendChild(taskDeadline);

                const taskPriority = document.createElement('p');
                taskPriority.textContent = `Priority: ${task.priority}`;
                taskDiv.appendChild(taskPriority);

                const aiNote = document.createElement('p');
                aiNote.textContent = `AI Note: ${task.ai_note}`;
                taskDiv.appendChild(aiNote);

                scheduleOutput.appendChild(taskDiv);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to fetch tasks.');
        });
}
