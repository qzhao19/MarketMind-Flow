from crewai import LLM
from crewai.flow.flow import Flow, listen, start

from src.core.crews.content_creator.content_creator import ContentCreatorCrew
from src.core.crews.market_analyst.market_analyst import MarketAnalystCrew

class Workflow(Flow):
    """market analysis pipeline."""
    
    def __init__(self, job_id: str, llm: LLM, input_data):
        super().__init__()
        self.job_id = job_id
        self.llm = llm
        self.input_data = input_data

    @start()
    def analyze_market_crew(self):
        """Execute market analysis phase"""
        return MarketAnalystCrew(
            job_id=self.job_id,
            llm=self.llm,
            input_data=self.input_data
        ).execute()

    @listen(analyze_market_crew)
    def content_creator_crew(self):
        """Execute market analysis phase"""
        return ContentCreatorCrew(
            job_id=self.job_id,
            llm=self.llm,
            input_data=self.input_data
        ).execute()

