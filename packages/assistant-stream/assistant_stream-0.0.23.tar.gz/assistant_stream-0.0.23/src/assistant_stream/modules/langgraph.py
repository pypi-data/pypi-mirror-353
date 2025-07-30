from typing import Any
from langchain_core.messages.base import message_to_dict
from langchain_core.messages.base import BaseMessage
from assistant_stream.create_run import RunController


def merge_ai_message_chunk_dicts(chunk1_dict, chunk2_dict):
    """
    Manually merge two AIMessageChunk dictionaries.

    Args:
        chunk1_dict: Dictionary representation of first AIMessageChunk
        chunk2_dict: Dictionary representation of second AIMessageChunk

    Returns:
        Dictionary representing the merged AIMessageChunk
    """

    # Merge content - concatenate if both are strings, otherwise merge as lists
    content1 = chunk1_dict.get("content", "")
    content2 = chunk2_dict.get("content", "")

    if isinstance(content1, str) and isinstance(content2, str):
        merged_content = content1 + content2
    else:
        # Handle list content blocks
        if isinstance(content1, str):
            content1 = [{"type": "text", "text": content1}] if content1 else []
        if isinstance(content2, str):
            content2 = [{"type": "text", "text": content2}] if content2 else []
        merged_content = (content1 or []) + (content2 or [])

    # Merge additional_kwargs and response_metadata
    merged_additional_kwargs = merge_dicts(
        chunk1_dict.get("additional_kwargs", {}),
        chunk2_dict.get("additional_kwargs", {}),
    )

    merged_response_metadata = merge_dicts(
        chunk1_dict.get("response_metadata", {}),
        chunk2_dict.get("response_metadata", {}),
    )

    # Merge tool call chunks
    tool_call_chunks1 = chunk1_dict.get("tool_call_chunks", [])
    tool_call_chunks2 = chunk2_dict.get("tool_call_chunks", [])
    merged_tool_call_chunks = merge_lists(tool_call_chunks1, tool_call_chunks2)

    # Merge usage metadata if present
    usage1 = chunk1_dict.get("usage_metadata")
    usage2 = chunk2_dict.get("usage_metadata")
    merged_usage = None

    if usage1 or usage2:
        # Simple addition of usage metadata fields
        merged_usage = {}
        if usage1:
            merged_usage.update(usage1)
        if usage2:
            for key, value in usage2.items():
                if key in merged_usage and isinstance(value, (int, float)):
                    merged_usage[key] += value
                else:
                    merged_usage[key] = value

    # Handle ID selection (prefer non-run IDs)
    chunk_id = None
    candidates = [chunk1_dict.get("id"), chunk2_dict.get("id")]
    for id_ in candidates:
        if id_ and not id_.startswith("run-"):
            chunk_id = id_
            break
    else:
        # Fallback to first non-null ID
        for id_ in candidates:
            if id_:
                chunk_id = id_
                break

    # Build merged dictionary
    merged_dict = {
        "type": "AIMessageChunk",
        "content": merged_content,
        "additional_kwargs": merged_additional_kwargs,
        "response_metadata": merged_response_metadata,
        "tool_call_chunks": merged_tool_call_chunks,
        "example": chunk1_dict.get("example", False),  # Should be same for both
    }

    if merged_usage:
        merged_dict["usage_metadata"] = merged_usage

    if chunk_id:
        merged_dict["id"] = chunk_id

    return merged_dict


def append_langgraph_event(
    controller: RunController, _namespace: str, type: str, payload: Any
) -> None:
    state = controller.state

    if type == "message":
        if "messages" not in state:
            state["messages"] = []

        messages = payload[0]

        if not isinstance(messages, list):
            messages = [messages]

        for message in messages:
            if not isinstance(message, BaseMessage):
                raise TypeError(
                    f"Expected message to be BaseMessage, got {type(message)}: {message}"
                )
            message_dict = message_to_dict(message)
            is_ai_message_chunk = False

            if message_dict["type"] == "AIMessageChunk":
                message_dict["type"] = "ai"
                is_ai_message_chunk = True

            existing_message_index = None
            if "id" in message_dict:
                for i, existing_message in enumerate(state["messages"]):
                    if existing_message.get("id") == message_dict["id"]:
                        existing_message_index = i
                        break

            if existing_message_index is not None:

                if is_ai_message_chunk:
                    existing_message = state["messages"][existing_message_index]
                    new_message = merge_ai_message_chunk_dicts(
                        existing_message, message_dict
                    )
                    state["messages"][existing_message_index] = new_message
                else:
                    state["messages"][existing_message_index] = message_dict
            else:
                state["messages"].append(message_dict)

    elif type == "updates":
        for _node_name, channels in payload.items():
            if not isinstance(channels, dict):
                continue

            for channel, value in channels.items():
                if channel == "messages":
                    continue
                state[channel] = value
