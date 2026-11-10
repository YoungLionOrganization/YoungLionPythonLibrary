"""Reusable DDM-based mathematical, geometric, temporal and tabular models.

The module contains compact structures that are useful across applications
without requiring NumPy, pandas or geometry packages: Range, Vector, Timeline,
Dataset, Size, Point, Color, Matrix and TreeDDM.  They retain DDM serialization
and inspection behavior while adding domain-specific operations.

These classes favor predictable, dependency-free behavior over exhaustive
scientific-computing functionality.  They are suitable for configuration,
application state, game logic, lightweight analytics and transport objects; use
specialized numerical libraries when very large matrix/dataframe workloads are
the primary requirement.
"""
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from typing import Any, Dict, List
from ._core import DDM

class Range(DDM):
    """Bounded numeric interval model.

    ``Range`` provides containment, clamp, normalization, subdivision, intersection and iteration.

    When to use it
    --------------
    Use for progress scales, game/stat bounds, coordinate intervals and normalization.
    """
    min_val: float
    max_val: float
    step: float

    def __init__(self, min_val: float=0.0, max_val: float=1.0, step: float=1.0) -> None:
        """Initialize a new Range instance using the supplied configuration and input data.

        Parameters
        ----------
        min_val : float (default: ``0.0``)
            Lower numeric bound of the range.
        max_val : float (default: ``1.0``)
            Upper numeric bound of the range.
        step : float (default: ``1.0``)
            Iteration step used by Range.
        """
        ...

    def contains(self, value: float) -> bool:
        """Return whether a value/substring lies within the represented range or indexed path data.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        """
        ...

    def clamp(self, value: float) -> float:
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        """
        ...

    def span(self) -> float:
        """Return the numeric width of the range."""
        ...

    def midpoint(self) -> float:
        """Return the midpoint of this object relative to its range/geometry semantics."""
        ...

    def normalize(self, value: float) -> float:
        """Convert a raw value into normalized range/vector form.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        """
        ...

    def denormalize(self, value: float) -> float:
        """Convert a normalized scalar back into the range's coordinate space.

        Parameters
        ----------
        value : float
            Target, new or comparison value.
        """
        ...

    def random(self) -> float:
        """Return a random value drawn from the represented range."""
        ...

    def iterate(self) -> Iterator[float]:
        """Iterate upward from min_val or downward from max_val for a negative step.

        Bounds are inclusive within the existing 1e-12 endpoint tolerance.
        Raise ValueError if floating-point precision prevents step from advancing
        before the endpoint; this avoids an endless iterator for tiny steps.
        """
        ...

    def subdivide(self, parts: int) -> List[Range]:
        """Split the range into the requested number of contiguous subranges.

        Parameters
        ----------
        parts : int
            Number of subranges requested.
        """
        ...

    def intersect(self, other: Range) -> Range | None:
        """Return the overlapping portion of two ranges when one exists.

        Parameters
        ----------
        other : 'Range'
            Another compatible object/value used by the operation.
        """
        ...

    def overlaps(self, other: Range) -> bool:
        """Return whether this range overlaps another range.

        Parameters
        ----------
        other : 'Range'
            Another compatible object/value used by the operation.
        """
        ...

class Vector(DDM):
    """N-dimensional vector model.

    ``Vector`` provides magnitude, normalization, dot/cross products, projection, interpolation and arithmetic.

    When to use it
    --------------
    Use for dependency-free geometry/game/application calculations.
    """
    components: List[float]

    def __init__(self, components: Sequence[float]) -> None:
        """Initialize a new Vector instance using the supplied configuration and input data.

        Parameters
        ----------
        components : Sequence[float]
            Numeric components used to initialize the vector.
        """
        ...

    def magnitude(self) -> float:
        """Return the Euclidean magnitude of the vector."""
        ...

    def normalize(self) -> Vector:
        """Convert a raw value into normalized range/vector form."""
        ...

    def dot(self, other: Vector) -> float:
        """Return the dot product with another vector.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def cross(self, other: Vector) -> Vector:
        """Return the cross product for supported vector dimensions.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def distance_to(self, other: Vector) -> float:
        """Return Euclidean distance to another compatible point/vector.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def angle_to(self, other: Vector) -> float:
        """Return the angle between this vector and another vector.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def add(self, other: Vector) -> Vector:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def subtract(self, other: Vector) -> Vector:
        """Subtract another value or queue a subtraction operation.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def scale(self, scalar: float) -> Vector:
        """Return a scaled version of the represented numeric/geometry object.

        Parameters
        ----------
        scalar : float
            Numeric scalar multiplier.
        """
        ...

    def project_onto(self, other: Vector) -> Vector:
        """Project this vector onto another vector.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        """
        ...

    def perpendicular(self) -> Vector:
        """Return a perpendicular vector where the operation is defined."""
        ...

    def lerp(self, other: Vector, t: float) -> Vector:
        """Linearly interpolate between this value and another compatible value.

        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        t : float
            Interpolation parameter, normally between 0 and 1.
        """
        ...

    def __add__(self, other: Vector) -> Vector:
        ...

    def __sub__(self, other: Vector) -> Vector:
        ...

    def __mul__(self, scalar: float) -> Vector:
        ...

    def __truediv__(self, scalar: float) -> Vector:
        ...
    __rmul__ = __mul__

