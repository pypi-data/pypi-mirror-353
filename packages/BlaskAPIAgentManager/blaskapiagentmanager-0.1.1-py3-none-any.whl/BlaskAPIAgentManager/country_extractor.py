import os
import logging
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta

from .agent import BlaskAPIAgent
from .utils import extract_country_ids
from .prompts import fetch_ids_prompt

load_dotenv()

logger = logging.getLogger(__name__)


class CountryIDMapping(BaseModel):
    """Dictionary mapping country names to their IDs."""

    country_mapping: Dict[str, int] = Field(
        description="Dictionary mapping country names to their IDs. Empty dict if no location specified.",
        default={},
    )


class CountryExtractor:
    """Tool for extracting country IDs from user queries."""

    def __init__(
        self, api_agent: Optional[BlaskAPIAgent] = None, llm: Optional[Any] = None
    ):
        """Initialize the CountryExtractor.

        Args:
            api_agent: BlaskAPIAgent instance
            llm: Language model to use for extraction
        """
        self.api_agent = api_agent or BlaskAPIAgent()
        self.llm = llm or ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            temperature=0.0,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.parser = JsonOutputParser(pydantic_object=CountryIDMapping)

    def extract_country_ids_from_query(self, query: str) -> Dict[str, int]:
        """Extract country IDs from a user query.

        Args:
            query: The user query to extract country IDs from

        Returns:
            Dict[str, int]: Dictionary mapping country names to their IDs.
            Empty dict if all countries should be included,
            None if no location is specified in the query.
        """
        # Get all countries with their IDs from the API
        current_time = datetime.now()
        one_month_ago = current_time - timedelta(days=30)

        date_to = current_time.strftime("%Y-%m-%d %H:%M:%S")
        date_from = one_month_ago.strftime("%Y-%m-%d %H:%M:%S")

        query_params = {"date_from": date_from, "date_to": date_to}

        country_response = self.api_agent.execute_api_call(
            path="/v1/countries", method="GET", query_params=query_params
        )

        countries_map = extract_country_ids({"GET /v1/countries": country_response})

        try:
            # Format the country data for the prompt
            country_data = []
            for name, id in countries_map.items():
                country_data.append(f"{name}: {id}")

            formatted_countries = ", ".join(country_data)

            chain = fetch_ids_prompt | self.llm | self.parser

            result = chain.invoke({"query": query, "countries": formatted_countries})

            if isinstance(result, dict):
                return result.get("country_mapping", {})
            else:
                return result.country_mapping

        except Exception as e:
            logger.error(f"Error extracting country IDs: {str(e)}")
            return {}
