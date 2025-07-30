# lh
logging functions

To install:	```pip install lh```

## Overview

The `lh` package provides a set of utilities for logging and progress tracking in Python applications. It includes functions to print progress messages with timestamps, manage logging configurations, and output iterable items one per line.

## Features

- **Progress Printing**: Functions to display progress messages with the current time.
- **Logging Setup**: Simplified setup for logging with custom configurations.
- **Iterable Printing**: Utility to print each item of an iterable on a new line.

## Usage

### Progress Printing

#### `print_progress`

Prints a progress message with an optional timestamp.

```python
from lh import print_progress

print_progress("Processing data...", refresh=True)
```

#### `printProgress`

Prints a formatted progress message with an optional timestamp, supporting sprintf-style string formatting.

```python
from lh import printProgress

printProgress("Step {0} of {1}", args=[1, 10], refresh=True)
```

### Logging Setup

#### `get_a_logger`

Creates and returns a logger with a specified configuration. Defaults to DEBUG level and outputs to 'default_log.log'.

```python
from lh import get_a_logger

logger = get_a_logger(filename='app.log', level='INFO')
logger.info("Application started")
```

### Iterable Printing

#### `print_iter_one_per_line`

Prints each element of an iterable on a new line.

```python
from lh import print_iter_one_per_line

print_iter_one_per_line(['apple', 'banana', 'cherry'])
```

## Function Documentation

### `hms_message`

Generates a timestamped message.

- **Parameters**:
  - `msg` (str): The message to timestamp.
- **Returns**:
  - str: A string with the current day and time followed by the message.

### `print_progress`

Prints a progress message, optionally refreshing the line and displaying the current time.

- **Parameters**:
  - `msg` (str): The message to print.
  - `refresh` (bool, optional): Whether to refresh the line. Defaults to None.
  - `display_time` (bool, optional): Whether to display the current time. Defaults to True.

### `printProgress`

Formatted version of `print_progress` supporting variable arguments.

- **Parameters**:
  - `message` (str): The message template.
  - `args` (list, optional): List of arguments to format the message.
  - `refresh` (bool, optional): Whether to refresh the line.
  - `refresh_suffix` (str, optional): Suffix to append after the message when refreshing.

### `print_iter_one_per_line`

Prints each item of an iterable on a new line.

- **Parameters**:
  - `it` (iterable): The iterable whose items are to be printed.

### `get_a_logger`

Sets up and returns a logger with specified configurations.

- **Parameters**:
  - `**kwargs`: Arbitrary keyword arguments for logger configuration.
- **Returns**:
  - logging.Logger: Configured logger object.

This package streamlines logging and progress tracking in Python, making it easier to manage output and diagnostics in your applications.