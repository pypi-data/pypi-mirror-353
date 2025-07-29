from __future__ import annotations

__all__ = ["OpenAI"]

from typing import Any

from verse.core import Context, NCall, Operation, Provider, Response

from .._models import TextEmbeddingResult, Usage
from .._operation import TextEmbeddingOperation
from .._operation_parser import TextEmbeddingOperationParser


class OpenAI(Provider):
    model: str | None
    api_key: str | None
    organization: str | None
    project: str | None
    base_url: str | None
    timeout: float | None
    service_tier: str | None
    dimension: int | None
    nparams: dict

    _client: Any
    _aclient: Any

    def __init__(
        self,
        model: str | None = "text-embedding-3-small",
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        service_tier: str | None = None,
        dimension: int | None = None,
        nparams: dict = dict(),
    ):
        """Initialize.

        Args:
            model:
                OpenAI model to use for text embedding.
            api_key:
                OpenAI API key.
            organization:
                OpenAI organization.
            project:
                OpenAI project.
            base_url:
                OpenAI base url.
            timeout:
                Timeout for client.
            service_tier:
                OpenAI service tier.
            dimension:
                Embedding dimension.
            nparams:
                Native params for OpenAI client.
        """
        self.model = model
        self.api_key = api_key
        self.organization = organization
        self.project = project
        self.base_url = base_url
        self.timeout = timeout
        self.service_tier = service_tier
        self.dimension = dimension
        self.nparams = nparams

        self._client = None
        self._aclient = None

    def __setup__(self, context: Context | None = None) -> None:
        if self._client is not None:
            return

        from openai import OpenAI

        self._client = OpenAI(**self._get_client_params())

    async def __asetup__(self, context: Context | None = None) -> None:
        if self._aclient is not None:
            return

        from openai import AsyncOpenAI

        self._aclient = AsyncOpenAI(**self._get_client_params())

    def _get_client_params(self) -> dict[str, Any]:
        args: dict = {}
        if self.api_key is not None:
            args["api_key"] = self.api_key
        if self.organization is not None:
            args["organization"] = self.organization
        if self.project is not None:
            args["project"] = self.project
        if self.base_url is not None:
            args["base_url"] = self.base_url
        if self.timeout is not None:
            args["timeout"] = self.timeout
        args = args | self.nparams
        return args

    def __run__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        self.__setup__(context=context)
        op_parser = TextEmbeddingOperationParser(operation)
        ncall, state = self._get_ncall(
            op_parser,
            self._client,
        )
        if ncall is None:
            return super().__run__(
                operation=operation,
                context=context,
                **kwargs,
            )
        nresult = ncall.invoke()
        result = self._convert_nresult(
            nresult,
            state,
            op_parser,
        )
        return Response(result=result, native=dict(call=ncall, result=nresult))

    async def __arun__(
        self,
        operation: Operation | None = None,
        context: Context | None = None,
        **kwargs,
    ) -> Any:
        await self.__asetup__(context=context)
        op_parser = TextEmbeddingOperationParser(operation)
        ncall, state = self._get_ncall(
            op_parser,
            self._aclient,
        )
        if ncall is None:
            return await super().__arun__(
                operation=operation,
                context=context,
                **kwargs,
            )
        nresult = await ncall.ainvoke()
        result = self._convert_nresult(
            nresult,
            state,
            op_parser,
        )
        return Response(result=result, native=dict(call=ncall, result=nresult))

    def _get_ncall(
        self,
        op_parser: TextEmbeddingOperationParser,
        client: Any,
    ) -> tuple[NCall | None, dict]:
        call = None
        state: dict = {}
        nargs = op_parser.get_nargs()
        op_converter = OperationConverter(
            self.model, self.dimension, self.service_tier
        )
        # EMBED
        if op_parser.op_equals(TextEmbeddingOperation.EMBED):
            args = op_converter.convert_embed(
                texts=op_parser.get_texts(),
            )
            call = NCall(
                client.embeddings.create,
                args,
                nargs,
            )
        return call, state

    def _convert_nresult(
        self,
        nresult: Any,
        state: dict,
        op_parser: TextEmbeddingOperationParser,
    ) -> Any:
        result: Any = None
        result_converter = ResultConverter()
        # EMBED
        if op_parser.op_equals(TextEmbeddingOperation.EMBED):
            result = result_converter.convert_embed_result(
                nresult,
            )
        return result


class ResultConverter:
    def __init__(self):
        pass

    def convert_embed_result(
        self,
        nresult: Any,
    ) -> TextEmbeddingResult:
        embeddings = [e.embedding for e in nresult.data]
        usage = None
        if nresult.usage:
            usage = Usage(
                prompt_tokens=nresult.usage.prompt_tokens,
                total_tokens=nresult.usage.total_tokens,
            )
        return TextEmbeddingResult(embeddings=embeddings, usage=usage)


class OperationConverter:
    model: str | None
    dimension: int | None
    service_tier: str | None

    def __init__(
        self,
        model: str | None,
        dimension: int | None,
        service_tier: str | None,
    ):
        self.model = model
        self.dimension = dimension
        self.service_tier = service_tier

    def convert_embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> dict:
        args: dict = {"input": texts, "model": self.model}
        if self.dimension:
            args["dimensions"] = self.dimension
        return args
