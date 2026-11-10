from __future__ import annotations

import io
import json
from xml.etree import ElementTree

import pytest

from YoungLion import (
    Color, DDM, Dataset, FileTransferManager, FrozenDDM, ListDDM, ParseError, Point,
    Range, Size, SmartCache, TextProcessor, ensure_int_list, flatten_to_single_dict,
    split_any,
)


def test_display_preserves_models_unicode_and_container_types():
    class Profile(DDM):
        pass
    model = DDM({"profile": Profile({"name": "Çağrı"}), "rows": [{"id": 1}],
                 "tuple": (True, None), "empty": {}, "set": set(), "_hidden": "secret"})
    text = model.to_string(color=False)
    assert "Profile({" in text and "Çağrı" in text
    assert "'rows': [" in text and "'tuple': (" in text
    assert "True" in text and "None" in text
    assert "'empty': {}" in text and "set()" in text
    assert "secret" not in text
    assert "secret" in model.to_string(color=False, include_private=True)
    assert model.to_dict()["profile"] == {"name": "Çağrı"}


def test_display_cycles_and_shared_children_are_distinguished():
    shared = {"value": 4}
    sequence = []
    sequence.append(sequence)
    model = DDM({"left": shared, "right": shared, "list": sequence})
    model.self = model
    text = model.to_string(color=False)
    assert text.count("'value': 4") == 2
    assert "<recursion: list>" in text and "<recursion: DDM>" in text
    assert "<recursion: DDM>" in repr(model)


def test_display_is_bounded_and_does_not_serialize_or_evaluate_lazy_fields():
    class NoSerialization(DDM):
        def to_dict(self):
            raise AssertionError("display must not serialize")
    from YoungLion import LazyDDM
    calls = []
    model = NoSerialization({"large": list(range(10000)), "text": "x" * 10000,
                             "lazy": LazyDDM({}, lazy={"computed": lambda _: calls.append(1)})})
    text = model.to_string(color=False, max_items=3)
    assert len(text) < 1500 and "<more items>" in text
    assert not calls
    assert "'large': [...]" in model.to_string(color=False, max_depth=1)
    assert model.to_string(max_depth=0, color=False) == "NoSerialization({...})"
    assert model.to_string(max_items=0, color=False).count("<more items>") == 1
    assert len(DDM({"key" * 10000: "value"}).to_string(color=False)) < 500


@pytest.mark.parametrize("argument,value,error", [
    ("max_items", -1, ValueError), ("max_depth", -1, ValueError),
    ("max_depth", 101, ValueError), ("indent", -1, ValueError),
    ("indent", 1.5, TypeError), ("max_items", True, TypeError),
])
def test_display_rejects_invalid_limits(argument, value, error):
    with pytest.raises(error):
        DDM({}).to_string(**{argument: value})


def test_display_color_detection_and_sorting(monkeypatch):
    from YoungLion import Colors
    class Stream(io.StringIO):
        def isatty(self):
            return True
    monkeypatch.setattr("sys.stdout", Stream())
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm-256color")
    model = DDM({"z": 1, "a": "two\nlines"})
    plain = model.to_string(color=False, sort_keys=True)
    assert plain.index("'a'") < plain.index("'z'")
    assert "two\\nlines" in plain
    assert Colors.strip(model.to_string(color=True, sort_keys=True)) == plain
    assert "\x1b[" in str(model)
    monkeypatch.setenv("NO_COLOR", "")
    assert "\x1b[" not in str(model)
    monkeypatch.delenv("NO_COLOR")
    monkeypatch.setenv("TERM", "dumb")
    assert "\x1b[" not in str(model)
    monkeypatch.setattr("sys.stdout", io.StringIO())
    assert "\x1b[" not in str(model)


def test_json_stays_machine_readable_and_display_keys_can_shadow_methods():
    model = DDM({"name": "Leyla", "roles": ["admin"]})
    assert json.loads(model.to_json()) == model.to_dict()
    assert DDM.from_json(model.to_json()).to_dict() == model.to_dict()
    assert "'to_string': 'field'" in str(DDM({"to_string": "field"}))


@pytest.mark.parametrize("container", ["model", "dict", "list"])
@pytest.mark.parametrize("operation", ["to_dict", "to_json", "clone"])
def test_cyclic_native_conversion_raises_instead_of_crashing(container, operation):
    value = {} if container != "list" else []
    model = DDM({"child": value})
    if container == "model":
        model.self = model
    elif container == "dict":
        value["self"] = value
    else:
        value.append(value)
    with pytest.raises(RecursionError):
        getattr(model, operation)()
    # Failed recursion must not leak CPython's recursion budget.
    assert DDM({"valid": {"n": 1}}).to_dict() == {"valid": {"n": 1}}


