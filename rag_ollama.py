
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import requests

# 1. Set up ChromaDB & embedding model
client = chromadb.Client()
collection = client.create_collection("mental_health")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Add documents to the vector db (run once)
docs = [
    "If you feel anxious, try deep breathing or grounding exercises.",
    "Talk to someone you trust about your feelings.",
    "Regular exercise and enough sleep can improve your mental health.",
    "If you're feeling down for a long time, consider reaching out to a mental health professional.",
    "Journaling can help you process your emotions.",
]
collection.add(
    documents=docs,
    embeddings=[embedder.encode(doc) for doc in docs],
    ids=[f"doc{i}" for i in range(len(docs))]
)

# 3. Function for RAG retrieval
def retrieve_context(query):
    query_embedding = embedder.encode(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )
    return " ".join(results['documents'][0])

# 4. Function to query Ollama LLM
def call_ollama(prompt, model="llama3"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    return response.json()["response"]

# 5. Chat loop
if __name__ == "__main__":
    print("Mental Health Agent (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break
        context = retrieve_context(user_input)
        full_prompt = f"You are a mental health assistant. Context: {context}\nUser: {user_input}\nAnswer:"
        answer = call_ollama(full_prompt)
        print(f"Bot: {answer}\n")







