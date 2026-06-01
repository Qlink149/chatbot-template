"""[BOILERPLATE] OpenAI API client and LLM calling.

Do not modify per client.
"""
import json
import os

from openai import AsyncOpenAI

from src.utils.logger_config import logger

_client = None


def get_openai_client():
    """Get singleton OpenAI async client."""
    global _client
    if not _client:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _client = AsyncOpenAI(api_key=api_key)
        logger.info("OpenAI client initialized")
    return _client


async def call_llm(
    messages: list,
    tools: list = None,
    system_prompt: str = "",
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 2048,
):
    """Call OpenAI with tools support.

    Args:
        messages: Chat history messages.
        tools: Tool definitions for function calling.
        system_prompt: System instruction.
        model: Model name.
        temperature: Creativity parameter.
        max_tokens: Max response length.

    Returns:
        Tuple of (response_text, tool_calls_list).
    """
    try:
        client = get_openai_client()

        # Prepend system prompt
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        logger.info("LLM response received", extra={"model": model})

        # Parse response
        content = response.choices[0].message.content or ""
        tool_calls = response.choices[0].message.tool_calls or []

        return content, [
            {
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments),
                "id": tc.id,
            }
            for tc in tool_calls
        ]

    except Exception as e:
        logger.error("LLM call failed", extra={"error": str(e)})
        raise
