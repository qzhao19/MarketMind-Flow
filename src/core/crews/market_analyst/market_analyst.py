from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from src.services.database.job_store import append_event

@CrewBase
class MarketAnalystCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, job_id, llm, input_data):
        self.job_id = job_id
        self.llm = llm
        self.input_data = input_data

    def append_event_callback(self, task_output):
        # print("Callback called: %s", task_output)
        append_event(self.job_id, task_output.raw)

    @agent
    def lead_market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['lead_market_analyst'],
            verbose=True,
            llm=self.llm,
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            callback=self.append_event_callback,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def execute(self):
        if not self.crew():
            append_event(self.job_id, "MarketAnalystCrew not set up")
            return {"status": "error", "message": "MarketAnalystCrew not set up"}
        
        append_event(self.job_id, "MarketAnalystCrew's Task Started")
        try:
            results = self.crew().kickoff(inputs=self.input_data)
            append_event(self.job_id, "MarketAnalystCrew's Task Complete")

            return results
        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return {"status": "error", "message": str(e)}
        

