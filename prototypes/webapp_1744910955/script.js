document.addEventListener('DOMContentLoaded', function() {
    const tasksList = document.getElementById('tasks-list');
    const newTaskForm = document.getElementById('new-task-form');
    const newTaskInput = document.getElementById('new-task-input');

    newTaskForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const taskText = newTaskInput.value.trim();
        if (taskText) {
            addTask(taskText);
            newTaskInput.value = '';
            newTaskInput.focus();
        }
    });

    function addTask(text) {
        const taskEl = document.createElement('li');
        taskEl.textContent = text;
        taskEl.addEventListener('click', () => toggleTask(taskEl));
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.onclick = () => deleteTask(taskEl);
        taskEl.appendChild(deleteBtn);
        tasksList.appendChild(taskEl);
    }

    function toggleTask(taskEl) {
        taskEl.classList.toggle('completed');
    }

    function deleteTask(taskEl) {
        tasksList.removeChild(taskEl);
    }
});