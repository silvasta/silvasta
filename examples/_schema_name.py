from sstcore import printer
from sstcore.utils.parse import SchemaName

pattern = "t_{id}_{topic}"
schema = SchemaName(pattern=pattern)
printer(str(schema))
printer(schema)

printer(f"{schema!r}")

name = "t_33_validation"
printer(schema(name))
keys = (11, "test")
printer(schema(keys))
