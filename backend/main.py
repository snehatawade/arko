from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, upload, subscriptions, harvey, profile, notifications
from config import settings

# Create database tables (checkfirst=True prevents error if tables already exist)
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(title="Arko API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(subscriptions.router)
app.include_router(harvey.router)
app.include_router(profile.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {"message": "Arko API - Welcome!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

