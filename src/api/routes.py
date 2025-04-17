import logging
from fastapi import APIRouter, HTTPException
from uuid import uuid4
from .api_schemas import MarketFlowRequest
from src.services.database.job_store import get_job_by_id
from src.services.celery.celery_app import app as celery_app
import json

logger = logging.getLogger(__name__)

flow_router = APIRouter(tags=["MarketFlow"])

@flow_router.post("/marketflow")
async def start_marketflow_job(request: MarketFlowRequest):
    """starting work flow"""
    try:
        job_id = str(uuid4())
        logger.info(f"Starting marketflow job: {job_id}")
        input_data = {
            "customer_domain": request.customer_domain,
            "project_description": request.project_description
        }
        celery_app.send_task(
            'src.tasks.market_tasks.kickoff_flow', 
            args=[job_id, input_data],
            queue='market_flow'
        )
        logger.debug(f"Job dispatched: {job_id}")
        return {"job_id": job_id}
    except Exception as e:
        logger.error("Failed to start job", exc_info=True)
        raise HTTPException(500, detail=f"Startup failure: {str(e)}")

@flow_router.get("/marketflow/{job_id}")
async def get_marketflow_status(job_id: str):
    """Querying Workflow Status"""
    logger.info(f"Querying job status: {job_id}")

    job = get_job_by_id(job_id)
    if not job:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(404, detail="Task does not exist")
    
    try:
        result = json.loads(str(job.result))
    except json.JSONDecodeError:
        logger.warning(f"Job runtime error: {job_id}")
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
