from src.core.flows.workflow import Workflow
from src.core.llm.llm_config import create_llm_client
from src.services.celery.celery_app import app
from src.services.database.job_store import append_event, update_job_by_id

@app.task(bind=True, max_retries=3)
def execute_flow(self, job_id, input_data):
    print(f"Market-Flow job {job_id} is starting")
    results = None
    try:
        append_event(job_id, "Flow Started")
        results = Workflow(job_id, create_llm_client, input_data).kickoff()
        # update_job_by_id(job_id, "COMPLETE", str(results), ["Flow complete"])
        return results
    except Exception as e:
        print(f"Error in kickoff_flow for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        update_job_by_id(job_id, "ERROR", "Error: {}".format(str(e)), ["Flow Start Error"])
    update_job_by_id(job_id, "COMPLETE", str(results), ["Flow complete"])
