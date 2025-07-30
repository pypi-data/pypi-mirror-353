from katalyst_agent.state import KatalystState
from katalyst_agent.utils.logger import get_logger
from katalyst_agent.utils.tools import get_tool_functions_map
from langchain_core.agents import AgentAction
from katalyst_agent.utils.error_handling import (
    ErrorType,
    create_error_message,
    classify_error,
    format_error_for_llm,
)
from langgraph.errors import GraphRecursionError
import os

REGISTERED_TOOL_FUNCTIONS_MAP = get_tool_functions_map()


def tool_runner(state: KatalystState) -> KatalystState:
    """
    Runs the tool from state.agent_outcome (an AgentAction) and appends to action_trace.
    Always returns state.

    * Primary Task: Execute the specified tool with the provided arguments.
    * State Changes:
    * Retrieves tool_name and tool_input_dict from state.agent_outcome.
    * Looks up and calls the tool function from your TOOL_REGISTRY, passing auto_approve and other necessary context.
    * Captures the observation_string (tool's return value, or an error string if the tool fails).
    * Appends the tuple (state.agent_outcome, observation_string) to state.action_trace.
    * Clears state.agent_outcome = None (as the action has been processed).
    * If the tool execution itself caused an error that should immediately halt this ReAct sub-task or even the P-n-E loop, it could set state.error_message or even state.response. (Usually, tool errors become observations for the next agent_react step).
    * Returns: The updated KatalystState.
    """
    logger = get_logger()
    logger.debug("[TOOL_RUNNER] Starting tool_runner node...")

    # Only run if agent_outcome is an AgentAction (otherwise skip)
    agent_action = state.agent_outcome
    if not isinstance(agent_action, AgentAction):
        logger.warning(
            "[TOOL_RUNNER] No AgentAction found in state.agent_outcome. Skipping tool execution."
        )
        return state

    # Extract tool name and input arguments from the AgentAction
    tool_name = agent_action.tool
    tool_input = agent_action.tool_input or {}
    logger.debug(f"[TOOL_RUNNER] Executing tool: {tool_name} with input: {tool_input}")

    # Look up the tool function in the registry
    tool_fn = REGISTERED_TOOL_FUNCTIONS_MAP.get(tool_name)
    if not tool_fn:
        # Tool not found: record error and skip execution
        observation = create_error_message(
            ErrorType.TOOL_ERROR,
            f"Tool '{tool_name}' not found in registry.",
            "TOOL_RUNNER",
        )
        logger.error(f"[TOOL_RUNNER] {observation}")
        state.error_message = observation
    else:
        try:
            # If the tool accepts auto_approve, always pass it from state
            if "auto_approve" in tool_fn.__code__.co_varnames:
                tool_input = {**tool_input, "auto_approve": state.auto_approve}
            # Resolve any relative 'path' argument using state.project_root_cwd
            tool_input_resolved = dict(tool_input)  # Make a copy
            if (
                "path" in tool_input_resolved
                and isinstance(tool_input_resolved["path"], str)
                and not os.path.isabs(tool_input_resolved["path"])
            ):
                tool_input_resolved["path"] = os.path.abspath(
                    os.path.join(state.project_root_cwd, tool_input_resolved["path"])
                )
            # Call the tool function with the provided arguments
            observation = tool_fn(**tool_input_resolved)
            logger.debug(
                f"[TOOL_RUNNER] Tool '{tool_name}' returned observation: {observation}"
            )
        except GraphRecursionError as e:
            # Handle graph recursion error by triggering replanning
            error_msg = create_error_message(
                ErrorType.GRAPH_RECURSION,
                f"Graph recursion detected: {str(e)}",
                "TOOL_RUNNER",
            )
            logger.warning(f"[TOOL_RUNNER] {error_msg}")
            state.error_message = error_msg
            observation = error_msg
        except Exception as e:
            # Catch and log any other exceptions during tool execution
            observation = create_error_message(
                ErrorType.TOOL_ERROR,
                f"Exception while running tool '{tool_name}': {e}",
                "TOOL_RUNNER",
            )
            logger.exception(f"[TOOL_RUNNER] {observation}")
            state.error_message = observation

    # Record the (AgentAction, observation) tuple in the action trace
    state.action_trace.append((agent_action, observation))
    # Clear agent_outcome after processing
    state.agent_outcome = None

    logger.debug("[TOOL_RUNNER] End of tool_runner node.")
    return state
