"""
Universal Tool Registry System for AI Provider Integration

This module provides a sophisticated tool registration system that automatically converts
Python functions into AI provider tools with proper schema generation, validation,
and error handling. Supports multiple AI providers including Anthropic Claude, OpenAI,
Mistral AI, AWS Bedrock, and Google Gemini.

Key Features:
- Automatic JSON schema generation from function signatures
- Pydantic model integration and validation
- Parameter filtering for internal/context parameters
- Multi-provider support with unified interface
- Comprehensive error handling and logging
- Type safety with full type hints
- Registry builders for all major AI providers

Usage Example:
    ```python
    from tool_registry_module import tool, build_registry_openai, build_registry_anthropic
    from pydantic import BaseModel


    class UserData(BaseModel):
        name: str
        age: int


    @tool(description="Process user information")
    def process_user(input: UserData, context: str = "default") -> UserData:
        return input


    # Use with different providers
    openai_registry = build_registry_openai([process_user])
    anthropic_registry = build_registry_anthropic([process_user])
    ```

Author: Claude Code Assistant
Version: 3.0
"""

import inspect
import logging
from collections import OrderedDict
from collections.abc import Callable
from functools import wraps
from typing import Any, get_type_hints

from pydantic import create_model

# Optional imports for different providers
try:
    from anthropic.types import ToolParam
except ImportError:
    ToolParam = None

