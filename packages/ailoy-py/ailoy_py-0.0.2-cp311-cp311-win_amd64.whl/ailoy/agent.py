import json
import warnings
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Generator
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Literal,
    Optional,
    TypeVar,
    Union,
)
from urllib.parse import urlencode, urlparse, urlunparse

import jmespath
from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from rich.panel import Panel

from ailoy.ailoy_py import generate_uuid
from ailoy.mcp import MCPServer, MCPTool, StdioServerParameters
from ailoy.runtime import Runtime
from ailoy.tools import DocstringParsingException, TypeHintParsingException, get_json_schema

__all__ = ["Agent"]

## Types for internal data structures


class TextData(BaseModel):
    type: Literal["text"]
    text: str


class FunctionData(BaseModel):
    class FunctionBody(BaseModel):
        name: str
        arguments: Any

    type: Literal["function"]
    id: Optional[str] = None
    function: FunctionBody


class SystemMessage(BaseModel):
    role: Literal["system"]
    content: list[TextData]


class UserMessage(BaseModel):
    role: Literal["user"]
    content: list[TextData]


class AssistantMessage(BaseModel):
    role: Literal["assistant"]
    reasoning: Optional[list[TextData]] = None
    content: Optional[list[TextData]] = None
    tool_calls: Optional[list[FunctionData]] = None


class ToolMessage(BaseModel):
    role: Literal["tool"]
    name: str
    content: list[TextData]
    tool_call_id: Optional[str] = None


Message = Union[
    SystemMessage,
    UserMessage,
    AssistantMessage,
    ToolMessage,
]


class MessageOutput(BaseModel):
    class AssistantMessageDelta(BaseModel):
        content: Optional[list[TextData]] = None
        reasoning: Optional[list[TextData]] = None
        tool_calls: Optional[list[FunctionData]] = None

    message: AssistantMessageDelta
    finish_reason: Optional[Literal["stop", "tool_calls", "invalid_tool_call", "length", "error"]] = None


## Types for LLM Model Definitions

