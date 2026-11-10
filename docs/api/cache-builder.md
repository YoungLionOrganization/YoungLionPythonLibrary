# SmartCache and DDMBuilder

`SmartCache` completes partial mappings from a reusable template, supports batch completion, missing/extra-key reporting and stats. `DDMBuilder` is a fluent constructor for programmatic DDM creation.

Module helpers cover DDM merge/compare, batch transform/filter/validation, structure analysis and one-shot template completion.

`complete(raw_data, recursive=True)` and `complete_batch(records, recursive=True)`
fill nested dictionaries by default. Set `recursive=False` to replace a template
submapping with the input submapping as a whole. Returned container data is copied
so editing a completed record does not mutate the template.

`get_template()` returns an independent deep copy. `clone_with_template(mapping)`
creates a fresh cache with zero counters and an independent template. `fill`,
`fill_batch` and `report` are aliases for `complete`, `complete_batch` and
`completion_report`. Current statistics are `completed`, `filled_keys` and
`template_keys`.

`flatten_to_single_dict(*models)` combines flattened paths with `ddm0_`, `ddm1_`,
etc. prefixes so different models' fields do not collide.