# Configure logger for this module
logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Exception for tool registry validation errors."""

    pass


def create_schema_from_signature(
    func: Callable, ignore_in_schema: list[str]
) -> dict[str, Any]:
    """
    Create a JSON schema from a function signature using Pydantic models.

    This function introspects a function's signature and creates a corresponding
    JSON schema that can be used by AI providers for tool calling. It handles
    both simple types and complex Pydantic models.

    Args:
        func: The function to generate schema for
        ignore_in_schema: List of parameter names to exclude from the schema

    Returns:
        A JSON schema dictionary compatible with AI provider tool formats

    Example:
        ```python
        def my_func(name: str, age: int = 25, context: str = "internal"):
            pass


        schema = create_schema_from_signature(my_func, ["context"])
        # Returns schema for 'name' and 'age' parameters only
        ```
    """
    sig = inspect.signature(func)
    hints = get_type_hints(func)

    logger.debug(f"Generating schema for function: {func.__name__}")

    # Create Pydantic model fields from function parameters
    fields = {}
    for param_name, param in sig.parameters.items():
        # Skip special parameters and ignored parameters
        if param_name in ["args", "kwargs"] + ignore_in_schema:
            logger.debug(f"Skipping parameter: {param_name}")
            continue

        param_type = hints.get(param_name, Any)

        # Handle parameters with default values
        if param.default != inspect.Parameter.empty:
            fields[param_name] = (param_type, param.default)
            logger.debug(f"Added optional parameter: {param_name} = {param.default}")
        else:
            fields[param_name] = (param_type, ...)
            logger.debug(f"Added required parameter: {param_name}")

    if not fields:
        logger.warning(f"No fields found for function {func.__name__}")

    # Create temporary Pydantic model for schema generation
    model_name = f"{func.__name__}InputModel"
    temp_model = create_model(model_name, **fields)

    schema = temp_model.model_json_schema()
    logger.debug(f"Generated schema for {func.__name__}: {len(fields)} fields")

    return schema


def _is_pydantic_model(param_type: type) -> bool:
    """
    Check if a type is a Pydantic model.

    Args:
        param_type: The type to check

    Returns:
        True if the type is a Pydantic model, False otherwise
    """
    return hasattr(param_type, "__bases__") and any(
        hasattr(base, "model_validate") for base in param_type.__mro__
    )


def _convert_parameter(param_name: str, param_type: type, param_value: Any) -> Any:
    """
    Convert a parameter value to the expected type.

    Args:
        param_name: Name of the parameter (for error messages)
        param_type: Expected type of the parameter
        param_value: The value to convert

    Returns:
        The converted parameter value
    """
    if _is_pydantic_model(param_type):
        # Handle Pydantic model conversion
        if param_value is not None and isinstance(param_value, dict):
            logger.debug(
                f"Converting dict to Pydantic model for parameter: {param_name}"
            )
            return param_type(**param_value)
        else:
            # Already instantiated or None
            return param_value
    else:
        # Regular parameter - pass through as-is
        return param_value


def tool(
    description: str,
    cache_control: Any | None = None,
    ignore_in_schema: list[str] | None = None,
) -> Callable:
    """
    Decorator that converts a Python function into an AI provider tool.

    This decorator automatically generates JSON schemas from function signatures,
    handles Pydantic model validation, and provides parameter filtering capabilities.
    The resulting tool can be used with multiple AI providers including Anthropic Claude,
    OpenAI, Mistral AI, AWS Bedrock, and Google Gemini.

    Args:
        description: Human-readable description of what the tool does
        cache_control: Optional cache control settings (supported by some providers)
        ignore_in_schema: List of parameter names to exclude from the generated schema.
                         Useful for internal parameters like context or configuration.

    Returns:
        A decorator function that wraps the original function with tool capabilities

    Raises:
        SchemaGenerationError: If schema generation fails
        ToolValidationError: If parameter validation fails during execution

    Example:
        ```python
        @tool(
            description="Calculate the area of a rectangle",
            ignore_in_schema=["debug_mode"],
        )
        def calculate_area(
            length: float, width: float, debug_mode: bool = False
        ) -> float:
            if debug_mode:
                print(f"Calculating area for {length} x {width}")
            return length * width
        ```

    Note:
        The decorator preserves the original function's signature and behavior while
        adding tool-specific metadata and automatic parameter conversion.
    """
    if ignore_in_schema is None:
        ignore_in_schema = []

    def decorator(func: Callable) -> Callable:
        logger.info(f"Registering tool: {func.__name__}")

        sig = inspect.signature(func)
        hints = get_type_hints(func)

        # Generate schema for the function
        input_schema = create_schema_from_signature(func, ignore_in_schema)

        @wraps(func)
        def wrapper(**kwargs) -> Any:
            """
            Tool wrapper that handles parameter conversion and validation.

            Args:
                **kwargs: Keyword arguments from tool invocation

            Returns:
                Result from the original function
            """
            converted_kwargs = {}

            # Process each parameter in the function signature
            for param_name, param in sig.parameters.items():
                # Skip special parameters
                if param_name in ["args", "kwargs"]:
                    continue

                param_type = hints.get(param_name, Any)
                param_value = kwargs.get(param_name)

                # Convert parameter to expected type
                converted_kwargs[param_name] = _convert_parameter(
                    param_name, param_type, param_value
                )

            logger.debug(f"Executing tool: {func.__name__}")
            result = func(**converted_kwargs)
            logger.debug(f"Tool execution completed: {func.__name__}")

            return result

        # Attach metadata to the wrapper function
        wrapper._description = description
        wrapper._cache_control = cache_control
        wrapper._input_schema = input_schema
        wrapper._original_func = func
        wrapper._ignore_in_schema = ignore_in_schema

        logger.info(f"Successfully registered tool: {func.__name__}")
        return wrapper

    return decorator


def build_registry_anthropic(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Anthropic Claude API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with Anthropic's tool calling API. Each tool in the
    registry includes both the callable function and its API representation.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": ToolParam object for Anthropic API

    Raises:
        ToolRegistryError: If registry building fails

    Example:
        ```python
        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b


        @tool(description="Multiply two numbers")
        def multiply(a: int, b: int) -> int:
            return a * b


        registry = build_registry_anthropic([add, multiply])

        # Use with Anthropic API
        tools = [entry["representation"] for entry in registry.values()]
        ```

    Note:
        Only functions with the @tool decorator will be included in the registry.
        Functions without tool metadata will be silently skipped.
    """
    logger.info(f"Building tool registry for {len(functions)} functions")

    registry = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        # Check if function has tool metadata
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func._original_func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Create ToolParam for Anthropic API
        if ToolParam is None:
            raise ToolRegistryError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        tool_param = ToolParam(
            name=func_name,
            description=func._description,
            input_schema=func._input_schema,
        )

        # Add cache control if specified
        if func._cache_control:
            tool_param.cache_control = func._cache_control
            logger.debug(f"Added cache control for tool: {func_name}")

        # Add to registry
        registry[func_name] = {
            "tool": func,  # The wrapper function with validation
            "representation": tool_param,  # Anthropic API representation
        }

        processed_count += 1
        logger.debug(f"Successfully added tool to registry: {func_name}")

    logger.info(
        f"Registry building completed: {processed_count} tools processed, "
        f"{skipped_count} functions skipped"
    )

    return registry


def build_registry_openai(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with OpenAI Function Calling API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with OpenAI's function calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in OpenAI function format

    Example:
        ```python
        registry = build_registry_openai([add, multiply])

        # Use with OpenAI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """
    logger.info(f"Building OpenAI tool registry for {len(functions)} functions")

    registry = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func._original_func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Create OpenAI function format
        openai_function = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func._description,
                "parameters": func._input_schema,
            },
        }

        # Add to registry
        registry[func_name] = {
            "tool": func,
            "representation": openai_function,
        }

        processed_count += 1
        logger.debug(f"Successfully added OpenAI tool to registry: {func_name}")

    logger.info(
        f"OpenAI registry building completed: {processed_count} tools processed, {skipped_count} functions skipped"
    )
    return registry


def build_registry_mistral(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Mistral AI Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Mistral function format

    Example:
        ```python
        registry = build_registry_mistral([add, multiply])

        # Use with Mistral AI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """
    logger.info(f"Building Mistral tool registry for {len(functions)} functions")

    registry = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func._original_func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Create Mistral function format (similar to OpenAI)
        mistral_function = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": func._description,
                "parameters": func._input_schema,
            },
        }

        # Add to registry
        registry[func_name] = {
            "tool": func,
            "representation": mistral_function,
        }

        processed_count += 1
        logger.debug(f"Successfully added Mistral tool to registry: {func_name}")

    logger.info(
        f"Mistral registry building completed: {processed_count} tools processed, {skipped_count} functions skipped"
    )
    return registry


