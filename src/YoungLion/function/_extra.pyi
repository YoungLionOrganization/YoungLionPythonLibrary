"""Extended file, script, archive and lightweight document helpers.

FileExtraMixin adds Markdown/RTF/HTML/CSS/JavaScript/TeX/Python writing,
compression helpers, SQLite execution and small conversion/execution utilities
to the main File facade.  Operations that invoke external runtimes or TeX tools
require those executables to be installed by the host system; YoungLion does not
bundle them.
"""
from collections.abc import Sequence
from typing import Any

class FileExtraMixin:
    """Extended File mixin.

    ``FileExtraMixin`` provides document/script/archive/SQLite helpers and lightweight format conversions.

    When to use it
    --------------
    Used through YoungLion.File; external-runtime features require the corresponding system tools.
    """

    def md_write(self, path: str, content: str, append: bool=False) -> None:
        """Write Markdown text to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def rtf_write(self, path: str, content: str, append: bool=False) -> None:
        """Write RTF content to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def html_write(self, path: str, content: str, append: bool=False) -> None:
        """Write HTML content to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def css_write(self, path: str, content: str, append: bool=False) -> None:
        """Write CSS content to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def js_write(self, path: str, content: str, append: bool=False) -> None:
        """Write JavaScript content to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def tex_write(self, path: str, content: str) -> None:
        """Write TeX/LaTeX source to a file.

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

    def tex_append(self, path: str, content: str) -> None:
        """Append TeX/LaTeX source to a file.

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

    def py_write(self, path: str, content: str, append: bool=False) -> None:
        """Write Python source code to a file.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def handle_compressed(self, path: str, action: str, target: str | None=None) -> Any:
        """Create/extract/list compressed archive content using the supported archive formats.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        action : str
            Archive action such as create/extract/list supported by the method.
        target : Optional[str] (default: ``None``)
            Target path used by an archive/link/conversion operation.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def sql_execute(self, path: str, query: str, params: Sequence[Any]=()) -> Any:
        """Execute a SQLite query against a database file and return the operation result.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        query : str
            Search text, structured query or SQL/XML expression according to the method.
        params : Sequence[Any] (default: ``()``)
            Optional SQL parameter sequence/mapping passed separately from the query.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    @staticmethod
    def markdown_to_latex(markdown: str) -> str:
        """Convert a lightweight supported subset of Markdown syntax into LaTeX source.

        Parameters
        ----------
        markdown : str
            Value supplied for ``markdown`` according to the FileExtraMixin contract.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    @staticmethod
    def latex_compile(content: str) -> str:
        """Compile LaTeX source with an available external TeX tool and return the produced result/path.

        Parameters
        ----------
        content : str
            Text/bytes/content payload to write, search or convert.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    @staticmethod
    def tex_to_markdown(content: str) -> str:
        """Convert a limited supported subset of TeX/LaTeX markup back to Markdown-like text.

        Parameters
        ----------
        content : str
            Text/bytes/content payload to write, search or convert.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def latex_to_html(self, content: str, output_path: str | None=None) -> str:
        """Convert supported LaTeX content to HTML and write it to the requested output path.

        Parameters
        ----------
        content : str
            Text/bytes/content payload to write, search or convert.
        output_path : Optional[str] (default: ``None``)
            Filesystem or dotted-data path used by this operation.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def latex_to_image(self, content: str, output_path: str) -> str:
        """Render/convert LaTeX content to an image using available external tooling.

        Parameters
        ----------
        content : str
            Text/bytes/content payload to write, search or convert.
        output_path : str
            Filesystem or dotted-data path used by this operation.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def py_run(self, path: str, args: Sequence[str] | None=None, terminal: bool=False) -> str | None:
        """Execute a Python script with optional arguments/terminal behavior.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        args : Optional[Sequence[str]] (default: ``None``)
            Arguments passed to a script/callable/subprocess.
        terminal : bool (default: ``False``)
            Whether to open the script in a separate terminal where supported.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def py_add_code(self, path: str, code: str, position: str | int='end') -> None:
        """Insert Python source text at a requested position in an existing script.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        code : str
            Value supplied for ``code`` according to the FileExtraMixin contract.
        position : Union[str, int] (default: ``'end'``)
            Insertion position used when modifying a script.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def js_run(self, path: str, args: Sequence[str] | None=None, terminal: bool=False) -> str | None:
        """Execute a JavaScript file through an available Node.js runtime.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        args : Optional[Sequence[str]] (default: ``None``)
            Arguments passed to a script/callable/subprocess.
        terminal : bool (default: ``False``)
            Whether to open the script in a separate terminal where supported.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...
