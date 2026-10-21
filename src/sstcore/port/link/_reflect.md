# Reflector

Below the current status of the naming research, feels like more research than at university... anyway, the "idea 2" looks like it starts to settle.

Meanwhile I realised that the slot for `inject` is already covered by the class level pipeline in `forge`, there I want to use the products of `brick` and if somehow possible avoide naming confusion.

Somehow unclear for the overall naming concept, probably unrelated to the `-ector` pipeline in the port, is the role of `labor`. It was like the other candidate beside `reflect` that recently took over the role in `brick` and as well in the port, as well because it fits for both.

Still the `labor` idea is too good to just drop it, probably parts of the current package can be split into primitives for `reflect` and the rest moves as components into `forge`. There they are still somehow bricks but not like already usable products, some `ns` parts or `mixin` related stuff is needed for meta and cls compostions, but no where else useful.
Could that be the new home, like `forge.labor`? As the experimental area where the future stuff for the heavy assembler is developped?

- Overall I would be happy about a final review of the naming of the most urgent issue, `port.link`, how and how well the philosophy of idea 2 evaluates
- Finally a brief check about the naming of the Levels zero to two (hopefully possible with just the module names) could help for future development

## brainstorming

- `PortOperator` keeps the registry in the background
  - `Reflector` the facade
    - `Detector` inspecting objects
    - `Injector` modifying objects
    - `Collector` walks `MRO` and gathers information
- `Confector`
- `Projector` cast forward
- `Connector`
- `Compactor` pressing pieces together
- `Redactor` prepare multiple texts together
- `Collator` collect and combine
- `Weaver` silently interleaving cross-cutting concerns

## idea 1

- `PortOperator` organize, lead back
  - `Reflector` orchestrate, lead front
    - `Detector` analyze, extract
    - `Projector` modify, inject
    - `Collector` walk , gather
  - One of:
    - `Redactor` create publication with rendered results
    - `Collator`
    - `Confector`

## idea 2

- `Reflector` orchestrate, lead front
  - `Operator` lead execution on outer objects
    - `Detector` analyze, extract
    - `Projector` modify, inject
  - `Collector` walk, gather, find target for detect/project
  - `Redactor` render multiple docs to final result

The operator as intermediate base, detect/project have huge overlapping parts, covered by the operator, they are like the only ones that acually work with outer objects. Collect finds them without interaction, redact just merges the gathered information and returns the summary, from where the input comes or where it goes doesn't even matter.

## so far missing

Not for this pipeline but for the general concept, `invoke`.

The `brick.reflect.invoke` module with a collection of invoking functions is fine so far, from there on probably never a full `Invoker`class will be needed.

Another used name is `brick.labor` that so far consist out of separated function for `namespace` modification, `mro` walking but mainly is a dumpp for unsorted ideas about `cls` or `meta` operations.

## used otherwise

For the class level operation pipeline in `forge.compose` the `Builder` as the mixin assembler and the `Injector` as decorator for class injection are used.

Both are already used in `forge.view` where they build together with the `presets` the final `ViewComposer`. Decoupling `inject` from the port pipeline is definitely benefitial.

### sstcore.forge L2

```sh
.
├── __init__.py
├── compose
│   ├── ___typed_builder.py
│   ├── __init__.py
│   ├── _builder.py
│   ├── _injector.py
│   ├── _mixer.py
│   └── _vault.py
├── engine
│   ├── ___static_reflect.py
│   ├── __init__.py
│   ├── _functor.py
│   ├── _meta_base.py
│   ├── _meta_view.py
│   ├── _resolve.py
│   └── _static_func.py
├── func
│   ├── __init__.py
│   ├── _hybrid.py
│   ├── _safe.py
│   ├── _tor.py
│   └── _zero.py
├── typed
│   ├── ___extract.py
│   ├── ___render.py
│   ├── __init__.py
│   ├── _assemble.py
│   ├── _classify.py
│   ├── _forge_typer.py
│   └── _typed_well.py
└── view
    ├── __init__.py
    ├── _compose.py
    ├── _preset.py
    ├── _views
    │   ├── __init__.py
    │   ├── _cli.py
    │   ├── _log.py
    │   ├── _repr.py
    │   ├── _rich.py
    │   └── _str.py
    ├── catalog.py
    └── factory
        ├── __init__.py
        ├── _produce.py
        └── _table.py
```

### sstcore.brick L1

```sh
.
├── __init__.py
├── call
│   ├── __init__.py
│   ├── _argcast.py
│   ├── _cast.py
│   ├── _hybrid.py
│   ├── _inspect.py
│   ├── _some.py
│   └── stack
│       ├── __init__.py
│       ├── _base.py
│       ├── _core.py
│       └── _run.py
├── color
│   ├── ___intersect.py
│   ├── __init__.py
│   ├── _adapter
│   │   ├── __init__.py
│   │   ├── _ansi.py
│   │   ├── _base.py
│   │   ├── _hex.py
│   │   ├── _plot.py
│   │   └── _rich.py
│   ├── _colorize.py
│   ├── _mappings.py
│   └── box
│       ├── __init__.py
│       ├── _colors.py
│       ├── _colors.pyi
│       ├── _manager.py
│       └── _paint.py
├── field
│   ├── ___interact.py
│   ├── __init__.py
│   ├── _base.py
│   ├── _combos.py
│   ├── _decorate.py
│   ├── _extend.py
│   ├── _functor.py
│   ├── _policy.py
│   ├── _raise.py
│   ├── _strategy.py
│   └── _zero.py
├── format
│   ├── __init__.py
│   ├── _norm.py
│   ├── name
│   │   ├── __init__.py
│   │   ├── _colored.py
│   │   ├── _parse.py
│   │   ├── _str.py
│   │   └── _zero.py
│   ├── text
│   │   ├── __init__.py
│   │   ├── _align.py
│   │   ├── _ansi.py
│   │   └── _case.py
│   └── tstring
│       ├── __init__.py
│       ├── _base.py
│       ├── _definition.py
│       └── _rich.py
├── labor
│   ├── ___spawner.py
│   ├── ___tree_dto_printy.py
│   ├── ___tree_tests.py
│   ├── __init__.py
│   ├── _mro.py
│   └── _namespace.py
├── reflect
│   ├── ___filter.py
│   ├── __init__.py
│   ├── _attr.py
│   ├── _check.py
│   ├── _core.py
│   ├── _dict.py
│   ├── _invoke.py
│   └── _scan.py
├── time
│   └── __init__.py
└── vault
    ├── ___bisect.py
    ├── __init__.py
    ├── _access.py
    ├── _base.py
    ├── _contract.py
    ├── _mapping.py
    └── _sequence.py
```

### sstcore.port L0

```sh
.
├── __init__.py
├── _enum.py
├── _error.py
├── _raise.py
├── _types.py
├── annotate.py
├── attach.py
├── casting.py
├── color.py
├── config.py
├── empty.py
├── event
│   ├── __init__.py
│   ├── _core.py
│   ├── _fabric.py
│   ├── _param.py
│   ├── dto.py
│   ├── emit.py
│   └── name.py
├── files.py
├── filter.py
├── functorial.py
├── link
│   ├── __init__.py
│   ├── _define.py
│   ├── _model.py
│   ├── _operator.py
│   ├── _render.py
│   ├── _storage.py
│   └── _tap.py
├── normalize.py
├── printer.py
├── raising.py
├── register.py
├── represent.py
├── scanner.py
├── shape.py
├── solid.py
├── stacking.py
├── system.py
└── tree.py
```
