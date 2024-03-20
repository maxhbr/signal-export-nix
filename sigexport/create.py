from datetime import datetime
from pathlib import Path

from sigexport import models, utils
from sigexport.logging import log


def create_message(
    msg: models.Convo,
    name: str,  # only used for debug logging
    is_group: bool,
    contacts: models.Contacts,
) -> models.Message:
    try:
        date = utils.dt_from_ts(msg["sent_at"])
    except (KeyError, TypeError):
        try:
            date = utils.dt_from_ts(msg["sent_at"])
        except (KeyError, TypeError):
            date = datetime(1970, 1, 1, 0, 0, 0)
            log("\t\tNo timestamp or sent_at; date set to 1970")
    log(f"\t\tDoing {name}, msg: {date}")

    try:
        if msg["type"] == "call-history":
            body = (
                "Incoming call"
                if msg["callHistoryDetails"]["wasIncoming"]
                else "Outgoing call"
            )
        else:
            body = msg["body"]
    except KeyError:
        log(f"\t\tNo body:\t\t{date}")
        body = ""
    if not body:
        body = ""
    body = body.replace("`", "")  # stop md code sections forming
    body += "  "  # so that markdown newlines

    sender = "No-Sender"
    if "type" in msg.keys() and msg["type"] == "outgoing":
        sender = "Me"
    else:
        try:
            if is_group:
                for c in contacts.values():
                    num = c["number"]
                    if num is not None and num == msg["source"]:
                        sender = c["name"]
            else:
                sender = contacts[msg["conversationId"]]["name"]
        except KeyError:
            log(f"\t\tNo sender:\t\t{date}")

    attachments: list[models.Attachment] = []
    for att in msg["attachments"]:
        file_name = att["fileName"]
        path = Path("media") / file_name
        path = Path(str(path).replace(" ", "%20"))
        attachments.append(models.Attachment(name=file_name, path=str(path)))

    reactions: list[models.Reaction] = []
    if "reactions" in msg and msg["reactions"]:
        for r in msg["reactions"]:
            try:
                reactions.append(
                    models.Reaction(contacts[r["fromId"]]["name"], r["emoji"])
                )
            except KeyError:
                log(
                    f"\t\tReaction fromId not found in contacts: "
                    f"[{date}] {sender}: {r}"
                )

    sticker = ""
    if "sticker" in msg and msg["sticker"]:
        try:
            sticker = msg["sticker"]["data"]["emoji"]
        except KeyError:
            pass

    quote = ""
    try:
        quote = msg["quote"]["text"].rstrip("\n")
        quote = quote.replace("\n", "\n> ")
        quote = f"\n\n> {quote}\n\n"
    except (KeyError, TypeError):
        pass

    return models.Message(
        date=date,
        sender=sender,
        body=body,
        quote=quote,
        sticker=sticker,
        reactions=reactions,
        attachments=attachments,
    )


def create_chats(
    convos: models.Convos,
    contacts: models.Contacts,
) -> models.Chats:
    """Convert convos and contacts into messages"""
    res: models.Chats = {}
    for key, raw_messages in convos.items():
        name = contacts[key]["name"]
        log(f"\tDoing markdown for: {name}")
        is_group = bool(contacts[key]["is_group"])
        # some contact names are None
        if not name:
            name = "None"

        messages: list[models.Message] = []
        for raw in raw_messages:
            messages.append(create_message(raw, name, is_group, contacts))

        res[name] = messages

    return res
