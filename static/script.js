const userId = prompt("Masukkan ID Telegram kamu:");

async function fetchTasks() {
  const response = await fetch("/api/tasks");
  const tasks = await response.json();

  const taskList = document.getElementById("task-list");
  taskList.innerHTML = "";

  tasks.forEach(task => {
    const visitURL = `/api/visit?user_id=${userId}&task_id=${task.id}&url=${encodeURIComponent(task.url)}`;
    const div = document.createElement("div");
    div.className = "task";
    div.innerHTML = `
      <p>${task.name}</p>
      <a href="${visitURL}" target="_blank">
        <button>Selesaikan Tugas</button>
      </a>
    `;
    taskList.appendChild(div);
  });
}

fetchTasks();
