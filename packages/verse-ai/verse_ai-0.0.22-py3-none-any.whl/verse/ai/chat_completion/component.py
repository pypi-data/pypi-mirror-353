from __future__ import annotations

from typing import Any

from verse.core import Component, Response, operation

from ._models import (
    ChatCompletionMessage,
    ChatCompletionResult,
    ResponseFormat,
    Stream,
    StreamOptions,
    Tool,
    ToolChoice,
)


class ChatCompletion(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @operation()
    def complete(
        self,
        messages: str | list[dict | ChatCompletionMessage],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: str | list[str] | None = None,
        n: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        tools: list[dict | Tool] | None = None,
        tool_choice: str | dict | ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        response_format: dict | ResponseFormat | None = None,
        seed: int | None = None,
        **kwargs: Any,
    ) -> Response[ChatCompletionResult]: ...

    @operation()
    def stream(
        self,
        messages: str | list[dict | ChatCompletionMessage],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: str | list[str] | None = None,
        n: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        tools: list[dict | Tool] | None = None,
        tool_choice: str | dict | ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        response_format: dict | ResponseFormat | None = None,
        seed: int | None = None,
        stream_options: StreamOptions | None = None,
        **kwargs: Any,
    ) -> Response[Stream[ChatCompletionResult]]: ...

    @operation()
    async def acomplete(
        self,
        messages: str | list[dict | ChatCompletionMessage],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: str | list[str] | None = None,
        n: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        tools: list[dict | Tool] | None = None,
        tool_choice: str | dict | ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        response_format: dict | ResponseFormat | None = None,
        seed: int | None = None,
        **kwargs: Any,
    ) -> Response[ChatCompletionResult]: ...

    @operation()
    async def astream(
        self,
        messages: str | list[dict | ChatCompletionMessage],
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        stop: str | list[str] | None = None,
        n: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        tools: list[dict | Tool] | None = None,
        tool_choice: str | dict | ToolChoice | None = None,
        parallel_tool_calls: bool | None = None,
        response_format: dict | ResponseFormat | None = None,
        seed: int | None = None,
        stream_options: StreamOptions | None = None,
        **kwargs: Any,
    ) -> Response[Stream[ChatCompletionResult]]: ...