class Timeline(DDM):
    """Event timeline model.

    ``Timeline`` provides bounded time range plus named event management, filtering and progress calculation.

    When to use it
    --------------
    Use for schedules, animation/event progress and milestone collections.
    """
    start_time: float
    end_time: float
    events: List[Dict[str, Any]]

    def __init__(self, start_time: float=0.0, end_time: float=1.0, events: List[Dict[str, Any]] | None=None) -> None:
        """Initialize a new Timeline instance using the supplied configuration and input data.

        Parameters
        ----------
        start_time : float (default: ``0.0``)
            Lower/start position of the timeline.
        end_time : float (default: ``1.0``)
            Upper/end position of the timeline.
        events : Optional[List[Dict[str, Any]]] (default: ``None``)
            Optional initial event records.
        """
        ...

    def add_event(self, time: float, name: str, data: Any=None) -> Dict[str, Any]:
        """Add a named event at a timeline position.

        Parameters
        ----------
        time : float
            Timeline position for the operation.
        name : str
            Name/label used by the object or event.
        data : Any (default: ``None``)
            Input mapping or record data used to initialize the object.
        """
        ...

    def remove_event(self, name: str) -> bool:
        """Remove timeline events matching the supplied name.

        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        """
        ...

    def get_event(self, name: str) -> Dict[str, Any] | None:
        """Return the first timeline event matching the supplied name.

        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        """
        ...

    def events_at(self, time: float) -> List[Dict[str, Any]]:
        """Return events occurring at the requested timeline position.

        Parameters
        ----------
        time : float
            Timeline position for the operation.
        """
        ...

    def events_between(self, start: float, end: float) -> List[Dict[str, Any]]:
        """Return events whose times lie within the requested interval.

        Parameters
        ----------
        start : float
            Whether the stopwatch starts immediately or remains stopped initially.
        end : float
            Value supplied for ``end`` according to the Timeline contract.
        """
        ...

    def duration(self) -> float:
        """Return the timeline's total span."""
        ...

    def get_progress(self, time: float) -> float:
        """Return the last known integer percentage for a transfer ID.

        Parameters
        ----------
        time : float
            Timeline position for the operation.
        """
        ...

    def sort(self, reverse: bool=False) -> Timeline:
        """Perform the ``sort`` operation for Timeline.

        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        """
        ...

    def reverse(self) -> Timeline:
        """Reverse record/event order, optionally mutating according to the class contract."""
        ...

