import logging

from src.config.logger import setup_logging
from src.core.flows.workflow import Workflow
from src.services.llm.llm_service import LLMService
from src.services.celery.celery_app import app
from src.services.database.job_store import append_event_by_id, update_job_by_id

logger = logging.getLogger(__name__)

@app.task(name='src.tasks.market_tasks.kickoff_flow')
def kickoff_flow(job_id, input_data):
    logger.info(f"MarketFlow job {job_id} is starting")

    results = None
    llm_service = LLMService()
    llm = llm_service.get_client()
    
    try:
        append_event_by_id(job_id, "Flow Started")
        results = Workflow(job_id, llm, input_data).kickoff()
        logger.info(f"Job {job_id} completed with results: {str(results)[:100]}...") 
        update_job_by_id(job_id, "COMPLETE", str(results), ["Flow complete"])
    except Exception as e:
        logger.error(f"Error in kickoff_flow for job {job_id}", exc_info=True)
        append_event_by_id(job_id, f"An error occurred: {e}")
        update_job_by_id(job_id, "ERROR", "Error: {}".format(str(e)), ["Flow Start Error"])
        raise