def test_chaining_checks_fields_and_preserves_defaults_and_frozen_semantics():
    model = DDM({"none": None, "n": 1})
    assert model.if_exists("none") is model
    assert model.if_exists("to_dict") is None
    assert model.ensure("none", 4) is model and model.none is None
    assert model.ensure("new", []) is model and model.new == []
    assert model.only("n", "absent").to_dict() == {"n": 1}
    assert model.without("none", "new").to_dict() == {"n": 1}
    frozen = FrozenDDM({"n": 1})
    assert frozen.ensure("n") is frozen
    with pytest.raises(TypeError):
        frozen.ensure("extra", 2)


@pytest.mark.parametrize("sep", [",", ";", "\t"])
def test_csv_single_record_roundtrip(sep):
    data = {"a": f"one{sep}two", "b": 'quoted "value"', "c": "two\nlines", "d": ""}
    model = DDM(data)
    line = model.to_csv_line(sep)
    assert not line.endswith("\r\n")
    assert DDM.from_csv_line(line, model.keys(), sep).to_dict() == data
    assert DDM.from_csv_line(DDM({}).to_csv_line(sep), [], sep).to_dict() == {}


@pytest.mark.parametrize("line,headers", [("a,b", ["one"]), ("a\nb", ["one"]), ("a,b", ["same", "same"])])
def test_csv_rejects_silent_data_loss(line, headers):
    with pytest.raises(ValueError):
        DDM.from_csv_line(line, headers)


def test_xml_text_and_names():
    model = DDM({"name": "<Çağrı & Leyla>"})
    xml = model.to_xml_like("person", indent=1)
    assert ElementTree.fromstring(xml).findtext("name") == "<Çağrı & Leyla>"
    assert xml.startswith("  <person>")
    for model, tag in [(DDM({}), "bad>"), (DDM({"bad name": 1}), "item")]:
        with pytest.raises(ValueError):
            model.to_xml_like(tag)


def test_list_slice_assignment_coerces_records_and_invalidates_indexes():
    rows = ListDDM([{"id": 1}, {"id": 2}, {"id": 3}])
    engine = rows.indexed("id")
    rows[1:2] = [{"id": 4}, DDM({"id": 5})]
    assert all(isinstance(row, DDM) for row in rows)
    assert rows.path_values("id") == [1, 4, 5, 3]
    assert not engine.find("id", 2)
    assert engine.find("id", 4)[0] is rows[1]
    rows[::2] = [{"id": 6}, {"id": 7}]
    assert rows.path_values("id") == [6, 4, 7, 3]
    before = list(rows)
    with pytest.raises(ValueError):
        rows[::2] = [{"id": 8}]
    assert list(rows) == before


def test_cache_compatibility_helpers_and_shallow_completion():
    cache = SmartCache({"profile": {"name": "", "score": 0}, "items": []})
    copy = cache.get_template()
    copy["items"].append(1)
    assert cache.template["items"] == []
    assert cache.complete({"profile": {"name": "A"}})["profile"]["score"] == 0
    assert cache.fill({"profile": {"name": "A"}}, recursive=False)["profile"] == {"name": "A"}
    assert cache.fill_batch([{}], recursive=False)[0] == cache.template
    assert cache.report({}) == cache.completion_report({})
    clone = cache.clone_with_template({"values": []})
    assert clone.get_stats()["completed"] == 0
    clone.complete({})["values"].append(3)
    assert clone.template["values"] == []
    assert flatten_to_single_dict(DDM({"a": {"n": 1}}), DDM({"a": 2})) == {"ddm0_a.n": 1, "ddm1_a": 2}


