from flask import Flask, render_template, request, jsonify
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Task class
class Task:
    def __init__(self, name, deadline, project_related, estimated_effort, is_personal=False):
        self.name = name
        self.deadline = deadline
        self.project_related = project_related
        self.is_personal = is_personal  # New parameter to indicate if the task is personal
        self.estimated_effort = int(estimated_effort)  # Convert estimated_effort to integer
        self.priority = self.generate_priority()
        self.ai_note = self.generate_ai_note()  # AI-generated note for the task

    def __repr__(self):
        return f"Task(name={self.name}, deadline={self.deadline}, project_related={self.project_related}, estimated_effort={self.estimated_effort}, priority={self.priority}, ai_note={self.ai_note})"

    def to_dict(self):
        return {
            'name': self.name,
            'deadline': self.deadline,
            'project_related': self.project_related,
            'estimated_effort': self.estimated_effort,
            'priority': self.priority,
            'ai_note': self.ai_note,  # Include AI note in the dictionary
            'is_personal': self.is_personal  # Include personal flag in the dict
        }

    def generate_priority(self):
        """ Automatically generate priority based on task attributes """
        current_time = datetime.datetime.now()
        deadline = datetime.datetime.strptime(self.deadline, '%Y-%m-%d')  # Assuming deadline is in 'YYYY-MM-DD' format
        
        # Priority generation logic
        if self.project_related:
            base_priority = 1  # Highest priority for project-related tasks
        elif self.is_personal and (deadline - current_time).days <= 2:
            base_priority = 2  # Personal tasks within 2 days are treated as urgent
        elif (deadline - current_time).days <= 1:
            base_priority = 2  # Tasks with a deadline in the next 24 hours are urgent
        else:
            base_priority = 3  # Default priority for other tasks
        
        # Include estimated effort in the priority (higher effort tasks will get higher priority if urgent)
        if self.estimated_effort > 5:
            base_priority += 1  # Increase priority for tasks requiring more effort
        
        return base_priority

    def generate_ai_note(self):
        """ Generate AI note based on task priority and deadline """
        if self.priority == 1:
            return "🚨 Urgent! This is a top priority task. It needs immediate attention, as it's related to a project or due soon."
        elif self.priority == 2:
            if self.is_personal:
                return "⚡ Urgent personal task! This task must be completed soon. Plan it well and manage your time wisely."
            else:
                return "🛑 High priority task! You have time, but it's approaching quickly. Prioritize this for better efficiency."
        else:
            return "✅ Low priority task. You can focus on this later. It's not urgent but should be done soon to stay organized."


# TaskPrioritizer class
class TaskPrioritizer:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task_name):
        self.tasks = [task for task in self.tasks if task.name != task_name]

    def prioritize_tasks(self, sort_by="priority"):
        """ Sort tasks by priority """
        if sort_by == "priority":
            self.tasks.sort(key=lambda x: (x.priority, x.deadline, not x.project_related))
        elif sort_by == "deadline":
            self.tasks.sort(key=lambda x: x.deadline)
        else:
            self.tasks.sort(key=lambda x: x.name)  # Default: Sort by task name
        return self.tasks

    def show_tasks(self):
        return [task.to_dict() for task in self.tasks]

    def get_task_by_name(self, task_name):
        for task in self.tasks:
            if task.name == task_name:
                return task
        return None

# Instantiate the TaskPrioritizer
prioritizer = TaskPrioritizer()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    task_data = request.get_json()
    task_name = task_data['name']
    task_deadline = task_data['deadline']
    task_project_related = task_data['project_related']
    task_estimated_effort = task_data['estimated_effort']
    task_is_personal = task_data.get('is_personal', False)  # Check if task is personal

    # Ensure estimated_effort is an integer
    try:
        task_estimated_effort = int(task_estimated_effort)
    except ValueError:
        return jsonify({"message": "Invalid estimated effort!"}), 400

    # Create and add the task with auto-generated priority
    task = Task(task_name, task_deadline, task_project_related, task_estimated_effort, is_personal=task_is_personal)
    prioritizer.add_task(task)

    return jsonify({"message": "Task added successfully!"})

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    tasks = prioritizer.show_tasks()  # Get the list of tasks
    return jsonify({"tasks": tasks})

@app.route('/sort_tasks', methods=['POST'])
def sort_tasks():
    sort_by = request.json.get('sort_by', 'priority')  # Default sorting by priority
    prioritizer.prioritize_tasks(sort_by)
    tasks = prioritizer.show_tasks()  # Get the sorted tasks
    return jsonify({"tasks": tasks})

@app.route('/update_task', methods=['POST'])
def update_task():
    task_data = request.get_json()
    task_name = task_data['name']
    task_priority = task_data.get('priority')
    task_deadline = task_data.get('deadline')
    task_estimated_effort = task_data.get('estimated_effort')
    
    task = prioritizer.get_task_by_name(task_name)
    if not task:
        return jsonify({"message": "Task not found!"}), 404

    # Update task details if provided
    if task_priority:
        task.priority = task_priority
    if task_deadline:
        task.deadline = task_deadline
    if task_estimated_effort:
        try:
            task.estimated_effort = int(task_estimated_effort)
        except ValueError:
            return jsonify({"message": "Invalid estimated effort!"}), 400

    # Recalculate priority and update AI note
    task.priority = task.generate_priority()
    task.ai_note = task.generate_ai_note()

    return jsonify({"message": "Task updated successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
