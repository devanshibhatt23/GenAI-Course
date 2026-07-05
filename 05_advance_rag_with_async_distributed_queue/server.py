from fastapi import FastAPI, Query
from .queue.connection import q
from .queue.worker import process_query

app = FastAPI()

@app.get("/")
def root() :
    return { "server is up and running!" }

@app.post("/chat")
def chat(query: str = Query(..., description="chat message")) :
    # query enqueued in queue
    job = q.enqueue(process_query, query)

    return { "status": "queued", "job_id": job.id}
