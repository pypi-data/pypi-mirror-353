import os
import json
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logger = logging.getLogger(__name__)


class BlaskAPIAgent:
    """Agent for interacting with Blask API based on Swagger spec."""

    def __init__(
        self,
        swagger_url: str = None,
        login_url: str = None,
        base_url: str = None,
        username: str = None,
        password: str = None,
        llm: Optional[Any] = None,
    ):
        """Initialize the BlaskAPIAgent.

        Args:
            swagger_url: URL for the Swagger JSON specification
            login_url: URL for API authentication
            base_url: Base URL for API requests
            username: Username for API authentication
            password: Password for API authentication
            llm: Language model to use for agent operations
        """

        self.swagger_url = swagger_url or os.getenv(
            "SWAGGER_JSON_URL", "https://app.stage.blask.com/api/swagger-json"
        )
        self.login_url = login_url or os.getenv(
            "LOGIN_URL", "https://app.stage.blask.com/api/auth/sign-in"
        )
        self.base_url = base_url or os.getenv(
            "BASE_URL", "https://app.stage.blask.com/api"
        )
        self.username = username or os.getenv("BLASK_USERNAME")
        self.password = password or os.getenv("BLASK_PASSWORD")

        allowed_categories_str = os.getenv("ALLOWED_API_CATEGORIES", "[]")
        try:
            self.allowed_categories = json.loads(allowed_categories_str)
        except json.JSONDecodeError:
            self.allowed_categories = []

        self.session = requests.Session()
        self.is_authenticated = False

        self.llm = llm or ChatOpenAI(
            model="perplexity/r1-1776",
            temperature=0.1,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        self.swagger_data = None
        logger.info("BlaskAPIAgent initialized.")

    def authenticate(self) -> bool:
        """Authenticate with the Blask API.

        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if self.is_authenticated:
            logger.debug("Already authenticated.")
            return True

        payload = {"identifier": self.username, "password": self.password}

        try:
            response = self.session.post(self.login_url, json=payload)

            if response.status_code in [200, 201]:
                self.is_authenticated = True
                logger.info("Authentication successful.")
                return True
            else:
                logger.error(
                    f"Authentication error: {response.status_code} - {response.text}"
                )
                self.is_authenticated = False
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request failed: {str(e)}")
            self.is_authenticated = False
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during authentication: {str(e)}"
            )
            self.is_authenticated = False
            return False

    def load_swagger_spec(self) -> Dict:
        """Load the Swagger specification.

        Returns:
            Dict: The Swagger specification as a dictionary
        """
        if self.swagger_data:
            return self.swagger_data

        try:
            logger.info(f"Loading Swagger spec from {self.swagger_url}")
            response = self.session.get(self.swagger_url)
            response.raise_for_status()
            self.swagger_data = response.json()
            logger.info("Swagger spec loaded successfully.")
            return self.swagger_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error loading Swagger spec: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding Swagger JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"An unexpected error occurred loading Swagger spec: {str(e)}")
            return {}

    def get_endpoint_summary(self) -> Dict[str, List[Dict[str, str]]]:
        """Get a summary of available API endpoints.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary of endpoint categories
                with endpoint names and descriptions
        """
        if not self.swagger_data:
            self.load_swagger_spec()

        if not self.swagger_data:
            return {}

        summary = {}

        for path, path_info in self.swagger_data.get("paths", {}).items():
            for method, method_info in path_info.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue

                tag = method_info.get("tags", ["Other"])[0]

                if self.allowed_categories and tag not in self.allowed_categories:
                    logger.debug(
                        f"Skipping endpoint in category '{tag}' due to allow list."
                    )
                    continue

                if tag not in summary:
                    summary[tag] = []
                summary[tag].append(
                    {
                        "method": method.upper(),
                        "path": path,
                        "summary": method_info.get("summary", "No description"),
                        "operationId": method_info.get(
                            "operationId", f"{method}_{path}"
                        ),
                    }
                )

        return summary

    def get_endpoint_details(self, path: str, method: str) -> Dict:
        """Get detailed information about a specific endpoint.

        Args:
            path: The API path
            method: The HTTP method (GET, POST, etc.)

        Returns:
            Dict: Detailed information about the endpoint
        """
        if not self.swagger_data:
            self.load_swagger_spec()

        if not self.swagger_data:
            logger.warning("Swagger data not loaded, cannot get endpoint details.")
            return {}

        path_info = self.swagger_data.get("paths", {}).get(path, {})
        method_info = path_info.get(method.lower(), {})

        if not method_info:
            return {}

        parameters = method_info.get("parameters", [])
        logger.debug(f"Parameters for {method} {path}: {parameters}")

        request_body = {}
        if "requestBody" in method_info:
            content = method_info["requestBody"].get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                request_body = self._resolve_schema_ref(schema)

        responses = {}
        for status, response_info in method_info.get("responses", {}).items():
            content = response_info.get("content", {})
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                responses[status] = {
                    "description": response_info.get("description", ""),
                    "schema": self._resolve_schema_ref(schema),
                }
            else:
                responses[status] = {
                    "description": response_info.get("description", ""),
                }

        return {
            "method": method.upper(),
            "path": path,
            "summary": method_info.get("summary", ""),
            "description": method_info.get("description", ""),
            "parameters": parameters,
            "requestBody": request_body,
            "responses": responses,
        }

    def _resolve_schema_ref(self, schema: Dict) -> Dict:
        """Resolve schema references.

        Args:
            schema: Schema with potentially nested references

        Returns:
            Dict: Resolved schema
        """
        if not schema:
            return {}

        logger.debug(
            f"Resolving schema reference: {schema.get('$ref', 'inline schema')}"
        )

        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.split("/")[-1]
                return (
                    self.swagger_data.get("components", {})
                    .get("schemas", {})
                    .get(schema_name, {})
                )

        return schema

    def execute_api_call(
        self,
        path: str,
        method: str,
        path_params: Dict[str, Any] = None,
        query_params: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
    ) -> Dict:
        """Execute an API call.

        Args:
            path: The API path
            method: The HTTP method (GET, POST, etc.)
            path_params: Parameters to substitute in the path
            query_params: Query parameters
            body: Request body for POST/PUT operations

        Returns:
            Dict: API response
        """
        if not self.is_authenticated:
            if not self.authenticate():
                return {"error": "Authentication failed"}

        actual_path = path
        if path_params:
            logger.debug(f"Applying path parameters: {path_params}")
            for param, value in path_params.items():
                actual_path = actual_path.replace(f"{{{param}}}", str(value))

        url = f"{self.base_url}{actual_path}"
        logger.info(f"Executing API call: {method.upper()} {url}")
        logger.debug(f"Query Params: {query_params}")
        logger.debug(f"Request Body: {body}")

        try:
            method = method.lower()
            if method == "get":
                response = self.session.get(url, params=query_params)
            elif method == "post":
                response = self.session.post(url, params=query_params, json=body)
            elif method == "put":
                response = self.session.put(url, params=query_params, json=body)
            elif method == "delete":
                response = self.session.delete(url, params=query_params, json=body)
            elif method == "patch":
                response = self.session.patch(url, params=query_params, json=body)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return {"error": f"Unsupported HTTP method: {method}"}

            logger.debug(f"API Response Status Code: {response.status_code}")
            response.raise_for_status()

            try:
                response_json = response.json()
                logger.debug(f"API Response JSON: {response_json}")
                return response_json
            except json.JSONDecodeError:
                logger.debug(f"API Response Text (non-JSON): {response.text}")
                return {"content": response.text}

        except requests.exceptions.HTTPError as e:
            logger.error(
                f"API call failed with status {e.response.status_code}: {e.response.text}"
            )
            return {
                "error": f"API call failed with status {e.response.status_code}",
                "details": e.response.text,
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"RequestException during API call to {url}: {str(e)}")
            return {"error": f"RequestException during API call: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected exception during API call to {url}: {str(e)}")
            return {"error": f"Exception during API call: {str(e)}"}
