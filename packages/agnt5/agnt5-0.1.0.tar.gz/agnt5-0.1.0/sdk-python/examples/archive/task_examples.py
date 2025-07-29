#!/usr/bin/env python3
"""
Comprehensive Task Examples for AGNT5 SDK

This example demonstrates various task patterns and use cases:
1. Basic Task Usage
2. JSON Extraction Tasks
3. Pydantic Model Tasks
4. String Processing Tasks
5. Task Chaining and Composition
6. Error Handling and Validation
7. Agent-Task Integration
8. Durable Task Workflows
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field

from agnt5 import Agent, task, json_extraction_task, pydantic_task, string_task
from agnt5.task import Task, TaskResult, OutputFormat
from agnt5.extraction import extract_json_from_text, extract_structured_data
from agnt5.durable import durable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# =============================================================================

class ContactInfo(BaseModel):
    """Contact information model."""
    name: str = Field(description="Full name of the person")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(description="Phone number", default=None)
    company: Optional[str] = Field(description="Company name", default=None)

class ProductReview(BaseModel):
    """Product review model."""
    product_name: str = Field(description="Name of the product")
    rating: int = Field(description="Rating from 1-5", ge=1, le=5)
    pros: List[str] = Field(description="List of positive aspects")
    cons: List[str] = Field(description="List of negative aspects")
    recommendation: str = Field(description="Overall recommendation")

class MeetingAgenda(BaseModel):
    """Meeting agenda model."""
    title: str = Field(description="Meeting title")
    date: str = Field(description="Meeting date")
    attendees: List[str] = Field(description="List of attendees")
    agenda_items: List[str] = Field(description="List of agenda items")
    estimated_duration: str = Field(description="Estimated meeting duration")

class CodeAnalysis(BaseModel):
    """Code analysis result model."""
    language: str = Field(description="Programming language")
    complexity: str = Field(description="Code complexity level")
    issues: List[str] = Field(description="List of potential issues")
    suggestions: List[str] = Field(description="List of improvement suggestions")
    quality_score: int = Field(description="Quality score from 1-10", ge=1, le=10)


# =============================================================================
# 1. BASIC TASK USAGE
# =============================================================================

@task(output_format=OutputFormat.STRING)
async def summarize_text(text: str, max_words: int = 50) -> str:
    """Summarize text to a specified word count."""
    agent = Agent(
        name="summarizer",
        model="anthropic/claude-3-5-sonnet",
        system_prompt=f"Summarize the given text in no more than {max_words} words. Be concise and capture the key points."
    )
    
    response = await agent.run(f"Summarize this text: {text}")
    return response.content

@task(output_format=OutputFormat.JSON)
async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment of given text."""
    agent = Agent(
        name="sentiment-analyzer",
        model="openai/gpt-4o",
        system_prompt="Analyze the sentiment of the given text. Return JSON with sentiment, confidence, and key emotions."
    )
    
    prompt = f"""
    Analyze the sentiment of this text: "{text}"
    
    Return a JSON object with:
    - sentiment: "positive", "negative", or "neutral"
    - confidence: number between 0-1
    - emotions: list of detected emotions
    - reasoning: brief explanation
    """
    
    response = await agent.run(prompt)
    return extract_json_from_text(response.content)