class Dataset(DDM):
    """Lightweight tabular dataset.

    ``Dataset`` provides rows/columns, filtering, mapping, grouping, aggregation, statistics and CSV export.

    When to use it
    --------------
    Use for modest in-memory analytics when a dataframe dependency would be excessive.
    """
    columns: List[str]
    rows: List[Dict[str, Any]]

    def __init__(self, columns: Sequence[str] | None=None, rows: Sequence[Mapping[str, Any]] | None=None) -> None:
        """Initialize a new Dataset instance using the supplied configuration and input data.

        Parameters
        ----------
        columns : Optional[Sequence[str]] (default: ``None``)
            Dataset column names.
        rows : Optional[Sequence[Mapping[str, Any]]] (default: ``None``)
            Dataset/matrix row data.
        """
        ...

    def add_row(self, row: Mapping[str, Any]) -> Dataset:
        """Append a row to the dataset after applying dataset shape rules.

        Parameters
        ----------
        row : Mapping[str, Any]
            One dataset record to append.
        """
        ...

    def add_column(self, name: str, default: Any=None) -> Dataset:
        """Add a column to the dataset and populate existing rows with a default value.

        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        """
        ...

    def remove_column(self, name: str) -> Dataset:
        """Remove a named dataset column from schema and rows.

        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        """
        ...

    def filter_rows(self, predicate: Callable[[Dict[str, Any]], bool]) -> Dataset:
        """Return a dataset containing only rows accepted by the predicate.

        Parameters
        ----------
        predicate : Callable[[Dict[str, Any]], bool]
            Callable returning truthy for records that should match/be selected.
        """
        ...

    def map_column(self, name: str, func: Callable[[Any], Any]) -> Dataset:
        """Transform one dataset column using a callable.

        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        func : Callable[[Any], Any]
            Callable applied by the operation.
        """
        ...

    def sort_by(self, column: str, reverse: bool=False) -> Dataset:
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.

        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        """
        ...

    def group_by(self, column: str) -> Dict[Any, Dataset]:  # type: ignore[override]  # Dataset groups rows by column, unlike DDM fields.
        """Group records or values by the requested field/callback and return the resulting buckets.

        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        """
        ...

    def aggregate(self, column: str, func: Callable[[Iterable[Any]], Any]) -> Any:  # type: ignore[override]  # Dataset aggregates a selected column.
        """Apply one or more aggregation callables to the selected data.

        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        func : Callable[[Iterable[Any]], Any]
            Callable applied by the operation.
        """
        ...

    def stats(self, column: str) -> Dict[str, float]:
        """Return numeric-column statistics with population variance and standard deviation.

        Keys: count, sum, mean, min, max, std, variance. Non-numeric and missing values are skipped. Empty numeric input returns count=0 and zero for every other statistic. The dataset is not mutated.
        """
        ...

    def to_csv(self, sep: str = ",") -> str:
        """Write columns and rows as CSV text using the one-character delimiter sep.

        The default is comma. Fields containing delimiters, quotes or newlines are quoted by the standard csv writer. The header follows self.columns order and records use CRLF terminators.
        """
        ...

    def transpose(self) -> List[List[Any]]:
        """Swap dataset/matrix row and column orientation."""
        ...

class Size(DDM):
    """2D dimension model.

    ``Size`` provides area, perimeter, aspect ratio, scaling and fit calculations.

    When to use it
    --------------
    Use for UI/media/layout dimensions and simple geometry.
    """
    width: float
    height: float

    def __init__(self, width: float=0.0, height: float=0.0) -> None:
        """Initialize a new Size instance using the supplied configuration and input data.

        Parameters
        ----------
        width : float (default: ``0.0``)
            Width in characters/pixels/units according to the API.
        height : float (default: ``0.0``)
            Height in pixels/units.
        """
        ...

    @property
    def area(self) -> float:
        """Return two-dimensional area."""
        ...

    @property
    def perimeter(self) -> float:
        """Return the perimeter of the 2D size."""
        ...

    @property
    def aspect_ratio(self) -> float:
        """Return width divided by height using the class's zero-height behavior."""
        ...

    def scale(self, factor: float) -> Size:
        """Return a scaled version of the represented numeric/geometry object.

        Parameters
        ----------
        factor : float
            Numeric scaling/multiplication factor.
        """
        ...

    def fit_inside(self, other: Size, *, upscale: bool=False) -> Size:
        """Return a size scaled to fit within another size while preserving aspect ratio.

        Parameters
        ----------
        other : 'Size'
            Another compatible object/value used by the operation.
        upscale : bool (default: ``False``)
            Whether fit calculations may enlarge a smaller source size.
        """
        ...

    def contains(self, other: Size) -> bool:
        """Return whether a value/substring lies within the represented range or indexed path data.

        Parameters
        ----------
        other : 'Size'
            Another compatible object/value used by the operation.
        """
        ...

    def to_tuple(self) -> tuple[float, float]:
        """Return (width, height), preserving the model's floating-point units."""
        ...

    def __str__(self) -> str:
        """Return dimensions as 'widthxheight', omitting redundant decimal zeros."""
        ...

    def scale_width(self, factor: float) -> 'Size':
        """Return a new size with width scaled and height preserved."""
        ...

    def scale_height(self, factor: float) -> 'Size':
        """Return a new size with height scaled and width preserved."""
        ...

    def fit_within(self, max_size: 'Size') -> 'Size':
        """Fit inside max_size without enlarging, preserving aspect ratio."""
        ...

    def clamp(self, min_size: 'Size', max_size: 'Size') -> 'Size':
        """Clamp dimensions independently; raise ValueError for inverted bounds."""
        ...

    def transpose(self) -> 'Size':
        """Return a new size with width and height exchanged."""
        ...

    def __mul__(self, factor: float) -> Size:
        ...

    def __rmul__(self, factor: float) -> Size:
        ...
    __rmul__ = __mul__

