import unittest
from typing import List
from pydantic import ValidationError
from src.services.llm.models import BaseDescriptionModel, MarketStrategy, CampaignDevelopment, ContentProduction

class TestMarketingModels(unittest.TestCase):
    # BaseDescriptionModel Tests
    def test_base_model_creation(self):
        """Test basic BaseDescriptionModel functionality"""
        # Test minimal valid model
        base = BaseDescriptionModel(name="Test Item")
        self.assertEqual(base.name, "Test Item")
        self.assertEqual(base.description, "")
        
        # Test full initialization
        base = BaseDescriptionModel(name="Test", description="Detailed info")
        self.assertEqual(base.description, "Detailed info")
        
        # Test name is required
        with self.assertRaises(ValidationError):
            BaseDescriptionModel(description="Missing name")

    # MarketStrategy Tests
    def test_market_strategy_validation(self):
        """Test MarketStrategy field validation"""
        # Valid strategy
        strategy = MarketStrategy(
            name="Q3 Campaign",
            tactics=["SEO", "Content Marketing"],
            channels=["Website", "Email"],
            kpis=["Traffic", "Conversions"]
        )
        self.assertEqual(len(strategy.tactics), 2)
        
        # Test default empty lists
        strategy = MarketStrategy(name="Empty Lists")
        self.assertEqual(strategy.tactics, [])
        self.assertEqual(strategy.channels, [])
        self.assertEqual(strategy.kpis, [])
        
        # Test invalid tactic type
        with self.assertRaises(ValidationError):
            MarketStrategy(
                name="Invalid",
                tactics=[1, 2, 3],  # Should be strings
                channels=["Valid"],
                kpis=["Valid"]
            )

    def test_market_strategy_examples(self):
        """Test documented examples work"""
        strategy = MarketStrategy(
            name="Example",
            tactics=["Social media ads", "Email campaigns"],
            channels=["Facebook", "Google Ads", "Email"],
            kpis=["Conversion rate", "Click-through rate"]
        )
        self.assertIn("Social media ads", strategy.tactics)
        self.assertIn("Email", strategy.channels)

    # CampaignDevelopment Tests
    def test_campaign_development(self):
        """Test CampaignDevelopment validation"""
        # Valid campaign
        campaign = CampaignDevelopment(
            name="Summer Sale",
            description="Seasonal promotion",
            audience="Young professionals aged 25-35",
            channel="Social media/Email marketing"
        )
        self.assertIn("25-35", campaign.audience)
        
        # Test required fields
        with self.assertRaises(ValidationError):
            CampaignDevelopment(
                name="Missing fields",
                description="Test"
            )
            
    # ContentProduction Tests
    def test_content_production_validation(self):
        """Test ContentProduction constraints"""
        # Valid content
        content = ContentProduction(
            name="Homepage Banner",
            title="Summer Specials",
            body="This is a detailed body that meets the minimum length requirement of 50 characters."
        )
        self.assertGreaterEqual(len(content.body), 50)
        
        # Test title length
        with self.assertRaises(ValidationError):
            ContentProduction(
                name="Long Title",
                title="x" * 101,  # Exceeds max_length
                body="x" * 50
            )
            
        # Test body length
        with self.assertRaises(ValidationError):
            ContentProduction(
                name="Short Body",
                title="Valid",
                body="Too short"  # Below min_length
            )

    def test_content_example(self):
        """Test documented example works"""
        content = ContentProduction(
            name="Example",
            title="Limited time offer: Summer sale",
            body="We are excited to announce our summer sale with amazing discounts on all products!"
        )
        self.assertIn("Summer sale", content.title)
        self.assertTrue(content.body.startswith("We are excited"))

    # Serialization Tests
    def test_model_serialization(self):
        """Test JSON serialization/deserialization"""
        campaign = CampaignDevelopment(
            name="Global Campaign",
            audience="International",
            channel="Multichannel"
        )
        
        # Roundtrip test
        json_data = campaign.model_dump_json()
        new_campaign = CampaignDevelopment.model_validate_json(json_data)
        self.assertEqual(campaign.name, new_campaign.name)
        self.assertEqual(campaign.channel, new_campaign.channel)

