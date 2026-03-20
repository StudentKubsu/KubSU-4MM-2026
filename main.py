import logging
import sqlite3
import requests  # type: ignore

from contextlib import closing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "page_views.db"
PROMPT_DEFAULT = """
Собери информацию о посещённых сайтах, исходя из их title. Сформулируй мои интересы.

Проанализируй список заголовков и структурируй ответ:
1. Основные сферы интересов (перечисли 2-4 ключевые категории)
2. Краткий вывод (1 предложение)

Список titles:
"""


class PageView(BaseModel):
    url: str
    title: str
    lang: str
    text: str
    timestamp: str


class LlmRequest(BaseModel):
    prompt: str


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                lang TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
            """
        )
        conn.commit()


def save_page_view(page_view: PageView):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO page_views (url, title, lang, text, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                page_view.url,
                page_view.title,
                page_view.lang,
                page_view.text,
                page_view.timestamp,
            ),
        )
        conn.commit()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized: %s", DB_PATH)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/page-view")
def page_view(page_view: PageView):
    logger.info("=" * 60)
    logger.info("URL:       %s", page_view.url)
    logger.info("Title:     %s", page_view.title)
    logger.info("Lang:      %s", page_view.lang)
    logger.info("Timestamp: %s", page_view.timestamp)
    logger.info("Text:      %s...", page_view.text[:100])
    logger.info("=" * 60)

    save_page_view(page_view)
    logger.info("Page view saved to database")

    return {"status": "ok"}


@app.get("/history")
def history():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        rows = conn.execute("SELECT title FROM page_views ORDER BY id ASC").fetchall()
        titles = ", ".join(row[0] for row in rows).strip()

    logger.info("Title:     %s", titles)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": PROMPT_DEFAULT + titles,
            "system": "Отвечай на русском языке. Будь кратким, дружелюбным и структурированным.",
            "temperature": 0.3,
            "stream": False,
        },
    )
    return response.json().get("response")