class Point(DDM):
    """2D coordinate model.

    ``Point`` provides distance, midpoint, translation, scaling and vector conversion.

    When to use it
    --------------
    Use for geometry, canvas/UI and game coordinates.
    """
    x: float
    y: float

    def __init__(self, x: float=0.0, y: float=0.0) -> None:
        """Initialize a new Point instance using the supplied configuration and input data.

        Parameters
        ----------
        x : float (default: ``0.0``)
            X coordinate.
        y : float (default: ``0.0``)
            Y coordinate.
        """
        ...

    def distance_to(self, other: Point) -> float:
        """Return Euclidean distance to another compatible point/vector.

        Parameters
        ----------
        other : 'Point'
            Another compatible object/value used by the operation.
        """
        ...

    def midpoint(self, other: Point) -> Point:
        """Return the midpoint of this object relative to its range/geometry semantics.

        Parameters
        ----------
        other : 'Point'
            Another compatible object/value used by the operation.
        """
        ...

    def translate(self, dx: float=0.0, dy: float=0.0) -> Point:
        """Perform the ``translate`` operation for Point.

        Parameters
        ----------
        dx : float (default: ``0.0``)
            Horizontal translation.
        dy : float (default: ``0.0``)
            Vertical translation.
        """
        ...

    def scale(self, factor: float, origin: Point | None=None) -> Point:
        """Return a scaled version of the represented numeric/geometry object.

        Parameters
        ----------
        factor : float
            Numeric scaling/multiplication factor.
        origin : Optional['Point'] (default: ``None``)
            Origin point used for scaling.
        """
        ...

    def to_vector(self) -> Vector:
        """Perform the ``to_vector`` operation for Point."""
        ...

    def to_tuple(self) -> tuple[float, float]:
        """Return (x, y) without rounding coordinates."""
        ...

    def __str__(self) -> str:
        """Return coordinates as 'x,y', omitting redundant decimal zeros."""
        ...

    def is_within_distance(self, other: 'Point', distance: float) -> bool:
        """Return whether Euclidean distance to other is at most distance."""
        ...

    def rotate_around(self, center: 'Point', angle_deg: float) -> 'Point':
        """Return a counterclockwise rotation around center, in degrees."""
        ...

    def normalize(self) -> tuple[float, float]:
        """Return unit coordinates; the zero point normalizes to (0.0, 0.0)."""
        ...

    def clamp(self, min_point: 'Point', max_point: 'Point') -> 'Point':
        """Clamp coordinates independently; reject inverted minimum/maximum bounds."""
        ...

    def reflect_x(self, origin_x: float=0) -> 'Point':
        """Reflect the x coordinate about the vertical line x=origin_x."""
        ...

    def reflect_y(self, origin_y: float=0) -> 'Point':
        """Reflect the y coordinate about the horizontal line y=origin_y."""
        ...

    def __add__(self, other: Point) -> Point:
        ...

    def __sub__(self, other: Point) -> Point:
        ...

    def __mul__(self, factor: float) -> Point:
        ...

    def __rmul__(self, factor: float) -> Point:
        ...
    __rmul__ = __mul__