async def demo_basic_tasks():
    """Demonstrate basic task usage."""
    print("\n📝 1. Basic Task Usage")
    print("=" * 40)
    
    # Test text summarization
    sample_text = """
    Artificial Intelligence (AI) has revolutionized numerous industries and aspects of daily life. 
    From healthcare diagnostics to autonomous vehicles, AI systems are becoming increasingly 
    sophisticated and capable. Machine learning algorithms can now process vast amounts of data 
    to identify patterns and make predictions with remarkable accuracy. However, the rapid 
    advancement of AI also raises important questions about ethics, privacy, and the future 
    of work. As we continue to develop more powerful AI systems, it's crucial that we consider 
    both the benefits and potential risks associated with this technology.
    """
    
    try:
        print("  📄 Text Summarization Task:")
        summary = await summarize_text(sample_text, max_words=30)
        print(f"    Original: {len(sample_text.split())} words")
        print(f"    Summary: {summary}")
        print(f"    Summary length: {len(summary.split())} words")
        
        print("\n  💭 Sentiment Analysis Task:")
        sentiment = await analyze_sentiment("I absolutely love this new product! It's amazing and works perfectly.")
        print(f"    Sentiment: {sentiment.get('sentiment', 'Unknown')}")
        print(f"    Confidence: {sentiment.get('confidence', 'Unknown')}")
        print(f"    Emotions: {sentiment.get('emotions', [])}")
        
    except Exception as e:
        print(f"  ❌ Basic tasks failed: {e}")


# =============================================================================
# 2. JSON EXTRACTION TASKS
# =============================================================================

