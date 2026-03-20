const API_URL = "http://127.0.0.1:8000";

const historyButton = document.getElementById("historyButton");
const responseDiv = document.getElementById("response");

historyButton.addEventListener("click", loadHistory);

async function loadHistory() {
  historyButton.disabled = true;

  // Показываем и настраиваем контейнер ответа
  responseDiv.style.display = "block";
  responseDiv.classList.add("loading");

  // Очищаем предыдущий контент
  const contentDiv = responseDiv.querySelector(".response-content");
  contentDiv.textContent = "";

  try {
    const res = await fetch(`${API_URL}/history`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      throw new Error(`Ошибка: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();

    // Убираем состояние загрузки
    responseDiv.classList.remove("loading");

    // Отображаем полученные данные
    if (typeof data === 'string') {
      contentDiv.textContent = data;
    } else {
      contentDiv.textContent = JSON.stringify(data, null, 2);
    }

  } catch (err) {
    responseDiv.classList.remove("loading");
    contentDiv.textContent = `❌ Ошибка: ${err.message}`;
    contentDiv.style.color = "#dc3545";
  } finally {
    historyButton.disabled = false;
  }
}

// Инициализация - скрываем контейнер ответа при старте
responseDiv.style.display = "none";
