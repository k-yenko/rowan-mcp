#!/usr/bin/env python3
"""
OpenRouter client for Rowan MCP server integration using STDIO transport.
This client connects to the Rowan MCP server via STDIO and uses OpenRouter's API to process queries.
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

class OpenRouterMCPClient:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # Fallback for OpenAI models

        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.session = None
        self.available_tools = []

    async def connect_to_rowan_mcp(self):
        """Connect to the Rowan MCP server via STDIO."""
        try:
            # Get the path to the virtual environment's python
            venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
            if not os.path.exists(venv_python):
                venv_python = sys.executable

            server_params = StdioServerParameters(
                command=venv_python,
                args=["-m", "rowan_mcp.server"],
                env=dict(os.environ)  # Pass current environment including .env variables
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # List available tools
                    tools_result = await session.list_tools()
                    self.available_tools = []

                    for tool in tools_result.tools:
                        tool_dict = {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {"type": "object", "properties": {}}
                        }
                        self.available_tools.append(tool_dict)

                    self.session = session
                    return True

        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            return False

    def convert_tools_for_openrouter(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to OpenRouter/OpenAI compatible format."""
        converted_tools = []
        for tool in self.available_tools:
            converted_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            converted_tools.append(converted_tool)
        return converted_tools

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Rowan MCP server via STDIO."""
        if not self.session:
            return {"error": "No active MCP session"}

        try:
            # Get the path to the virtual environment's python
            venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
            if not os.path.exists(venv_python):
                venv_python = sys.executable

            server_params = StdioServerParameters(
                command=venv_python,
                args=["-m", "rowan_mcp.server"],
                env=dict(os.environ)
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Call the tool
                    result = await session.call_tool(tool_name, arguments)

                    # Return the content
                    if hasattr(result, 'content') and result.content:
                        # Extract text content from the result
                        content_text = ""
                        for content_item in result.content:
                            if hasattr(content_item, 'text'):
                                content_text += content_item.text
                            else:
                                content_text += str(content_item)
                        return {"result": content_text}
                    else:
                        return {"result": str(result)}

        except Exception as e:
            return {"error": f"Failed to call MCP tool: {e}"}

    async def chat_with_openrouter(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3.5-sonnet",
        max_iterations: int = 5
    ) -> str:
        """Chat with OpenRouter using the available MCP tools."""

        tools = self.convert_tools_for_openrouter()

        async with httpx.AsyncClient() as client:
            current_messages = messages.copy()

            for iteration in range(max_iterations):
                # Prepare the request to OpenRouter
                request_data = {
                    "model": model,
                    "messages": current_messages,
                    "tools": tools,
                    "tool_choice": "auto"
                }

                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }

                try:
                    response = await client.post(
                        f"{self.openrouter_base_url}/chat/completions",
                        json=request_data,
                        headers=headers
                    )

                    if response.status_code != 200:
                        return f"OpenRouter API error: {response.status_code} - {response.text}"

                    response_data = response.json()

                    if "error" in response_data:
                        return f"OpenRouter error: {response_data['error']}"

                    message = response_data["choices"][0]["message"]
                    current_messages.append(message)

                    # Check if the model wants to use tools
                    if message.get("tool_calls"):
                        tool_results = []

                        for tool_call in message["tool_calls"]:
                            tool_name = tool_call["function"]["name"]
                            tool_args = json.loads(tool_call["function"]["arguments"])

                            print(f"🔧 Calling MCP tool: {tool_name} with args: {tool_args}")

                            # Call the MCP tool
                            tool_result = await self.call_mcp_tool(tool_name, tool_args)

                            # Add tool result to messages
                            tool_message = {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": json.dumps(tool_result)
                            }
                            current_messages.append(tool_message)
                            tool_results.append(tool_result)

                        # Continue the conversation with tool results
                        continue
                    else:
                        # No more tool calls, return the final response
                        return message["content"]

                except Exception as e:
                    return f"Error calling OpenRouter: {e}"

            return "Maximum iterations reached without completion"

async def main():
    """Main interactive loop."""
    client = OpenRouterMCPClient()

    print("Connecting to Rowan MCP server...")
    if not await client.connect_to_rowan_mcp():
        print("Failed to connect to MCP server")
        return

    print(f"Connected! Available tools: {[tool['name'] for tool in client.available_tools]}")
    print("\n🚀 OpenRouter + Rowan MCP Client (STDIO)")
    print("Type 'quit' to exit, 'models' to see available models")
    print("You can now ask questions and the AI will use Rowan tools as needed!\n")

    # Available models (you can expand this list)
    available_models = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemini-pro"
    ]

    current_model = "anthropic/claude-3.5-sonnet"

    while True:
        try:
            user_input = input(f"[{current_model}] You: ").strip()

            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'models':
                print("Available models:")
                for i, model in enumerate(available_models, 1):
                    print(f"{i}. {model}")
                try:
                    choice = int(input("Select model number: ")) - 1
                    if 0 <= choice < len(available_models):
                        current_model = available_models[choice]
                        print(f"Switched to {current_model}")
                    else:
                        print("Invalid choice")
                except ValueError:
                    print("Invalid input")
                continue
            elif not user_input:
                continue

            messages = [{"role": "user", "content": user_input}]

            print("AI: ", end="", flush=True)
            response = await client.chat_with_openrouter(messages, model=current_model)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())