TVMModelName = Literal["Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "Qwen/Qwen3-8B"]
OpenAIModelName = Literal["gpt-4o"]
ModelName = Union[TVMModelName, OpenAIModelName]


class TVMModel(BaseModel):
    name: TVMModelName
    quantization: Optional[Literal["q4f16_1"]] = None
    mode: Optional[Literal["interactive"]] = None


class OpenAIModel(BaseModel):
    name: OpenAIModelName
    api_key: str


class ModelDescription(BaseModel):
    model_id: str
    component_type: str
    default_system_message: Optional[str] = None


model_descriptions: dict[ModelName, ModelDescription] = {
    "Qwen/Qwen3-0.6B": ModelDescription(
        model_id="Qwen/Qwen3-0.6B",
        component_type="tvm_language_model",
        default_system_message="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    ),
    "Qwen/Qwen3-1.7B": ModelDescription(
        model_id="Qwen/Qwen3-1.7B",
        component_type="tvm_language_model",
        default_system_message="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    ),
    "Qwen/Qwen3-4B": ModelDescription(
        model_id="Qwen/Qwen3-4B",
        component_type="tvm_language_model",
        default_system_message="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    ),
    "Qwen/Qwen3-8B": ModelDescription(
        model_id="Qwen/Qwen3-8B",
        component_type="tvm_language_model",
        default_system_message="You are Qwen, created by Alibaba Cloud. You are a helpful assistant.",
    ),
    "gpt-4o": ModelDescription(
        model_id="gpt-4o",
        component_type="openai",
    ),
}


class ComponentState(BaseModel):
    name: str
    valid: bool


## Types for agent's responses

_console = Console(highlight=False, force_jupyter=False, force_terminal=True)


class AgentResponseOutputText(BaseModel):
    type: Literal["output_text", "reasoning"]
    role: Literal["assistant"]
    is_type_switched: bool = False
    content: str

    def print(self):
        if self.is_type_switched:
            _console.print()  # add newline if type has been switched
        _console.print(self.content, end="", style=("yellow" if self.type == "reasoning" else None))


class AgentResponseToolCall(BaseModel):
    type: Literal["tool_call"]
    role: Literal["assistant"]
    is_type_switched: bool = False
    content: FunctionData

    def print(self):
        title = f"[magenta]Tool Call[/magenta]: [bold]{self.content.function.name}[/bold]"
        if self.content.id is not None:
            title += f" ({self.content.id})"
        panel = Panel(
            json.dumps(self.content.function.arguments, indent=2),
            title=title,
            title_align="left",
        )
        _console.print(panel)


class AgentResponseToolResult(BaseModel):
    type: Literal["tool_call_result"]
    role: Literal["tool"]
    is_type_switched: bool = False
    content: ToolMessage

    def print(self):
        try:
            # Try to parse as json
            content = json.dumps(json.loads(self.content.content[0].text), indent=2)
        except json.JSONDecodeError:
            # Use original content if not json deserializable
            content = self.content.content[0].text
        # Truncate long contents
        if len(content) > 500:
            content = content[:500] + "...(truncated)"

        title = f"[green]Tool Result[/green]: [bold]{self.content.name}[/bold]"
        if self.content.tool_call_id is not None:
            title += f" ({self.content.tool_call_id})"
        panel = Panel(
            content,
            title=title,
            title_align="left",
        )
        _console.print(panel)


class AgentResponseError(BaseModel):
    type: Literal["error"]
    role: Literal["assistant"]
    is_type_switched: bool = False
    content: str

    def print(self):
        panel = Panel(
            self.content,
            title="[bold red]Error[/bold red]",
        )
        _console.print(panel)


AgentResponse = Union[
    AgentResponseOutputText,
    AgentResponseToolCall,
    AgentResponseToolResult,
    AgentResponseError,
]

## Types and functions related to Tools

ToolDefinition = Union["BuiltinToolDefinition", "RESTAPIToolDefinition"]


class ToolDescription(BaseModel):
    name: str
    description: str
    parameters: "ToolParameters"
    return_type: Optional[dict[str, Any]] = Field(default=None, alias="return")
    model_config = ConfigDict(populate_by_name=True)


class ToolParameters(BaseModel):
    type: Literal["object"]
    properties: dict[str, "ToolParametersProperty"]
    required: Optional[list[str]] = []


class ToolParametersProperty(BaseModel):
    type: Literal["string", "number", "boolean", "object", "array", "null"]
    description: Optional[str] = None
    model_config = ConfigDict(extra="allow")


class BuiltinToolDefinition(BaseModel):
    type: Literal["builtin"]
    description: ToolDescription
    behavior: "BuiltinToolBehavior"


class BuiltinToolBehavior(BaseModel):
    output_path: Optional[str] = Field(default=None, alias="outputPath")
    model_config = ConfigDict(populate_by_name=True)


class RESTAPIToolDefinition(BaseModel):
    type: Literal["restapi"]
    description: ToolDescription
    behavior: "RESTAPIBehavior"


class RESTAPIBehavior(BaseModel):
    base_url: str = Field(alias="baseURL")
    method: Literal["GET", "POST", "PUT", "DELETE"]
    authentication: Optional[Literal["bearer"]] = None
    headers: Optional[dict[str, str]] = None
    body: Optional[str] = None
    output_path: Optional[str] = Field(default=None, alias="outputPath")
    model_config = ConfigDict(populate_by_name=True)


class Tool:
    def __init__(
        self,
        desc: ToolDescription,
        call_fn: Callable[..., Any],
    ):
        self.desc = desc
        self.call = call_fn


class ToolAuthenticator(ABC):
    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        return self.apply(request)

    @abstractmethod
    def apply(self, request: dict[str, Any]) -> dict[str, Any]:
        pass


class BearerAuthenticator(ToolAuthenticator):
    def __init__(self, token: str, bearer_format: str = "Bearer"):
        self.token = token
        self.bearer_format = bearer_format

    def apply(self, request: dict[str, Any]) -> dict[str, Any]:
        headers = request.get("headers", {})
        headers["Authorization"] = f"{self.bearer_format} {self.token}"
        return {**request, "headers": headers}


T_Retval = TypeVar("T_Retval")


def run_async(coro: Callable[..., Awaitable[T_Retval]]) -> T_Retval:
    try:
        import anyio

        # Running outside async loop
        return anyio.run(lambda: coro)
    except RuntimeError:
        import anyio.from_thread

        # Already in a running event loop: use anyio from_thread
        return anyio.from_thread.run(coro)


class Agent:
    """
    The `Agent` class provides a high-level interface for interacting with large language models (LLMs) in Ailoy.
    It abstracts the underlying runtime and VM logic, allowing users to easily send queries and receive streaming
    responses.

    Agents can be extended with external tools or APIs to provide real-time or domain-specific knowledge, enabling
    more powerful and context-aware interactions.
    """

    def __init__(
        self,
        runtime: Runtime,
        model_name: ModelName,
        system_message: Optional[str] = None,
        api_key: Optional[str] = None,
        **attrs,
    ):
        """
        Create an instance.

        :param runtime: The runtime environment associated with the agent.
        :param model_name: The name of the LLM model to use.
        :param system_message: Optional system message to set the initial assistant context.
        :param api_key: (web agent only) The API key for AI API.
        :param attrs: Additional initialization parameters (for `define_component` runtime call)
        :raises ValueError: If model name is not supported or validation fails.
        """
        self._runtime = runtime

        # Initialize component state
        self._component_state = ComponentState(
            name=generate_uuid(),
            valid=False,
        )

        # Initialize messages
        self._messages: list[Message] = []

        # Initialize system message
        self._system_message = system_message

        # Initialize tools
        self._tools: list[Tool] = []

        # Initialize MCP servers
        self._mcp_servers: list[MCPServer] = []

        # Define the component
        self.define(model_name, api_key=api_key, **attrs)

    def __del__(self):
        self.delete()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.delete()

    def define(self, model_name: ModelName, api_key: Optional[str] = None, **attrs) -> None:
        """
        Initializes the agent by defining its model in the runtime.
        This must be called before running the agent. If already initialized, this is a no-op.
        :param model_name: The name of the LLM model to use.
        :param api_key: (web agent only) The API key for AI API.
        :param attrs: Additional initialization parameters (for `define_component` runtime call)
        """
        if self._component_state.valid:
            return

        if not self._runtime.is_alive():
            raise ValueError("Runtime is currently stopped.")

        if model_name not in model_descriptions:
            raise ValueError(f"Model `{model_name}` not supported")

        model_desc = model_descriptions[model_name]

        # Add model name into attrs
        if "model" not in attrs:
            attrs["model"] = model_desc.model_id

        # Set default system message if not given; still can be None
        if self._system_message is None:
            self._system_message = model_desc.default_system_message

        self.clear_messages()

        # Add API key
        if api_key:
            attrs["api_key"] = api_key

        # Call runtime's define
        self._runtime.define(
            model_descriptions[model_name].component_type,
            self._component_state.name,
            attrs,
        )

        # Mark as defined
        self._component_state.valid = True

    def delete(self) -> None:
        """
        Deinitializes the agent and releases resources in the runtime.
        This should be called when the agent is no longer needed. If already deinitialized, this is a no-op.
        """
        if not self._component_state.valid:
            return

        if self._runtime.is_alive():
            self._runtime.delete(self._component_state.name)

        self.clear_messages()

        for mcp_server in self._mcp_servers:
            mcp_server.cleanup()

        self._component_state.valid = False

    def query(
        self,
        message: str,
        reasoning: bool = False,
    ) -> Generator[AgentResponse, None, None]:
        """
        Runs the agent with a new user message and yields streamed responses.

        :param message: The user message to send to the model.
        :param reasoning: If True, enables reasoning capabilities. (Default: False)
        :return: An iterator over the output, where each item represents either a generated token from the assistant or a tool call.
        :rtype: Iterator[:class:`AgentResponse`]
        """  # noqa: E501
        if not self._component_state.valid:
            raise ValueError("Agent is not valid. Create one or define newly.")

        if not self._runtime.is_alive():
            raise ValueError("Runtime is currently stopped.")

        self._messages.append(UserMessage(role="user", content=[{"type": "text", "text": message}]))

        prev_resp_type = None

        while True:
            infer_args = {
                "messages": [msg.model_dump(exclude_none=True) for msg in self._messages],
                "tools": [{"type": "function", "function": t.desc.model_dump(exclude_none=True)} for t in self._tools],
            }
            if reasoning:
                infer_args["reasoning"] = reasoning

            assistant_reasoning = None
            assistant_content = None
            assistant_tool_calls = None
            finish_reason = ""
            for result in self._runtime.call_iter_method(self._component_state.name, "infer", infer_args):
                msg = MessageOutput.model_validate(result)

                if msg.message.reasoning:
                    for v in msg.message.reasoning:
                        if not assistant_reasoning:
                            assistant_reasoning = [v]
                        else:
                            assistant_reasoning[0].text += v.text
                        resp = AgentResponseOutputText(
                            type="reasoning",
                            role="assistant",
                            is_type_switched=(prev_resp_type != "reasoning"),
                            content=v.text,
                        )
                        prev_resp_type = resp.type
                        yield resp
                if msg.message.content:
                    for v in msg.message.content:
                        if not assistant_content:
                            assistant_content = [v]
                        else:
                            assistant_content[0].text += v.text
                        resp = AgentResponseOutputText(
                            type="output_text",
                            role="assistant",
                            is_type_switched=(prev_resp_type != "output_text"),
                            content=v.text,
                        )
                        prev_resp_type = resp.type
                        yield resp
                if msg.message.tool_calls:
                    for v in msg.message.tool_calls:
                        if not assistant_tool_calls:
                            assistant_tool_calls = [v]
                        else:
                            assistant_tool_calls.append(v)
                        resp = AgentResponseToolCall(
                            type="tool_call",
                            role="assistant",
                            is_type_switched=True,
                            content=v,
                        )
                        prev_resp_type = resp.type
                        yield resp
                if msg.finish_reason:
                    finish_reason = msg.finish_reason
                    break

            # Append output
            self._messages.append(
                AssistantMessage(
                    role="assistant",
                    reasoning=assistant_reasoning,
                    content=assistant_content,
                    tool_calls=assistant_tool_calls,
                )
            )

            if finish_reason == "tool_calls":

                def run_tool(tool_call: FunctionData) -> ToolMessage:
                    tool_ = next(
                        (t for t in self._tools if t.desc.name == tool_call.function.name),
                        None,
                    )
                    if not tool_:
                        raise RuntimeError("Tool not found")
                    tool_result = tool_.call(**tool_call.function.arguments)
                    return ToolMessage(
                        role="tool",
                        name=tool_call.function.name,
                        content=[TextData(type="text", text=json.dumps(tool_result))],
                        tool_call_id=tool_call.id if tool_call.id else None,
                    )

                tool_call_results = [run_tool(tc) for tc in assistant_tool_calls]
                for result_msg in tool_call_results:
                    self._messages.append(result_msg)
                    resp = AgentResponseToolResult(
                        type="tool_call_result",
                        role="tool",
                        is_type_switched=True,
                        content=result_msg,
                    )
                    prev_resp_type = resp.type
                    yield resp
                # Infer again if tool calls happened
                continue

            # Finish this generator
            break

    def get_messages(self) -> list[Message]:
        """
        Get the current conversation history.
        Each item in the list represents a message from either the user or the assistant.

        :return: The conversation history so far in the form of a list.
        :rtype: list[Message]
        """
        return self._messages

    def clear_messages(self):
        """
        Clear the history of conversation messages.
        """
        self._messages.clear()
        if self._system_message is not None:
            self._messages.append(
                SystemMessage(role="system", content=[TextData(type="text", text=self._system_message)])
            )

    def print(self, resp: AgentResponse):
        resp.print()

    def add_tool(self, tool: Tool) -> None:
        """
        Adds a custom tool to the agent.

        :param tool: Tool instance to be added.
        """
        if any(t.desc.name == tool.desc.name for t in self._tools):
            warnings.warn(f'Tool "{tool.desc.name}" is already added.')
            return
        self._tools.append(tool)

    def add_py_function_tool(self, f: Callable[..., Any], desc: Optional[dict] = None):
        """
        Adds a Python function as a tool using callable.

        :param f: Function will be called when the tool invocation occured.
        :param desc: Tool description to override. If not given, parsed from docstring of function `f`.

        :raises ValueError: Docstring parsing is failed.
        :raises ValidationError: Given or parsed description is not a valid `ToolDescription`.
        """
        tool_description = None
        if desc is not None:
            tool_description = ToolDescription.model_validate(desc)

        if tool_description is None:
            try:
                json_schema = get_json_schema(f)
            except (TypeHintParsingException, DocstringParsingException) as e:
                raise ValueError("Failed to parse docstring", e)

            tool_description = ToolDescription.model_validate(json_schema.get("function", {}))

        self.add_tool(Tool(desc=tool_description, call_fn=f))

    def add_builtin_tool(self, tool_def: BuiltinToolDefinition) -> bool:
        """
        Adds a built-in tool.

        :param tool_def: The built-in tool definition.
        :returns: True if the tool was successfully added.
        :raises ValueError: If the tool type is not "builtin" or required inputs are missing.
        """
        if tool_def.type != "builtin":
            raise ValueError('Tool type is not "builtin"')

        def call(**inputs: dict[str, Any]) -> Any:
            required = tool_def.description.parameters.required or []
            for param_name in required:
                if param_name not in inputs:
                    raise ValueError(f'Parameter "{param_name}" is required but not provided')

            output = self._runtime.call(tool_def.description.name, inputs)
            if tool_def.behavior.output_path is not None:
                output = jmespath.search(tool_def.behavior.output_path, output)

            return output

        return self.add_tool(Tool(desc=tool_def.description, call_fn=call))

    def add_restapi_tool(
        self,
        tool_def: RESTAPIToolDefinition,
        authenticator: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
    ) -> bool:
        """
        Adds a REST API tool that performs external HTTP requests.

        :param tool_def: REST API tool definition.
        :param authenticator: Optional authenticator to inject into the request.
        :returns: True if the tool was successfully added.
        :raises ValueError: If the tool type is not "restapi".
        """
        if tool_def.type != "restapi":
            raise ValueError('Tool type is not "restapi"')

        behavior = tool_def.behavior

        def call(**inputs: dict[str, Any]) -> Any:
            def render_template(template: str, context: dict[str, Any]) -> tuple[str, list[str]]:
                import re

                variables = set()

                def replacer(match: re.Match):
                    key = match.group(1).strip()
                    variables.add(key)
                    return str(context.get(key, f"{{{key}}}"))

                rendered_url = re.sub(r"\$\{\s*([^}\s]+)\s*\}", replacer, template)
                return rendered_url, list(variables)

            # Handle path parameters
            url, path_vars = render_template(behavior.base_url, inputs)

            # Handle body
            if behavior.body is not None:
                body, body_vars = render_template(behavior.body, inputs)
            else:
                body, body_vars = None, []

            # Handle query parameters
            query_params = {k: v for k, v in inputs.items() if k not in set(path_vars + body_vars)}

            # Construct a full URL
            full_url = urlunparse(urlparse(url)._replace(query=urlencode(query_params)))

            # Construct a request payload
            request = {
                "url": full_url,
                "method": behavior.method,
                "headers": behavior.headers,
            }
            if body:
                request["body"] = body

            # Apply authentication
            if callable(authenticator):
                request = authenticator(request)

            # Call HTTP request
            output = None
            resp = self._runtime.call("http_request", request)
            output = json.loads(resp["body"])

            # Parse output path if defined
            if behavior.output_path is not None:
                output = jmespath.search(tool_def.behavior.output_path, output)

            return output

        return self.add_tool(Tool(desc=tool_def.description, call_fn=call))

    def add_tools_from_preset(
        self, preset_name: str, authenticator: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None
    ):
        """
        Loads tools from a predefined JSON preset file.

        :param preset_name: Name of the tool preset.
        :param authenticator: Optional authenticator to use for REST API tools.
        :raises ValueError: If the preset file is not found.
        """
        tool_presets_path = Path(__file__).parent / "presets" / "tools"
        preset_json = tool_presets_path / f"{preset_name}.json"
        if not preset_json.exists():
            raise ValueError(f'Tool preset "{preset_name}" does not exist')

        data: dict[str, dict[str, Any]] = json.loads(preset_json.read_text())
        for tool_name, tool_def in data.items():
            tool_type = tool_def.get("type", None)
            if tool_type == "builtin":
                self.add_builtin_tool(BuiltinToolDefinition.model_validate(tool_def))
            elif tool_type == "restapi":
                self.add_restapi_tool(RESTAPIToolDefinition.model_validate(tool_def), authenticator=authenticator)
            else:
                warnings.warn(f'Tool type "{tool_type}" is not supported. Skip adding tool "{tool_name}".')

    def add_tools_from_mcp_server(
        self, name: str, params: StdioServerParameters, tools_to_add: Optional[list[str]] = None
    ):
        """
        Create a MCP server and register its tools to agent.

        :param name: The unique name of the MCP server.
                     If there's already a MCP server with the same name, it raises RuntimeError.
        :param params: Parameters for connecting to the MCP stdio server.
        :param tools_to_add: Optional list of tool names to add. If None, all tools are added.
        """
        if any([s.name == name for s in self._mcp_servers]):
            raise RuntimeError(f"MCP server with name '{name}' is already registered")

        # Create and register MCP server
        mcp_server = MCPServer(name, params)
        self._mcp_servers.append(mcp_server)

        # Register tools
        for tool in mcp_server.list_tools():
            # Skip if this tool is not in the whitelist
            if tools_to_add is not None and tool.name not in tools_to_add:
                continue

            desc = ToolDescription(
                name=f"{name}/{tool.name}", description=tool.description, parameters=tool.inputSchema
            )

            def call(tool: MCPTool, **inputs: dict[str, Any]) -> list[str]:
                return mcp_server.call_tool(tool, inputs)

            self.add_tool(Tool(desc=desc, call_fn=partial(call, tool)))

    def remove_mcp_server(self, name: str):
        """
        Removes the MCP server and its tools from the agent, with terminating the MCP server process.

        :param name: The unique name of the MCP server.
                     If there's no MCP server matches the name, it raises RuntimeError.
        """
        if all([s.name != name for s in self._mcp_servers]):
            raise RuntimeError(f"MCP server with name '{name}' does not exist")

        # Remove the MCP server
        mcp_server = next(filter(lambda s: s.name == name, self._mcp_servers))
        self._mcp_servers.remove(mcp_server)
        mcp_server.cleanup()

        # Remove tools registered from the MCP server
        self._tools = list(filter(lambda t: not t.desc.name.startswith(f"{mcp_server.name}/"), self._tools))
