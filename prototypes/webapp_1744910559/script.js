document.getElementById('taskInput').addEventListener("keyup", function(event) {
    if (event.key === 'Enter') {
        newElement();
    }
});

document.querySelector("button").addEventListener("click", newElement);

function newElement() {
    let input = document.getElementById("taskInput");
    let inputValue = input.value.trim();
    if (inputValue === '') {
        alert("You must write something!");
        return;
    }

    let li = document.createElement("li");
    let taskText = document.createTextNode(inputValue);
    li.appendChild(taskText);

    let span = document.createElement("SPAN");
    let closeText = document.createTextNode("\u00D7");
    span.className = "close";
    span.appendChild(closeText);
    li.appendChild(span);

    li.addEventListener("click", function() {
        this.classList.toggle('done');
    });

    span.onclick = function() {
        this.parentElement.remove();
    };

    document.getElementById("taskList").appendChild(li);
    input.value = "";
}