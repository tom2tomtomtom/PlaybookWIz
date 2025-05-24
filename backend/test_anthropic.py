#!/usr/bin/env python3
"""
Test script to verify Anthropic API integration.

This script tests the basic functionality of the Anthropic Claude API
to ensure proper setup and configuration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_anthropic_connection():
    """Test basic Anthropic API connection."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please add your Anthropic API key to backend/.env:")
        print("ANTHROPIC_API_KEY=your-api-key-here")
        return False
    
    try:
        print("🔍 Testing Anthropic API connection...")
        
        # Initialize client
        client = AsyncAnthropic(api_key=api_key)
        
        # Test basic message
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'API connection successful' to confirm the connection is working."
                }
            ]
        )
        
        response_text = response.content[0].text
        print(f"✅ Anthropic API Response: {response_text}")
        
        if "API connection successful" in response_text:
            print("✅ Anthropic API integration is working correctly!")
            return True
        else:
            print("⚠️  Unexpected response from Anthropic API")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Anthropic API: {e}")
        return False

async def test_brand_analysis():
    """Test brand analysis functionality."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return False
    
    try:
        print("\n🎨 Testing brand analysis functionality...")
        
        client = AsyncAnthropic(api_key=api_key)
        
        # Sample brand content
        brand_content = """
        Brand Guidelines for TechFlow Inc.
        
        Our brand represents innovation, reliability, and user-centric design.
        
        Colors:
        - Primary: #2563EB (Blue)
        - Secondary: #10B981 (Green)
        - Accent: #F59E0B (Orange)
        
        Typography:
        - Headings: Inter Bold
        - Body: Inter Regular
        
        Voice & Tone:
        - Professional yet approachable
        - Clear and concise
        - Empowering and confident
        
        Target Audience:
        - Tech professionals aged 25-45
        - Decision makers in technology companies
        - Innovation-focused individuals
        """
        
        prompt = f"""
        Analyze the following brand guidelines and extract key brand elements:

        {brand_content}

        Please provide a structured analysis including:
        1. Brand identity elements (colors, fonts, visual style)
        2. Brand voice and tone characteristics
        3. Target audience insights
        4. Key brand values and personality traits

        Format your response as a clear, structured summary.
        """
        
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        analysis = response.content[0].text
        print("✅ Brand Analysis Result:")
        print("-" * 50)
        print(analysis)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in brand analysis test: {e}")
        return False

async def test_creative_ideation():
    """Test creative ideation functionality."""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return False
    
    try:
        print("\n💡 Testing creative ideation functionality...")
        
        client = AsyncAnthropic(api_key=api_key)
        
        prompt = """
        You are Aiden, a Strategic Brand Visionary with an analytical, forward-thinking, and philosophically inclined personality. Your expertise is in brand strategy, market positioning, and cultural trends.

        Based on the following brand context, generate 3 creative campaign ideas:

        Brand: EcoTech Solutions
        Mission: Making sustainable technology accessible to everyone
        Values: Innovation, Sustainability, Accessibility
        Target: Environmentally conscious consumers aged 25-40

        For each idea, provide:
        1. Campaign concept
        2. Key message
        3. Strategic rationale
        4. Implementation approach

        Think deeply about cultural relevance and long-term brand impact.
        """
        
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1200,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        ideas = response.content[0].text
        print("✅ Creative Ideation Result:")
        print("-" * 50)
        print(ideas)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in creative ideation test: {e}")
        return False

async def main():
    """Run all tests."""
    
    print("🚀 PlaybookWiz Anthropic API Test Suite")
    print("=" * 50)
    
    # Test basic connection
    connection_success = await test_anthropic_connection()
    
    if connection_success:
        # Test brand analysis
        await test_brand_analysis()
        
        # Test creative ideation
        await test_creative_ideation()
        
        print("\n🎉 All tests completed!")
        print("Your Anthropic API integration is ready for PlaybookWiz!")
    else:
        print("\n❌ Basic connection test failed. Please check your API key and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
