import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .prompts import synthesis_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class ResultSynthesizer:
    """Synthesizes processed API results into a coherent summary."""

    def __init__(self, llm: Optional[Any] = None):
        """Initialize the ResultSynthesizer.

        Args:
            llm: Language model to use for synthesis
        """
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.5-flash-preview-05-20:thinking",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()

    def synthesize_results(
        self,
        query: str,
        country_map: dict,
        api_results: Dict[str, Any],
        explanation: Optional[str] = None,
    ) -> str:
        """Synthesize API results into a coherent summary.

        Args:
            query: The user query
            country_map: Dictionary mapping country names to IDs
            api_results: Processed API results
            explanation: Optional explanation of the API plan

        Returns:
            str: Synthesized summary
        """
        try:
            api_results_str = json.dumps(api_results, indent=2)

            response_text = self.synthesis_chain.invoke(
                {
                    "query": query,
                    "country_map": country_map or "No location provided",
                    "api_results": api_results_str,
                    "explanation": explanation or "No explanation provided",
                }
            )

            return response_text.strip()
        except Exception as e:
            logger.error(f"Error synthesizing results: {str(e)}")
            return f"Failed to synthesize API results: {str(e)}"
