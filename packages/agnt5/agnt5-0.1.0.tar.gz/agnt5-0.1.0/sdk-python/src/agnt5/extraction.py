"""
Data extraction utilities for AGNT5 SDK.

Provides specialized tools for extracting structured data from text,
particularly JSON data extraction with validation and error handling.
"""

import json
import re
from typing import Any, Dict, List, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum

from .task import task, json_extraction_task, OutputFormat, TaskResult
from .types import Message, MessageRole


class ExtractionStrategy(Enum):
    """Different strategies for data extraction."""
    REGEX = "regex"
    LLM_GUIDED = "llm_guided"
    TEMPLATE_BASED = "template_based"
    HYBRID = "hybrid"


@dataclass
class ExtractionPattern:
    """Pattern for data extraction."""
    name: str
    pattern: str
    description: Optional[str] = None
    required: bool = True
    data_type: Type = str


class JSONExtractor:
    """Utility class for JSON data extraction."""
    
    def __init__(self):
        self.common_patterns = {
            "json_block": r'```json\s*(\{.*?\})\s*```',
            "json_object": r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
            "json_array": r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]',
            "code_block": r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```',
        }
    
    def extract_json_from_text(self, text: str, strategy: ExtractionStrategy = ExtractionStrategy.HYBRID) -> List[Dict[str, Any]]:
        """
        Extract JSON objects from text using various strategies.
        
        Args:
            text: Input text to extract JSON from
            strategy: Extraction strategy to use
            
        Returns:
            List of extracted JSON objects
        """
        if strategy == ExtractionStrategy.REGEX:
            return self._extract_with_regex(text)
        elif strategy == ExtractionStrategy.TEMPLATE_BASED:
            return self._extract_with_templates(text)
        elif strategy == ExtractionStrategy.HYBRID:
            return self._extract_hybrid(text)
        else:
            return self._extract_with_regex(text)  # Default fallback
    
    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON using regex patterns."""
        results = []
        
        # Try different patterns in order of specificity
        patterns = [
            self.common_patterns["json_block"],
            self.common_patterns["code_block"],
            self.common_patterns["json_object"],
            self.common_patterns["json_array"],
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                json_text = match.group(1) if match.groups() else match.group(0)
                try:
                    parsed = json.loads(json_text)
                    if isinstance(parsed, dict):
                        results.append(parsed)
                    elif isinstance(parsed, list):
                        # If it's a list of objects, add each one
                        for item in parsed:
                            if isinstance(item, dict):
                                results.append(item)
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def _extract_with_templates(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON using common templates and structures."""
        results = []
        
        # Look for common JSON-like structures
        # Pattern: key: value pairs
        key_value_pattern = r'(\w+):\s*(["\'].*?["\']|\d+(?:\.\d+)?|true|false|null)'
        matches = re.findall(key_value_pattern, text)
        
        if matches:
            # Build a JSON object from key-value pairs
            obj = {}
            for key, value in matches:
                try:
                    # Try to parse the value as JSON
                    parsed_value = json.loads(value)
                    obj[key] = parsed_value
                except json.JSONDecodeError:
                    # Keep as string if not valid JSON
                    obj[key] = value.strip('"\'')
            
            if obj:
                results.append(obj)
        
        return results
    
    def _extract_hybrid(self, text: str) -> List[Dict[str, Any]]:
        """Combine multiple extraction strategies."""
        results = []
        
        # First try regex-based extraction
        regex_results = self._extract_with_regex(text)
        results.extend(regex_results)
        
        # If no results, try template-based
        if not results:
            template_results = self._extract_with_templates(text)
            results.extend(template_results)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for result in results:
            result_str = json.dumps(result, sort_keys=True)
            if result_str not in seen:
                seen.add(result_str)
                unique_results.append(result)
        
        return unique_results
    
    def clean_and_validate_json(self, json_text: str) -> Optional[Dict[str, Any]]:
        """Clean and validate JSON text."""
        # Remove common formatting issues
        cleaned = json_text.strip()
        
        # Remove markdown code block markers
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE)
        
        # Fix common JSON issues
        cleaned = self._fix_common_json_issues(cleaned)
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"JSON validation failed: {e}")
            return None
    
    def _fix_common_json_issues(self, text: str) -> str:
        """Fix common JSON formatting issues."""
        # Fix single quotes to double quotes
        text = re.sub(r"'([^']*)':", r'"\1":', text)
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)
        
        # Fix trailing commas
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        # Fix missing commas between object properties
        text = re.sub(r'"\s*\n\s*"', '",\n"', text)
        
        # Fix unquoted keys
        text = re.sub(r'(\w+):', r'"\1":', text)
        
        return text


# Pre-built extraction tasks
@json_extraction_task(
    name="extract_json_from_text",
    description="Extract JSON objects from any text content"
)
async def extract_json_from_text(text: str, strategy: str = "hybrid") -> List[Dict[str, Any]]:
    """Extract JSON objects from text."""
    extractor = JSONExtractor()
    strategy_enum = ExtractionStrategy(strategy) if strategy in [s.value for s in ExtractionStrategy] else ExtractionStrategy.HYBRID
    return extractor.extract_json_from_text(text, strategy_enum)


@json_extraction_task(
    name="extract_structured_data",
    description="Extract structured data using LLM guidance",
    schema={
        "type": "object",
        "properties": {
            "extracted_data": {"type": "array"},
            "confidence": {"type": "number"},
            "method": {"type": "string"}
        },
        "required": ["extracted_data"]
    }
)
async def extract_structured_data(
    text: str, 
    data_description: str,
    agent: Optional['Agent'] = None
) -> Dict[str, Any]:
    """
    Extract structured data using LLM guidance.
    
    Args:
        text: Input text to extract data from
        data_description: Description of what data to extract
        agent: Optional agent to use for extraction (uses default if not provided)
        
    Returns:
        Dictionary with extracted data, confidence score, and method used
    """
    from .agent import Agent
    
    # First try regex-based extraction
    extractor = JSONExtractor()
    regex_results = extractor.extract_json_from_text(text, ExtractionStrategy.REGEX)
    
    if regex_results:
        return {
            "extracted_data": regex_results,
            "confidence": 0.8,
            "method": "regex"
        }
    
    # If no results, use LLM guidance
    if agent is None:
        agent = Agent(name="data_extractor", model="gpt-4o-mini")
    
    prompt = f"""Extract structured data from the following text. 
    
Data to extract: {data_description}

Text:
{text}

Please return the extracted data as a JSON object. If multiple items are found, return them as an array.
Focus on accuracy and completeness. If no relevant data is found, return an empty object.

Example format:
{{
    "item1": {{"field1": "value1", "field2": "value2"}},
    "item2": {{"field1": "value3", "field2": "value4"}}
}}

Extracted data:"""

    try:
        response = await agent.run(prompt)
        
        # Extract JSON from agent response
        llm_results = extractor.extract_json_from_text(response.content, ExtractionStrategy.HYBRID)
        
        return {
            "extracted_data": llm_results if llm_results else [],
            "confidence": 0.9 if llm_results else 0.1,
            "method": "llm_guided"
        }
    except Exception as e:
        return {
            "extracted_data": [],
            "confidence": 0.0,
            "method": "failed",
            "error": str(e)
        }


@json_extraction_task(
    name="clean_and_validate_json",
    description="Clean and validate JSON text for proper formatting"
)
async def clean_and_validate_json(json_text: str) -> Dict[str, Any]:
    """Clean and validate JSON text."""
    extractor = JSONExtractor()
    result = extractor.clean_and_validate_json(json_text)
    
    if result is None:
        raise ValueError("Invalid JSON that cannot be cleaned")
    
    return result


@task(
    name="extract_entities",
    description="Extract named entities and their relationships",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "type": {"type": "string"},
                        "confidence": {"type": "number"}
                    }
                }
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "relation": {"type": "string"}
                    }
                }
            }
        }
    }
)
async def extract_entities(text: str, entity_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Extract named entities from text.
    
    Args:
        text: Input text
        entity_types: Optional list of entity types to focus on
        
    Returns:
        Dictionary with entities and relationships
    """
    # This is a simplified implementation
    # In a real scenario, you'd use NLP libraries like spaCy or use LLM for extraction
    
    entities = []
    relationships = []
    
    # Simple regex-based entity extraction (can be enhanced)
    patterns = {
        "PERSON": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "PHONE": r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\) \d{3}-\d{4}\b',
        "DATE": r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b',
    }
    
    for entity_type, pattern in patterns.items():
        if entity_types is None or entity_type in entity_types:
            matches = re.finditer(pattern, text)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": entity_type,
                    "confidence": 0.8  # Simple confidence score
                })
    
    return {
        "entities": entities,
        "relationships": relationships
    }


# Utility functions for common extraction patterns
def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',
        r'\b\(\d{3}\) \d{3}-\d{4}\b',
        r'\b\d{3}\.\d{3}\.\d{4}\b',
        r'\b\d{10}\b'
    ]
    
    numbers = []
    for pattern in phone_patterns:
        numbers.extend(re.findall(pattern, text))
    
    return numbers


def extract_dates(text: str) -> List[str]:
    """Extract dates from text."""
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b',
        r'\b\d{1,2}-\d{1,2}-\d{4}\b',
        r'\b[A-Za-z]+ \d{1,2}, \d{4}\b'
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    
    return dates