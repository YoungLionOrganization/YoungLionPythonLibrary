"""YoungLion.function — file operations and application utilities.

The package combines YoungLion's dependency-free File facade with developer
utilities for subprocess execution, scheduling, logging, e-mail, transfers, text
processing, events, caching, rate limiting, retry/circuit-breaker resilience,
timing and terminal formatting.  File is assembled from a core filesystem class
and format/extra mixins so one object exposes common text, binary, JSON, CSV,
XML, YAML-like, INI, properties, script and archive workflows.

Public classes are also re-exported from ``YoungLion`` for convenient discovery.
"""
from ._base import Debugger as Debugger, FileBase as FileBase
from ._formats import FileFormatsMixin as FileFormatsMixin
from ._extra import FileExtraMixin as FileExtraMixin
from ._utilities import CommandResult as CommandResult, TaskInfo as TaskInfo, ScriptRunner as ScriptRunner, TaskScheduler as TaskScheduler, Logger as Logger, EmailManager as EmailManager, FileTransferManager as FileTransferManager, TextProcessor as TextProcessor, EventBus as EventBus, TTLCache as TTLCache, RateLimiter as RateLimiter, RetryPolicy as RetryPolicy, CircuitBreaker as CircuitBreaker, Stopwatch as Stopwatch, Terminal as Terminal

class File(FileExtraMixin, FileFormatsMixin, FileBase):
    """Unified YoungLion file facade.

    ``File`` provides FileBase plus structured-format and extended file/script helpers in one dependency-free interface.

    When to use it
    --------------
    Use this as the normal entry point for filesystem and file-format workflows.
    """
    ...
