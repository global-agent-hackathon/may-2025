function addTask() {
    const taskInput = document.getElementById("taskInput");
    const newTaskText = taskInput.value.trim();

    if (newTaskText !== "") {
        const taskList = document.getElementById("taskList");
        const newTask = document.createElement("li");
        newTask.textContent = newTaskText;
        newTask.onclick = function() { toggleTaskDone(this); };
        
        taskList.appendChild(newTask);
        taskInput.value = ""; // Clear input after adding
    } else {
        alert("Please enter a task.");
    }
}

function toggleTaskDone(taskItem) {
    taskItem.classList.toggle("done");
}

document.getElementById("taskInput").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        addTask();
    }
});