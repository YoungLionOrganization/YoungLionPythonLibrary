"""Dependency-free application utilities used across YoungLion projects.

This module collects focused building blocks that are useful in command-line,
desktop and service applications without introducing third-party runtime
requirements: structured subprocess results, script execution, in-process task
scheduling, rotating logging, SMTP/IMAP e-mail, local/FTP transfer tracking, text
analysis, priority event dispatch, TTL/LRU caching, token-bucket rate limiting,
retry policies, circuit breakers, stopwatches and terminal rendering.

Concurrency-sensitive classes document their thread-safety guarantees.  Network
helpers expose standard protocol behavior and allow connection/authentication
errors to propagate so callers can implement application-specific recovery.
"""
R = TypeVar('R')
P = ParamSpec('P')
import subprocess
from email.message import EmailMessage
from typing import Optional, ParamSpec, TypeVar
from types import TracebackType
from dataclasses import dataclass
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from typing import Any

@dataclass(slots=True)
class CommandResult:
    """Structured subprocess result.

    ``CommandResult`` provides command arguments, return code, captured streams, duration and success/check helpers.

    When to use it
    --------------
    Returned by ScriptRunner.run for inspectable process execution.
    """
    args: tuple[str, ...]
    returncode: int
    stdout: str = ''
    stderr: str = ''
    duration: float = 0.0

    @property
    def ok(self) -> bool:
        """Return True when the subprocess return code indicates success."""
        ...

    def check(self) -> CommandResult:
        """Return this result when successful or raise CalledProcessError for a non-zero return code."""
        ...

class ScriptRunner:
    """Cross-platform subprocess/script runner.

    ``ScriptRunner`` provides interpreter detection, synchronous structured execution, asynchronous processes and script launching.

    When to use it
    --------------
    Use for explicit commands or script files while retaining cwd/env/timeout control.
    """
    INTERPRETERS: dict[str, Callable[[], str]]
    default_interpreter: str

    def __init__(self, default_interpreter: str='node') -> None:
        """Initialize a new ScriptRunner instance using the supplied configuration and input data.

        Parameters
        ----------
        default_interpreter : str (default: ``'node'``)
            Fallback executable used when a script extension has no registered interpreter.
        """
        ...

    def set_default_interpreter(self, interpreter: str) -> ScriptRunner:
        """Change the fallback interpreter used for script extensions that are not recognized explicitly.

        Parameters
        ----------
        interpreter : str
            Explicit interpreter executable; when omitted automatic detection is used.
        """
        ...

    def detect_interpreter(self, path: str) -> str:
        """Choose an interpreter from a script filename extension or fall back to the configured default.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        """
        ...

    def run(self, command: Sequence[Any], *, cwd: str | None=None, env: Mapping[str, str] | None=None, timeout: float | None=None, input_text: str | None=None, check: bool=False, capture_output: bool=True) -> CommandResult:
        """Execute a command synchronously and return a structured CommandResult.

        Parameters
        ----------
        command : Sequence[Union[str, os.PathLike[str]]]
            Sequence containing executable and command arguments.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        input_text : Optional[str] (default: ``None``)
            Optional standard-input text supplied to the subprocess.
        check : bool (default: ``False``)
            Whether non-zero process exit status should raise CalledProcessError.
        capture_output : bool (default: ``True``)
            Whether stdout/stderr are captured into CommandResult.

        Returns
        -------
        CommandResult containing exit code, streams and duration.

        Example::

            result = runner.run(["python", "--version"], timeout=10)
            result.check()
        """
        ...

    def run_async(self, command: Sequence[Any], *, cwd: str | None=None, env: Mapping[str, str] | None=None, stdout: Any=..., stderr: Any=...) -> subprocess.Popen[str]:
        """Start a subprocess asynchronously and return the live Popen object.

        Parameters
        ----------
        command : Sequence[Union[str, os.PathLike[str]]]
            Sequence containing executable and command arguments.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        stdout : Any (default: ``subprocess.PIPE``)
            stdout target passed to subprocess.Popen.
        stderr : Any (default: ``subprocess.PIPE``)
            stderr target passed to subprocess.Popen.

        Returns
        -------
        Live ``subprocess.Popen`` process handle.
        """
        ...

    def run_script(self, path: str, interpreter: str | None=None, terminal: bool=False, inputs: str | Sequence[str] | None=None, output: bool=True, *, cwd: str | None=None, env: Mapping[str, str] | None=None, timeout: float | None=None, check: bool=True) -> str | None:
        """Resolve a script interpreter and execute/open the script according to the requested mode.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        interpreter : Optional[str] (default: ``None``)
            Explicit interpreter executable; when omitted automatic detection is used.
        terminal : bool (default: ``False``)
            Whether to open the script in a separate terminal where supported.
        inputs : Optional[Union[str, Sequence[str]]] (default: ``None``)
            Additional script arguments/input values.
        output : bool (default: ``True``)
            Whether captured output is returned by the convenience method.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        check : bool (default: ``True``)
            Whether non-zero process exit status should raise CalledProcessError.
        """
        ...