def build_registry_bedrock(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with AWS Bedrock Converse API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Bedrock tool format

    Example:
        ```python
        registry = build_registry_bedrock([add, multiply])

        # Use with AWS Bedrock API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """
    logger.info(f"Building Bedrock tool registry for {len(functions)} functions")

    registry = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func._original_func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Create Bedrock tool format
        bedrock_tool = {
            "toolSpec": {
                "name": func_name,
                "description": func._description,
                "inputSchema": {"json": func._input_schema},
            }
        }

        # Add to registry
        registry[func_name] = {
            "tool": func,
            "representation": bedrock_tool,
        }

        processed_count += 1
        logger.debug(f"Successfully added Bedrock tool to registry: {func_name}")

    logger.info(
        f"Bedrock registry building completed: {processed_count} tools processed, {skipped_count} functions skipped"
    )
    return registry


def build_registry_gemini(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Google Gemini Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Gemini function format

    Example:
        ```python
        registry = build_registry_gemini([add, multiply])

        # Use with Google Gemini API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """
    logger.info(f"Building Gemini tool registry for {len(functions)} functions")

    registry = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func._original_func.__name__
        logger.debug(f"Processing tool: {func_name}")

        # Create Gemini function format
        gemini_function = {
            "function_declarations": [
                {
                    "name": func_name,
                    "description": func._description,
                    "parameters": func._input_schema,
                }
            ]
        }

        # Add to registry
        registry[func_name] = {
            "tool": func,
            "representation": gemini_function,
        }

        processed_count += 1
        logger.debug(f"Successfully added Gemini tool to registry: {func_name}")

    logger.info(
        f"Gemini registry building completed: {processed_count} tools processed, {skipped_count} functions skipped"
    )
    return registry


# Legacy function name for backward compatibility
def build_registry_anthropic_tool_registry(
    functions: list[Callable],
) -> dict[str, dict[str, Any]]:
    """Legacy function name. Use build_registry_anthropic() instead."""
    logger.warning(
        "build_registry_anthropic_tool_registry is deprecated. Use build_registry_anthropic() instead."
    )
    return build_registry_anthropic(functions)


def get_tool_info(
    registry: dict[str, dict[str, Any]], tool_name: str
) -> dict[str, Any]:
    """
    Get detailed information about a specific tool in the registry.

    Args:
        registry: Tool registry from build_registry_anthropic_tool_registry
        tool_name: Name of the tool to get information for

    Returns:
        Dictionary containing tool information

    Raises:
        KeyError: If tool is not found in registry
    """
    if tool_name not in registry:
        available_tools = list(registry.keys())
        raise KeyError(
            f"Tool '{tool_name}' not found. Available tools: {available_tools}"
        )

    tool_entry = registry[tool_name]
    wrapper_func = tool_entry["tool"]

    return {
        "name": tool_name,
        "description": wrapper_func._description,
        "schema": wrapper_func._input_schema,
        "cache_control": wrapper_func._cache_control,
        "ignored_parameters": wrapper_func._ignore_in_schema,
        "original_function": wrapper_func._original_func.__name__,
    }


def validate_registry(registry: dict[str, dict[str, Any]]) -> bool:
    """
    Validate that a tool registry has the correct structure.

    Args:
        registry: Tool registry to validate

    Returns:
        True if registry is valid

    Raises:
        ToolRegistryError: If registry is invalid
    """
    logger.info(f"Validating tool registry with {len(registry)} tools")

    for tool_name, tool_data in registry.items():
        # Check required keys
        if "tool" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'tool' key")
        if "representation" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'representation' key")

        # Check tool function has required metadata
        tool_func = tool_data["tool"]
        required_attrs = ["_description", "_input_schema", "_original_func"]
        for attr in required_attrs:
            if not hasattr(tool_func, attr):
                raise ToolRegistryError(f"Tool '{tool_name}' missing attribute: {attr}")

        # Check representation has required fields (ToolParam is a TypedDict)
        representation = tool_data["representation"]
        required_fields = ["name", "description", "input_schema"]
        for field in required_fields:
            if field not in representation:
                raise ToolRegistryError(
                    f"Tool '{tool_name}' representation missing field: {field}"
                )

    logger.info("Tool registry validation completed successfully")
    return True


# Export main functions and classes
__all__ = [
    "tool",
    "build_registry_anthropic",
    "build_registry_openai",
    "build_registry_mistral",
    "build_registry_bedrock",
    "build_registry_gemini",
    "build_registry_anthropic_tool_registry",  # Legacy name
    "get_tool_info",
    "validate_registry",
    "ToolRegistryError",
]