class Color(DDM):
    """RGBA color model.

    ``Color`` provides hex conversion, normalized channels, blending, luminance and contrast ratio.

    When to use it
    --------------
    Use for theme, UI and accessibility calculations independent of terminal ANSI colors.
    """
    r: int
    g: int
    b: int
    a: int

    def __init__(self, r: int=0, g: int=0, b: int=0, a: int=255) -> None:
        """Initialize a new Color instance using the supplied configuration and input data.

        Parameters
        ----------
        r : int (default: ``0``)
            Red channel 0..255.
        g : int (default: ``0``)
            Green channel 0..255.
        b : int (default: ``0``)
            Second string/value.
        a : int (default: ``255``)
            First string/value.
        """
        ...

    @classmethod
    def from_hex(cls, value: str) -> Color:
        """Construct a color from hexadecimal RGB/RGBA notation.

        Parameters
        ----------
        value : str
            Target, new or comparison value.
        """
        ...

    def to_hex(self, include_alpha: bool=False) -> str:
        """Return the color as a hexadecimal string.

        Parameters
        ----------
        include_alpha : bool (default: ``False``)
            Whether hexadecimal output includes the alpha channel.
        """
        ...

    def normalized(self) -> tuple[float, float, float, float]:
        """Return RGBA channels normalized to floating-point 0..1 values."""
        ...

    def blend(self, other: Color, t: float=0.5) -> Color:
        """Interpolate between this color and another color.

        Parameters
        ----------
        other : 'Color'
            Another compatible object/value used by the operation.
        t : float (default: ``0.5``)
            Interpolation parameter, normally between 0 and 1.
        """
        ...

    def luminance(self) -> float:
        """Return relative luminance for accessibility/contrast calculations."""
        ...

    def contrast_ratio(self, other: Color) -> float:
        """Return the WCAG-style contrast ratio between this color and another color.

        Parameters
        ----------
        other : 'Color'
            Another compatible object/value used by the operation.
        """
        ...

    def to_hex_lower(self, include_alpha: bool=False) -> str:
        """Return lowercase #rrggbb or #rrggbbaa hex notation."""
        ...

    def to_rgb(self) -> tuple[int, int, int]:
        """Return integer red, green and blue channels in the range 0..255."""
        ...

    def to_rgba(self) -> tuple[int, int, int, int]:
        """Return integer RGBA channels, including opacity in the range 0..255."""
        ...

    def to_int_rgb(self) -> int:
        """Pack channels into an unsigned 24-bit 0xRRGGBB integer."""
        ...

    def to_int_rgba(self) -> int:
        """Pack channels into an unsigned 32-bit 0xRRGGBBAA integer."""
        ...

    def to_int_argb(self) -> int:
        """Pack channels into an unsigned 32-bit 0xAARRGGBB integer."""
        ...

    def to_css(self) -> str:
        """Return CSS rgba(r,g,b,a), with normalized alpha to three decimals."""
        ...

    def __str__(self) -> str:
        """Return #RRGGBB for opaque colors, otherwise #RRGGBBAA."""
        ...

    def is_transparent(self) -> bool:
        """Return whether alpha is zero (fully transparent)."""
        ...

    def is_opaque(self) -> bool:
        """Return whether alpha is 255 (fully opaque)."""
        ...

    def brightness(self) -> float:
        """Return perceived RGB brightness in 0..1; this is not WCAG luminance."""
        ...

    def lighten(self, amount: int=30) -> 'Color':
        """Add amount to RGB channels, clipping to 0..255; preserve alpha."""
        ...

    def darken(self, amount: int=30) -> 'Color':
        """Subtract amount from RGB channels, clipping to 0..255; preserve alpha."""
        ...

    def invert(self) -> 'Color':
        """Invert RGB channels and preserve alpha in a new color."""
        ...

    def grayscale(self) -> 'Color':
        """Return a perceived-brightness grayscale color with unchanged alpha."""
        ...

    def adjust_alpha(self, amount: int) -> 'Color':
        """Add amount to opacity, clipping to 0..255, and preserve RGB."""
        ...

    def to_hsl(self) -> tuple[float, float, float]:
        """Return hue in degrees, saturation and lightness in 0..1."""
        ...

    def to_hsv(self) -> tuple[float, float, float]:
        """Return hue in degrees, saturation and value in 0..1."""
        ...

    def saturate(self, amount: float=0.1) -> 'Color':
        """Increase HSL saturation, clipping to 0..1; preserve hue/lightness/alpha."""
        ...

    def desaturate(self, amount: float=0.1) -> 'Color':
        """Decrease HSL saturation, clipping to 0..1; preserve alpha."""
        ...
    to_tuple = to_rgba
    to_pillow = to_rgba
    to_tuple_normalized = normalized

