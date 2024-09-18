from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import uvicorn

app = FastAPI()

# إنشاء قاعدة البيانات SQLite
conn = sqlite3.connect('apps.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS apps
             (name TEXT PRIMARY KEY, status BOOLEAN)''')
conn.commit()

class AppRequest(BaseModel):
    app_name: str

@app.post("/register")
async def register_app(request: AppRequest):
    try:
        c.execute("INSERT INTO apps (name, status) VALUES (?, ?)", (request.app_name, False))
        conn.commit()
        return {"message": f"تم تسجيل التطبيق {request.app_name} بنجاح"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="اسم التطبيق موجود بالفعل")

@app.post("/stop")
async def stop_app(request: AppRequest):
    c.execute("UPDATE apps SET status = ? WHERE name = ?", (False, request.app_name))
    conn.commit()
    return {"message": f"تم إيقاف {request.app_name}"}

@app.post("/start")
async def start_app(request: AppRequest):
    c.execute("UPDATE apps SET status = ? WHERE name = ?", (True, request.app_name))
    conn.commit()
    return {"message": f"تم تشغيل {request.app_name}"}

@app.get("/status")
async def get_status(app_name: str):
    c.execute("SELECT status FROM apps WHERE name = ?", (app_name,))
    result = c.fetchone()
    if result is not None:
        return {"status": bool(result[0])}
    else:
        raise HTTPException(status_code=404, detail="التطبيق غير موجود")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
