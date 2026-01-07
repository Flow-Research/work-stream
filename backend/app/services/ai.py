"""AI service for task decomposition and claim extraction."""
import json
import uuid
from typing import Any, Optional

import httpx

from app.core.config import settings


class AIService:
    """Service for AI-powered features using Claude API."""
    
    def __init__(self):
        self.api_key = settings.claude_api_key
        self.base_url = "https://api.anthropic.com/v1"
    
    async def _call_claude(self, prompt: str, system: str = "") -> str:
        """
        Call Claude API with a prompt.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            
        Returns:
            The response text
        """
        if not self.api_key:
            raise ValueError("Claude API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4096,
                    "system": system,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    async def decompose_task(
        self,
        research_question: str,
        budget: float,
        context: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Decompose a research question into subtasks.
        
        Args:
            research_question: The research question to decompose
            budget: Total budget for the task
            context: Optional additional context
            
        Returns:
            List of proposed subtasks
        """
        system = """You are an expert research project manager. Your job is to decompose research questions into actionable subtasks.

Each subtask should be one of these types:
- discovery: Finding and collecting relevant sources
- extraction: Extracting specific information from sources
- mapping: Creating relationships between extracted information
- assembly: Compiling and organizing the extracted data
- narrative: Writing summaries and synthesis

Respond ONLY with a JSON array of subtasks. Each subtask must have:
- title: Short descriptive title
- description: Detailed description of what needs to be done
- subtask_type: One of the types above
- sequence_order: Order in which tasks should be completed (1-based)
- budget_allocation_percent: Percentage of total budget (must sum to 100)"""

        prompt = f"""Research Question: {research_question}
Total Budget: {budget}

{f'Additional Context: {context}' if context else ''}

Break this research question down into 5-7 subtasks that can be completed by human workers with AI assistance. Focus on the research synthesis workflow: discovery → extraction → mapping → assembly → narrative.

Return ONLY valid JSON array, no explanation."""

        try:
            response = await self._call_claude(prompt, system)
            # Parse JSON from response
            subtasks = json.loads(response)
            return subtasks
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            match = re.search(r'\[[\s\S]*\]', response)
            if match:
                return json.loads(match.group())
            raise ValueError("Failed to parse AI response as JSON")
    
    async def extract_claims(
        self,
        paper_id: str,
        paper_text: str,
    ) -> list[dict[str, Any]]:
        """
        Extract claims from paper text.
        
        Args:
            paper_id: The paper identifier
            paper_text: The paper text to analyze
            
        Returns:
            List of extracted claims
        """
        system = """You are an expert at extracting claims from academic papers. 

Each claim should have:
- id: A unique identifier (UUID format)
- statement: The claim statement in clear, standalone language
- claim_type: One of: finding, method, limitation, future_work
- confidence: high, medium, or low based on how strongly the paper supports this claim
- source_quote: Direct quote from the paper supporting this claim (if available)

Focus on extracting specific, verifiable claims about:
- Research findings and results
- Methods and techniques used
- Limitations acknowledged
- Future work suggested

Return ONLY valid JSON array."""

        prompt = f"""Paper ID: {paper_id}

Paper Text:
{paper_text[:8000]}  # Limit text length

Extract all significant claims from this paper. Return ONLY a JSON array of claims."""

        try:
            response = await self._call_claude(prompt, system)
            claims = json.loads(response)
            # Ensure each claim has an ID
            for claim in claims:
                if "id" not in claim:
                    claim["id"] = str(uuid.uuid4())
            return claims
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[[\s\S]*\]', response)
            if match:
                claims = json.loads(match.group())
                for claim in claims:
                    if "id" not in claim:
                        claim["id"] = str(uuid.uuid4())
                return claims
            raise ValueError("Failed to parse AI response as JSON")
    
    async def synthesize(
        self,
        claims: list[dict],
        format: str = "summary",
    ) -> str:
        """
        Synthesize claims into coherent content.
        
        Args:
            claims: List of claims to synthesize
            format: Output format (summary or structured)
            
        Returns:
            Synthesized content
        """
        system = """You are an expert at synthesizing research findings. Your job is to combine multiple claims from different sources into a coherent narrative or structured analysis."""

        claims_text = "\n".join([
            f"- [{c.get('claim_type', 'finding')}] {c.get('statement', '')}"
            for c in claims
        ])

        if format == "summary":
            prompt = f"""Synthesize these research claims into a coherent summary:

{claims_text}

Write a clear, well-organized summary that:
1. Groups related findings together
2. Notes any contradictions or debates
3. Highlights the most significant findings
4. Maintains academic tone

Length: 500-1000 words"""
        else:
            prompt = f"""Synthesize these research claims into a structured analysis:

{claims_text}

Create a structured analysis with:
1. Main themes/categories
2. Key findings under each theme
3. Areas of agreement
4. Areas of debate/contradiction
5. Research gaps identified

Use markdown formatting."""

        return await self._call_claude(prompt, system)
