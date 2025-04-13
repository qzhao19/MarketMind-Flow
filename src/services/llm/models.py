from typing import List
from pydantic import BaseModel, Field

class BaseDescriptionModel(BaseModel):
    """Base model containing name and description fields"""
    name: str = Field(..., description="Name of the item")
    description: str = Field("", description="Detailed description")

class MarketStrategy(BaseDescriptionModel):
    """Market strategy model"""
    tactics: List[str] = Field(
        default_factory=list,
        description="List of tactics used in the marketing strategy",
        json_schema_extra={
            "example": ["Social media ads", "Email campaigns"]
        }
    )
    channels: List[str] = Field(
        default_factory=list,
        description="List of channels used in the marketing strategy", 
        json_schema_extra={
            "example": ["Facebook", "Google Ads", "Email"]
        }
    )
    kpis: List[str] = Field(
        default_factory=list,
        description="List of key performance indicators",
        json_schema_extra={
            "example": ["Conversion rate", "Click-through rate"]
        }
    )

class CampaignDevelopment(BaseDescriptionModel):
    """Marketing campaign idea model"""
    audience: str = Field(
        ...,
        description="Target audience description",
        json_schema_extra={
            "example": "Young professionals aged 25-35"
        }
    )
    channel: str = Field(
        ...,
        description="Primary marketing channel",
        json_schema_extra={
            "example": "Social media/Email marketing"
        }
    )

class ContentProduction(BaseDescriptionModel):
    """Marketing copy content model"""
    title: str = Field(
        ...,
        max_length=100,
        description="Title/headline of the marketing copy",
        json_schema_extra={
            "example": "Limited time offer: Summer sale"
        }
    )
    body: str = Field(
        ...,
        description="Main content body",
        min_length=50,
        json_schema_extra={
            "example": "We are excited to announce our new product line..."
        }
    )