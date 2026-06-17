import sqlite3
import hashlib
import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Demostración SQL Injection")
templates = Jinja2Templates(directory="templates")

SECURE_DB = os.getenv("SECURE_DB_PATH", "seguro.db")
VULNERABLE_DB = "vulnerable.db"

DB_USER_ENV = os.getenv("DB_USER", "admin_db")
DB_PASS_ENV = os.getenv("DB_PASSWORD", "contraseñaxd")

def init_dbs():
    # Vulnerable
    conn = sqlite3.connect(VULNERABLE_DB)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT);
        DELETE FROM users;
        INSERT INTO users (username, password) VALUES ('admin', 'admin1234');
    """)
    conn.commit()
    conn.close()

    # Segura
    conn = sqlite3.connect(SECURE_DB)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT)")
    cursor.execute("DELETE FROM users")
    pwd_hash = hashlib.sha256("admin1234".encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ('admin', pwd_hash))
    conn.commit()
    conn.close()

init_dbs()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/vulnerable", response_class=HTMLResponse)
async def get_vulnerable(request: Request):
    return templates.TemplateResponse("vulnerable.html", {"request": request, "status": None})

@app.post("/vulnerable", response_class=HTMLResponse)
async def post_vulnerable(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(VULNERABLE_DB)
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    status = "error"
    try:
        # executescript permite inyectar sentencias como DROP TABLE
        cursor.executescript(query)
        
        # vemos si login funcionó o si la tabla sigue existiendo
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        if cursor.fetchone():
            status = "success"
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            status = "destroyed"
            init_dbs()
    finally:
        conn.close()

    return templates.TemplateResponse("vulnerable.html", {"request": request, "status": status, "query": query})

#           SEGURA (.env y Consultas Parametrizadas)
@app.get("/seguro", response_class=HTMLResponse)
async def get_seguro(request: Request):
    return templates.TemplateResponse("seguro.html", {"request": request, "status": None})

@app.post("/seguro", response_class=HTMLResponse)
async def post_seguro(request: Request, username: str = Form(...), password: str = Form(...)):
    # 1. Validación Base de Datos .env
    if DB_USER_ENV != "admin_db" or DB_PASS_ENV != "contraseñaxd":
        return templates.TemplateResponse("seguro.html", {"request": request, "status": "db_error"})

    # 2. Conexión y consulta parametrizada
    conn = sqlite3.connect(SECURE_DB)
    cursor = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pwd_hash))
    user = cursor.fetchone()
    conn.close()

    status = "success" if user else "error"
    return templates.TemplateResponse("seguro.html", {"request": request, "status": status})