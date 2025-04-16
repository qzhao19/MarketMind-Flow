from src.core.flows.workflow import Workflow
from src.services.llm.llm_service import LLMService
from src.services.celery.celery_app import app
from src.services.database.job_store import append_event_by_id, update_job_by_id

@app.task(bind=True, max_retries=3)
def kickoff_flow(job_id, input_data):
    print(f"MarketFlow job {job_id} is starting")
    results = None
    llm_service = LLMService()
    try:
        append_event_by_id(job_id, "Flow Started")
        results = Workflow(job_id, llm_service.get_client(), input_data).kickoff()
        update_job_by_id(job_id, "COMPLETE", str(results), ["Flow complete"])
    except Exception as e:
        print(f"Error in kickoff_flow for job {job_id}: {e}")
        append_event_by_id(job_id, f"An error occurred: {e}")
        update_job_by_id(job_id, "ERROR", "Error: {}".format(str(e)), ["Flow Start Error"])
