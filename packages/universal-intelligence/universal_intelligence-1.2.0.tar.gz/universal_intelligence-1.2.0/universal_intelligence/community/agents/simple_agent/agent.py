from typing import Any, ClassVar

import yaml

from ....community.__utils__.logger import Color, Logger, LogLevel
from ....community.models.local.default import UniversalModel
from ....core.universal_agent import AbstractUniversalAgent
from ....core.universal_model import AbstractUniversalModel
from ....core.universal_tool import AbstractUniversalTool
from ....core.utils.types import Compatibility, Contract, Message, Requirement


class UniversalAgent(AbstractUniversalAgent):
    """A simple generic agent that can use tools and other agents to accomplish tasks"""

    _contract: ClassVar[Contract] = {
        "name": "Simple Agent",
        "description": "A simple generic agent that can use tools and other agents to accomplish tasks",
        "methods": [
            {
                "name": "process",
                "description": "Process text input through the agent, using available tools and team members as needed",
                "arguments": [
                    {
                        "name": "input",
                        "type": "str | List[Message]",
                        "schema": {
                            "nested": [
                                {
                                    "name": "role",
                                    "type": "str",
                                    "schema": {"pattern": "^(system|user|assistant)$"},
                                    "description": "The role of the message sender",
                                    "required": True,
                                },
                                {
                                    "name": "content",
                                    "type": "str",
                                    "schema": {},
                                    "description": "The content of the message",
                                    "required": True,
                                },
                            ]
                        },
                        "description": "Input string or list of messages in chat format",
                        "required": True,
                    },
                    {
                        "name": "context",
                        "type": "List[Any]",
                        "schema": {},
                        "description": "Optional context items to prepend as system messages",
                        "required": False,
                    },
                    {
                        "name": "configuration",
                        "type": "Dict",
                        "schema": {},
                        "description": "Optional runtime configuration",
                        "required": False,
                    },
                    {
                        "name": "remember",
                        "type": "bool",
                        "schema": {},
                        "description": "Whether to remember this interaction in history",
                        "required": False,
                    },
                    {
                        "name": "stream",
                        "type": "bool",
                        "schema": {},
                        "description": "Whether to stream output asynchronously",
                        "required": False,
                    },
                    {
                        "name": "extra_tools",
                        "type": "List[AbstractUniversalTool]",
                        "schema": {},
                        "description": "Additional tools for this specific inference",
                        "required": False,
                    },
                    {
                        "name": "extra_team",
                        "type": "List[AbstractUniversalAgent]",
                        "schema": {},
                        "description": "Additional agents for this specific inference",
                        "required": False,
                    },
                    {
                        "name": "keep_alive",
                        "type": "bool",
                        "schema": {},
                        "description": "Keep underlaying model loaded for faster consecutive interactions",
                        "required": False,
                    },
                ],
                "outputs": [
                    {
                        "type": "Tuple[Any, Dict]",
                        "schema": {
                            "nested": [
                                {
                                    "name": "response",
                                    "type": "str",
                                    "schema": {},
                                    "description": "Generated text response",
                                    "required": True,
                                },
                                {
                                    "name": "logs",
                                    "type": "Dict",
                                    "schema": {},
                                    "description": "Processing logs and metadata",
                                    "required": True,
                                },
                            ]
                        },
                        "description": "Generated response and processing logs",
                        "required": True,
                    }
                ],
            },
            {
                "name": "load",
                "description": "Load the agent's model into memory",
                "arguments": [],
                "outputs": [
                    {
                        "type": "None",
                        "schema": {},
                        "description": "No return value",
                        "required": True,
                    }
                ],
            },
            {
                "name": "loaded",
                "description": "Check if the agent's model is loaded",
                "arguments": [],
                "outputs": [
                    {
                        "type": "bool",
                        "schema": {},
                        "description": "True if the model is loaded, False otherwise",
                        "required": True,
                    }
                ],
            },
            {
                "name": "unload",
                "description": "Unload the agent's model from memory",
                "arguments": [],
                "outputs": [
                    {
                        "type": "None",
                        "schema": {},
                        "description": "No return value",
                        "required": True,
                    }
                ],
            },
            {
                "name": "reset",
                "description": "Reset the agent's chat history",
                "arguments": [],
                "outputs": [
                    {
                        "type": "None",
                        "schema": {},
                        "description": "No return value",
                        "required": True,
                    }
                ],
            },
            {
                "name": "connect",
                "description": "Connect additional tools and agents",
                "arguments": [
                    {
                        "name": "universal_tools",
                        "type": "List[AbstractUniversalTool]",
                        "schema": {},
                        "description": "Additional tools to connect",
                        "required": False,
                    },
                    {
                        "name": "universal_agents",
                        "type": "List[AbstractUniversalAgent]",
                        "schema": {},
                        "description": "Additional agents to connect",
                        "required": False,
                    },
                ],
                "outputs": [
                    {
                        "type": "None",
                        "schema": {},
                        "description": "No return value",
                        "required": True,
                    }
                ],
            },
            {
                "name": "disconnect",
                "description": "Disconnect tools and agents",
                "arguments": [
                    {
                        "name": "universal_tools",
                        "type": "List[AbstractUniversalTool]",
                        "schema": {},
                        "description": "Tools to disconnect",
                        "required": False,
                    },
                    {
                        "name": "universal_agents",
                        "type": "List[AbstractUniversalAgent]",
                        "schema": {},
                        "description": "Agents to disconnect",
                        "required": False,
                    },
                ],
                "outputs": [
                    {
                        "type": "None",
                        "schema": {},
                        "description": "No return value",
                        "required": True,
                    }
                ],
            },
        ],
    }

    _requirements: ClassVar[list[Requirement]] = []  # No special requirements for this example agent

    _compatibility: ClassVar[list[Compatibility]] = [
        {
            "engine": "any",  # Depends on the model used
            "quantization": "any",  # Depends on the model used
            "devices": ["cuda", "mps", "cpu"],
            "memory": 0.0,  # Depends on the model used
            "dependencies": ["pyyaml"],
            "precision": 4,  # Depends on the model used
        }
    ]

    _default_tools: ClassVar[list[AbstractUniversalTool]] = []  # may include any tools by default
    _default_team: ClassVar[list[AbstractUniversalAgent]] = []  # may include any agents by default

    @classmethod
    def contract(cls) -> Contract:
        return cls._contract.copy()

    @classmethod
    def compatibility(cls) -> list[Compatibility]:
        return cls._compatibility.copy()

    @classmethod
    def requirements(cls) -> list[Requirement]:
        return cls._requirements.copy()

    def __init__(
        self,
        model: AbstractUniversalModel | None = None,
        expand_tools: list[AbstractUniversalTool] | None = None,
        expand_team: list["AbstractUniversalAgent"] | None = None,
        verbose: bool | str = "DEFAULT",
        configuration: dict | None = None,
    ) -> None:
        """Initialize the example agent with a model and optional tools/team members."""
        self._log_level = LogLevel.NONE
        if verbose:
            if isinstance(verbose, bool):
                self._log_level = LogLevel.DEFAULT if verbose else LogLevel.NONE
            elif isinstance(verbose, str) and verbose.upper() in LogLevel.__members__:
                self._log_level = LogLevel[verbose.upper()]
            else:
                raise ValueError(f"Invalid verbose value: {verbose} (must be bool or str)")

        with Logger(self._log_level) as logger:
            logger.print(message=f'* Initializing agent.. ({self._contract["name"]}) *\n', color=Color.WHITE)

            logger.print(prefix="Agent", message="Setting model..", color=Color.GRAY)
            self.model = model if model is not None else UniversalModel(verbose=verbose if self._log_level == LogLevel.DEBUG else "NONE")
            logger.print(prefix="Agent", message="Setting tools..", color=Color.GRAY)
            self.tools = self._default_tools + (expand_tools if expand_tools else [])
            logger.print(prefix="Agent", message="Setting team..", color=Color.GRAY)
            self.team = self._default_team + (expand_team if expand_team else [])
            logger.print(prefix="Agent", message="Configuring..", color=Color.GRAY)
            self._configuration = configuration if configuration else {}
            logger.print(prefix="Agent", message="Initialization complete\n", color=Color.GREEN)

    def _plan_dependency_calls(
        self,
        query: str,
        extra_tools: list[AbstractUniversalTool] | None = None,
        extra_team: list["AbstractUniversalAgent"] | None = None,
    ) -> list[dict]:
        """Plan the sequence of dependency calls needed to satisfy the query.

        Args:
            query: The user's query to process
            extra_tools: Additional tools available for this specific inference
            extra_team: Additional agents available for this specific inference

        Returns:
            List of planned dependency calls with their arguments
        """
        # Combine permanent and temporary dependencies
        tools = self.tools + (extra_tools if extra_tools else [])
        team = self.team + (extra_team if extra_team else [])

        # Have the model analyze available tools and team members
        tool_contracts = [tool.contract() for tool in tools]
        team_contracts = [agent.contract() for agent in team]

        # Create YAML description of available capabilities
        capabilities = {
            "available_tools": [
                {
                    "name": contract["name"],
                    "description": contract["description"],
                    "methods": contract["methods"],
                }
                for contract in tool_contracts
            ],
            "available_team": [
                {
                    "name": contract["name"],
                    "description": contract["description"],
                    "methods": contract["methods"],
                }
                for contract in team_contracts
            ],
        }

        # Ask model to plan dependency calls
        planning_prompt = f"""Given the following user query and available capabilities, analyze if and how the available tools and team members can help satisfy the query.

FIRST, determine if the query actually requires using any avalaible tools:
1. If the query is asking to perform an action (like printing, searching, calling an API, etc.) and tools exists for that, then use appropriate tools
2. If the query requires recent information, past January 1st 2023, and tools exists for that, then use appropriate tools
3. If the query requires specialized information and tools exists for that, then use appropriate tools
4. If the query is just asking for conversation (like "how are you?"), then return an empty list - DO NOT use tools
5. If the query is just asking for generic information prior to January 1st 2023, then return an empty list - DO NOT use tools

When tools ARE needed:
- Use the EXACT names and arguments as specified in the tool contracts
- Tool name must match contract's "name" field
- Method name must match contract's "methods" list and only include the method name, not the class name
- Argument names must match the method's "arguments" list
- The method's "arguments" list always is an array presenting the key/value pairs for the method's first argument, which always is an object

DO NOT invent or use tools that are not listed in the capabilities below.
DO NOT answer the query.
DO NOT explain your reasoning.
DO NOT use any other tools than the ones listed in the capabilities below.
DO NOT use any other agents than the ones listed in the capabilities below.
DO NOT include any other text than the YAML list of tools to use in order along with their arguments.
DO NOT include specify that the output is in YAML format, just return the YAML list with no starting / ending indicators or delimiters.
DO NOT include backticks or indicator that the output is in YAML format.
ONLY return the list of tools to use in order along with their arguments, in a YAML format.
Make sure to prefix the dependency_type with `-` to indicate it's a list item.

For example, to print text using the Example Tool:
- dependency_type: tool
  dependency_name: Example Tool  # Exact name from contract
  method_name: example_method    # Exact method name
  arguments:
    text: "example text"        # Exact argument name

User Query: {query}

Available Capabilities:
{yaml.dump(capabilities, sort_keys=False)}
"""

        plan_response, _ = self.model.process(planning_prompt)
        try:
            # Parse the YAML response into a list of planned calls
            planned_calls = yaml.safe_load(plan_response)
            if not isinstance(planned_calls, list):
                return []

            # Validate and limit number of calls
            valid_calls = []
            for call in planned_calls[:10]:  # Limit to 10 calls
                if all(
                    k in call
                    for k in [
                        "dependency_type",
                        "dependency_name",
                        "method_name",
                        "arguments",
                    ]
                ):
                    valid_calls.append(call)
            return valid_calls

        except yaml.YAMLError:
            return []  # Return empty plan if YAML parsing fails

    def _execute_dependency_calls(
        self,
        planned_calls: list[dict],
        extra_tools: list[AbstractUniversalTool] | None = None,
        extra_team: list["AbstractUniversalAgent"] | None = None,
    ) -> list[dict]:
        """Execute the planned sequence of dependency calls.

        Args:
            planned_calls: List of planned dependency calls with their arguments
            extra_tools: Additional tools available for this specific inference
            extra_team: Additional agents available for this specific inference

        Returns:
            List of results from executing the calls
        """
        # Combine permanent and temporary dependencies
        tools = self.tools + (extra_tools if extra_tools else [])
        team = self.team + (extra_team if extra_team else [])

        results = []

        for call in planned_calls:
            dependency_type = call["dependency_type"]
            dependency_name = call["dependency_name"]
            method_name = call["method_name"]
            arguments = call["arguments"]

            # Find the matching dependency
            if dependency_type == "tool":
                dependencies = tools
            else:  # team
                dependencies = team

            dependency = next(
                (d for d in dependencies if d.contract()["name"] == dependency_name),
                None,
            )

            if dependency is not None:
                try:
                    method = getattr(dependency, method_name)
                    contract = dependency.contract()

                    # Check if the method is marked as asynchronous in the contract
                    is_async = False
                    for method_contract in contract.get("methods", []):
                        if method_contract.get("name") == method_name:
                            is_async = method_contract.get("asynchronous", False)
                            break

                    # Call the method with provided arguments and await if async
                    if is_async:
                        import asyncio

                        result, _ = asyncio.run(method(**arguments))
                    else:
                        result, _ = method(**arguments)

                    results.append({"dependency_type": dependency_type, "dependency_name": dependency_name, "method_name": method_name, "result": result})
                except (AttributeError, TypeError):
                    continue  # Skip failed calls

        return results

    def process(
        self, input: str | list[Message], context: list[Any] | None = None, configuration: dict | None = None, remember: bool = False, stream: bool = False, extra_tools: list[AbstractUniversalTool] | None = None, extra_team: list["AbstractUniversalAgent"] | None = None, keep_alive: bool = False
    ) -> tuple[Any, dict]:
        """Process input through the agent using available tools and team members."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Invoking agent.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            # Convert input to string if it's a message list
            query = input if isinstance(input, str) else input[-1]["content"]

            # Plan dependency calls with extra tools and agents
            logger.print(prefix="Agent", message="Planning dependency calls..", color=Color.CYAN)
            planned_calls = self._plan_dependency_calls(query, extra_tools, extra_team)
            logger.print(prefix="Agent", message="Planning dependency calls..", color=Color.GRAY, replace_last_line=True)
            logger.print(prefix="Agent", message="Dependency calls planned", color=Color.GREEN)

            # Execute planned calls with extra tools and agents
            logger.print(prefix="Agent", message="Executing dependency calls..", color=Color.CYAN)
            call_results = self._execute_dependency_calls(planned_calls, extra_tools, extra_team)
            logger.print(prefix="Agent", message="Executing dependency calls..", color=Color.GRAY, replace_last_line=True)
            logger.print(prefix="Agent", message="Dependency calls executed", color=Color.GREEN)

            logger.print(prefix="Agent", message="Generating output..", color=Color.CYAN)

            # Format results as YAML for the model
            results_yaml = yaml.dump({"original_query": query, "dependency_calls": call_results}, sort_keys=False)

            # Have model generate final response using call results
            final_prompt = f"""Given the original query and results from dependency calls, generate a final response.
    If dependency calls were made, explain what actions were taken and their results.
    If no dependency calls were made, provide a direct response to the query.

    For example, if a print tool was used, confirm what was printed to the console.

    Execution Results:
    {results_yaml}
    """

            # TODO: Add streaming support
            response, logs = self.model.process(
                final_prompt,
                context=context,
                configuration=configuration,
                remember=remember,
                keep_alive=keep_alive,
            )

            logger.print(prefix="Agent", message="Generating output..", color=Color.GRAY, replace_last_line=True)
            logger.print(prefix="Agent", message="Output generated\n", color=Color.GREEN)

            return response, {
                "model_logs": logs,
                "dependency_calls": call_results,
                "stream": stream,
            }

    def load(self) -> None:
        """Load the agent's model into memory."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Loading agent.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            logger.print(prefix="Agent", message="Loading model..", color=Color.CYAN)
            self.model.load()
            logger.print(prefix="Agent", message="Loading model..", color=Color.GRAY, replace_last_line=True)
            logger.print(prefix="Agent", message="Model loaded\n", color=Color.GREEN)

    def loaded(self) -> bool:
        """Check if the agent's model is loaded"""
        with Logger(self._log_level):
            return self.model.loaded()

    def unload(self) -> None:
        """Unload the agent's model from memory."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Unloading agent.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            logger.print(prefix="Agent", message="Unloading model..", color=Color.CYAN)
            self.model.unload()
            logger.print(prefix="Agent", message="Unloading model..", color=Color.GRAY, replace_last_line=True)
            logger.print(prefix="Agent", message="Model unloaded\n", color=Color.GREEN)

    def reset(self) -> None:
        """Reset the agent's chat history."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Resetting agent history.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            logger.print(prefix="Agent", message="Resetting history..", color=Color.GRAY)
            self.model.reset()
            logger.print(prefix="Agent", message="History reset\n", color=Color.GREEN)

    def connect(
        self,
        tools: list[AbstractUniversalTool] | None = None,
        agents: list["AbstractUniversalAgent"] | None = None,
    ) -> None:
        """Connect additional tools and agents."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Connecting additional tools and agents.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            if tools:
                logger.print(prefix="Agent", message="Connecting tools..", color=Color.GRAY)
                self.tools.extend(tools)
            if agents:
                logger.print(prefix="Agent", message="Connecting agents..", color=Color.GRAY)
                self.team.extend(agents)
            logger.print(prefix="Agent", message="Tools and agents connected\n", color=Color.GREEN)

    def disconnect(
        self,
        tools: list[AbstractUniversalTool] | None = None,
        agents: list["AbstractUniversalAgent"] | None = None,
    ) -> None:
        """Disconnect tools and agents."""
        with Logger(self._log_level) as logger:
            logger.print(message=f'* Disconnecting additional tools and agents.. ({self._contract["name"]}) *\n', color=Color.WHITE)
            if tools:
                logger.print(prefix="Agent", message="Disconnecting tools..", color=Color.GRAY)
                self.tools = [t for t in self.tools if t not in tools]
            if agents:
                logger.print(prefix="Agent", message="Disconnecting agents..", color=Color.GRAY)
                self.team = [a for a in self.team if a not in agents]
            logger.print(prefix="Agent", message="Tools and agents disconnected\n", color=Color.GREEN)
