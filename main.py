from fastapi import FastAPI, Request
from pydantic import BaseModel
import chromadb
from datetime import datetime

app = FastAPI()
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("user_conversations")

class Message(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(msg: Message):
    # Retrieve last conversation for context
    history = collection.get(where={"user_id": msg.user_id})
    previous_msgs = [h["message"] for h in history["metadatas"]] if history["ids"] else []
    
    # Human-like greeting if this is a new conversation
    if not previous_msgs:
        response = "Hello! How are you feeling today? I'm here to listen. Would you like to talk about how you're feeling, or anything that's on your mind?"
    else:
        # Reference yesterday's convo if available
        response = "Welcome back! How have you been since our last chat? Is there anything from yesterday you'd like to talk more about?"
    
    # Store new message
    collection.add(
        documents=[msg.message],
        metadatas=[{"user_id": msg.user_id, "message": msg.message, "timestamp": str(datetime.utcnow())}],
        ids=[f"{msg.user_id}_{datetime.utcnow().isoformat()}"]
    )

    return {"response": response}

@app.get("/daily_thought")
def get_daily_thought():
    # Example: fetch from DB or external API
    return {"thought": "Every day is a new beginning. Take a deep breath and start again."}

@app.get("/healthy_tip")
def get_healthy_tip():
    return {"tip": "Stay hydrated! Drinking water boosts your mood and energy."}

@app.get("/mood_stats/{user_id}")
def get_mood_stats(user_id: str):
    # Example aggregation
    history = collection.get(where={"user_id": user_id})
    # Dummy stats
    return {"mood": "😊 Happy", "trend": "Improving"}

# Add endpoints for music, video suggestions, RAG-generated content, etc.
