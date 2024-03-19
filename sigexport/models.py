import json
from collections import namedtuple
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from sigexport import utils

Convo = dict[str, Any]
Convos = dict[str, list[Convo]]
Contact = dict[str, str]
Contacts = dict[str, Contact]


Reaction = namedtuple("Reaction", ["name", "emoji"])


@dataclass
class Attachment:
    name: str
    path: str


@dataclass
class Message:
    name: str  # TODO: this should be specified in a containing obj
    date: datetime
    sender: str
    body: str
    quote: str
    sticker: str
    reactions: list[Reaction]
    attachments: list[Attachment]

    def repr(self: "Message") -> str:
        date_str = utils.timestamp_format(self.date)
        body = self.body

        if len(self.reactions) > 0:
            reactions = [f"{r.name}: {r.emoji}" for r in self.reactions]
            body = body + "\n(- " + ", ".join(reactions) + " -)"

        if len(self.sticker) > 0:
            body = body + "\n" + self.sticker

        for att in self.attachments:
            suffix = att.path.split(".")
            if len(suffix) > 1 and suffix[-1] in [
                "png",
                "jpg",
                "jpeg",
                "gif",
                "tif",
                "tiff",
            ]:
                body += "!"
            body += f"[{att.name}](./{att.path})  "

        return f"[{date_str}] {self.sender}: {self.quote}{body}\n"

    def dict(self: "Message") -> dict:
        msg_dict = asdict(self)
        msg_dict["date"] = msg_dict["date"].isoformat()
        del msg_dict["name"]
        return msg_dict

    def dict_str(self: "Message") -> str:
        return json.dumps(self.dict(), ensure_ascii=False)


@dataclass
class MergeMessage:
    date: str
    sender: str
    body: str

    def repr(self: "MergeMessage") -> str:
        return self.date + self.sender + self.body

    def comp(self: "MergeMessage") -> str:
        return self.repr().replace("\n", "").replace(">", "")
