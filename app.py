from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

app = FastAPI()

# Set up static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'smart_home.db'

# Ensure the database and tables are created
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE devices (
            device_id TEXT PRIMARY KEY,
            type TEXT,
            status TEXT,
            last_communication TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE events (
            event_id TEXT PRIMARY KEY,
            device_id TEXT,
            timestamp TEXT,
            description TEXT
        )
    ''')
    # Seed data
    cursor.execute("INSERT INTO devices VALUES ('device1', 'Thermostat', 'online', ?)", (datetime.now().isoformat(),))
    cursor.execute("INSERT INTO users VALUES ('admin', 'admin', 'admin')")
    cursor.execute("INSERT INTO events VALUES ('event1', 'device1', ?, 'Device turned on')", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()

# Pydantic models
class Device(BaseModel):
    device_id: str
    type: str
    status: str
    last_communication: datetime

class User(BaseModel):
    username: str
    password: str
    role: str

class Event(BaseModel):
    event_id: str
    device_id: str
    timestamp: datetime
    description: str

# API Endpoints
@app.get("/api/devices", response_model=List[Device])
async def get_devices():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()
    conn.close()
    return [Device(device_id=d[0], type=d[1], status=d[2], last_communication=datetime.fromisoformat(d[3])) for d in devices]

@app.post("/api/devices")
async def add_device(device: Device):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO devices VALUES (?, ?, ?, ?)", (device.device_id, device.type, device.status, device.last_communication.isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Device already exists")
    finally:
        conn.close()
    return {"message": "Device added successfully"}

@app.get("/api/events", response_model=List[Event])
async def get_events():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    conn.close()
    return [Event(event_id=e[0], device_id=e[1], timestamp=datetime.fromisoformat(e[2]), description=e[3]) for e in events]

@app.post("/api/users")
async def create_user(user: User):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user.username, user.password, user.role))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()
    return {"message": "User created successfully"}

@app.get("/api/users", response_model=List[User])
async def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [User(username=u[0], password=u[1], role=u[2]) for u in users]

# HTML Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/devices", response_class=HTMLResponse)
async def read_devices(request):
    return templates.TemplateResponse("devices.html", {"request": request})

@app.get("/events", response_class=HTMLResponse)
async def read_events(request):
    return templates.TemplateResponse("events.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
async def read_users(request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request):
    return templates.TemplateResponse("settings.html", {"request": request})
