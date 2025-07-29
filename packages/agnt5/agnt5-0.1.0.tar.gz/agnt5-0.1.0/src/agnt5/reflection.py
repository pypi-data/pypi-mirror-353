"""
Reflection capabilities for AGNT5 SDK.

Provides self-reflection, meta-cognition, and performance evaluation
capabilities for agents to improve their responses and learn from experience.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .types import Message, MessageRole
from .task import task, OutputFormat
from .tracing import trace_agent_run, span, traced, log, TraceLevel

logger = logging.getLogger(__name__)


class ReflectionType(Enum):
    """Types of reflection."""
    RESPONSE_QUALITY = "response_quality"
    GOAL_ACHIEVEMENT = "goal_achievement"
    PROCESS_EVALUATION = "process_evaluation"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_REVIEW = "performance_review"


class ReflectionLevel(Enum):
    """Levels of reflection depth."""
    SURFACE = "surface"  # Basic quality check
    ANALYTICAL = "analytical"  # Detailed analysis
    METACOGNITIVE = "metacognitive"  # Deep self-awareness


@dataclass
class ReflectionCriteria:
    """Criteria for reflection evaluation."""
    name: str
    description: str
    weight: float = 1.0
    min_score: float = 0.0
    max_score: float = 10.0


@dataclass 
class ReflectionResult:
    """Result of a reflection process."""
    reflection_type: ReflectionType
    level: ReflectionLevel
    overall_score: float
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection_type": self.reflection_type.value,
            "level": self.level.value,
            "overall_score": self.overall_score,
            "criteria_scores": self.criteria_scores,
            "insights": self.insights,
            "improvements": self.improvements,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class ReflectionEngine:
    """Engine for conducting various types of reflection."""
    
    def __init__(self):
        self.default_criteria = {
            ReflectionType.RESPONSE_QUALITY: [
                ReflectionCriteria("accuracy", "How accurate is the response?", weight=2.0),
                ReflectionCriteria("completeness", "How complete is the response?", weight=1.5),
                ReflectionCriteria("clarity", "How clear and understandable is the response?", weight=1.0),
                ReflectionCriteria("relevance", "How relevant is the response to the question?", weight=2.0),
                ReflectionCriteria("helpfulness", "How helpful is the response to the user?", weight=1.5),
            ],
            ReflectionType.GOAL_ACHIEVEMENT: [
                ReflectionCriteria("goal_alignment", "How well aligned is the response with stated goals?", weight=2.0),
                ReflectionCriteria("task_completion", "How completely was the task accomplished?", weight=2.0),
                ReflectionCriteria("efficiency", "How efficiently was the goal achieved?", weight=1.0),
            ],
            ReflectionType.PROCESS_EVALUATION: [
                ReflectionCriteria("reasoning_quality", "Quality of the reasoning process", weight=2.0),
                ReflectionCriteria("tool_usage", "Appropriateness of tool usage", weight=1.5),
                ReflectionCriteria("information_gathering", "Effectiveness of information gathering", weight=1.0),
                ReflectionCriteria("decision_making", "Quality of decision making", weight=1.5),
            ]
        }
    
    async def reflect(
        self,
        reflection_type: ReflectionType,
        level: ReflectionLevel,
        context: Dict[str, Any],
        agent: Optional['Agent'] = None,
        custom_criteria: Optional[List[ReflectionCriteria]] = None
    ) -> ReflectionResult:
        """
        Conduct reflection of specified type and level.
        
        Args:
            reflection_type: Type of reflection to conduct
            level: Depth level of reflection
            context: Context information for reflection
            agent: Agent to use for reflection (if not provided, creates one)
            custom_criteria: Custom criteria for evaluation
            
        Returns:
            ReflectionResult with scores, insights, and improvements
        """
        with traced(f"reflection.{reflection_type.value}") as reflection_span:
            reflection_span.set_attribute("reflection.type", reflection_type.value)
            reflection_span.set_attribute("reflection.level", level.value)
            
            # Get criteria for evaluation
            criteria = custom_criteria or self.default_criteria.get(reflection_type, [])
            
            # Use provided agent or create a reflection-focused one
            if agent is None:
                from .agent import Agent
                agent = Agent(
                    name="reflection_agent",
                    model="gpt-4o",
                    system_prompt="You are a metacognitive AI assistant specialized in reflection and self-evaluation. Provide thoughtful, honest assessments."
                )
            
            # Conduct reflection based on type and level
            if reflection_type == ReflectionType.RESPONSE_QUALITY:
                return await self._reflect_on_response_quality(context, criteria, level, agent)
            elif reflection_type == ReflectionType.GOAL_ACHIEVEMENT:
                return await self._reflect_on_goal_achievement(context, criteria, level, agent)
            elif reflection_type == ReflectionType.PROCESS_EVALUATION:
                return await self._reflect_on_process(context, criteria, level, agent)
            elif reflection_type == ReflectionType.ERROR_ANALYSIS:
                return await self._reflect_on_errors(context, criteria, level, agent)
            else:
                return await self._reflect_generic(reflection_type, context, criteria, level, agent)
    
    async def _reflect_on_response_quality(
        self,
        context: Dict[str, Any],
        criteria: List[ReflectionCriteria],
        level: ReflectionLevel,
        agent: 'Agent'
    ) -> ReflectionResult:
        """Reflect on the quality of a response."""
        user_query = context.get("user_query", "")
        agent_response = context.get("agent_response", "")
        
        prompt = self._build_reflection_prompt(
            reflection_type="response quality",
            level=level,
            criteria=criteria,
            context_description=f"""
