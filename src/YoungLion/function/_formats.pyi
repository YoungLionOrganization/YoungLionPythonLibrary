"""Structured file-format helpers mixed into :class:`YoungLion.File`.

The mixin implements dependency-free or standard-library-backed readers/writers
for PDF text output, XML, CSV, a deliberately limited YAML subset, INI and Java-
style properties files.  The goal is convenient application interchange without
adding runtime dependencies.  It is not intended to replace full standards-
compliant third-party parsers for advanced PDF/YAML features.
"""
from typing import Any

class FileFormatsMixin:
    """Structured-format File mixin.

    ``FileFormatsMixin`` provides PDF/XML/CSV/YAML-like/INI/properties read-write helpers.

    When to use it
    --------------
    Used through YoungLion.File rather than instantiated directly.
    """

    def pdf_read(self, path: str) -> str:
        """Extract text from the subset of PDF files supported by YoungLion's dependency-free reader.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        The dependency-free PDF helper supports a practical/basic subset and is not a replacement for a full PDF parser/OCR engine.
        """
        ...

    def pdf_write(self, path: str, content: str) -> None:
        """Create a basic PDF document containing the supplied text content.

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
        The dependency-free writer is intended for basic text documents rather than advanced page-layout, font embedding or graphics workflows.
        """
        ...

    def xml_read(self, path: str) -> dict[str, Any] | None:
        """Parse XML into YoungLion's mapping-oriented representation.

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

    def xml_write(self, path: str, data: dict[str, Any], root_element: str='root') -> None:
        """Serialize mapping-like data as XML with the requested root element.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Dict[str, Any]
            Input mapping or record data used to initialize the object.
        root_element : str (default: ``'root'``)
            Root XML element name.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def xml_append(self, path: str, data: dict[str, Any], root_element: str='root') -> None:
        """Append data to an XML document using the helper's supported structure.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Dict[str, Any]
            Input mapping or record data used to initialize the object.
        root_element : str (default: ``'root'``)
            Root XML element name.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def xml_find(self, path: str, query: str) -> dict[str, Any] | None:
        """Find XML elements matching the supplied query expression.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        query : str
            Search text, structured query or SQL/XML expression according to the method.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def csv_read(self, path: str, delimiter: str=',', quotechar: str='"') -> list[dict[str, str]]:
        """Read CSV rows using configurable delimiter and quote character.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        delimiter : str (default: ``','``)
            CSV field delimiter character.
        quotechar : str (default: ``'"'``)
            CSV quote character.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def csv_write(self, path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"') -> None:
        """Write mapping/sequence records to CSV with explicit field names and dialect characters.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : List[Dict[str, str]]
            Input mapping or record data used to initialize the object.
        fieldnames : Optional[List[str]] (default: ``None``)
            Ordered CSV column names.
        delimiter : str (default: ``','``)
            CSV field delimiter character.
        quotechar : str (default: ``'"'``)
            CSV quote character.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def csv_append(self, path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"') -> None:
        """Append CSV records while preserving the configured dialect.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : List[Dict[str, str]]
            Input mapping or record data used to initialize the object.
        fieldnames : Optional[List[str]] (default: ``None``)
            Ordered CSV column names.
        delimiter : str (default: ``','``)
            CSV field delimiter character.
        quotechar : str (default: ``'"'``)
            CSV quote character.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def csv_update(self, path: str, data: list[dict[str, str]], identifier: str, delimiter: str=',', quotechar: str='"') -> None:
        """Update CSV rows identified by a key/identifier field.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : List[Dict[str, str]]
            Input mapping or record data used to initialize the object.
        identifier : str
            CSV field used to identify rows for update.
        delimiter : str (default: ``','``)
            CSV field delimiter character.
        quotechar : str (default: ``'"'``)
            CSV quote character.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def yaml_read(self, path: str, default: dict[str, Any] | None=None) -> dict[str, Any]:
        """Read YoungLion's supported dependency-free YAML subset.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Optional[dict] (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        YoungLion intentionally implements a small dependency-free YAML subset. Use a full YAML parser when anchors, tags, custom types or complex YAML semantics are required.
        """
        ...

    def yaml_write(self, path: str, data: dict[str, Any]) -> None:
        """Write data using YoungLion's supported dependency-free YAML subset.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : dict
            Input mapping or record data used to initialize the object.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.

        Notes
        -----
        YoungLion intentionally writes a small portable YAML-like subset rather than claiming full YAML specification coverage.
        """
        ...

    def ini_read(self, path: str, default: dict[str, dict[str, str]] | None=None) -> dict[str, dict[str, str]]:
        """Read an INI configuration into nested mapping data.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Optional[Dict[str, Dict[str, str]]] (default: ``None``)
            Fallback returned/used when the requested value or path is absent.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def ini_write(self, path: str, data: dict[str, dict[str, str]], append: bool=False) -> None:
        """Write or append INI sections and values.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Dict[str, Dict[str, str]]
            Input mapping or record data used to initialize the object.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...

    def properties_read(self, path: str) -> dict[str, str]:
        """Read Java-style key=value properties.

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

    def properties_write(self, path: str, data: dict[str, str], append: bool=False) -> None:
        """Write Java-style key=value properties.

        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Dict[str, str]
            Input mapping or record data used to initialize the object.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.


        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        ...