def test_geometry_helpers_preserve_float_coordinates():
    size = Size(2.5, 5)
    assert size.to_tuple() == (2.5, 5)
    assert str(size) == "2.5x5"
    assert size.scale_width(2).to_tuple() == (5, 5)
    assert size.scale_height(2).to_tuple() == (2.5, 10)
    assert size.transpose().to_tuple() == (5, 2.5)
    assert size.fit_within(Size(1, 1)).to_tuple() == (0.5, 1)
    assert (2 * size).to_tuple() == (5, 10)
    point = Point(3, 4)
    assert point.normalize() == (0.6, 0.8)
    assert Point().normalize() == (0, 0)
    assert point.rotate_around(Point(), 90).to_tuple() == pytest.approx((-4, 3))
    assert point.reflect_x(1).to_tuple() == (-1, 4)
    assert point.reflect_y(1).to_tuple() == (3, -2)
    assert (point + Point(1, 2)).to_tuple() == (4, 6)
    assert (point - Point(1, 2)).to_tuple() == (2, 2)
    assert (2 * point).to_tuple() == (6, 8)
    assert point.is_within_distance(Point(), 5)
    assert point.clamp(Point(0, 0), Point(2, 2)).to_tuple() == (2, 2)
    assert size.clamp(Size(3, 3), Size(4, 4)).to_tuple() == (3, 4)
    with pytest.raises(ValueError):
        point.clamp(Point(2, 0), Point(1, 1))
    with pytest.raises(ValueError):
        size.clamp(Size(2, 2), Size(1, 1))


def test_color_helpers_pack_channels_and_preserve_alpha():
    color = Color(10, 20, 30, 40)
    assert color.to_rgb() == (10, 20, 30)
    assert color.to_rgba() == color.to_tuple() == color.to_pillow() == (10, 20, 30, 40)
    assert color.to_int_rgb() == 0x0A141E
    assert color.to_int_rgba() == 0x0A141E28
    assert color.to_int_argb() == 0x280A141E
    assert color.to_hex_lower(True) == "#0a141e28"
    assert color.to_css() == "rgba(10,20,30,0.157)"
    assert color.to_tuple_normalized() == color.normalized()
    assert color.lighten(300).to_rgba() == (255, 255, 255, 40)
    assert color.darken(300).to_rgba() == (0, 0, 0, 40)
    assert color.invert().to_rgba() == (245, 235, 225, 40)
    assert color.adjust_alpha(300).is_opaque()
    assert color.adjust_alpha(-300).is_transparent()
    assert color.saturate().a == color.desaturate().a == color.grayscale().a == 40
    assert Color(255, 0, 0).to_hsl() == (0, 1, 0.5)
    assert Color(255, 0, 0).to_hsv() == (0, 1, 1)


def test_text_and_parsing_compatibility_helpers():
    processor = TextProcessor("stored")
    assert processor.find_keywords("Ababa", ["aba", "B"]) == {"aba": 1, "B": 2}
    assert processor.replace_text("abc", "a", "z") == "zbc"
    assert processor.remove_stopwords("THE cat and dog", ["the", "AND"]) == "cat dog"
    assert processor.unique_words("Dog cat dog") == ["cat", "dog"]
    assert processor.text_summary("One. Two. Three.", 2) == "One. Two."
    assert processor.find_longest_word("small longest tiny") == "longest"
    assert processor.find_longest_word("") == ""
    assert processor.calculate_readability("Some words.") == processor.readability_score("Some words.")
    assert FileTransferManager().check_transfer_status("missing") is None
    assert split_any("800 x 600") == ["800", "600"]
    assert ensure_int_list(iter([" 3 ", 4]), 2, "point") == [3, 4]
    with pytest.raises(ParseError):
        split_any("single")
    with pytest.raises(ParseError):
        ensure_int_list(["bad"], 1, "point")
    with pytest.raises(ParseError):
        ensure_int_list([1], 2, "point")


def test_dataset_restores_documented_variance_and_csv_delimiter():
    import csv
    data = Dataset(["n", "text"], [{"n": 1, "text": "a;b"}, {"n": 3, "text": "c"}])
    assert data.stats("n")["variance"] == 1
    assert data.stats("n")["std"] == 1
    assert data.stats("text")["variance"] == 0
    assert list(csv.DictReader(io.StringIO(data.to_csv(sep=";")), delimiter=";")) == [
        {"n": "1", "text": "a;b"}, {"n": "3", "text": "c"}]


def test_range_descending_and_nonadvancing_step():
    assert list(Range(1, 3, -1).iterate()) == [3, 2, 1]
    assert list(Range(1, 3, 1).iterate()) == [1, 2, 3]
    assert list(Range(1, 1, -1).iterate()) == [1]
    with pytest.raises(ValueError):
        list(Range(1e16, 1e16 + 4, 1).iterate())
    for values in [(0, float("inf"), 1), (0, 1, float("nan")), (0, 1, float("inf"))]:
        with pytest.raises(ValueError):
            Range(*values)