@dataclass(slots=True)
class TaskInfo:
    """Immutable-style scheduler task snapshot.

    ``TaskInfo`` provides task identity, state, timing, repeat configuration, run/failure counters and latest result/error.

    When to use it
    --------------
    Returned by TaskScheduler inspection methods.
    """
    id: str
    state: str
    created_at: float
    next_run: float
    repeat: float | None
    priority: int
    runs: int = 0
    failures: int = 0
    last_result: Any = None
    last_error: BaseException | None = None

class TaskScheduler:
    """In-process task scheduler.

    ``TaskScheduler`` provides delayed, absolute-time and repeating tasks with pause/resume/cancel/retry state.

    When to use it
    --------------
    Use for lightweight application scheduling; it is not a durable distributed job queue.

    Concurrency model
    -----------------
    Tasks execute in daemon timer/worker threads inside the current process. Scheduler state is synchronized, but scheduled callables are normal application code and must coordinate their own shared data. Pending tasks do not survive process restart.

    Example::

        scheduler = TaskScheduler()
        task_id = scheduler.schedule_task(lambda: "done", delay=0.1)
        info = scheduler.wait(task_id, timeout=2.0)
        scheduler.shutdown()
    """

    def __init__(self) -> None:
        """Initialize a new TaskScheduler instance using the supplied configuration and input data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def schedule_task(self, func: Callable[..., Any], delay: float=0.0, repeat: float | None=None, priority: int=0, args: Sequence[Any]=(), kwargs: dict[str, Any] | None=None, *, retries: int=0, retry_delay: float=0.0, task_id: str | None=None) -> str:
        """Schedule a callable after a delay with optional repetition, priority metadata and retry behavior.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        delay : float (default: ``0.0``)
            Initial delay in seconds.
        repeat : Optional[float] (default: ``None``)
            Repeat interval in seconds; None schedules only one execution.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.
        args : Sequence[Any] (default: ``()``)
            Arguments passed to a script/callable/subprocess.
        kwargs : Optional[Dict[str, Any]] (default: ``None``)
            Keyword arguments forwarded to the target callable/helper.
        retries : int (default: ``0``)
            Number of retry attempts after task execution failures.
        retry_delay : float (default: ``0.0``)
            Delay in seconds between scheduler retry attempts.
        task_id : Optional[str] (default: ``None``)
            Optional caller-defined task identifier.

        Returns
        -------
        Task identifier string.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def schedule_at(self, when: datetime, func: Callable[..., Any], **kwargs: Any) -> str:
        """Schedule a callable for an absolute datetime by converting it to an appropriate delay.

        Parameters
        ----------
        when : datetime
            Absolute datetime at which the task should become eligible to run.
        func : Callable[..., Any]
            Callable applied by the operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.

        Returns
        -------
        Task identifier string.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def run_now(self, task_id: str) -> bool:
        """Trigger a queued task immediately in a daemon worker thread.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a known task and its pending timer.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def pause_task(self, task_id: str) -> bool:
        """Pause a pending task while retaining its remaining delay.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def resume_task(self, task_id: str) -> bool:
        """Resume a previously paused task using its recorded remaining delay.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def get_task(self, task_id: str) -> TaskInfo | None:
        """Return a TaskInfo snapshot for one task ID or None when unknown.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def list_tasks(self) -> list[dict[str, Any]]:
        """Return serializable-style snapshots of all scheduler tasks without internal timer/callable objects.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def wait(self, task_id: str, timeout: float | None=None, poll_interval: float=0.01) -> TaskInfo | None:
        """Poll task state until completion/failure/cancellation or timeout.

        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        poll_interval : float (default: ``0.01``)
            Seconds between state checks while waiting.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def shutdown(self, cancel_pending: bool=True) -> None:
        """Stop the scheduler and optionally cancel all unfinished tasks.

        Parameters
        ----------
        cancel_pending : bool (default: ``True``)
            Whether shutdown marks/cancels unfinished tasks.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

