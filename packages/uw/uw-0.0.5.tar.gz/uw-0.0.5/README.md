# uw
useful decorators

To install:	```pip install uw```

## Overview
The `uw` package provides a collection of Python decorators and utilities designed to simplify common programming tasks such as argument injection, automatic method decoration, resource management, and property caching. These tools are especially useful for enhancing code readability and reducing boilerplate.

## Features

### Decorators

#### `inject_args`
Injects arguments into a function, ignoring those that are not accepted by the function. This is useful when you want to pre-specify some of the arguments a function should use without modifying the function itself.

**Usage Example:**

```python
from uw import inject_args

@inject_args(a=2, b=3)
def formula(a, b, c=1):
    return (a - b) * c

print(formula())  # Output: -1
print(formula(c=10))  # Output: -10
```

#### `make_sure_to_close`
Creates an ad-hoc context manager to ensure that resources are closed after use. This is particularly useful when dealing with objects that require explicit closure.

**Usage Example:**

```python
from uw import make_sure_to_close

with make_sure_to_close(open('file.txt', 'w')) as f:
    f.write('Hello, world!')
# File is automatically closed after the block
```

#### `decorate_all_methods`
Applies a decorator to all methods of a class, optionally excluding or including specific methods.

**Usage Example:**

```python
from uw import decorate_all_methods, just_print_exceptions

@decorate_all_methods(just_print_exceptions)
class Processor:
    def process(self):
        raise Exception("Processing error")

    def calculate(self):
        raise Exception("Calculation error")

p = Processor()
p.process()  # Prints "Processing error"
p.calculate()  # Prints "Calculation error"
```

#### `autoargs`
Automatically assigns constructor arguments to instance variables, reducing the need for boilerplate code in the `__init__` method.

**Usage Example:**

```python
from uw import autoargs

class Configuration:
    @autoargs()
    def __init__(self, host, port, debug=False):
        pass

config = Configuration('localhost', 8080)
print(config.host)  # Output: localhost
print(config.port)  # Output: 8080
print(config.debug)  # Output: False
```

### Utilities

#### `lazyprop`
A descriptor for creating properties that are computed on first access and cached for subsequent accesses.

**Usage Example:**

```python
from uw import lazyprop

class DataSet:
    def __init__(self, data):
        self._data = data

    @lazyprop
    def summary(self):
        print("Calculating summary")
        return sum(self._data) / len(self._data)

ds = DataSet([1, 2, 3])
print(ds.summary)  # Output: Calculating summary, then 2.0
print(ds.summary)  # Output: 2.0 (cached, no recalculation)
```

### Contributing
Contributions to the `uw` package are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests on our GitHub repository.

For more detailed information on each function and class, refer to the source code documentation available in the `__init__.py` file within the package.