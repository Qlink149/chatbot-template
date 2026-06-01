"""[BOILERPLATE] Multi-turn LLM orchestration with tools.

Do not modify per client. Tool execution is client-specific.
"""
import json

from src.adapters.openai_adapter import call_llm
from src.utils.logger_config import logger


async def chat_agent(
    user_message: str,
    chat_history: list,
    session_id: str,
    system_prompt: str,
    tools: list = None,
    model: str = "gpt-4o-mini",
):
    """Multi-turn LLM with tool support.

    Orchestrates: call → tool exec → final response.

    Args:
        user_message: Latest user input.
        chat_history: Previous messages.
        session_id: Session identifier.
        system_prompt: System instruction.
        tools: Tool definitions.
        model: LLM model name.

    Returns:
        Final response text.
    """
    try:
        # Format history (last 10 messages)
        messages = [
            {
                "role": "user" if h["role"] == "user" else "assistant",
                "content": h["content"],
            }
            for h in (chat_history[-10:] or [])
        ]
        messages.append({"role": "user", "content": user_message})

        # Step 1: Call LLM
        response_text, tool_calls = await call_llm(
            messages=messages,
            tools=tools,
            system_prompt=system_prompt,
            model=model,
        )

        # Step 2: If tools called, execute and refetch
        if tool_calls:
            tool_results = []
            for tc in tool_calls:
                result = await _execute_tool(
                    tc["name"], tc["arguments"], session_id
                )
                tool_results.append(
                    {
                        "tool_call_id": tc["id"],
                        "result": result,
                    }
                )

            # Step 3: Call LLM again with tool results
            messages.append({"role": "assistant", "content": response_text})
            for tr in tool_results:
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(tr["result"]),
                        "tool_call_id": tr["tool_call_id"],
                    }
                )

            response_text, _ = await call_llm(
                messages=messages,
                system_prompt=system_prompt,
                model=model,
            )

        return response_text or "I couldn't generate a response."

    except Exception as e:
        logger.error(
            "Chat agent error", extra={"error": str(e), "session": session_id}
        )
        raise


async def _execute_tool(tool_name: str, args: dict, session_id: str) -> dict:
    """[CLIENT-SPECIFIC] Execute tool by name.

    Args:
        tool_name: Name of tool to execute.
        args: Tool arguments.
        session_id: Session identifier.

    Returns:
        Tool execution result.
    """
    logger.info(
        f"Tool called: {tool_name}",
        extra={"args": args, "session": session_id},
    )
    # [CLIENT-SPECIFIC] Add your tool implementations here
    return {"status": "executed", "tool": tool_name}
