from sstcore.port.casting import LspViolation

flag = LspViolation.POS_ONLY_RENAMED
print(f"{flag}")
print(f"{flag:b}")
print(f"{flag:d}")
print(f"{flag:t}")
print(f"{flag:e}")
print(f"{flag:n}")
print(f"{flag:it}")

preset = LspViolation.HOOK_PLUGIN
print(f"{preset:t}")

combo = LspViolation.POS_ONLY_RENAMED | LspViolation.DROPPED_VAR_POS
print(f"{combo:t}")
print(f"{combo:tn}")
print(f"{combo:n}")
