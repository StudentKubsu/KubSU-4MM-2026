const MAX_TEXT_LENGTH = 1_000;

function parseTextContent(maxLen) {
  if (!document.body) {
    return "";
  }

  // Сначала пытаемся найти основную область контента
  const rootElement = document.querySelector('article, main, [role="main"]') || document.body;

  // Извлекаем текст в основном из семантических тегов, чтобы избежать меню, футеров и боковых панелей
  const textElements = rootElement.querySelectorAll('h1, h2, h3, h4, h5, h6, p, li, blockquote');
  let extractedText = "";

  if (textElements.length > 0) {
    const chunks = [];
    textElements.forEach(el => {
      // Игнорируем скрытые элементы (базовая проверка)
      if (el.offsetParent !== null) {
        const text = el.innerText || el.textContent || "";
        const cleanText = text.replace(/\s+/g, ' ').trim();
        if (cleanText) {
          chunks.push(cleanText);
        }
      }
    });
    extractedText = chunks.join('\n');
  } else {
    // Запасной вариант для страниц без хорошей семантической структуры
    extractedText = rootElement.innerText || rootElement.textContent || "";
    extractedText = extractedText.replace(/\s+/g, ' ').trim();
  }

  // Обрезаем текст аккуратно по границе слова, если это возможно
  if (extractedText.length > maxLen) {
    let truncated = extractedText.slice(0, maxLen);
    const lastSpace = truncated.lastIndexOf(' ');
    if (lastSpace > 0) {
      truncated = truncated.slice(0, lastSpace);
    }
    return truncated + '...';
  }

  return extractedText;
}

window.addEventListener('load', (event) => {
  const payload = {
    type: "view",
    url: location.href,
    title: document.title || "",
    lang: document.documentElement?.lang || "",
    text: parseTextContent(MAX_TEXT_LENGTH)
  };

  chrome.runtime.sendMessage(payload);
});
