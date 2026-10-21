# Operator Names

Currently I am building a pipeline of multiple operators.

So far the head was `PortOperator` with 3 children: `Reflect`, `Inject` and `Collect` but I want to reorganize this somehow.

New is another member that's job is simply merging docs together, because of reasons this is now as well a member of the operators.

All names above are used as pairs of verbs and nouns, reflect -> reflector and so on.

The reflector, now as pure detector of information, is already in another part of the library used as top-level name for all of the related tasks. Reflect as figuring out something, but as well as changing something and get a new inner awareness.

> The **philosophy** maps to the task in Python as follows, working on classes without they ever notice, the class gets decorated, some attributes are evaluated and some information is silently added while pretending to just return the class as it was, leading it to something like an inner recognition.

It is exclusively about inserting information and documentation, nothing that adds a real value to a raw, not inspected runtime pipeline and nothing the type checker knows that happens.

Right now it is only about naming, not about the implementation, the structure should look as follows:

- `PortOperator` still keeps the registry, but in the background
  - `Reflector` as the new facade
    - `Detector` inspecting objects (like reflect before)
    - `Injector` modifying objects (like before)
    - `Collector` walks MROs and prepares for the 2 above
  - `Xxxector` derives for sure from `PortOperator`, sibling of the 3 above maybe or maybe not derives from `Reflector`, task is merging multiple docs together, using the (independent) rendering engine, but as well works in cooperation with the upper 3, (collect,detect,`Xxxect` processes the data, inject) and for sure needs a proper name.

For sure it would be amazing if there exists a verb and noun that matches exactly the `-ector` / `-ect` pattern of the other 4, but before the name is too exotic or to less related or otherwise weird I would prefer some solid, obvious name for this part of the pipeline.

- Show and discuss different possible promising name combinations
- Explain how `reflect` fits into and on top of this pipeline

The pipeline itself works (or breaks...) with or without a well thought out naming concept. Still, this pattern could be reused in other parts of the library, showing consistency and a deeper connection on multiple (or at least one...) levels.

- Come up with a varied selection of naming pairs
