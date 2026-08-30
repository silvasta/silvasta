import msgspec


class User(msgspec.Struct):
    name: str
    groups: set[str] = set()
    email: str | None = None


alice = User(name="alice", groups={"admin", "engineering"})

data = msgspec.json.encode(alice)
print(data)

user_obj = msgspec.json.decode(data, type=User)
print(user_obj)
