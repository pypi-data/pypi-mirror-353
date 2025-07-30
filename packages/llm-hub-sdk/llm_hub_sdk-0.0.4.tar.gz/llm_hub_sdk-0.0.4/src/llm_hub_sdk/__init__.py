import sys
import os

print("--- Executing llm_hub_sdk/__init__.py ---")
print(f"Current directory: {os.getcwd()}")
print(f"Python Path: {sys.path}")
print("Attempting to import submodules...")

try:
    from . import gemini
    print(f"Successfully imported .gemini: {gemini}")
except ImportError as e:
    print(f"!!! FAILED to import .gemini: {e}")

try:
    from . import openai
    print(f"Successfully imported .openai: {openai}")
except ImportError as e:
    print(f"!!! FAILED to import .openai: {e}")

try:
    from . import anthropic
    print(f"Successfully imported .anthropic: {anthropic}")
except ImportError as e:
    print(f"!!! FAILED to import .anthropic: {e}")

try:
    from .core import SDKError, APIRequestError, ConnectionError, TimeoutError
    print("Successfully imported exceptions from .core")
except ImportError as e:
    print(f"!!! FAILED to import exceptions from .core: {e}")

# Try importing client classes
try:
    from .gemini import GeminiClient
    print("Successfully imported GeminiClient")
except ImportError as e:
    print(f"!!! FAILED to import GeminiClient: {e}")

try:
    from .openai import OpenAIClient
    print("Successfully imported OpenAIClient")
except ImportError as e:
    print(f"!!! FAILED to import OpenAIClient: {e}")

try:
    from .anthropic import AnthropicClient
    print("Successfully imported AnthropicClient")
except ImportError as e:
    print(f"!!! FAILED to import AnthropicClient: {e}")

# Define __all__
__all__ = [
    "gemini",
    "openai",
    "anthropic",
    "GeminiClient",
    "OpenAIClient",
    "AnthropicClient",
    "SDKError",
    "APIRequestError",
    "ConnectionError",
    "TimeoutError",
]

print("--- Finished llm_hub_sdk/__init__.py ---")
