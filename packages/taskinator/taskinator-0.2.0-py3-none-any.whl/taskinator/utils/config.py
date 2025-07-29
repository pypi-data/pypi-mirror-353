"""
Configuration utilities for Taskinator.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import dotenv
import httpx
from rich.console import Console

console = Console()

# Global flag to track if the AI credentials warning has been shown
_ai_credentials_warning_shown = False

# Default configuration values
DEFAULT_CONFIG = {
    "tasks_dir": "tasks",
    "tasks_file": "tasks.json",
    "task_complexity_report_file": "task-complexity-report.json",
    "DEFAULT_SUBTASKS": 3,
    "DEFAULT_COMPLEXITY_THRESHOLD": 5,
    "PROJECT_NAME": "Taskinator",
    "MODEL": "claude-3-7-sonnet",
    "MAX_TOKENS": 4000,
    "TEMPERATURE": 0.7,
    "PERPLEXITY_MODEL": "sonar-pro",
    "DEBUG": False,
    "LOG_LEVEL": "info",
    "DEFAULT_PRIORITY": "medium",
    "PRD_PATH": None,
}


def get_project_path() -> str:
    """
    Get the project path from the environment or use the current working directory.

    Returns:
        str: The project path
    """
    return os.environ.get("TASKINATOR_PROJECT_PATH", os.getcwd())


def get_tasks_dir() -> str:
    """
    Get the tasks directory path.

    Returns:
        str: The tasks directory path
    """
    project_path = get_project_path()
    tasks_dir = os.path.join(project_path, DEFAULT_CONFIG["tasks_dir"])
    os.makedirs(tasks_dir, exist_ok=True)
    return tasks_dir


def get_tasks_path() -> str:
    """
    Get the tasks.json file path.

    Returns:
        str: The tasks.json file path
    """
    tasks_dir = get_tasks_dir()
    return os.path.join(tasks_dir, DEFAULT_CONFIG["tasks_file"])


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and defaults.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # Load environment variables from .env file if it exists
    dotenv.load_dotenv()

    # Start with default configuration
    config = DEFAULT_CONFIG.copy()

    # Add project path
    config["project_path"] = get_project_path()
    config["tasks_dir_path"] = get_tasks_dir()
    config["tasks_file_path"] = get_tasks_path()
    
    # Set project name to current directory name if not overridden
    if config["PROJECT_NAME"] == "Taskinator" and "PROJECT_NAME" not in os.environ:
        config["PROJECT_NAME"] = os.path.basename(os.getcwd())

    # Override with environment variables
    for key in config.keys():
        if key in os.environ:
            # Convert boolean strings to actual booleans
            if key == "DEBUG":
                config[key] = os.environ[key].lower() in ("true", "1", "yes", "y")
            # Convert numeric values
            elif isinstance(config[key], int):
                try:
                    config[key] = int(os.environ[key])
                except ValueError:
                    console.print(
                        f"[WARNING] Invalid value for {key}: {os.environ[key]}. "
                        f"Using default: {config[key]}",
                        style="bold yellow",
                    )
            # Convert temperature to float
            elif key == "TEMPERATURE":
                try:
                    config[key] = float(os.environ[key])
                except ValueError:
                    console.print(
                        f"[WARNING] Invalid value for {key}: {os.environ[key]}. "
                        f"Using default: {config[key]}",
                        style="bold yellow",
                    )
            else:
                config[key] = os.environ[key]

    # AI credentials will be checked by LiteLLM when needed
    # No need for upfront warnings since LiteLLM handles all providers

    return config


def get_config() -> Dict[str, Any]:
    """
    Get the configuration.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return load_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a configuration value by key.

    Args:
        key (str): Configuration key
        default (Any, optional): Default value if key is not found. Defaults to None.

    Returns:
        Any: Configuration value
    """
    config = get_config()
    return config.get(key, default)


def check_ai_available() -> bool:
    """
    Check if AI functionality is available by testing LiteLLM.
    This is done by the AI client, so we just return True here.
    LiteLLM will handle credential validation when needed.

    Returns:
        bool: True (LiteLLM handles validation)
    """
    return True


def save_config_value(key: str, value: Any) -> None:
    """
    Save a configuration value to environment (in-memory for current session).
    
    Args:
        key (str): Configuration key
        value (Any): Configuration value
    """
    os.environ[key] = str(value)


def show_ai_credentials_info():
    """Show information about AI credentials for LiteLLM."""
    global _ai_credentials_warning_shown

    if not _ai_credentials_warning_shown:
        console.print(
            "[INFO] AI features use LiteLLM. Ensure proper credentials are set for your chosen model.",
            style="blue",
        )
        _ai_credentials_warning_shown = True