class Matrix(DDM):
    """Dense numeric matrix model.

    ``Matrix`` provides shape, identity, transpose, scalar/arithmetic multiplication and vector multiplication.

    When to use it
    --------------
    Use for lightweight matrix workflows without a numerical dependency.
    """
    rows: List[List[float]]

    @property
    def shape(self) -> tuple[int, int]:
        """Return matrix dimensions as a rows/columns pair."""
        ...

    def __init__(self, rows: Sequence[Sequence[float]]) -> None:
        """Initialize a new Matrix instance using the supplied configuration and input data.

        Parameters
        ----------
        rows : Sequence[Sequence[float]]
            Dataset/matrix row data.
        """
        ...

    @classmethod
    def identity(cls, size: int) -> Matrix:
        """Construct an identity matrix of the requested square size.

        Parameters
        ----------
        size : int
            Requested size/dimension/chunk width.
        """
        ...

    def transpose(self) -> Matrix:
        """Swap dataset/matrix row and column orientation."""
        ...

    def add(self, other: Matrix) -> Matrix:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.

        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        """
        ...

    def subtract(self, other: Matrix) -> Matrix:
        """Subtract another value or queue a subtraction operation.

        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        """
        ...

    def scale(self, scalar: float) -> Matrix:
        """Return a scaled version of the represented numeric/geometry object.

        Parameters
        ----------
        scalar : float
            Numeric scalar multiplier.
        """
        ...

    def matmul(self, other: Matrix) -> Matrix:
        """Return matrix multiplication with another compatible matrix.

        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        """
        ...

    def vector_mul(self, vector: Vector) -> Vector:
        """Multiply the matrix by a compatible vector.

        Parameters
        ----------
        vector : Vector
            Value supplied for ``vector`` according to the Matrix contract.
        """
        ...

    def __add__(self, other: Matrix) -> Matrix:
        ...

    def __sub__(self, other: Matrix) -> Matrix:
        ...

    def __matmul__(self, other: Matrix) -> Matrix:
        ...

    def __mul__(self, scalar: float) -> Matrix:
        ...
    __rmul__ = __mul__

class TreeDDM(DDM):
    """Hierarchical DDM tree node.

    ``TreeDDM`` provides children, traversal orders, predicate search, depth and size.

    When to use it
    --------------
    Use for menus, categories, ownership trees and other recursive domain structures.
    """
    value: Any
    children: List[TreeDDM]

    def __init__(self, value: Any=None, children: Iterable[TreeDDM] | None=None, **data: Any) -> None:
        """Initialize a new TreeDDM instance using the supplied configuration and input data.

        Parameters
        ----------
        value : Any (default: ``None``)
            Target, new or comparison value.
        children : Optional[Iterable['TreeDDM']] (default: ``None``)
            Optional initial child nodes/values.
        **data : Any
            Input mapping or record data used to initialize the object.
        """
        ...

    def add_child(self, child: Any, **data: Any) -> TreeDDM:
        """Append a child node/value and return the resulting child node.

        Parameters
        ----------
        child : Any
            Value supplied for ``child`` according to the TreeDDM contract.
        **data : Any
            Input mapping or record data used to initialize the object.
        """
        ...

    def walk(self, order: str='dfs') -> Iterator[TreeDDM]:
        """Traverse the tree in the requested supported order.

        Parameters
        ----------
        order : str (default: ``'dfs'``)
            Traversal order name supported by TreeDDM.
        """
        ...

    def find(self, predicate: Callable[[TreeDDM], bool]) -> TreeDDM | None:
        """Return tree/search records that satisfy a predicate or query.

        Parameters
        ----------
        predicate : Callable[['TreeDDM'], bool]
            Callable returning truthy for records that should match/be selected.
        """
        ...

    def depth(self) -> int:
        """Return the maximum depth of the tree rooted at this node."""
        ...

    def size(self) -> int:
        """Return the number of nodes/items or terminal dimensions, depending on the class."""
        ...