@json_extraction_task
async def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract contact information from text."""
    agent = Agent(
        name="contact-extractor",
        model="anthropic/claude-3-5-sonnet",
        system_prompt="Extract contact information from text. Return structured JSON data."
    )
    
    prompt = f"""
    Extract contact information from this text: "{text}"
    
    Return JSON with:
    - name: full name
    - email: email address 
    - phone: phone number (if found)
    - company: company name (if found)
    - address: address (if found)
    """
    
    response = await agent.run(prompt)
    return response.content

@json_extraction_task
async def extract_key_facts(text: str) -> Dict[str, Any]:
    """Extract key facts and figures from text."""
    agent = Agent(
        name="fact-extractor",
        model="google/gemini-1.5-pro",
        system_prompt="Extract key facts, figures, dates, and statistics from text. Return structured JSON."
    )
    
    prompt = f"""
    Extract key facts from: "{text}"
    
    Return JSON with:
    - facts: list of key facts
    - numbers: list of important numbers/statistics
    - dates: list of dates mentioned
    - entities: list of people, places, organizations
    """
    
    response = await agent.run(prompt)
    return response.content

async def demo_json_extraction_tasks():
    """Demonstrate JSON extraction tasks."""
    print("\n📊 2. JSON Extraction Tasks")
    print("=" * 40)
    
    # Test contact extraction
    contact_text = """
    Hi, this is John Smith from TechCorp Inc. You can reach me at john.smith@techcorp.com 
    or call me at (555) 123-4567. Our office is located at 123 Main Street, San Francisco, CA.
    I'm the Director of Engineering and I'd like to discuss the new project.
    """
    
    # Test fact extraction
    fact_text = """
    The company reported revenue of $2.3 billion in Q3 2024, representing a 15% increase 
    from the previous quarter. The CEO, Sarah Johnson, announced that they hired 1,200 new 
    employees this year and plan to expand to 5 new countries by December 2024. The stock 
    price reached an all-time high of $145.67 on October 15th.
    """
    
    try:
        print("  👤 Contact Information Extraction:")
        contact_info = await extract_contact_info(contact_text)
        print(f"    Name: {contact_info.get('name', 'Not found')}")
        print(f"    Email: {contact_info.get('email', 'Not found')}")
        print(f"    Company: {contact_info.get('company', 'Not found')}")
        
        print("\n  📈 Key Facts Extraction:")
        facts = await extract_key_facts(fact_text)
        print(f"    Facts: {len(facts.get('facts', []))} found")
        print(f"    Numbers: {facts.get('numbers', [])}")
        print(f"    Entities: {facts.get('entities', [])}")
        
    except Exception as e:
        print(f"  ❌ JSON extraction failed: {e}")


# =============================================================================
# 3. PYDANTIC MODEL TASKS
# =============================================================================

@pydantic_task(model=ProductReview)
async def create_product_review(product_description: str, user_feedback: str) -> ProductReview:
    """Create a structured product review from description and feedback."""
    agent = Agent(
        name="review-creator",
        model="anthropic/claude-3-5-sonnet",
        system_prompt="Create detailed product reviews based on product descriptions and user feedback."
    )
    
    prompt = f"""
    Product: {product_description}
    User Feedback: {user_feedback}
    
    Create a comprehensive product review with:
    - Product name
    - Rating (1-5 stars)
    - List of pros and cons
    - Overall recommendation
    
    Be objective and balanced in your assessment.
    """
    
    response = await agent.run(prompt)
    return response.content

@pydantic_task(model=MeetingAgenda)
async def generate_meeting_agenda(meeting_purpose: str, participants: List[str], duration: str) -> MeetingAgenda:
    """Generate a structured meeting agenda."""
    agent = Agent(
        name="meeting-planner",
        model="openai/gpt-4o",
        system_prompt="Create well-structured meeting agendas with clear objectives and time allocations."
    )
    
    prompt = f"""
    Create a meeting agenda for:
    Purpose: {meeting_purpose}
    Participants: {', '.join(participants)}
    Duration: {duration}
    
    Include:
    - Clear meeting title
    - Date (use tomorrow's date)
    - List of attendees
    - Detailed agenda items with time allocations
    - Estimated total duration
    """
    
    response = await agent.run(prompt)
    return response.content

async def demo_pydantic_tasks():
    """Demonstrate Pydantic model tasks."""
    print("\n🏗️ 3. Pydantic Model Tasks")
    print("=" * 40)
    
    try:
        print("  📝 Product Review Generation:")
        product_desc = "Wireless Bluetooth headphones with noise cancellation, 30-hour battery life"
        user_feedback = "Great sound quality and comfort, but expensive. Battery life is excellent."
        
        review = await create_product_review(product_desc, user_feedback)
        print(f"    Product: {review.product_name}")
        print(f"    Rating: {review.rating}/5 stars")
        print(f"    Pros: {len(review.pros)} points")
        print(f"    Recommendation: {review.recommendation[:50]}...")
        
        print("\n  📅 Meeting Agenda Generation:")
        agenda = await generate_meeting_agenda(
            "Q4 Planning Review",
            ["Alice Smith", "Bob Johnson", "Carol Davis", "David Wilson"],
            "2 hours"
        )
        print(f"    Title: {agenda.title}")
        print(f"    Attendees: {len(agenda.attendees)} people")
        print(f"    Agenda Items: {len(agenda.agenda_items)} items")
        print(f"    Duration: {agenda.estimated_duration}")
        
    except Exception as e:
        print(f"  ❌ Pydantic tasks failed: {e}")


# =============================================================================
# 4. STRING PROCESSING TASKS
# =============================================================================

@string_task
async def generate_creative_story(prompt: str, style: str = "adventure") -> str:
    """Generate a creative story based on a prompt."""
    agent = Agent(
        name="story-writer",
        model="anthropic/claude-3-5-sonnet",
        system_prompt=f"You are a creative writer specializing in {style} stories. Write engaging, well-structured narratives."
    )
    
    response = await agent.run(f"Write a {style} story based on: {prompt}")
    return response.content

@string_task
async def explain_concept(concept: str, audience: str = "general") -> str:
    """Explain a complex concept for a specific audience."""
    agent = Agent(
        name="explainer",
        model="google/gemini-1.5-pro",
        system_prompt=f"Explain complex concepts clearly for a {audience} audience. Use analogies and examples."
    )
    
    prompt = f"Explain '{concept}' in simple terms for a {audience} audience. Use analogies and examples to make it clear."
    response = await agent.run(prompt)
    return response.content

async def demo_string_tasks():
    """Demonstrate string processing tasks."""
    print("\n📚 4. String Processing Tasks")
    print("=" * 40)
    
    try:
        print("  ✍️ Creative Story Generation:")
        story = await generate_creative_story(
            "A detective discovers that time moves backwards in a mysterious library",
            "mystery"
        )
        print(f"    Story length: {len(story.split())} words")
        print(f"    Story preview: {story[:200]}...")
        
        print("\n  🎓 Concept Explanation:")
        explanation = await explain_concept("quantum computing", "high school students")
        print(f"    Explanation length: {len(explanation.split())} words")
        print(f"    Explanation preview: {explanation[:200]}...")
        
    except Exception as e:
        print(f"  ❌ String tasks failed: {e}")


# =============================================================================
# 5. TASK CHAINING AND COMPOSITION
# =============================================================================

@task(output_format=OutputFormat.JSON)
async def research_topic(topic: str) -> Dict[str, Any]:
    """Research a topic and return structured information."""
    agent = Agent(
        name="researcher",
        model="google/gemini-1.5-pro",
        system_prompt="Research topics thoroughly and provide structured, factual information."
    )
    
    prompt = f"""
    Research the topic: {topic}
    
    Return JSON with:
    - key_points: list of main points
    - applications: practical applications
    - benefits: list of benefits
    - challenges: list of challenges
    - future_outlook: future prospects
    """
    
    response = await agent.run(prompt)
    return extract_json_from_text(response.content)

@pydantic_task(model=CodeAnalysis)
async def analyze_code_quality(code: str, language: str) -> CodeAnalysis:
    """Analyze code quality and provide suggestions."""
    agent = Agent(
        name="code-reviewer",
        model="anthropic/claude-3-5-sonnet",
        system_prompt="Analyze code quality, identify issues, and provide improvement suggestions."
    )
    
    prompt = f"""
    Analyze this {language} code:
    
    ```{language}
    {code}
    ```
    
    Provide:
    - Programming language
    - Complexity assessment
    - List of potential issues
    - Improvement suggestions
    - Quality score (1-10)
    """
    
    response = await agent.run(prompt)
    return response.content

async def chained_analysis_workflow(topic: str) -> Dict[str, Any]:
    """Demonstrate task chaining for complex analysis."""
    print(f"    🔗 Starting chained analysis for: {topic}")
    
    # Step 1: Research the topic
    research_data = await research_topic(topic)
    
    # Step 2: Generate a summary
    key_points = research_data.get('key_points', [])
    summary = await summarize_text(
        f"Key points about {topic}: {'. '.join(key_points)}",
        max_words=40
    )
    
    # Step 3: Analyze sentiment of the research
    sentiment = await analyze_sentiment(summary)
    
    # Step 4: Generate recommendations
    recommendations = await generate_creative_story(
        f"Create actionable recommendations based on: {summary}",
        "informative"
    )
    
    return {
        "topic": topic,
        "research": research_data,
        "summary": summary,
        "sentiment": sentiment,
        "recommendations": recommendations[:200] + "..."
    }

async def demo_task_chaining():
    """Demonstrate task chaining and composition."""
    print("\n🔗 5. Task Chaining and Composition")
    print("=" * 40)
    
    try:
        # Simple code analysis
        print("  🔍 Code Quality Analysis:")
        sample_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
        
result = factorial(5)
print(result)
        """
        
        analysis = await analyze_code_quality(sample_code, "python")
        print(f"    Language: {analysis.language}")
        print(f"    Complexity: {analysis.complexity}")
        print(f"    Quality Score: {analysis.quality_score}/10")
        print(f"    Issues: {len(analysis.issues)} found")
        
        # Complex chained workflow
        print("\n  🔄 Chained Analysis Workflow:")
        result = await chained_analysis_workflow("renewable energy")
        print(f"    Research points: {len(result['research'].get('key_points', []))}")
        print(f"    Summary: {result['summary'][:100]}...")
        print(f"    Sentiment: {result['sentiment'].get('sentiment', 'Unknown')}")
        
    except Exception as e:
        print(f"  ❌ Task chaining failed: {e}")


# =============================================================================
# 6. ERROR HANDLING AND VALIDATION
# =============================================================================

@task(output_format=OutputFormat.JSON, retry_count=3)
async def robust_data_extraction(text: str) -> Dict[str, Any]:
    """Extract data with robust error handling."""
    agent = Agent(
        name="robust-extractor",
        model="anthropic/claude-3-5-sonnet",
        system_prompt="Extract structured data with proper error handling and validation."
    )
    
    try:
        prompt = f"""
        Extract and validate data from: "{text}"
        
        Return JSON with:
        - extracted_data: the main data found
        - confidence: confidence level (0-1)
        - validation_status: "valid" or "invalid"
        - errors: list of any validation errors
        """
        
        response = await agent.run(prompt)
        data = extract_json_from_text(response.content)
        
        # Validate the extracted data
        if not data.get('extracted_data'):
            raise ValueError("No data extracted")
        
        if data.get('confidence', 0) < 0.5:
            raise ValueError("Confidence too low")
        
        return data
        
    except Exception as e:
        return {
            "extracted_data": None,
            "confidence": 0.0,
            "validation_status": "invalid",
            "errors": [str(e)]
        }

async def demo_error_handling():
    """Demonstrate error handling and validation in tasks."""
    print("\n⚠️ 6. Error Handling and Validation")
    print("=" * 40)
    
    test_cases = [
        "John Doe works at Example Corp, email: john@example.com",  # Valid data
        "This text has no meaningful data to extract",              # Minimal data
        "",                                                         # Empty input
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"  Test {i}: {'Valid data' if i == 1 else 'Invalid data' if i == 2 else 'Empty input'}")
            result = await robust_data_extraction(test_case)
            print(f"    Status: {result.get('validation_status', 'Unknown')}")
            print(f"    Confidence: {result.get('confidence', 0):.2f}")
            if result.get('errors'):
                print(f"    Errors: {result['errors'][0]}")
            
        except Exception as e:
            print(f"    ❌ Test {i} failed: {e}")


# =============================================================================
# 7. AGENT-TASK INTEGRATION
# =============================================================================

class TaskOrchestrator:
    """Orchestrates multiple tasks using different agents."""
    
    def __init__(self):
        self.agents = {
            "researcher": Agent(
                name="research-agent",
                model="google/gemini-1.5-pro",
                system_prompt="Research topics and provide comprehensive information."
            ),
            "writer": Agent(
                name="writing-agent", 
                model="anthropic/claude-3-5-sonnet",
                system_prompt="Create engaging, well-structured written content."
            ),
            "analyst": Agent(
                name="analysis-agent",
                model="openai/gpt-4o",
                system_prompt="Analyze data and provide insights and recommendations."
            )
        }
    
    async def create_content_pipeline(self, topic: str) -> Dict[str, Any]:
        """Create a content pipeline using multiple agents and tasks."""
        
        # Step 1: Research (using researcher agent)
        research_data = await research_topic(topic)
        
        # Step 2: Create summary (using writer agent)
        key_info = f"Research findings on {topic}: {json.dumps(research_data)}"
        summary = await summarize_text(key_info, max_words=50)
        
        # Step 3: Generate article (using writer agent)
        article_prompt = f"Write an informative article about {topic} based on: {summary}"
        article_response = await self.agents["writer"].run(article_prompt)
        
        # Step 4: Analyze sentiment and quality
        sentiment = await analyze_sentiment(article_response.content)
        
        return {
            "topic": topic,
            "research": research_data,
            "summary": summary,
            "article": article_response.content[:300] + "...",
            "sentiment": sentiment,
            "word_count": len(article_response.content.split())
        }

async def demo_agent_task_integration():
    """Demonstrate integration between agents and tasks."""
    print("\n🤝 7. Agent-Task Integration")
    print("=" * 40)
    
    try:
        orchestrator = TaskOrchestrator()
        
        print("  📖 Content Creation Pipeline:")
        result = await orchestrator.create_content_pipeline("artificial intelligence in healthcare")
        
        print(f"    Topic: {result['topic']}")
        print(f"    Research points: {len(result['research'].get('key_points', []))}")
        print(f"    Summary: {result['summary']}")
        print(f"    Article length: {result['word_count']} words")
        print(f"    Article sentiment: {result['sentiment'].get('sentiment', 'Unknown')}")
        print(f"    Article preview: {result['article'][:150]}...")
        
    except Exception as e:
        print(f"  ❌ Agent-task integration failed: {e}")


# =============================================================================
# 8. DURABLE TASK WORKFLOWS
# =============================================================================

@durable.function
async def durable_content_generation(ctx, topic: str, content_type: str) -> Dict[str, Any]:
    """Generate content with durable state management."""
    
    # Set initial state
    await ctx.state.set("topic", topic)
    await ctx.state.set("content_type", content_type)
    await ctx.state.set("stage", "starting")
    
    try:
        # Stage 1: Research
        await ctx.state.set("stage", "research")
        research_result = await research_topic(topic)
        await ctx.state.set("research_completed", True)
        await ctx.state.set("research_data", research_result)
        
        # Stage 2: Content creation
        await ctx.state.set("stage", "content_creation")
        if content_type == "summary":
            key_points = research_result.get('key_points', [])
            content = await summarize_text('. '.join(key_points), max_words=100)
        elif content_type == "story":
            content = await generate_creative_story(f"Write about {topic}", "informative")
        else:
            content = f"Generated content about {topic}"
        
        await ctx.state.set("content_completed", True)
        await ctx.state.set("content", content)
        
        # Stage 3: Analysis
        await ctx.state.set("stage", "analysis")
        sentiment = await analyze_sentiment(content)
        await ctx.state.set("analysis_completed", True)
        
        # Final result
        await ctx.state.set("stage", "completed")
        
        return {
            "topic": topic,
            "content_type": content_type,
            "content": content,
            "sentiment": sentiment,
            "research_points": len(research_result.get('key_points', [])),
            "status": "completed"
        }
        
    except Exception as e:
        await ctx.state.set("stage", "failed")
        await ctx.state.set("error", str(e))
        raise

async def demo_durable_tasks():
    """Demonstrate durable task workflows."""
    print("\n💾 8. Durable Task Workflows")
    print("=" * 40)
    
    try:
        print("  🔄 Durable Content Generation:")
        
        # This would typically run in the durable runtime
        # For demo purposes, we'll simulate the concept
        result = await durable_content_generation(None, "machine learning", "summary")
        
        print(f"    Topic: {result['topic']}")
        print(f"    Content Type: {result['content_type']}")
        print(f"    Status: {result['status']}")
        print(f"    Research Points: {result['research_points']}")
        print(f"    Content Preview: {result['content'][:150]}...")
        print(f"    Sentiment: {result['sentiment'].get('sentiment', 'Unknown')}")
        
        print("    ✅ Durable workflow completed with state persistence")
        
    except Exception as e:
        print(f"  ❌ Durable tasks failed: {e}")


# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

async def main():
    """Run all task examples."""
    print("📋 AGNT5 Task Examples")
    print("=" * 60)
    print("Demonstrating various task patterns and capabilities:")
    print("- Basic task creation and execution")
    print("- JSON extraction and structured output")
    print("- Pydantic model validation")
    print("- String processing and generation")
    print("- Task chaining and composition")
    print("- Error handling and validation")
    print("- Agent-task integration")
    print("- Durable task workflows")
    
    try:
        await demo_basic_tasks()
        await demo_json_extraction_tasks()
        await demo_pydantic_tasks()
        await demo_string_tasks()
        await demo_task_chaining()
        await demo_error_handling()
        await demo_agent_task_integration()
        await demo_durable_tasks()
        
        print("\n" + "=" * 60)
        print("✨ All task examples completed successfully!")
        print("📚 Key takeaways:")
        print("  • Tasks provide structured output validation")
        print("  • JSON extraction enables data processing")
        print("  • Pydantic models ensure type safety")
        print("  • Task chaining creates complex workflows")
        print("  • Error handling improves reliability")
        print("  • Agent-task integration enables specialization")
        print("  • Durable tasks ensure persistence and reliability")
        
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())