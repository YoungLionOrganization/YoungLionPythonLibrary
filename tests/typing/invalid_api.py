"""These invalid calls must remain rejected by the shipped type contracts."""
from YoungLion import DDM, ListDDM, RetryPolicy, Size, Vector, _native


def stringify(value: int) -> str:
    return str(value)


Size(2, 3).area()  # expect: operator
Vector([1, 2]) + "invalid"  # expect: operator
RetryPolicy().call(stringify, "invalid")  # expect: arg-type
_native.json_loads(data="{}")  # expect: call-arg
rows = ListDDM([DDM({"x": 1})])
rows[0] = [DDM({"x": 2})]  # expect: call-overload
