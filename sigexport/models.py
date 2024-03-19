"""Package typing."""

from dataclasses import dataclass
from typing import Any

Convo = dict[str, Any]
Convos = dict[str, list[Convo]]
Contact = dict[str, str]
Contacts = dict[str, Contact]


@dataclass
class Message:
    date: str
    sender: str
    body: str

    def repr(self: "Message") -> str:
        return self.date + self.sender + self.body

    def comp(self: "Message") -> str:
        return self.repr().replace("\n", "").replace(">", "")
