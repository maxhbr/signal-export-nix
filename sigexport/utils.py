import re
import sys
from datetime import datetime
from pathlib import Path

import emoji
from typer import Exit, secho

from sigexport import __version__
from sigexport.models import Contacts, Message


def timestamp_format(ts: float) -> str:
    """Format timestamp as 2000-01-01 00:00."""
    return datetime.fromtimestamp(ts / 1000.0).strftime("%Y-%m-%d %H:%M")


def lines_to_msgs(lines: list[str]) -> list[Message]:
    """Extract messages from lines of Markdown."""
    p = re.compile(r"^(\[\d{4}-\d{2}-\d{2},{0,1} \d{2}:\d{2}\])(.*?:)(.*\n)")
    msgs: list[Message] = []
    for li in lines:
        m = p.match(li)
        if m:
            msg = Message(*m.groups())
            msgs.append(msg)
        else:
            msgs[-1].body += li
    return msgs


def version_callback(value: bool) -> None:
    """Get sigexport version."""
    if value:
        print(f"v{__version__}")
        raise Exit()


def source_location() -> Path:
    """Get OS-dependent source location."""
    home = Path.home()
    paths = {
        "linux": home / ".config/Signal",
        "linux2": home / ".config/Signal",
        "darwin": home / "Library/Application Support/Signal",
        "win32": home / "AppData/Roaming/Signal",
    }
    try:
        source_path = paths[sys.platform]
    except KeyError:
        secho("Please manually enter Signal location using --source.")
        raise Exit(code=1)

    return source_path


def fix_names(contacts: Contacts) -> Contacts:
    """Convert contact names to filesystem-friendly."""
    fixed_contact_names = set()
    for key, item in contacts.items():
        contact_name = item["number"] if item["name"] is None else item["name"]
        if contacts[key]["name"] is not None:
            contacts[key]["name"] = "".join(
                x for x in emoji.demojize(contact_name) if x.isalnum()
            )
            if contacts[key]["name"] == "":
                contacts[key]["name"] = "unnamed"
            fixed_contact_name = contacts[key]["name"]
            if fixed_contact_name in fixed_contact_names:
                name_differentiating_number = 2
                while (
                    fixed_contact_name + str(name_differentiating_number)
                ) in fixed_contact_names:
                    name_differentiating_number += 1
                fixed_contact_name += str(name_differentiating_number)
                contacts[key]["name"] = fixed_contact_name
            fixed_contact_names.add(fixed_contact_name)

    return contacts
