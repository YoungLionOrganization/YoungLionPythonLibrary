"""Static regression examples; checked by tools/check_typing.py, not executed."""
from typing import Any, Literal
from typing_extensions import assert_type

from YoungLion import (
    Color, CommandResult, DDM, DictDDM, ListDDM, Matrix, Point, RetryPolicy,
    SchemaDDM, SearchAlgorithm, Size, SmartCache, Stopwatch, TaskInfo, Vector,
    flatten_to_single_dict,
)
from YoungLion.DataModel import batch_transform
from YoungLion.function import CircuitBreaker
from YoungLion import _native


class User(DDM):
    name: str


user = User({"name": "Leyla"})
assert_type(user.clone(), User)
assert_type(user.ensure("score", 0), User)
assert_type(user.if_exists("score"), User | None)
user.get("missing", 42)
user.get_path("missing.path", "fallback")
user.pop("missing", False)
assert_type(user.to_string(color=False, max_depth=4), str)
assert_type(user.to_csv_line(), str)
assert_type(flatten_to_single_dict(user), dict[str, Any])
assert_type(SchemaDDM({"x": 1}, {"x": int}).clone(), SchemaDDM)

rows = ListDDM([user, {"name": "Çağrı"}])
rows[1:2] = [{"name": "new"}]
assert_type(rows[:], list[DDM])
assert_type(rows.sort_by("name"), list[DDM])
assert_type(rows.sort_by("name", inplace=True), ListDDM)
assert_type(rows.deduplicate(inplace=True), ListDDM)
assert_type(rows.shuffle(), ListDDM)
assert_type(rows.shuffle(inplace=False), list[DDM])
assert_type(rows.reverse(), ListDDM)
assert_type(rows.reverse(inplace=False), list[DDM])
assert_type(rows.map(lambda row: str(row.get("name"))), list[str])
assert_type(rows.first(), DDM | None)
assert_type(rows.first(default=42), DDM | int)
assert_type(rows.first(None, "absent"), DDM | str)
assert_type(rows.first_path("name", default=False), DDM | bool)
assert_type(rows.for_each(lambda row: None), ListDDM)
assert_type(rows.search("name", "Leyla"), list[DDM])
assert_type(batch_transform([user], lambda model: str(model.get("name"))), list[str])

def dynamic_inplace(flag: bool) -> None:
    assert_type(rows.sort_by("name", inplace=flag), list[DDM] | ListDDM)

mapping: DictDDM[str] = DictDDM({"one": user})
for key, item in mapping.items():
    assert_type(key, str)
    assert_type(item, DDM)

assert_type(Size(2, 3).area, float)
assert_type(Size(2, 3).perimeter, float)
assert_type(Size(2, 3).aspect_ratio, float)
assert_type(2 * Size(2, 3), Size)
assert_type(2 * Point(1, 2), Point)
assert_type(Vector([1, 2]) + Vector([2, 3]), Vector)
assert_type(Vector([1, 2]) / 2, Vector)
assert_type(2 * Vector([1, 2]), Vector)
assert_type(Matrix([[1]]) @ Matrix([[2]]), Matrix)
assert_type(2 * Matrix([[1]]), Matrix)
assert_type(Color(1, 2, 3).to_pillow(), tuple[int, int, int, int])
assert_type(SearchAlgorithm.BM25.value, Literal["bm25"])
assert_type(CommandResult(("python",), 0).ok, bool)
TaskInfo("id", "pending", 0.0, 1.0, None, 0)
with Stopwatch() as timer:
    assert_type(timer, Stopwatch)

def stringify(value: int, *, prefix: str = "") -> str:
    return prefix + str(value)

assert_type(RetryPolicy().call(stringify, 2, prefix="n="), str)
assert_type(CircuitBreaker().call(stringify, 2), str)
cache = SmartCache({"name": ""})
assert_type(cache.fill({}, recursive=False), dict[str, Any])
assert_type(cache.report({})["complete"], bool)
assert_type(cache.report({})["missing_keys"], list[str])
assert_type(cache.get_stats()["completed"], int)
assert_type(user.validate_schema({"name": str})["valid"], bool)
assert_type(user.validate_schema({"name": str})["errors"], list[str])
assert_type(user.memory_info()["recursive_bytes"], int)
assert_type(_native.json_dumps(obj={"name": "Leyla"}, indent=-1), str)
