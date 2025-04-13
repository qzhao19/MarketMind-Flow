from fastapi import APIRouter, HTTPException
from uuid import uuid4
from .api_schemas import MarketFlowRequest
from src.services.database.job_store import get_job_by_id
from src.services.celery.celery_app import app as celery_app
import json

flow_router = APIRouter(tags=["MarketFlow"])

@flow_router.post("/marketflow")
async def start_marketflow_job(request: MarketFlowRequest):
    """starting work flow"""
    try:
        job_id = str(uuid4())
        input_data = {
            "customer_domain": request.customer_domain,
            "project_description": request.project_description
        }
        celery_app.send_task(
            'market_tasks.kickoff_flow', 
            args=[job_id, input_data]
        )
        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(500, detail=f"Startup failure: {str(e)}")


@flow_router.get("/marketflow/{job_id}")
async def get_marketflow_status(job_id: str):
    """Querying Workflow Status"""
    
    job = get_job_by_id(job_id)
    if not job:
        raise HTTPException(404, detail="Task does not exist")
    
    try:
        result = json.loads(str(job.result))
    except json.JSONDecodeError:
        result = str(job.result)
    
    return {
        "job_id": job_id,
        "status": job.status,
        "result": result,
        "events": [
            {"timestamp": event.timestamp, "data": event.data}
            for event in job.events
        ]
    }
