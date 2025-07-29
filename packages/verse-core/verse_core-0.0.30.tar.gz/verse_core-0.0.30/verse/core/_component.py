from __future__ import annotations

import uuid
from typing import Any

from ._context import ComponentContext, Context, ProviderContext
from ._operation import Operation
from ._provider import Provider
from ._response import Response


class Component:
    __provider__: Provider
    __handle__: str | None
    __unpack__: bool
    __native__: bool

    def __init__(
        self,
        **kwargs,
    ):
        self.__native__ = kwargs.pop("__native__", False)
        self.__unpack__ = kwargs.pop("__unpack__", False)
        self.__handle__ = kwargs.pop("__handle__", None)
        if "__provider__" in kwargs:
            self.__bind__(kwargs.pop("__provider__"))

    @property
    def __type__(self):
        module_name = self.__class__.__module__.rsplit(".", 1)[0]
        if "." in module_name:
            return ".".join(module_name.split(".")[-2:])
        return f"custom.{module_name}"

    def __bind__(
        self,
        provider: Provider | dict | str | None,
    ) -> None:
        if provider is None:
            return
        if isinstance(provider, Provider):
            provider.__component__ = self
            self.__provider__ = provider
        else:
            if isinstance(provider, dict):
                type = provider.pop("type")
                parameters = provider.pop("parameters", dict())
            elif isinstance(provider, str):
                type = provider
                parameters = dict()
            from ._loader import Loader

            module_name = self.__class__.__module__.rsplit(".", 1)[0]
            provider_path = f"{module_name}.providers.{type}"
            provider_instance = Loader.load_provider_instance(
                path=provider_path,
                parameters=parameters,
            )
            self.__bind__(provider=provider_instance)

    def __setup__(self, context: Context | None = None) -> None:
        self.__provider__.__setup__(context=context)

    async def __asetup__(self, context: Context | None = None) -> None:
        await self.__provider__.__asetup__(context=context)

    def __run__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        current_context = self._init_context(context)
        response = self.__provider__.__run__(
            operation=self._convert_operation(operation),
            context=current_context,
            **kwargs,
        )
        if not self.__native__ and isinstance(response, Response):
            response.native = None
        if self.__unpack__ and isinstance(response, Response):
            return response.result
        return response

    async def __arun__(
        self,
        operation: dict | str | Operation | None = None,
        context: dict | Context | None = None,
        **kwargs,
    ) -> Any:
        current_context = self._init_context(context)
        response = await self.__provider__.__arun__(
            operation=self._convert_operation(operation),
            context=current_context,
            **kwargs,
        )
        if not self.__native__ and isinstance(response, Response):
            response.native = None
        if self.__unpack__ and isinstance(response, Response):
            return response.result
        return response

    def __supports__(self, feature: str) -> bool:
        return self.__provider__.__supports__(feature)

    def __execute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        return self.__provider__.__execute__(
            statement, params, context, **kwargs
        )

    async def __aexecute__(
        self,
        statement: str,
        params: dict[str, Any] | None = None,
        context: Context | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self.__provider__.__aexecute__(
            statement, params, context, **kwargs
        )

    def _convert_operation(
        self,
        operation: dict | str | Operation | None,
    ) -> Operation | None:
        if isinstance(operation, dict):
            return Operation.from_dict(operation)
        elif isinstance(operation, str):
            return Operation(name=operation)
        return operation

    def _init_context(
        self,
        context: dict | Context | None,
    ) -> Context:
        if isinstance(context, dict):
            context = Context.from_dict(context)
        if context is not None:
            id = context.id
        else:
            id = str(uuid.uuid4())
        component_type = self.__module__.split(".")[-2]
        provider_type = self.__provider__.__module__.split(".")[-1]
        ctx = Context(
            id=id,
            component=ComponentContext(
                type=component_type,
                handle=self.__handle__,
            ),
            provider=ProviderContext(
                type=provider_type,
                handle=self.__provider__.__handle__,
            ),
            data=context.data if context else None,
        )
        return ctx
