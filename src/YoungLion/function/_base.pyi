"""Core filesystem and debugging primitives used by YoungLion.function.

:class:`FileBase` provides normalized path handling plus dependency-free file and
directory operations, structured JSON/text helpers, binary I/O, checksums,
atomic writes, chunked reads, backups and simple log persistence.  :class:`Debugger`
is the lightweight console diagnostic helper retained for compatibility.

Methods generally raise the underlying Python/OSError family exception when the
requested operation cannot be completed; they do not silently hide filesystem
failures.  Atomic-write helpers are the preferred choice when replacing important
configuration or state files.
"""
from collections.abc import Iterator, Mapping
from typing import Any

class Debugger:
    """Lightweight console debugger.

    ``Debugger`` provides severity-filtered colored diagnostic messages and custom symbols.

    When to use it
    --------------
    Use for compatibility/simple scripts; Logger is preferred when persistent structured logging is needed.
    """
    COLORS: dict[str, str]
    SYMBOLS: dict[str, str]
    level: int
    DefaultSymbol: bool
    ansi: bool

    def __init__(self, level: int=0, DefaultSymbol: bool=False) -> None:
        """Initialize a new Debugger instance using the supplied configuration and input data.

        Parameters
        ----------
        level : int (default: ``0``)
            Minimum severity level name.
        DefaultSymbol : bool (default: ``False``)
            Whether the compatibility debugger uses its default status symbols.
        """
        ...

    def info(self, message: str) -> None:
        """Emit an informational diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def debug(self, message: str) -> None:
        """Emit a debug diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def success(self, message: str) -> None:
        """Emit a success diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def warning(self, message: str) -> None:
        """Emit a warning diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def error(self, message: str) -> None:
        """Emit an error diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def critical(self, message: str) -> None:
        """Emit a critical diagnostic message if enabled by the configured level.

        Parameters
        ----------
        message : str
            Human-readable message text.
        """
        ...

    def custom(self, message: str, color_code: str='\x1b[1;95m', symbol: str='*') -> None:
        """Emit a diagnostic message with caller-provided color/symbol styling.

        Parameters
        ----------
        message : str
            Human-readable message text.
        color_code : str (default: ``'[1;95m'``)
            Value supplied for ``color_code`` according to the Debugger contract.
        symbol : str (default: ``'*'``)
            Value supplied for ``symbol`` according to the Debugger contract.
        """
        ...

    def set_level(self, level: int) -> None:
        """Change the minimum severity level used by future diagnostic/logging calls.

        Parameters
        ----------
        level : int
            Minimum severity level name.
        """
        ...

class FileBase:
    """Core filesystem facade.

    ``FileBase`` provides safe path resolution, file/directory management, text/binary/JSON I/O, checksums and atomic persistence.

    When to use it
    --------------
    Use directly only for core behavior; the public File facade adds format and extra mixins.
    """
    SUPPORTED_FORMATS: list[str]
    filefolder: str | None
    debug: bool
    debugger: Debugger

    def __init__(self, filefolder: str | None=None, debug: bool=False, debugger: Debugger | None=None) -> None:
        """Initialize a new FileBase instance using the supplied configuration and input data.

        Parameters
        ----------
        filefolder : Optional[str] (default: ``None``)
            Optional base folder used for resolving relative paths.
        debug : bool (default: ``False``)
            Whether compatibility debug behavior is enabled.
        debugger : Optional[Debugger] (default: ``None``)
            Optional Debugger instance used by file operations.

        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def get_info(self, path: str) -> dict[str, Any]:
        """Return filesystem metadata for a resolved path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def rename_file(self, old_path: str, new_name: str) -> bool:
        """Rename a file while preserving its parent directory.

        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_name : str
            Value supplied for ``new_name`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def rename_folder(self, old_path: str, new_name: str) -> bool:
        """Rename a directory while preserving its parent directory.

        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_name : str
            Value supplied for ``new_name`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def create_shortcut(self, target_path: str, shortcut_path: str, description: str='') -> bool:
        """Create a platform-appropriate shortcut/link to a target path where supported.

        Parameters
        ----------
        target_path : str
            Filesystem or dotted-data path used by this operation.
        shortcut_path : str
            Filesystem or dotted-data path used by this operation.
        description : str (default: ``''``)
            Value supplied for ``description`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def list_files_and_folders(self, path: str | None=None) -> list[str]:
        """List immediate directory entries grouped or represented by the File API.

        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def create_folder(self, folder_path: str) -> bool:
        """Create a directory path, including required parents.

        Parameters
        ----------
        folder_path : str
            Filesystem or dotted-data path used by this operation.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file to the requested destination.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def copy_folder(self, source: str, destination: str) -> bool:
        """Recursively copy a directory tree to the requested destination.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def move_file(self, source: str, destination: str) -> bool:
        """Move a file to the requested destination.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def move_folder(self, source: str, destination: str) -> bool:
        """Move a directory tree to the requested destination.

        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def delete_file(self, path: str) -> bool:
        """Delete the requested file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def delete_folder(self, path: str) -> bool:
        """Recursively delete the requested directory.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def json_read(self, path: str, default: dict[str, Any] | list[Any] | None=None) -> dict[str, Any] | list[Any]:
        """Read and decode a JSON file, returning a default according to the method contract when appropriate.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Optional[Union[dict, list]] (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def json_write(self, path: str, data: dict[str, Any] | list[Any]) -> None:
        """Serialize data as JSON and write it to the resolved path.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[dict, list]
            Input mapping or record data used to initialize the object.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def txt_read_str(self, path: str) -> str:
        """Read an entire text file as one string.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def txt_read_linear(self, path: str) -> dict[str, str]:
        """Read a text file into a line-oriented representation.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def txt_write_str(self, path: str, content: str) -> None:
        """Write one string to a text file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def txt_write_linear(self, path: str, data: Mapping[int, str]) -> None:
        """Write an iterable of line values to a text file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Mapping[int, str]
            Input mapping or record data used to initialize the object.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def exists(self, path: str) -> bool:
        """Return whether any record satisfies the dotted-path comparison.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.

        Returns
        -------
        ``True`` if at least one matching record exists.
        """
        ...

    def is_file(self, path: str) -> bool:
        """Return whether the resolved path exists and is a regular file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        """
        ...

    def is_folder(self, path: str) -> bool:
        """Return whether the resolved path exists and is a directory.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        """
        ...

    def file_size(self, path: str) -> int:
        """Return a file's size in bytes.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def directory_size(self, path: str | None=None, recursive: bool=True) -> int:
        """Calculate directory size, optionally recursing into descendants.

        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def read_bytes(self, path: str) -> bytes:
        """Read a file as raw bytes.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def write_bytes(self, path: str, data: bytes | bytearray | memoryview, append: bool=False) -> None:
        """Write raw bytes, optionally appending instead of replacing.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.

        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def append_bytes(self, path: str, data: bytes | bytearray | memoryview) -> None:
        """Append raw bytes to an existing/new file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def touch(self, path: str) -> bool:
        """Create the file if absent and/or update its modification time.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def line_count(self, path: str) -> int:
        """Count logical lines in a text file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def compare_files(self, first: str, second: str) -> bool:
        """Compare two files for content equality using the implementation's efficient path.

        Parameters
        ----------
        first : str
            Value supplied for ``first`` according to the FileBase contract.
        second : str
            Value supplied for ``second`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def checksum(self, path: str, algorithm: str='sha256') -> str:
        """Calculate a cryptographic/content digest using the requested hashlib algorithm.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        algorithm : str (default: ``'sha256'``)
            Algorithm name used for hashing, fuzzy matching or search ranking.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def head(self, path: str, lines: int=10) -> list[str]:
        """Return the first requested number of lines from a text file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        lines : int (default: ``10``)
            Value supplied for ``lines`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def tail(self, path: str, lines: int=10, block_size: int=8192) -> list[str]:
        """Return the final requested number of lines from a text file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        lines : int (default: ``10``)
            Value supplied for ``lines`` according to the FileBase contract.
        block_size : int (default: ``8192``)
            Value supplied for ``block_size`` according to the FileBase contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def atomic_write_text(self, path: str, content: str) -> None:
        """Replace a text file atomically using a same-directory temporary file and fsync/replace sequence where supported.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        Atomic replacement is strongest when source/temp/destination reside on the same filesystem. The implementation writes a unique same-directory temporary file, flushes/fsyncs where supported and then replaces the destination.
        """
        ...

    def atomic_write_bytes(self, path: str, data: bytes | bytearray | memoryview) -> None:
        """Replace a binary file atomically using a same-directory temporary file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        Atomic replacement is strongest when source/temp/destination reside on the same filesystem.
        """
        ...

    def atomic_write_json(self, path: str, data: dict[str, Any] | list[Any], indent: int=4) -> None:
        """Serialize JSON and atomically replace the destination file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[dict, list]
            Input mapping or record data used to initialize the object.
        indent : int (default: ``4``)
            JSON indentation level; use the supported compact value for minimal output.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        Serialization happens before replacement, reducing the chance that a partially written JSON document becomes the final destination.

        Example::

            File().atomic_write_json("settings.json", {"theme": "dark"})
        """
        ...

    def find_files(self, pattern: str='*', path: str | None=None, *, recursive: bool=True, extensions: list[str] | None=None, min_size: int | None=None, max_size: int | None=None) -> list[str]:
        """Discover files below a directory using name/extension/size filters.

        Parameters
        ----------
        pattern : str (default: ``'*'``)
            Filename/pattern filter.
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the FileBase contract.
        extensions : Optional[list[str]] (default: ``None``)
            Allowed file extensions, typically including leading dots.
        min_size : Optional[int] (default: ``None``)
            Optional minimum file/content size filter.
        max_size : Optional[int] (default: ``None``)
            Maximum number of cache entries retained.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def read_chunks(self, path: str, chunk_size: int=1024 * 1024) -> Iterator[bytes]:
        """Iterate a binary file in bounded chunks to avoid loading the entire file into memory.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        chunk_size : int (default: ``1024 * 1024``)
            Maximum number of bytes read per yielded chunk.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def backup(self, path: str, destination: str | None=None) -> str:
        """Create a backup copy of a file or directory at the requested destination.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        destination : Optional[str] (default: ``None``)
            Destination path or location.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def log_read(self, path: str) -> dict[str, str]:
        """Read a simple YoungLion log file representation.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def log_write(self, path: str, content: str) -> None:
        """Append/write log text through the File facade.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.

        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def log_write_entry(self, path: str, entry: str) -> None:
        """Persist one structured log entry in the File helper format.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        entry : str
            Structured or textual log entry to persist.

        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...
