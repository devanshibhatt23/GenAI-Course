from fastapi import FastAPI, Query, Path
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

@app.get("/result/{job_id}")
def get_result(job_id : str = Path(..., description="Job ID")) : 
    job = q.fetch_job(job_id=job_id)
    result = job.return_value()
    
    return { "result: ", result}