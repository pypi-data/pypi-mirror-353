import os

from agents.tool import FunctionTool
from dotenv import load_dotenv

from agency_swarm.agency import Agency
from agency_swarm.agent import Agent

load_dotenv()


def run_fastapi(
    agencies: list[Agency] | None = None,
    tools: list[type[FunctionTool]] | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    app_token_env: str = "APP_TOKEN",
):
    """
    Launch a FastAPI server exposing endpoints for multiple agencies and tools.
    Each agency is deployed at /[agency-name]/get_completion and /[agency-name]/get_completion_stream.
    Each tool is deployed at /tool/[tool-name].
    """
    if (agencies is None or len(agencies) == 0) and (tools is None or len(tools) == 0):
        print("No endpoints to deploy. Please provide at least one agency or tool.")
        return

    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        from .fastapi_utils.endpoint_handlers import (
            exception_handler,
            get_verify_token,
            make_completion_endpoint,
            make_stream_endpoint,
            make_tool_endpoint,
        )
        from .fastapi_utils.request_models import BaseRequest, add_agent_validator
    except ImportError:
        print("FastAPI deployment dependencies are missing. Please install agency-swarm[fastapi] package")
        return

    app_token = os.getenv(app_token_env)
    if app_token is None or app_token == "":
        print(f"Warning: {app_token_env} is not set. Authentication will be disabled.")
    verify_token = get_verify_token(app_token)

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    endpoints = []
    agency_names = []

    if agencies:
        for idx, agency in enumerate(agencies):
            agency_name = getattr(agency, "name", None)
            if agency_name is None:
                agency_name = "agency" if len(agencies) == 1 else f"agency_{idx + 1}"
            agency_name = agency_name.replace(" ", "_")
            if agency_name in agency_names:
                raise ValueError(
                    f"Agency name {agency_name} is already in use. "
                    "Please provide a unique name in the agency's 'name' parameter."
                )
            agency_names.append(agency_name)

            # Store agent instances for easy lookup
            AGENT_INSTANCES: dict[str, Agent] = dict(agency.agents.items())

            class VerboseRequest(BaseRequest):
                verbose: bool = False

            AgencyRequest = add_agent_validator(VerboseRequest, AGENT_INSTANCES)
            AgencyRequestStreaming = add_agent_validator(BaseRequest, AGENT_INSTANCES)

            app.add_api_route(
                f"/{agency_name}/get_completion",
                make_completion_endpoint(AgencyRequest, agency, verify_token),
                methods=["POST"],
            )
            app.add_api_route(
                f"/{agency_name}/get_completion_stream",
                make_stream_endpoint(AgencyRequestStreaming, agency, verify_token),
                methods=["POST"],
            )
            endpoints.append(f"/{agency_name}/get_completion")
            endpoints.append(f"/{agency_name}/get_completion_stream")

    if tools:
        for tool in tools:
            tool_name = tool.name
            tool_handler = make_tool_endpoint(tool, verify_token)
            app.add_api_route(f"/tool/{tool_name}", tool_handler, methods=["POST"], name=tool_name)
            endpoints.append(f"/tool/{tool_name}")

    app.add_exception_handler(Exception, exception_handler)

    print(f"Starting FastAPI server at http://{host}:{port}")
    print("Created endpoints:\n" + "\n".join(endpoints))
    uvicorn.run(app, host=host, port=port)
