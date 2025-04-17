import logging
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from src.services.llm.models import MarketStrategy, CampaignDevelopment, ContentProduction
from src.services.database.job_store import append_event_by_id

logger = logging.getLogger(__name__)

@CrewBase
class ContentCreatorCrew():
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, job_id, llm, input_data):
        self.job_id = job_id
        self.llm = llm
        self.input_data = input_data

    def append_event_callback(self, task_output):
        append_event_by_id(self.job_id, task_output.raw)

    @agent
    def chief_marketing_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['chief_marketing_strategist'],
            llm=self.llm,
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def creative_director(self) -> Agent:
        return Agent(
            config=self.agents_config['creative_director'],
            llm=self.llm,
            verbose=True
        )

    @task
    def project_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['project_research_task'],
            agent=self.chief_marketing_strategist(),
            callback=self.append_event_callback
        )

    @task
    def marketing_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['marketing_strategy_task'],
            agent=self.chief_marketing_strategist(),
            callback=self.append_event_callback,
            output_json=MarketStrategy,
            context=[self.project_research_task()]
        )

    @task
    def campaign_development_task(self) -> Task:
        return Task(
            config=self.tasks_config['campaign_development_task'],
            agent=self.creative_director(),
            callback=self.append_event_callback,
            output_json=CampaignDevelopment,
            context=[self.marketing_strategy_task()]
        )

    @task
    def content_production_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_production_task'],
            agent=self.creative_director(),
            callback=self.append_event_callback,
            output_json=ContentProduction,
            context=[self.campaign_development_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def kickoff(self):
        if not self.crew():
            append_event_by_id(self.job_id, "ContentCreatorCrew initialization failed")
            logger.error(f"Error: ContentCreatorCrew not initialized")
            return "Error: ContentCreatorCrew not initialized"

        append_event_by_id(self.job_id, "ContentCreatorCrew execution started")
        try:
            results = self.crew().kickoff(inputs = self.input_data)
            append_event_by_id(self.job_id, "ContentCreatorCrew execution completed")
            return results
        except Exception as e:
            append_event_by_id(self.job_id, f"ContentCreatorCrew execution error: {str(e)}")
            logger.error(f"ContentCreatorCrew execution error: {str(e)}")
            return "Error: {}".format(str(e))