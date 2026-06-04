import os
import sqlite3
import datetime
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

app = FastAPI(title="LunchTab")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Environment variables
DB_PATH = os.getenv("DB_PATH", "/app/data/app.db")
PORT = int(os.getenv("PORT", 8723))

def get_db():
    """Get a database connection, ensuring the directory and table exist."""
    data_dir = os.path.dirname(DB_PATH)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Create table if not exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT NOT NULL,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('owing', 'settled')),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    # Seed demo data if empty
    cursor = conn.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    if count == 0:
        demo_orders = [
            ("Alice", "Salad", 8.50, (datetime.date.today() - datetime.timedelta(days=5)).isoformat(), "owing"),
            ("Bob", "Pizza", 12.00, (datetime.date.today() - datetime.timedelta(days=4)).isoformat(), "settled"),
            ("Charlie", "Sushi", 15.75, (datetime.date.today() - datetime.timedelta(days=3)).isoformat(), "owing"),
            ("Diana", "Burger", 10.25, datetime.date.today().isoformat(), "owing"),
            ("Eve", "Pasta", 9.99, datetime.date.today().isoformat(), "settled"),
            ("Frank", "Burrito", 11.50, (datetime.date.today() - datetime.timedelta(days=2)).isoformat(), "owing"),
        ]
        conn.executemany(
            "INSERT INTO orders (person, item, amount, date, status) VALUES (?, ?, ?, ?, ?)",
            demo_orders,
        )
        conn.commit()
    return conn

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM orders ORDER BY date DESC, created_at DESC")
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Calculate metrics
    total_owed = sum(o["amount"] for o in orders if o["status"] == "owing")
    total_settled = sum(o["amount"] for o in orders if o["status"] == "settled")
    today = datetime.date.today()
    overdue_count = sum(
        1
        for o in orders
        if o["status"] == "owing"
        and datetime.date.fromisoformat(o["date"]) < today - datetime.timedelta(days=3)
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "orders": orders,
            "total_owed": total_owed,
            "total_settled": total_settled,
            "overdue_count": overdue_count,
            "today": today.isoformat(),
        },
    )

@app.post("/create")
async def create_order(
    person: str = Form(...),
    item: str = Form(...),
    amount: float = Form(...),
    date: Optional[str] = Form(None),
):
    if not date:
        date = datetime.date.today().isoformat()
    conn = get_db()
    conn.execute(
        "INSERT INTO orders (person, item, amount, date, status) VALUES (?, ?, ?, ?, 'owing')",
        (person, item, amount, date),
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/settle/{order_id}")
async def settle_order(order_id: int):
    conn = get_db()
    cursor = conn.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if row["status"] == "settled":
        # Already settled, do nothing
        conn.close()
        return RedirectResponse(url="/", status_code=303)
    conn.execute("UPDATE orders SET status = 'settled' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/health")
async def health():
    return {"status": "ok"}