User Query: {user_query}
Agent Response: {agent_response}

Evaluate the agent's response quality based on the criteria provided.
""")
        
        return await self._execute_reflection(
            ReflectionType.RESPONSE_QUALITY,
            level,
            criteria,
            prompt,
            agent,
            context
        )
    
    async def _reflect_on_goal_achievement(
        self,
        context: Dict[str, Any],
        criteria: List[ReflectionCriteria],
        level: ReflectionLevel,
        agent: 'Agent'
    ) -> ReflectionResult:
        """Reflect on how well goals were achieved."""
        goals = context.get("goals", [])
        actions_taken = context.get("actions_taken", [])
        outcomes = context.get("outcomes", [])
        
        prompt = self._build_reflection_prompt(
            reflection_type="goal achievement",
            level=level,
            criteria=criteria,
            context_description=f"""
Goals: {goals}
Actions Taken: {actions_taken}
Outcomes: {outcomes}

Evaluate how well the stated goals were achieved.
""")
        
        return await self._execute_reflection(
            ReflectionType.GOAL_ACHIEVEMENT,
            level,
            criteria,
            prompt,
            agent,
            context
        )
    
    async def _reflect_on_process(
        self,
        context: Dict[str, Any],
        criteria: List[ReflectionCriteria],
        level: ReflectionLevel,
        agent: 'Agent'
    ) -> ReflectionResult:
        """Reflect on the process used to complete a task."""
        process_steps = context.get("process_steps", [])
        tools_used = context.get("tools_used", [])
        reasoning = context.get("reasoning", "")
        
        prompt = self._build_reflection_prompt(
            reflection_type="process evaluation",
            level=level,
            criteria=criteria,
            context_description=f"""
Process Steps: {process_steps}
Tools Used: {tools_used}
Reasoning: {reasoning}

Evaluate the process and methodology used.
""")
        
        return await self._execute_reflection(
            ReflectionType.PROCESS_EVALUATION,
            level,
            criteria,
            prompt,
            agent,
            context
        )
    
    async def _reflect_on_errors(
        self,
        context: Dict[str, Any],
        criteria: List[ReflectionCriteria],
        level: ReflectionLevel,
        agent: 'Agent'
    ) -> ReflectionResult:
        """Reflect on errors and failures."""
        errors = context.get("errors", [])
        attempted_solutions = context.get("attempted_solutions", [])
        
        prompt = self._build_reflection_prompt(
            reflection_type="error analysis",
            level=level,
            criteria=criteria or [
                ReflectionCriteria("error_identification", "How well were errors identified?"),
                ReflectionCriteria("root_cause_analysis", "Quality of root cause analysis"),
                ReflectionCriteria("solution_appropriateness", "How appropriate were the attempted solutions?"),
            ],
            context_description=f"""
Errors Encountered: {errors}
Attempted Solutions: {attempted_solutions}

Analyze the errors and the approach to handling them.
""")
        
        return await self._execute_reflection(
            ReflectionType.ERROR_ANALYSIS,
            level,
            criteria,
            prompt,
            agent,
            context
        )
    
    async def _reflect_generic(
        self,
        reflection_type: ReflectionType,
        context: Dict[str, Any],
        criteria: List[ReflectionCriteria],
        level: ReflectionLevel,
        agent: 'Agent'
    ) -> ReflectionResult:
        """Generic reflection for custom types."""
        prompt = self._build_reflection_prompt(
            reflection_type=reflection_type.value,
            level=level,
            criteria=criteria,
            context_description=f"Context: {json.dumps(context, indent=2)}"
        )
        
        return await self._execute_reflection(
            reflection_type,
            level,
            criteria,
            prompt,
            agent,
            context
        )
    
    def _build_reflection_prompt(
        self,
        reflection_type: str,
        level: ReflectionLevel,
        criteria: List[ReflectionCriteria],
        context_description: str
    ) -> str:
        """Build a prompt for reflection."""
        level_instructions = {
            ReflectionLevel.SURFACE: "Provide a quick, high-level evaluation.",
            ReflectionLevel.ANALYTICAL: "Provide a detailed analysis with specific examples and reasoning.",
            ReflectionLevel.METACOGNITIVE: "Provide deep introspection, considering thinking patterns, biases, and meta-level insights."
        }
        
        criteria_text = "\n".join([
            f"- {criterion.name}: {criterion.description} (weight: {criterion.weight})"
            for criterion in criteria
        ])
        
        return f"""You are conducting a {reflection_type} reflection at the {level.value} level.

{level_instructions[level]}

{context_description}

Evaluation Criteria:
{criteria_text}