class Logger:
    """Thread-safe rotating application logger.

    ``Logger`` provides level filtering, contextual fields, console output, file persistence and size-based rotation.

    When to use it
    --------------
    Use for dependency-free application logging with bindable context.

    Logging behavior
    ----------------
    Messages below ``log_level`` are ignored. Accepted messages are rendered with an ISO local timestamp and level label, optional bound context fields are serialized as compact JSON, and file output is protected by a re-entrant lock. ``max_bytes=0`` disables rotation; otherwise numbered backups up to ``backup_count`` are maintained.

    Example::

        log = Logger("app.log", "INFO", max_bytes=1_000_000, backup_count=3)
        request_log = log.bind(component="api", request_id="req-42")
        request_log.info("request completed", status=200)
    """

    def __init__(self, log_file: str='app.log', log_level: str='INFO', *, console: bool=True, max_bytes: int=0, backup_count: int=5) -> None:
        """Initialize a new Logger instance using the supplied configuration and input data.

        Parameters
        ----------
        log_file : str (default: ``'app.log'``)
            Path of the plain UTF-8 log file.
        log_level : str (default: ``'INFO'``)
            Minimum accepted log severity name.
        console : bool (default: ``True``)
            Whether accepted log lines are also printed to stdout.
        max_bytes : int (default: ``0``)
            Maximum active log size before rotation; 0 disables rotation.
        backup_count : int (default: ``5``)
            Number of rotated backup files retained.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def set_log_level(self, level: str) -> Logger:
        """Change the minimum severity accepted by future log calls.

        Parameters
        ----------
        level : str
            Minimum severity level name.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def bind(self, **context: Any) -> Logger:
        """Create a logger sharing configuration but pre-populated with additional contextual fields.

        Parameters
        ----------
        **context : Any
            Value supplied for ``context`` according to the Logger contract.


        Notes
        -----
        The returned Logger has its own context mapping but writes to the same configured file path and uses the same severity/rotation settings. It is useful for request/module/entity context without modifying the parent logger.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def log_debug(self, message: str, **fields: Any) -> None:
        """Write a DEBUG message with optional structured context fields.

        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def log_info(self, message: str, **fields: Any) -> None:
        """Write an INFO message with optional structured context fields.

        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.

        Example::

            logger.info("user authenticated", user_id=42, method="token")
        """
        ...

    def log_warning(self, message: str, **fields: Any) -> None:
        """Write a WARNING message with optional structured context fields.

        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def log_error(self, message: str, **fields: Any) -> None:
        """Write an ERROR message with optional structured context fields.

        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def log_critical(self, message: str, **fields: Any) -> None:
        """Write a CRITICAL message with optional structured context fields.

        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...
    debug = log_debug
    info = log_info
    warning = log_warning
    error = log_error
    critical = log_critical

class EmailManager:
    """SMTP/IMAP e-mail helper.

    ``EmailManager`` provides plain/HTML message construction, CC/BCC, attachments, sending, delayed sends and inbox header inspection.

    When to use it
    --------------
    Use with provider credentials supplied by the application; protocol errors are not silently swallowed.
    """

    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str, imap_server: str | None=None, *, use_ssl: bool=False, starttls: bool=True) -> None:
        """Initialize a new EmailManager instance using the supplied configuration and input data.

        Parameters
        ----------
        smtp_server : str
            SMTP server hostname.
        smtp_port : int
            SMTP server port.
        email_address : str
            Account/from address used for SMTP authentication and message From.
        email_password : str
            Password/app-password supplied to SMTP/IMAP authentication.
        imap_server : Optional[str] (default: ``None``)
            Optional IMAP hostname; when omitted a hostname is derived from SMTP server.
        use_ssl : bool (default: ``False``)
            Use SMTP-over-SSL from connection start.
        starttls : bool (default: ``True``)
            Upgrade a non-SSL SMTP connection with STARTTLS before authentication.
        """
        ...

    def build_email(self, to: str | Sequence[str], subject: str, body: str, *, html: str | None=None, cc: str | Sequence[str] | None=None, bcc: str | Sequence[str] | None=None, attachments: Sequence[Any]=()) -> EmailMessage:
        """Construct an EmailMessage with plain text, optional HTML, CC/BCC and attachments.

        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        html : Optional[str] (default: ``None``)
            Optional HTML alternative body.
        cc : Union[str, Sequence[str], None] (default: ``None``)
            Optional visible carbon-copy recipients.
        bcc : Union[str, Sequence[str], None] (default: ``None``)
            Optional blind-carbon-copy recipients, intentionally omitted from visible headers.
        attachments : Iterable[Union[str, os.PathLike[str]]] (default: ``()``)
            Iterable of filesystem paths to attach.

        Returns
        -------
        Prepared ``email.message.EmailMessage``.
        """
        ...

    def send_message(self, message: EmailMessage) -> bool:
        """Send a prepared EmailMessage through the configured SMTP server.

        Parameters
        ----------
        message : EmailMessage
            Human-readable message text.

        Returns
        -------
        ``True`` after SMTP send completes without raising.
        """
        ...

    def send_email(self, to: str | Sequence[str], subject: str, body: str, **kwargs: Any) -> bool:
        """Build and send one e-mail in a convenience call.

        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.

        Returns
        -------
        ``True`` after message construction and SMTP send complete.
        """
        ...

    def schedule_email(self, to: str | Sequence[str], subject: str, body: str, send_time: datetime, **kwargs: Any) -> Any:
        """Schedule an e-mail send using an in-process daemon timer.

        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        send_time : datetime
            Datetime at which an in-process timer should send the message.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        ...

    def check_inbox(self, user: str | None=None, limit: int=10, mailbox: str='INBOX') -> list[dict[str, Any]]:
        """Fetch recent IMAP message headers from the selected mailbox.

        Parameters
        ----------
        user : Optional[str] (default: ``None``)
            Optional IMAP username overriding the configured e-mail address.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        mailbox : str (default: ``'INBOX'``)
            IMAP mailbox name.
        """
        ...

