import asyncio
import json
from typing import Dict, List, Optional, Any, Union

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

from .jenkins_client import jenkins_client
from .config import jenkins_settings

server = Server("jenkins-mcp-server")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available Jenkins resources.
    Each job is exposed as a resource with a custom jenkins:// URI scheme.
    """
    try:
        jobs = jenkins_client.get_jobs()
        return [
            types.Resource(
                uri=AnyUrl(f"jenkins://job/{job['name']}"),
                name=f"Job: {job['name']}",
                description=f"Jenkins job: {job['name']} ({job['color']})",
                mimeType="application/json",
            )
            for job in jobs
        ]
    except Exception as e:
        return [
            types.Resource(
                uri=AnyUrl(f"jenkins://error"),
                name="Error connecting to Jenkins",
                description=f"Error: {str(e)}",
                mimeType="text/plain",
            )
        ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific Jenkins resource by its URI.
    """
    if uri.scheme != "jenkins":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    path = uri.path
    if path is None:
        raise ValueError("Invalid Jenkins URI")
    
    path = path.lstrip("/")
    
    if path == "error":
        return "Failed to connect to Jenkins server. Please check your configuration."
    
    # Handle job request
    if path.startswith("job/"):
        job_name = path[4:]  # Remove "job/" prefix
        try:
            job_info = jenkins_client.get_job_info(job_name)
            last_build = job_info.get('lastBuild', {})
            
            if last_build:
                build_number = last_build.get('number')
                if build_number is not None:
                    build_info = jenkins_client.get_build_info(job_name, build_number)
                    return json.dumps(build_info, indent=2)
            
            return json.dumps(job_info, indent=2)
        except Exception as e:
            return f"Error retrieving job information: {str(e)}"
    
    raise ValueError(f"Unknown Jenkins resource: {path}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for Jenkins data analysis.
    """
    return [
        types.Prompt(
            name="analyze-job-status",
            description="Analyze the status of Jenkins jobs",
            arguments=[
                types.PromptArgument(
                    name="detail_level",
                    description="Level of analysis detail (brief/detailed)",
                    required=False,
                )
            ],
        ),
        types.Prompt(
            name="analyze-build-logs",
            description="Analyze build logs for a specific job",
            arguments=[
                types.PromptArgument(
                    name="job_name",
                    description="Name of the Jenkins job",
                    required=True,
                ),
                types.PromptArgument(
                    name="build_number",
                    description="Build number (default: latest)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate prompts for Jenkins data analysis.
    """
    arguments = arguments or {}
    
    if name == "analyze-job-status":
        detail_level = arguments.get("detail_level", "brief")
        detail_prompt = " Provide extensive analysis." if detail_level == "detailed" else ""
        
        try:
            jobs = jenkins_client.get_jobs()
            jobs_text = "\n".join(
                f"- {job['name']}: Status={job['color']}" for job in jobs
            )
            
            return types.GetPromptResult(
                description="Analyze Jenkins job statuses",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Here are the current Jenkins jobs to analyze:{detail_prompt}\n\n{jobs_text}\n\n"
                                 f"Please provide insights on the status of these jobs, identify any potential issues, "
                                 f"and suggest next steps to maintain a healthy CI/CD environment.",
                        ),
                    )
                ],
            )
        except Exception as e:
            return types.GetPromptResult(
                description="Error retrieving Jenkins jobs",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"I tried to get information about Jenkins jobs but encountered an error: {str(e)}\n\n"
                                 f"Please help diagnose what might be wrong with my Jenkins connection or configuration.",
                        ),
                    )
                ],
            )
    
    elif name == "analyze-build-logs":
        job_name = arguments.get("job_name")
        build_number_str = arguments.get("build_number")
        
        if not job_name:
            raise ValueError("Missing required argument: job_name")
        
        try:
            job_info = jenkins_client.get_job_info(job_name)
            
            if build_number_str:
                build_number = int(build_number_str)
            else:
                last_build = job_info.get('lastBuild', {})
                build_number = last_build.get('number') if last_build else None
            
            if build_number is None:
                return types.GetPromptResult(
                    description=f"No builds found for job: {job_name}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"I tried to analyze build logs for the Jenkins job '{job_name}', but no builds were found.\n\n"
                                     f"Please help me understand why this job might not have any builds and suggest how to investigate.",
                            ),
                        )
                    ],
                )
            
            console_output = jenkins_client.get_build_console_output(job_name, build_number)
            
            # Limit console output size if needed
            max_length = 10000
            if len(console_output) > max_length:
                console_output = console_output[:max_length] + "\n... (output truncated)"
            
            build_info = jenkins_client.get_build_info(job_name, build_number)
            result = build_info.get('result', 'UNKNOWN')
            duration = build_info.get('duration', 0) / 1000  # Convert ms to seconds
            
            return types.GetPromptResult(
                description=f"Analysis of build #{build_number} for job: {job_name}",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Please analyze the following Jenkins build logs for job '{job_name}' (build #{build_number}).\n\n"
                                 f"Build result: {result}\n"
                                 f"Build duration: {duration} seconds\n\n"
                                 f"Console output:\n```\n{console_output}\n```\n\n"
                                 f"Please identify any issues, errors, or warnings in these logs. "
                                 f"If there are problems, suggest how to fix them. "
                                 f"If the build was successful, summarize what happened.",
                        ),
                    )
                ],
            )
        except Exception as e:
            return types.GetPromptResult(
                description=f"Error retrieving build information",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"I tried to analyze build logs for the Jenkins job '{job_name}' but encountered an error: {str(e)}\n\n"
                                 f"Please help diagnose what might be wrong with my Jenkins connection, configuration, or the job itself.",
                        ),
                    )
                ],
            )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for interacting with Jenkins.
    """
    return [
        types.Tool(
            name="trigger-build",
            description="Trigger a Jenkins job build",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_name": {"type": "string"},
                    "parameters": {
                        "type": "object",
                        "additionalProperties": {"type": ["string", "number", "boolean"]},
                    },
                },
                "required": ["job_name"],
            },
        ),
        types.Tool(
            name="stop-build",
            description="Stop a running Jenkins build",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_name": {"type": "string"},
                    "build_number": {"type": "integer"},
                },
                "required": ["job_name", "build_number"],
            },
        ),
        types.Tool(
            name="get-job-details",
            description="Get detailed information about a Jenkins job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_name": {"type": "string"},
                },
                "required": ["job_name"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for Jenkins operations.
    """
    if not arguments:
        raise ValueError("Missing arguments")
    
    if name == "trigger-build":
        job_name = arguments.get("job_name")
        parameters = arguments.get("parameters", {})
        
        if not job_name:
            raise ValueError("Missing required argument: job_name")
        
        try:
            queue_item_number = jenkins_client.build_job(job_name, parameters)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully triggered build for job '{job_name}'.\n"
                         f"Build queued with ID: {queue_item_number}\n"
                         f"Parameters: {json.dumps(parameters, indent=2) if parameters else 'None'}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to trigger build for job '{job_name}': {str(e)}"
                )
            ]
    
    elif name == "stop-build":
        job_name = arguments.get("job_name")
        build_number = arguments.get("build_number")
        
        if not job_name or build_number is None:
            raise ValueError("Missing required arguments: job_name and build_number")
        
        try:
            jenkins_client.stop_build(job_name, build_number)
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully stopped build #{build_number} for job '{job_name}'."
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to stop build #{build_number} for job '{job_name}': {str(e)}"
                )
            ]
    
    elif name == "get-job-details":
        job_name = arguments.get("job_name")
        
        if not job_name:
            raise ValueError("Missing required argument: job_name")
        
        try:
            job_info = jenkins_client.get_job_info(job_name)
            
            # Format basic job details
            job_details = {
                "name": job_info.get("name", job_name),
                "url": job_info.get("url", ""),
                "description": job_info.get("description", ""),
                "buildable": job_info.get("buildable", False),
                "lastBuild": job_info.get("lastBuild", {}),
                "lastSuccessfulBuild": job_info.get("lastSuccessfulBuild", {}),
                "lastFailedBuild": job_info.get("lastFailedBuild", {}),
            }
            
            # Add recent builds info
            if "builds" in job_info:
                recent_builds = []
                for build in job_info["builds"][:5]:  # Limit to 5 most recent builds
                    try:
                        build_info = jenkins_client.get_build_info(job_name, build["number"])
                        recent_builds.append({
                            "number": build_info.get("number"),
                            "result": build_info.get("result"),
                            "timestamp": build_info.get("timestamp"),
                            "duration": build_info.get("duration") / 1000 if build_info.get("duration") else None,
                            "url": build_info.get("url"),
                        })
                    except:
                        pass
                job_details["recentBuilds"] = recent_builds
            
            # Notify clients that resources might have changed (new builds)
            await server.request_context.session.send_resource_list_changed()
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Job details for '{job_name}':\n\n{json.dumps(job_details, indent=2)}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Failed to get details for job '{job_name}': {str(e)}"
                )
            ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    import argparse
    import sys
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Jenkins MCP Server")
    parser.add_argument("--version", action="version", version="jenkins-mcp-server 0.1.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
        print(f"Jenkins MCP Server starting - connecting to {jenkins_settings.jenkins_url}", file=sys.stderr)
    
    # Run the server using stdin/stdout streams
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="jenkins-mcp-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        print(f"Error running MCP server: {e}", file=sys.stderr)
        sys.exit(1)