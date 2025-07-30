"""
Main QwenOpenAIChatCompletionClient class for interacting with Qwen3 models.
"""

import os
import logging
from typing import Sequence, Optional, Mapping, Any, AsyncGenerator, Union, Set
import copy
from textwrap import dedent

from pydantic import BaseModel
from autogen_core.models import LLMMessage
from autogen_core.tools import Tool, ToolSchema
from autogen_core._cancellation_token import CancellationToken
from autogen_core.models._types import CreateResult, SystemMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import CreateParams

class ModelFamily:
    QWEN = "qwen"
    DEEPSEEK = "deepseek"

class ModelInfo:

    extra_kwargs: set = {"extra_body"}

    DEFAULT_MODEL_INFO = {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.QWEN,
        "structured_output": True,
        "context_window": 32_000,
        "multiple_system_messages": False,
    }

    _MODEL_INFO: dict[str, dict] = {
        "qwen-max": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen2.5-Omni-7B": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen2.5-Omni-3B": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen2.5-VL-32B-Instruct": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen2.5-VL-7B-Instruct": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen3-32B": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen3-14B": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen3-8B": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen3-4B": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "Qwen3-1.7B": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 32_000,
            "multiple_system_messages": False,
        },
        "qwen-max-latest" : {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 128_000,
            "multiple_system_messages": False,
        },
        "qwen-plus": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 128_000,
            "multiple_system_messages": False,
        },
        "qwen-plus-latest": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 128_000,
            "multiple_system_messages": False,
        },
        "qwen-turbo": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 1_000_000,
            "multiple_system_messages": False,
        },
        "qwen-turbo-latest": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 1_000_000,
            "multiple_system_messages": False,
        },
        "qwen3-235b-a22b": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 128_000,
            "multiple_system_messages": False,
        },
        "qwen3-30b-a3b": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.QWEN,
            "structured_output": True,
            "context_window": 128_000,
            "multiple_system_messages": False,
        },
        "deepseek-chat": {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.DEEPSEEK,
            "structured_output": True,
            "context_window": 64_000,
            "multiple_system_messages": False,
        },
        "deepseek-reasoner": {
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": ModelFamily.DEEPSEEK,
            "structured_output": True,
            "context_window": 64_000,
            "multiple_system_messages": False,
        }
    }


class QwenOpenAIChatCompletionClient(OpenAIChatCompletionClient):
    """Client for interacting with Qwen3 models via OpenAI-compatible API."""

    def __init__(self,model:str,base_url:str,**kwargs):
        """
        Initialize the QwenOpenAIChatCompletionClient.

        Args:
            model (str): The model to use.
            base_url (Optional[str]): The base URL for the API.
            **kwargs: Additional parameters for the client.
        """
        self.model = model
        if not self.model:
            raise ValueError("Model is a required parameter.")
        self.base_url = base_url or os.getenv("OPENAI_API_BASE")
        if not self.base_url:
            raise ValueError("Base URL is a required parameter.")
        if "model_info" not in kwargs:
            kwargs["model_info"] = ModelInfo._MODEL_INFO.get(self.model, ModelInfo.DEFAULT_MODEL_INFO)

        super().__init__(model=self.model, base_url=self.base_url, **kwargs)
        for key in ModelInfo.extra_kwargs: # Add the model-specific extension parameters for Qwen3 in self._create_args
            if key in kwargs:
                self._create_args[key] = kwargs[key]

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.info(f"Initialized QwenOpenAIChatCompletionClient with model: {self.model} and base URL: {self.base_url}")

    @override
    def remaining_tokens(self, messages: Sequence[LLMMessage], *, tools: Sequence[Tool | ToolSchema] = []) -> int:
        token_limit = ModelInfo._MODEL_INFO[self.model]["context_window"]
        return token_limit - self.count_tokens(messages, tools=tools)

    @override
    async def create(
            self,
            messages: Sequence[LLMMessage],
            *,
            tools: Sequence[Tool | ToolSchema] = [],
            json_output: Optional[bool | type[BaseModel]] = None,
            extra_create_args: Mapping[str, Any] = {},
            cancellation_token: Optional[CancellationToken] = None,
    ) -> CreateResult:
        if json_output is not None and issubclass(json_output, BaseModel):
            messages = self._append_json_schema(messages, json_output)
            json_output = None
        result = await super().create(
            messages=messages,
            tools=tools,
            json_output=json_output,
            extra_create_args=extra_create_args,
            cancellation_token=cancellation_token
        )
        return result

    @override
    async def create_stream(
            self,
            messages: Sequence[LLMMessage],
            *,
            tools: Sequence[Tool | ToolSchema] = [],
            json_output: Optional[bool | type[BaseModel]] = None,
            extra_create_args: Mapping[str, Any] = {},
            cancellation_token: Optional[CancellationToken] = None,
            max_consecutive_empty_chunk_tolerance: int = 0,
    ) -> AsyncGenerator[Union[str, CreateResult], None]:
        if json_output is not None and issubclass(json_output, BaseModel):
            messages = self._append_json_schema(messages, json_output)
            json_output = None
        async for result in super().create_stream(
            messages=messages,
            tools=tools,
            json_output=json_output,
            extra_create_args=extra_create_args,
            cancellation_token=cancellation_token,
            max_consecutive_empty_chunk_tolerance=max_consecutive_empty_chunk_tolerance
        ):
            yield result

    def _append_json_schema(self, messages: Sequence[LLMMessage],
                            json_output: BaseModel) -> Sequence[LLMMessage]:
        messages = copy.deepcopy(messages)
        first_message = messages[0]
        if isinstance(first_message, SystemMessage):
            first_message.content += dedent(f'''\
            
            <output-format>
            Your output must adhere to the following JSON schema format, 
            without any Markdown syntax, and without any preface or explanation:
            
            {json_output.model_json_schema()}
            </output-format>
            ''')
        return messages

    def _process_create_args(
            self,
            messages: Sequence[LLMMessage],
            tools: Sequence[Tool | ToolSchema],
            json_output: Optional[bool | type[BaseModel]],
            extra_create_args: Mapping[str, Any],
    ) -> CreateParams:
        # print(self._create_args)
        params = super()._process_create_args(
            messages=messages,
            tools=tools,
            json_output=json_output,
            extra_create_args=extra_create_args
        )
        return params