Please provide:
1. A score (0-10) for each criterion
2. An overall weighted score
3. Key insights about what went well and what could be improved
4. Specific recommendations for improvement
5. Any meta-level observations about the thinking process

Format your response as JSON:
{{
    "criteria_scores": {{"criterion_name": score, ...}},
    "overall_score": weighted_average,
    "insights": ["insight1", "insight2", ...],
    "improvements": ["improvement1", "improvement2", ...],
    "meta_observations": ["observation1", "observation2", ...]
}}

Be honest, constructive, and specific in your evaluation."""
    
    async def _execute_reflection(
        self,
        reflection_type: ReflectionType,
        level: ReflectionLevel,
        criteria: List[ReflectionCriteria],
        prompt: str,
        agent: 'Agent',
        context: Dict[str, Any]
    ) -> ReflectionResult:
        """Execute the reflection and parse results."""
        try:
            # Get reflection response from agent
            response = await agent.run(prompt)
            
            # Extract JSON from response
            from .extraction import JSONExtractor
            extractor = JSONExtractor()
            json_results = extractor.extract_json_from_text(response.content)
            
            if not json_results:
                # Fallback: create a basic reflection result
                return ReflectionResult(
                    reflection_type=reflection_type,
                    level=level,
                    overall_score=5.0,
                    insights=["Unable to parse detailed reflection"],
                    improvements=["Improve reflection response parsing"]
                )
            
            reflection_data = json_results[0]
            
            # Calculate overall score if not provided
            criteria_scores = reflection_data.get("criteria_scores", {})
            if "overall_score" not in reflection_data and criteria_scores:
                total_weighted_score = 0
                total_weight = 0
                
                for criterion in criteria:
                    if criterion.name in criteria_scores:
                        score = criteria_scores[criterion.name]
                        total_weighted_score += score * criterion.weight
                        total_weight += criterion.weight
                
                overall_score = total_weighted_score / total_weight if total_weight > 0 else 5.0
            else:
                overall_score = reflection_data.get("overall_score", 5.0)
            
            return ReflectionResult(
                reflection_type=reflection_type,
                level=level,
                overall_score=overall_score,
                criteria_scores=criteria_scores,
                insights=reflection_data.get("insights", []),
                improvements=reflection_data.get("improvements", []),
                metadata={
                    "meta_observations": reflection_data.get("meta_observations", []),
                    "context": context
                }
            )
            
        except Exception as e:
            logger.error(f"Reflection execution failed: {e}")
            
            # Return a fallback reflection result
            return ReflectionResult(
                reflection_type=reflection_type,
                level=level,
                overall_score=5.0,
                insights=[f"Reflection failed: {str(e)}"],
                improvements=["Fix reflection execution errors"],
                metadata={"error": str(e)}
            )


# Pre-built reflection tasks
@task(
    name="reflect_on_response",
    description="Reflect on the quality of an agent response",
    output_format=OutputFormat.JSON
)
async def reflect_on_response(
    user_query: str,
    agent_response: str,
    level: str = "analytical",
    agent: Optional['Agent'] = None
) -> Dict[str, Any]:
    """Reflect on response quality."""
    engine = ReflectionEngine()
    level_enum = ReflectionLevel(level) if level in [l.value for l in ReflectionLevel] else ReflectionLevel.ANALYTICAL
    
    context = {
        "user_query": user_query,
        "agent_response": agent_response
    }
    
    result = await engine.reflect(
        ReflectionType.RESPONSE_QUALITY,
        level_enum,
        context,
        agent
    )
    
    return result.to_dict()


@task(
    name="reflect_on_goals",
    description="Reflect on goal achievement",
    output_format=OutputFormat.JSON
)
async def reflect_on_goals(
    goals: List[str],
    actions_taken: List[str],
    outcomes: List[str],
    level: str = "analytical",
    agent: Optional['Agent'] = None
) -> Dict[str, Any]:
    """Reflect on goal achievement."""
    engine = ReflectionEngine()
    level_enum = ReflectionLevel(level) if level in [l.value for l in ReflectionLevel] else ReflectionLevel.ANALYTICAL
    
    context = {
        "goals": goals,
        "actions_taken": actions_taken,
        "outcomes": outcomes
    }
    
    result = await engine.reflect(
        ReflectionType.GOAL_ACHIEVEMENT,
        level_enum,
        context,
        agent
    )
    
    return result.to_dict()


@task(
    name="analyze_errors",
    description="Analyze errors and failures for learning",
    output_format=OutputFormat.JSON
)
async def analyze_errors(
    errors: List[str],
    attempted_solutions: List[str],
    level: str = "analytical",
    agent: Optional['Agent'] = None
) -> Dict[str, Any]:
    """Analyze errors for learning."""
    engine = ReflectionEngine()
    level_enum = ReflectionLevel(level) if level in [l.value for l in ReflectionLevel] else ReflectionLevel.ANALYTICAL
    
    context = {
        "errors": errors,
        "attempted_solutions": attempted_solutions
    }
    
    result = await engine.reflect(
        ReflectionType.ERROR_ANALYSIS,
        level_enum,
        context,
        agent
    )
    
    return result.to_dict()