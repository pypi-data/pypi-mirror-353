from __future__ import annotations

__all__ = ["Cohere"]

from typing import Any

from verse.core import Context, NCall, Operation, Provider, Response

from .._models import TextEmbeddingResult, Usage
from .._operation import TextEmbeddingOperation
from .._operation_parser import TextEmbeddingOperationParser


class Cohere(Provider):
    api_key: str | None
    model: str | None
    input_type: str
    base_url: str | None
    client_name: str | None
    timeout: float | None
    nparams: dict

    _client: Any
    _aclient: Any

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "embed-english-v3.0",
        input_type: str = "search_query",
        base_url: str | None = None,
        client_name: str | None = None,
        timout: float | None = None,
        nparams: dict = dict(),
    ):
        """Initialize.

        Args:
            api_key:
                Cohere API key.
            model:
                Cohere model.
            input_type:
                Cohere embedding input type.
            base_url:
                Cohere base url.
            client_name:
                Cohere client name.
            timout:
                Timeout for client.
            nparams:
                Native params for Cohere client.
        """
        self.api_key = api_key
        self.model = model
        self.input_type = input_type
        self.base_url = base_url
        self.client_name = client_name
        self.timeout = timout
        self.nparams = nparams

        self._client = None
        self._aclient = None

    def __setup__(self, context: Context | None = None) -> None:
        if self._client is not None:
            return

        from cohere import Client

        self._client = Client(**self.get_client_params())

    async def __asetup__(self, context: Context | None = None) -> None:
        if self._aclient is not None:
            return

        from cohere import AsyncClient

        self._aclient = AsyncClient(**self.get_client_params())

    def get_client_params(self) -> dict:
        args: dict = {}
        if self.api_key is not None:
            args["api_key"] = self.api_key
        if self.base_url is not None:
            args["base_url"] = self.base_url
        if self.client_name is not None:
            args["client_name"] = self.client_name
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
                operation=operation, context=context, **kwargs
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
                operation=operation, context=context, **kwargs
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
            self.model,
            self.input_type,
        )
        # EMBED
        if op_parser.op_equals(TextEmbeddingOperation.EMBED):
            args = op_converter.convert_embed(texts=op_parser.get_texts())
            call = NCall(
                client.embed,
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
        # COMPLETE
        if op_parser.op_equals(TextEmbeddingOperation.EMBED):
            result = result_converter.convert_embed_result(nresult)
        return result


class ResultConverter:
    _generation_id: str
    _model: str

    def __init__(self):
        pass

    def convert_embed_result(
        self,
        nresult: Any,
    ) -> TextEmbeddingResult:
        embeddings = [e for e in nresult.embeddings]
        usage = None
        if nresult.meta.billed_units:
            usage = Usage(
                prompt_tokens=nresult.meta.billed_units.input_tokens,
                total_tokens=nresult.meta.billed_units.input_tokens,
            )
        return TextEmbeddingResult(embeddings=embeddings, usage=usage)


class OperationConverter:
    model: str | None
    input_type: str

    def __init__(
        self,
        model: str | None,
        input_type: str,
    ):
        self.model = model
        self.input_type = input_type

    def convert_embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> dict:
        args: dict = {
            "texts": texts,
            "model": self.model,
            "input_type": self.input_type,
        }
        return args
