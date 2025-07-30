This Python SDK that provides convenient clients for interacting with the **LLM-HUB** – a centralized backend service. Your Python applications can use this SDK to send chat completion requests to the LLM-HUB, which manages and routes these requests to its integrated LLM providers and their models (e.g., models from Anthropic, Google's Gemini, and OpenAI).

**Note:** This SDK communicates with _your specific LLM-HUB API_, not directly with the individual LLM providers. Your LLM-HUB service handles the authentication and interaction with the final LLM APIs it manages.

## Features

- Provider-specific clients (`GeminiClient`, `OpenAIClient`, `AnthropicClient`) for clear usage when targeting specific provider capabilities through the LLM-HUB.
- Handles communication with the LLM-HUB's chat endpoint (typically `/v1/chat`).
- Configuration of the LLM-HUB API URL via environment variables (`CHAT_API_BASE_URL`).
- Optional authentication with the LLM-HUB API via environment variables (`SDK_CHAT_API_KEY`) or direct initialization.
- Built-in custom exceptions (`APIRequestError`, `ConnectionError`, `TimeoutError`, `SDKError`) for easier error handling.
- Based on the robust `requests` library for HTTP communication.

<!-- Project Structure section is omitted as it's less relevant for SDK users -->

## Getting Started

### Prerequisites

- Python 3.8+
- `pip` package manager
- Access to a running instance of your LLM-HUB API that this SDK is designed to talk to.

### Installation

1.  **Set up a Virtual Environment (Recommended):**
    It's highly recommended to use a virtual environment to manage your project's dependencies and avoid conflicts with other Python projects.

        - **Create the virtual environment:**
          Open your terminal or command prompt in your project's root directory and run:

          ```bash
          python -m venv .venv
          # Or, if you have multiple Python versions, you might use:
          # python3 -m venv .venv
          # On Windows, you can also use the py launcher:
          # py -m venv .venv
          ```

          This will create a directory named `.venv` (or your chosen name) containing the virtual environment.

        - **Activate the virtual environment:**
          You need to activate the environment in each new terminal session where you want to use it.

          - **On Windows (Command Prompt or PowerShell):**
            ```bash
            .venv\Scripts\activate
            ```
          - **On macOS and Linux (bash/zsh):**
            `bash

    source .venv/bin/activate
    `        Once activated, your terminal prompt will usually change to indicate that you are in the virtual environment (e.g.,`(.venv) Your-User@Your-Machine:...$`).

2.  **Install the SDK:**
    With your virtual environment activated, you can now install the SDK.

    ```bash
    pip install llm-unified-sdk  # Replace llm-unified-sdk with your actual package name
    ```

    This will automatically install the required `requests` library within your active virtual environment.

3.  **(Optional) Install `python-dotenv`:**
    If you plan to manage configuration using a `.env` file in your application, install `python-dotenv` into your virtual environment:
    ```bash
    pip install python-dotenv
    ```

## Configuration

The SDK needs to know the URL of your LLM-HUB API. This is typically configured in the environment of the application _using_ the SDK.

1.  **Create a `.env` file** in the root directory of _your application project_:

    ```dotenv
    # .env file for YOUR application

    # REQUIRED: The full base URL of your running LLM-HUB API
    # Example: CHAT_API_BASE_URL="http://localhost:8000"
    # Example: CHAT_API_BASE_URL="https://your-llm-hub-api.com"
    CHAT_API_BASE_URL="YOUR_LLM_HUB_API_URL_HERE"

    # OPTIONAL: API key required BY YOUR LLM-HUB API itself (if it's protected)
    # The SDK will use this as a fallback if no api_key is passed during init.
    # Leave blank or omit if your LLM-HUB doesn't require a key from clients.
    # SDK_CHAT_API_KEY="YOUR_LLM_HUB_API_ACCESS_KEY_HERE"
    ```

2.  **Load the `.env` file** in your application code _before_ initializing the SDK client:

    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv() # Loads variables from .env into the environment

    # Retrieve the base URL for the SDK
    api_url = os.getenv("CHAT_API_BASE_URL")

    if not api_url:
        print("Error: CHAT_API_BASE_URL is not set in the environment!")
        # Handle error appropriately
    ```

## Usage Example

This section guides you through using the SDK to send chat completion requests to your LLM-HUB. We'll start with a basic setup and then show how to make it more dynamic.

**Prerequisites:**

- You have completed the "Getting Started" and "Configuration" sections.
- Your `.env` file is in your project root, with `CHAT_API_BASE_URL` pointing to your LLM-HUB.
- Create a Python file for your application, e.g., `app.py`.

### 1. Basic Setup: Imports and Configuration

First, import the necessary modules and load your LLM-HUB configuration.

```python
# app.py
import os
import logging
import json # For pretty-printing responses
from dotenv import load_dotenv

# Import your SDK package
# If your package is named 'llm_unified_sdk', use:
# import llm_unified_sdk as SDK
import llm_hub_sdk # Make sure this matches your SDK's import name

# Load environment variables from .env
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the LLM-HUB API URL from environment
API_URL = os.getenv("CHAT_API_BASE_URL")
if not API_URL:
    logging.error("FATAL: CHAT_API_BASE_URL (LLM-HUB URL) not set. Please create a .env file or set the environment variable.")
    exit(1)


logging.info(f"LLM-HUB URL set to: {API_URL}")
```

This sets up essential imports, loads your .env configuration, and verifies that CHAT_API_BASE_URL is available.

2. Initializing a Specific Client
   - The SDK uses provider-specific clients (e.g., OpenAIClient, GeminiClient) to help your LLM-HUB route requests correctly.
   - Let's initialize an OpenAIClient to interact with an OpenAI-compatible model available through your LLM-HUB.

```python
# app.py (continued)

# Import the specific client and its exceptions
# (Assumes SDK.openai.OpenAIClient and its exceptions exist)
try:
    from SDK.openai import OpenAIClient
    # Import specific exceptions for targeted error handling
    from SDK.openai import APIRequestError, ConnectionError, TimeoutError, SDKError as OpenAI_SDKError
except ImportError:
    logging.error("Could not import OpenAIClient or its exceptions. Ensure SDK is structured correctly.")
    exit(1) # INDENTED if it belongs to the except block

# Define the model identifier known to YOUR LLM-HUB
# This tells the LLM-HUB which underlying model to use (e.g., "gpt-4o", "your-custom-openai-model-id")
TARGET_MODEL_ID = "gpt-4o" # Example: an OpenAI model identifier

try: # Initialize the client for your LLM-HUB
    # VV INDENTED LINES BELOW VV
    chat_client = OpenAIClient(
        base_url=API_URL,       # Your LLM-HUB's URL
        model=TARGET_MODEL_ID,  # The model identifier for the LLM-HUB
        # api_key="YOUR_HUB_KEY"  # Optional: Pass API key directly. If used, uncomment and place on its own line.
                                # Or ensure it's picked from SDK_CHAT_API_KEY in .env
    )
    logging.info(f"OpenAIClient initialized for model '{TARGET_MODEL_ID}' via LLM-HUB.")
except (ValueError, TypeError) as e:
    # VV INDENTED LINES BELOW VV
    logging.error(f"Failed to initialize OpenAIClient: {e}")
    exit(1)
```

- We import OpenAIClient and its specific exceptions.
- TARGET_MODEL_ID is the name/ID your LLM-HUB uses to identify the target model.
- The client is initialized with your LLM-HUB's base_url and the model ID.

## License

Copyright (c) 2025 NTV360. All rights reserved.

This software is proprietary and is distributed without any license granting rights to use, copy, modify, or distribute. Use of this software requires specific permission from the copyright holder. Please refer to the NOTICE file (if provided) or contact the copyright holder for terms of use.
