# QwenOpenAIChatCompletionClient

A Python client library for interacting with Qwen3 and DeepSeek models via OpenAI-compatible API, built on top of AutoGen. This client provides structured output support, function calling, and comprehensive model configuration for building agentic AI applications.

## Installation

You can install the package using either of the following methods:

- From PyPI (recommended):

```bash
pip install qwen3-autogen-client
```

- From source (for development):

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Build a Wheel File

To build a wheel file for distribution, run the following script from the project root:

```bash
./build_wheel.sh
```

This will generate a `.whl` file in the `dist/` directory.

## Attribution

This project is based on the excellent work from:
- **Author**: [Data Leads Future](https://www.dataleadsfuture.com/build-autogen-agents-with-qwen3-structured-output-thinking-mode/)
- **GitHub Repository**: [Agentic AI Playground - AutoGen-Qwen3 Integration](https://github.com/qtalen/agentic-ai-playground/tree/main/03_Master_AutoGen-Qwen3_Integration)

## Features

- **Multi-Model Support**: Qwen3, Qwen2.5, and DeepSeek models
- **Structured Output**: Pydantic model-based JSON schema enforcement for reliable AI responses
- **Function Calling**: Full support for tool usage and function calling capabilities
- **Async Support**: Both streaming and non-streaming async operations
- **Token Management**: Intelligent token counting and remaining token calculation
- **Comprehensive Logging**: Built-in logging for debugging and monitoring
- **AutoGen Integration**: Seamless integration with AutoGen's agent framework

## Supported Models

### Qwen3 Models
- `Qwen3-32B` (32K context)
- `Qwen3-14B` (32K context)
- `Qwen3-8B` (32K context)
- `Qwen3-4B` (32K context)
- `Qwen3-1.7B` (32K context)
- `qwen-max` (32K context)
- `qwen-max-latest` (128K context)
- `qwen-plus` (128K context)
- `qwen-plus-latest` (128K context)
- `qwen-turbo` (1M context)
- `qwen-turbo-latest` (1M context)
- `qwen3-235b-a22b` (128K context)
- `qwen3-30b-a3b` (128K context)

### Qwen2.5 Models
- `Qwen2.5-Omni-7B` (32K context, vision)
- `Qwen2.5-Omni-3B` (32K context, vision)
- `Qwen2.5-VL-32B-Instruct` (32K context, vision)
- `Qwen2.5-VL-7B-Instruct` (32K context, vision)

### DeepSeek Models
- `deepseek-chat` (64K context, function calling supported)
- `deepseek-reasoner` (64K context, reasoning mode)

## Quick Start

### Basic Usage

```python
from qwen3_autogen_client import QwenOpenAIChatCompletionClient
from autogen_core.models import UserMessage

# Initialize the client
client = QwenOpenAIChatCompletionClient(
    model="qwen-max-latest",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="your_api_key_here"
)

# Create a simple completion
messages = [UserMessage(content="Hello, how are you?")]
result = await client.create(messages=messages)
print(result.content)
```

### Structured Output with Pydantic

```python
from pydantic import BaseModel
from typing import List

class TaskList(BaseModel):
    tasks: List[str]
    priority: str

# Get structured output
messages = [UserMessage(content="Create a task list for planning a vacation")]
result = await client.create(
    messages=messages,
    json_output=TaskList
)
# Result will be automatically formatted according to TaskList schema
```

### Streaming Response

```python
async for chunk in client.create_stream(messages=messages):
    if isinstance(chunk, str):
        print(chunk, end="")
    else:
        # Final result
        print(f"\nFinal result: {chunk}")
```

### Function Calling

```python
from autogen_core.tools import Tool

# Define a tool
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

tool = Tool(get_weather, name="get_weather", description="Get weather for a location")

# Use with function calling
result = await client.create(
    messages=[UserMessage(content="What's the weather in Tokyo?")],
    tools=[tool]
)
```

## Usage Example: Simple Agent and Function Calling

Below is an example demonstrating how to use a simple agent with function calling capability:

```python
import os
import sys
import asyncio
import logging
from datetime import datetime
from qwen3_autogen_client import QwenOpenAIChatCompletionClient
from autogen import AssistantAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_time() -> str:
    """Returns the current server time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def print_result(result):
    for msg in result.messages:
        if hasattr(msg, 'content'):
            print(f"Message: {msg.content}")
        elif hasattr(msg, 'tool_calls'):
            print(f"Tool Calls: {msg.tool_calls}")
        else:
            print(f"Unknown message type: {msg}")

async def main():
    logger.info("Starting Qwen client script")
    logger.info("Checking required environment variables")

    # 1. Instantiate your LLM client (here using Local Qwen Model)
    logger.info("Instantiating QwenOpenAIChatCompletionClient")
    model_client = QwenOpenAIChatCompletionClient(model=os.getenv("MODEL_NAME"), base_url=os.getenv("OPENAI_API_BASE"))
    logger.info(f"Client instantiated: {model_client}")

    # 2. Create an assistant agent
    agent = AssistantAgent("assistant", model_client=model_client, tools=[get_time])
    logger.info(f"Agent instantiated: {agent}")
    # 3. Run the agent on simple Knowledge task
    logger.info("Running agent")
    result = await agent.run(task="What is most common language in the world?/no_think")
    logger.info(f"Result: {result}")
    print_result(result)

    # 4. Run the agent on a more complex task
    logger.info("Running agent on a task that requires function calling")
    result = await agent.run(task="What is the current server time?, Is it afternoon?")
    logger.info(f"Result: returned {len(result.messages)} messages")
    print_result(result)
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

### Sample Output

```
\033[90m2025-06-08 17:18:22,855 - Instantiating QwenOpenAIChatCompletionClient\033[0m
\033[90m2025-06-08 17:18:22,915 - Initialized QwenOpenAIChatCompletionClient with model: Qwen3 4B and base URL: [MASKED_URL]\033[0m
\033[90m2025-06-08 17:18:22,915 - Client instantiated: <qwen3_autogen_client.qwen_client.QwenOpenAIChatCompletionClient object at 0x117ab51d0>\033[0m
\033[90m2025-06-08 17:18:22,916 - Agent instantiated: <autogen_agentchat.agents._assistant_agent.AssistantAgent object at 0x117b33190>\033[0m
\033[90m2025-06-08 17:18:22,916 - Running agent\033[0m
\033[90m2025-06-08 17:18:44,330 - HTTP Request: POST [MASKED_URL] "HTTP/1.1 200 OK"\033[0m
\033[90m2025-06-08 17:18:44,338 - { ... "model": "Qwen3 4B", ... }\033[0m
\033[90m2025-06-08 17:18:44,339 - Result: messages=[TextMessage(source='user', ...), TextMessage(source='assistant', ...)] stop_reason=None\033[0m
\033[90m2025-06-08 17:18:44,339 - Running agent on a task that requires function calling\033[0m
Message: What is most common language in the world?/no_think
Message: The most common language in the world is Mandarin Chinese. It is spoken by approximately 1.3 billion people, making it the most spoken language globally. However, if we consider the number of native speakers, Spanish is the most spoken language.
\033[90m2025-06-08 17:18:52,078 - HTTP Request: POST [MASKED_URL] "HTTP/1.1 200 OK"\033[0m
\033[90m2025-06-08 17:18:52,082 - { ... "model": "Qwen3 4B", ... }\033[0m
\033[90m2025-06-08 17:18:52,083 - {"type": "ToolCall", "tool_name": "get_time", "arguments": {}, "result": "2025-06-08 17:18:52", "agent_id": null}\033[0m
\033[90m2025-06-08 17:18:52,083 - Result: returned 4 messages\033[0m
Message: What is the current server time?, Is it afternoon?
Message: [FunctionCall(id='1rX3Ta4NkgrJsgzUZrijIxVbxKRNGaDD', arguments='{}', name='get_time')]
Message: [FunctionExecutionResult(content='2025-06-08 17:18:52', name='get_time', call_id='1rX3Ta4NkgrJsgzUZrijIxVbxKRNGaDD', is_error=False)]
Message: 2025-06-08 17:18:52
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### Direct Configuration

```python
client = QwenOpenAIChatCompletionClient(
    model="qwen-max-latest",
    base_url="https://your-api-endpoint.com",
    api_key="your_api_key",
    # Additional OpenAI client parameters
    timeout=30.0,
    max_retries=3
)
```

## API Reference

### QwenOpenAIChatCompletionClient

#### `__init__(model: str, base_url: str, **kwargs)`

Initialize the client.

**Parameters:**
- `model` (str): The model name to use (required)
- `base_url` (str): Base URL for the API endpoint (required)
- `**kwargs`: Additional parameters passed to the underlying OpenAI client

**Example:**
```python
client = QwenOpenAIChatCompletionClient(
    model="qwen-max-latest",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="your_key"
)
```

#### `async create(messages, *, tools=[], json_output=None, extra_create_args={}, cancellation_token=None) -> CreateResult`

Create a completion.

**Parameters:**
- `messages`: Sequence of LLMMessage objects
- `tools`: Optional sequence of Tool or ToolSchema objects
- `json_output`: Optional bool or Pydantic BaseModel class for structured output
- `extra_create_args`: Additional arguments for the API call
- `cancellation_token`: Optional cancellation token

#### `async create_stream(...) -> AsyncGenerator[Union[str, CreateResult], None]`

Create a streaming completion with the same parameters as `create()`.

#### `remaining_tokens(messages, *, tools=[]) -> int`

Calculate remaining tokens available for the conversation.

## Model Capabilities

| Model | Function Calling | JSON Output | Vision | Context Window |
|-------|-----------------|-------------|---------|----------------|
| qwen-max | ✅ | ✅ | ❌ | 32K |
| qwen-max-latest | ✅ | ✅ | ❌ | 128K |
| qwen-plus | ✅ | ✅ | ❌ | 128K |
| qwen-turbo | ✅ | ✅ | ❌ | 1M |
| deepseek-chat | ✅ | ✅ | ❌ | 64K |
| deepseek-reasoner | ❌ | ❌ | ❌ | 64K |

## License

This project is licensed under the MIT License - see the LICENSE file for details.
