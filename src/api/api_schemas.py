from pydantic import BaseModel

class MarketFlowRequest(BaseModel):
    """workflow request schema"""
    customer_domain: str
    project_description: str