class FileTransferManager:
    """Tracked local/FTP transfer manager.

    ``FileTransferManager`` provides upload/download operations with IDs, progress callbacks and queryable status.

    When to use it
    --------------
    Use for simple file movement; SFTP is intentionally not emulated without an explicit dependency.
    """

    def __init__(self) -> None:
        """Initialize a new FileTransferManager instance using the supplied configuration and input data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def upload(self, file_path: str, destination: str, protocol: str='ftp', host: str='', username: str='', password: str='', port: int | None=None, *, progress: Callable[[int, int], Any] | None=None) -> str:
        """Upload/copy a local file using the selected local/FTP protocol and track progress.

        Parameters
        ----------
        file_path : str
            Local file path participating in transfer/log operations.
        destination : str
            Destination path or location.
        protocol : str (default: ``'ftp'``)
            Transfer protocol name (local/FTP where supported).
        host : str (default: ``''``)
            Remote host for network transfer.
        username : str (default: ``''``)
            Remote authentication username.
        password : str (default: ``''``)
            Remote authentication password.
        port : Optional[int] (default: ``None``)
            Optional remote port; protocol default is used when omitted.
        progress : Optional[Callable[[int, int], Any]] (default: ``None``)
            Optional callback receiving transferred and total byte counts.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def download(self, source: str, destination: str, protocol: str='ftp', host: str='', username: str='', password: str='', port: int | None=None, *, progress: Callable[[int, int], Any] | None=None) -> str:
        """Download/copy a file using the selected local/FTP protocol and track progress.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        protocol : str (default: ``'ftp'``)
            Transfer protocol name (local/FTP where supported).
        host : str (default: ``''``)
            Remote host for network transfer.
        username : str (default: ``''``)
            Remote authentication username.
        password : str (default: ``''``)
            Remote authentication password.
        port : Optional[int] (default: ``None``)
            Optional remote port; protocol default is used when omitted.
        progress : Optional[Callable[[int, int], Any]] (default: ``None``)
            Optional callback receiving transferred and total byte counts.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def get_status(self, transfer_id: str) -> str | None:
        """Return the last known status string for a transfer ID.

        Parameters
        ----------
        transfer_id : str
            Identifier returned when a transfer was started.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def get_progress(self, transfer_id: str) -> int | None:
        """Return the last known integer percentage for a transfer ID.

        Parameters
        ----------
        transfer_id : str
            Identifier returned when a transfer was started.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def check_transfer_status(self, transfer_id: str) -> Optional[str]:
        """Compatibility alias for get_status(); unknown transfer IDs return None."""
        ...

class TextProcessor:
    """Text analysis and transformation helper.

    ``TextProcessor`` provides token/sentence counts, search/replace, normalization, n-grams, extraction, summary, similarity and readability.

    When to use it
    --------------
    Use for lightweight text workflows without NLP dependencies.
    """

    def __init__(self, text: str='') -> None:
        """Initialize a new TextProcessor instance using the supplied configuration and input data.

        Parameters
        ----------
        text : str (default: ``''``)
            Text/content input.
        """
        ...

    def set_text(self, text: str) -> TextProcessor:
        """Replace the processor's default text and return the processor for fluent reuse.

        Parameters
        ----------
        text : str
            Text/content input.
        """
        ...

    def words(self, text: str | None=None) -> list[str]:
        """Tokenize text into the processor's word representation.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def sentences(self, text: str | None=None) -> list[str]:
        """Split text into sentence-like units using the dependency-free rules.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def word_count(self, text: str | None=None) -> int:
        """Return the number of words in the selected/default text.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def sentence_count(self, text: str | None=None) -> int:
        """Return the number of sentence-like units in the selected/default text.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def line_count(self, text: str | None=None) -> int:
        """Count logical lines in a text file.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def character_count(self, text: str | None=None, include_spaces: bool=True) -> int:
        """Count characters, optionally excluding whitespace.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        include_spaces : bool (default: ``True``)
            Whether whitespace contributes to character count.
        """
        ...

    def keyword_search(self, keyword: str, text: str | None=None, case_sensitive: bool=False) -> list[int]:
        """Return positions/matches for a keyword with optional case sensitivity.

        Parameters
        ----------
        keyword : str
            Keyword/substring to locate.
        text : Optional[str] (default: ``None``)
            Text/content input.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        """
        ...

    def replace(self, old: str, new: str, text: str | None=None) -> str:
        """Replace occurrences of one substring with another in selected/default text.

        Parameters
        ----------
        old : str
            Substring to replace.
        new : str
            Replacement substring.
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def normalize_whitespace(self, text: str | None=None) -> str:
        """Collapse/normalize whitespace while preserving text content semantics as defined by the helper.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def most_frequent_words(self, n: int=10, text: str | None=None) -> list[tuple[str, int]]:
        """Return the most frequent normalized words and their counts.

        Parameters
        ----------
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def ngrams(self, n: int=2, text: str | None=None) -> list[tuple[str, ...]]:
        """Return contiguous n-word groups from the selected/default text.

        Parameters
        ----------
        n : int (default: ``2``)
            Requested count, rank or n-gram width depending on the API.
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def extract_emails(self, text: str | None=None) -> list[str]:
        """Extract e-mail-address-like substrings using the helper's regular expression.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def extract_urls(self, text: str | None=None) -> list[str]:
        """Extract URL-like substrings using the helper's regular expression.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def summarize(self, sentences: int=3, text: str | None=None) -> str:
        """Create a simple extractive summary containing the requested number of sentences.

        Parameters
        ----------
        sentences : int (default: ``3``)
            Number of sentences requested in an extractive summary.
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def similarity(self, other: str, text: str | None=None, algorithm: str='hybrid') -> float:
        """Compare text with another string using the selected YoungLion fuzzy similarity algorithm.

        Parameters
        ----------
        other : str
            Another compatible object/value used by the operation.
        text : Optional[str] (default: ``None``)
            Text/content input.
        algorithm : str (default: ``'hybrid'``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        """
        ...

    def readability_score(self, text: str | None=None) -> float:
        """Return a lightweight readability metric derived from words/sentences/characteristics.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        """
        ...

    def stats(self, text: str | None=None) -> dict[str, Any]:
        """Return diagnostic counts describing the current cache/index/processor state.

        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        """
        ...

    def find_keywords(self, text: str, keywords: Sequence[str]) -> dict[str, int]:
        """Count case-insensitive, non-overlapping substring occurrences per keyword."""
        ...

    def replace_text(self, text: str, old: str, new: str) -> str:
        """Replace all occurrences of old in explicit text, preserving stored text."""
        ...

    def remove_stopwords(self, text: str, stopwords: Sequence[str]) -> str:
        """Remove case-insensitive whitespace-delimited stopwords; normalize spaces."""
        ...

    def unique_words(self, text: str) -> list[str]:
        """Return sorted, case-folded unique tokens using the current tokenizer."""
        ...

    def text_summary(self, text: str, max_sentences: int=3) -> str:
        """Return the first max_sentences sentences without changing stored text."""
        ...

    def find_longest_word(self, text: str) -> str:
        """Return the first longest token, or an empty string when text has no words."""
        ...

    def calculate_readability(self, text: str) -> float:
        """Compatibility entry point for the approximate Flesch reading-ease score."""
        ...

class EventBus:
    """Thread-safe in-process event bus.

    ``EventBus`` provides priority listeners, one-shot subscriptions, unsubscribe tokens and synchronous emission.

    When to use it
    --------------
    Use for decoupled application components where callbacks run in the emitting thread.
    """

    def __init__(self) -> None:
        """Initialize a new EventBus instance using the supplied configuration and input data.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def subscribe(self, event: str, callback: Callable[..., Any], *, once: bool=False, priority: int=0) -> str:
        """Register an event callback with priority and optional one-shot behavior; return its unsubscribe token.

        Parameters
        ----------
        event : str
            Event name.
        callback : Callable[..., Any]
            Listener/progress/callback function invoked by the operation.
        once : bool (default: ``False``)
            Whether an event listener automatically unregisters after one emission.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...
    on = subscribe

    def once(self, event: str, callback: Callable[..., Any], *, priority: int=0) -> str:
        """Register a callback that automatically unsubscribes after its first successful emission.

        Parameters
        ----------
        event : str
            Event name.
        callback : Callable[..., Any]
            Listener/progress/callback function invoked by the operation.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def unsubscribe(self, token: str) -> bool:
        """Remove a listener by subscription token and report whether it existed.

        Parameters
        ----------
        token : str
            Subscription token returned by EventBus.subscribe/once.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...
    off = unsubscribe

    def emit(self, event: str, *args: Any, **kwargs: Any) -> list[Any]:
        """Synchronously invoke listeners for an event in priority order and return callback results.

        Parameters
        ----------
        event : str
            Event name.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Listeners are invoked synchronously in the emitting thread. A slow listener therefore delays emit(); use your own worker/executor when asynchronous dispatch is required.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def listener_count(self, event: str | None=None) -> int:
        """Return the number of listeners for one event or across the entire bus.

        Parameters
        ----------
        event : Optional[str] (default: ``None``)
            Event name.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def clear(self, event: str | None=None) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.

        Parameters
        ----------
        event : Optional[str] (default: ``None``)
            Event name.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

class TTLCache:
    """Thread-safe TTL/LRU-style cache.

    ``TTLCache`` provides per-entry expiry, bounded size, recency updates, purge operations and hit/miss/eviction stats.

    When to use it
    --------------
    Use for small application memoization; values are held in-process only.
    """

    def __init__(self, max_size: int=1024, default_ttl: float | None=300.0) -> None:
        """Initialize a new TTLCache instance using the supplied configuration and input data.

        Parameters
        ----------
        max_size : int (default: ``1024``)
            Maximum number of cache entries retained.
        default_ttl : Optional[float] (default: ``300.0``)
            Default time-to-live in seconds; None means no expiry.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def set(self, key: Any, value: Any, ttl: Any=...) -> None:
        """Add a field assignment to the builder/plan and return self for fluent chaining.

        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        value : Any
            Target, new or comparison value.
        ttl : Any (default: ``_UTIL_MISSING``)
            Per-entry time-to-live override.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def get(self, key: Any, default: Any=None) -> Any:
        """Return a value for a key, falling back to a default when the key is absent.

        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        A successful get updates recency for LRU-style eviction. Expired entries are treated as misses and removed lazily.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def pop(self, key: Any, default: Any=...) -> Any:
        """Remove a key and return its value, optionally using a default when absent.

        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        default : Any (default: ``_UTIL_MISSING``)
            Fallback returned/used when the requested value or path is absent.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def delete(self, key: Any) -> bool:
        """Remove one cache entry and report whether it existed.

        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def purge(self) -> int:
        """Remove expired cache entries and return how many were discarded.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def items(self) -> list[tuple[Any, Any]]:
        """Return key/value pairs for the current mapping-like object.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def stats(self) -> dict[str, int]:
        """Return diagnostic counts describing the current cache/index/processor state.

        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def __contains__(self, key: object) -> bool:
        ...

    def __len__(self) -> int:
        ...

class RateLimiter:
    """Thread-safe token-bucket limiter.

    ``RateLimiter`` provides instant availability checks plus blocking/non-blocking token acquisition.

    When to use it
    --------------
    Use to smooth local request/task rates; it does not coordinate across processes.
    """

    def __init__(self, rate: float, capacity: float | None=None) -> None:
        """Initialize a new RateLimiter instance using the supplied configuration and input data.

        Parameters
        ----------
        rate : float
            Tokens replenished per second.
        capacity : Optional[float] (default: ``None``)
            Maximum token bucket size; defaults from rate when omitted.

        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def available(self) -> float:
        """Return the currently available token count after applying elapsed-time refill.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def try_acquire(self, tokens: float=1.0) -> bool:
        """Attempt to consume tokens immediately without waiting.

        Parameters
        ----------
        tokens : float (default: ``1.0``)
            Number of rate-limit tokens requested.

        Returns
        -------
        ``True`` if tokens were consumed immediately; otherwise ``False``.

        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def acquire(self, tokens: float=1.0, timeout: float | None=None) -> bool:
        """Wait up to an optional timeout until enough tokens are available, then consume them.

        Parameters
        ----------
        tokens : float (default: ``1.0``)
            Number of rate-limit tokens requested.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.

        Returns
        -------
        ``True`` when tokens were acquired before timeout, otherwise ``False``.

        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.

        Notes
        -----
        This limiter is process-local. Multiple processes or hosts need an external/shared rate-limiting coordinator if they must enforce one global quota.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

class RetryPolicy:
    """Synchronous retry policy.

    ``RetryPolicy`` provides bounded attempts with exponential backoff, maximum delay and configurable exception classes.

    When to use it
    --------------
    Use around idempotent or otherwise retry-safe operations.
    """

    def __init__(self, attempts: int=3, delay: float=0.0, backoff: float=2.0, max_delay: float | None=None, exceptions: tuple[type[BaseException], ...]=(Exception,)) -> None:
        """Initialize a new RetryPolicy instance using the supplied configuration and input data.

        Parameters
        ----------
        attempts : int (default: ``3``)
            Maximum total attempts including the first call.
        delay : float (default: ``0.0``)
            Initial delay in seconds.
        backoff : float (default: ``2.0``)
            Multiplier applied to delay after each failed attempt.
        max_delay : Optional[float] (default: ``None``)
            Optional upper bound for retry sleep seconds.
        exceptions : tuple[type[BaseException], ...] (default: ``(Exception,)``)
            Exception classes that trigger retry rather than immediate propagation.

        Raises
        ------
        ValueError
            If attempts is not positive or backoff is below 1.
        """
        ...

    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute a callable through this policy object, applying retry/circuit-breaker behavior defined by the class.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        Only retry operations that are safe to repeat or whose side effects are explicitly handled by the caller.
        """
        ...
    __call__ = call

class CircuitBreaker:
    """Thread-safe circuit breaker.

    ``CircuitBreaker`` provides closed/open/half-open states with failure threshold, recovery timeout and success threshold.

    When to use it
    --------------
    Use to stop repeatedly calling a failing dependency and probe recovery later.
    """
    CLOSED: str
    OPEN: str
    HALF_OPEN: str

    def __init__(self, failure_threshold: int=5, recovery_timeout: float=30.0, success_threshold: int=1) -> None:
        """Initialize a new CircuitBreaker instance using the supplied configuration and input data.

        Parameters
        ----------
        failure_threshold : int (default: ``5``)
            Consecutive/accumulated failure count that opens the circuit.
        recovery_timeout : float (default: ``30.0``)
            Seconds the circuit remains open before permitting a half-open probe.
        success_threshold : int (default: ``1``)
            Successful half-open calls required before closing the circuit.

        Raises
        ------
        ValueError
            If failure/success thresholds are not positive.

        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    @property
    def state(self) -> str:
        """Return the current circuit-breaker state, advancing OPEN to HALF_OPEN after the recovery timeout.


        Notes
        -----
        Reading state may transition OPEN to HALF_OPEN after the configured recovery timeout; state inspection is therefore not a purely passive field read.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def allow(self) -> bool:
        """Return whether a call is currently permitted by circuit-breaker state.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def reset(self) -> None:
        """Reset internal state/counters to their initial healthy configuration.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...

    def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute a callable through this policy object, applying retry/circuit-breaker behavior defined by the class.

        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.


        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        ...
    __call__ = call

class Stopwatch:
    """Monotonic stopwatch.

    ``Stopwatch`` provides elapsed-time measurement, start/stop/reset, laps and context-manager support.

    When to use it
    --------------
    Use for application timing and benchmarks where wall-clock changes must not matter.
    """

    def __init__(self, start: bool=True) -> None:
        """Initialize a new Stopwatch instance using the supplied configuration and input data.

        Parameters
        ----------
        start : bool (default: ``True``)
            Whether the stopwatch starts immediately or remains stopped initially.
        """
        ...

    @property
    def running(self) -> bool:
        """Return whether the stopwatch is currently accumulating time."""
        ...

    @property
    def elapsed(self) -> float:
        """Return accumulated elapsed seconds using a monotonic high-resolution clock.

        Returns
        -------
        Elapsed seconds as a floating-point value.
        """
        ...

    def start(self) -> Stopwatch:
        """Start or resume the stopwatch and return self."""
        ...

    def stop(self) -> float:
        """Stop timing and return total accumulated seconds.

        Returns
        -------
        Total accumulated elapsed seconds.
        """
        ...

    def reset(self, *, start: bool=True) -> Stopwatch:
        """Reset internal state/counters to their initial healthy configuration.

        Parameters
        ----------
        start : bool (default: ``True``)
            Whether the stopwatch starts immediately or remains stopped initially.
        """
        ...

    def lap(self) -> float:
        """Return seconds since the previous lap/start without stopping the stopwatch.

        Returns
        -------
        Seconds since the previous lap/start.
        """
        ...

    def __enter__(self) -> Stopwatch:
        ...

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        ...

class Terminal:
    """Dependency-free terminal rendering helper.

    ``Terminal`` provides color capability detection, visible widths, truncation/padding, tables, clearing and progress bars.

    When to use it
    --------------
    Use for compact CLI presentation without a terminal UI dependency.
    """

    @staticmethod
    def supports_color(stream: Any=None) -> bool:
        """Detect whether an output stream is likely to support ANSI color while respecting NO_COLOR/FORCE_COLOR.

        Parameters
        ----------
        stream : Any (default: ``None``)
            Output stream used for capability checks/clearing.

        Returns
        -------
        Boolean terminal capability decision.
        """
        ...

    @staticmethod
    def size(fallback: tuple[int, int]=(80, 24)) -> tuple[int, int]:
        """Return the number of nodes/items or terminal dimensions, depending on the class.

        Parameters
        ----------
        fallback : tuple[int, int] (default: ``(80, 24)``)
            Fallback terminal dimensions when the OS cannot determine them.
        """
        ...

    @classmethod
    def strip_ansi(cls, text: object) -> str:
        """Perform the ``strip_ansi`` operation for Terminal.

        Parameters
        ----------
        text : object
            Text/content input.
        """
        ...

    @classmethod
    def visible_width(cls, text: object) -> int:
        """Return display width after removing ANSI escape sequences.

        Parameters
        ----------
        text : object
            Text/content input.
        """
        ...

    @classmethod
    def truncate(cls, text: object, width: int, suffix: str='…') -> str:
        """Truncate styled/plain text to a target visible width and append a suffix when required.

        Parameters
        ----------
        text : object
            Text/content input.
        width : int
            Width in characters/pixels/units according to the API.
        suffix : str (default: ``'…'``)
            Suffix appended when truncation occurs.
        """
        ...

    @classmethod
    def pad(cls, text: object, width: int, align: str='left') -> str:
        """Pad text to a target visible width using left/right/center alignment.

        Parameters
        ----------
        text : object
            Text/content input.
        width : int
            Width in characters/pixels/units according to the API.
        align : str (default: ``'left'``)
            Text alignment: left, right or center where supported.
        """
        ...

    @classmethod
    def table(cls, rows: Iterable[Sequence[Any]], headers: Sequence[Any] | None=None, *, padding: int=1, max_width: int | None=None) -> str:
        """Render rows and optional headers as a dependency-free fixed-width text table.

        Parameters
        ----------
        rows : Iterable[Sequence[Any]]
            Dataset/matrix row data.
        headers : Optional[Sequence[Any]] (default: ``None``)
            Optional table header row.
        padding : int (default: ``1``)
            Spaces inserted around table cell content.
        max_width : Optional[int] (default: ``None``)
            Optional maximum visible width of a rendered table cell/table.
        """
        ...

    @staticmethod
    def clear(stream: Any=None) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.

        Parameters
        ----------
        stream : Any (default: ``None``)
            Output stream used for capability checks/clearing.
        """
        ...

    @staticmethod
    def progress(current: float, total: float, *, width: int=30, label: str='', fill: str='#', empty: str='-') -> str:
        """Render a compact textual progress bar and percentage.

        Parameters
        ----------
        current : float
            Current progress position.
        total : float
            Total progress size.
        width : int (default: ``30``)
            Width in characters/pixels/units according to the API.
        label : str (default: ``''``)
            Optional text label prefixed to a progress bar.
        fill : str (default: ``'#'``)
            Character used for completed progress.
        empty : str (default: ``'-'``)
            Character used for remaining progress.
        """
        ...
