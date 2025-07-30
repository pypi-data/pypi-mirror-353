"""
CLI Test Framework - A powerful command-line testing framework

This package provides tools for testing command-line applications and scripts
with support for parallel execution and advanced file comparison capabilities.
"""

__version__ = "0.2.2"
__author__ = "Xiaotong Wang"
__email__ = "xiaotongwang98@gmail.com"

# Import main classes for convenient access
from .runners.json_runner import JSONRunner
from .runners.parallel_json_runner import ParallelJSONRunner
from .runners.yaml_runner import YAMLRunner

__all__ = [
    'JSONRunner',
    'ParallelJSONRunner', 
    'YAMLRunner',
] 