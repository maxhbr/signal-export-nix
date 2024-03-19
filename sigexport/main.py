"""Main script for sigexport."""

import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from typer import Argument, Exit, Option, colors, run, secho

from sigexport import __version__, logging, templates, utils
from sigexport.logging import log
from sigexport.merge import merge_with_old
from sigexport.models import Contacts, Convos

DATA_DELIM = "-----DATA-----"


def copy_attachments(
    src: Path, dest: Path, convos: Convos, contacts: Contacts
) -> Iterable[tuple[Path, Path]]:
    """Copy attachments and reorganise in destination directory."""
    src_att = Path(src) / "attachments.noindex"
    dest = Path(dest)

    for key, messages in convos.items():
        name = contacts[key]["name"]
        log(f"\tCopying attachments for: {name}")
        # some contact names are None
        if not name:
            name = "None"
        contact_path = dest / name / "media"
        contact_path.mkdir(exist_ok=True, parents=True)
        for msg in messages:
            if "attachments" in msg and msg["attachments"]:
                attachments = msg["attachments"]
                date = (
                    datetime.fromtimestamp(msg["timestamp"] / 1000.0)
                    .isoformat(timespec="milliseconds")
                    .replace(":", "-")
                )
                for i, att in enumerate(attachments):
                    try:
                        # Account for no fileName key
                        file_name = (
                            str(att["fileName"]) if "fileName" in att else "None"
                        )
                        # Sometimes the key is there but it is None, needs extension
                        if "." not in file_name:
                            content_type = att["contentType"].split("/")
                            try:
                                ext = content_type[1]
                            except IndexError:
                                ext = content_type[0]
                            file_name += "." + ext
                        att["fileName"] = (
                            f"{date}_{i:02}_{file_name}".replace(" ", "_")
                            .replace("/", "-")
                            .replace(",", "")
                            .replace(":", "-")
                            .replace("|", "-")
                        )
                        # account for erroneous backslash in path
                        att_path = str(att["path"]).replace("\\", "/")
                        yield src_att / att_path, contact_path / att["fileName"]
                    except KeyError:
                        p = att["path"] if "path" in att else ""
                        log(f"\t\tBroken attachment:\t{name}\t{p}")
                    except FileNotFoundError:
                        p = att["path"] if "path" in att else ""
                        log(f"\t\tAttachment not found:\t{name}\t{p}")
            else:
                msg["attachments"] = []


def create_markdown(
    dest: Path,
    convos: Convos,
    contacts: Contacts,
    add_quote: bool = False,
    add_newline: bool = False,
) -> Iterable[tuple[Path, str]]:
    """Output each conversation into a simple text file."""
    dest = Path(dest)
    for key, messages in convos.items():
        name = contacts[key]["name"]
        log(f"\tDoing markdown for: {name}")
        is_group = contacts[key]["is_group"]
        # some contact names are None
        if not name:
            name = "None"
        md_path = dest / name / "index.md"
        with md_path.open("w", encoding="utf-8") as _:
            pass  # overwrite file if it exists

        for msg in messages:
            try:
                date = utils.timestamp_format(msg["sent_at"])
            except (KeyError, TypeError):
                try:
                    date = utils.timestamp_format(msg["sent_at"])
                except (KeyError, TypeError):
                    date = "1970-01-01 00:00"
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

            for att in msg["attachments"]:
                file_name = att["fileName"]
                path = Path("media") / file_name
                path = Path(str(path).replace(" ", "%20"))
                if path.suffix and path.suffix.split(".")[1] in [
                    "png",
                    "jpg",
                    "jpeg",
                    "gif",
                    "tif",
                    "tiff",
                ]:
                    body += "!"
                body += f"[{file_name}](./{path})  "

            if "reactions" in msg and msg["reactions"]:
                reactions = []
                for r in msg["reactions"]:
                    try:
                        reactions.append(
                            f"{contacts[r['fromId']]['name']}: {r['emoji']}"
                        )
                    except KeyError:
                        log(
                            f"\t\tReaction fromId not found in contacts: "
                            f"[{date}] {sender}: {r}"
                        )
                body += "\n(- " + ", ".join(reactions) + " -)"

            if "sticker" in msg and msg["sticker"]:
                try:
                    body = msg["sticker"]["data"]["emoji"]
                except KeyError:
                    pass

            quote = ""
            if add_quote:
                try:
                    quote = msg["quote"]["text"].rstrip("\n")
                    quote = quote.replace("\n", "\n> ")
                    quote = f"\n\n> {quote}\n\n"
                except (KeyError, TypeError):
                    pass

            maybe_newline = "\n" if add_newline else ""
            yield md_path, f"[{date}] {sender}: {quote}{body}{maybe_newline}"


def create_html(dest: Path, msgs_per_page: int = 100) -> Iterable[tuple[Path, str]]:
    """Create HTML version from Markdown input."""
    root = Path(__file__).resolve().parents[0]
    css_source = root / "style.css"
    css_dest = dest / "style.css"
    if os.path.isfile(css_source):
        shutil.copy2(css_source, css_dest)
    else:
        secho(
            f"Stylesheet ({css_source}) not found."
            f"You might want to install one manually at {css_dest}."
        )

    md = markdown.Markdown()

    for sub in dest.iterdir():
        if sub.is_dir():
            name = sub.stem
            log(f"\tDoing html for {name}")
            path = sub / "index.md"
            # touch first
            open(path, "a", encoding="utf-8")
            with path.open(encoding="utf-8") as f:
                lines_raw = f.readlines()
            lines = utils.lines_to_msgs(lines_raw)
            last_page = int(len(lines) / msgs_per_page)
            ht_path = sub / "index.html"
            ht_content = ""

            page_num = 0
            for i, msg in enumerate(lines):
                if i % msgs_per_page == 0:
                    nav = "\n"
                    if i > 0:
                        nav += "</div>"
                    nav += f"<div class=page id=pg{page_num}>"
                    nav += "<nav>"
                    nav += "<div class=prev>"
                    if page_num != 0:
                        nav += f"<a href=#pg{page_num-1}>PREV</a>"
                    else:
                        nav += "PREV"
                    nav += "</div><div class=next>"
                    if page_num != last_page:
                        nav += f"<a href=#pg{page_num+1}>NEXT</a>"
                    else:
                        nav += "NEXT"
                    nav += "</div></nav>\n"
                    ht_content += nav
                    page_num += 1

                sender = msg.sender[1:-1]
                date, time = msg.date[1:-1].replace(",", "").split(" ")

                # reactions
                p = re.compile(r"\(- (.*) -\)")
                m = p.search(msg.body)
                reactions = m.groups()[0].replace(",", "") if m else ""
                body = p.sub("", msg.body)

                # quote
                p = re.compile(r">\n> (.*)\n>", flags=re.DOTALL)
                m = p.search(body)
                if m:
                    quote = m.groups()[0]
                    quote = f"<div class=quote>{quote}</div>"
                else:
                    quote = ""
                body = p.sub("", body)

                try:
                    body = md.convert(body)
                except RecursionError:
                    log(f"Maximum recursion on message {body}, not converted")

                # links
                p = re.compile(r"(https{0,1}://\S*)")
                template = r"<a href='\1' target='_blank'>\1</a> "
                body = re.sub(p, template, body)

                # images
                soup = BeautifulSoup(body, "html.parser")
                imgs = soup.find_all("img")
                for im in imgs:
                    if im.get("src"):
                        temp = templates.figure.format(src=im["src"], alt=im["alt"])
                        im.replace_with(BeautifulSoup(temp, "html.parser"))

                # voice notes
                voices = soup.select("a")
                p = re.compile(r'a href=".*\.(m4a|aac)"')
                for v in voices:
                    if p.search(str(v)):
                        temp = templates.audio.format(src=v["href"])
                        v.replace_with(BeautifulSoup(temp, "html.parser"))

                # videos
                videos = soup.select(r"a[href*=\.mp4]")
                for v in videos:
                    temp = templates.video.format(src=v["href"])
                    v.replace_with(BeautifulSoup(temp, "html.parser"))

                cl = "msg me" if sender == "Me" else "msg"
                ht_content += templates.message.format(
                    cl=cl,
                    date=date,
                    time=time,
                    sender=sender,
                    quote=quote,
                    body=soup,
                    reactions=reactions,
                )
            ht_text = templates.html.format(
                name=name,
                last_page=last_page,
                content=ht_content,
            )
            ht_text = BeautifulSoup(ht_text, "html.parser").prettify()
            ht_text = re.compile(r"^(\s*)", re.MULTILINE).sub(r"\1\1\1\1", ht_text)
            yield ht_path, ht_text


def main(
    dest: Path = Argument(None),
    source: Path | None = Option(None, help="Path to Signal source database"),
    old: Path | None = Option(None, help="Path to previous export to merge"),
    overwrite: bool = Option(
        False, "--overwrite", "-o", help="Overwrite existing output"
    ),
    quote: bool = Option(True, "--quote/--no-quote", "-q", help="Include quote text"),
    newlines: bool = Option(
        False,
        "--newlines/--no-newlines",
        "-n",
        help="Whether to insert blank lines between each message to improve Markdown rendering",  # NoQA: E501
    ),
    paginate: int = Option(
        100, "--paginate", "-p", help="Messages per page in HTML; set to 0 for infinite"
    ),
    chats: str | None = Option(
        None, help="Comma-separated chat names to include: contact names or group names"
    ),
    html: bool = Option(True, help="Whether to create HTML output"),
    list_chats: bool = Option(
        False, "--list-chats", "-l", help="List available chats and exit"
    ),
    include_empty: bool = Option(
        False, "--include-empty", help="Whether to include empty chats"
    ),
    manual: bool = Option(
        False, "--manual", "-m", help="Attempt to manually decrypt DB"
    ),
    verbose: bool = Option(False, "--verbose", "-v"),
    use_docker: bool = Option(
        True, help="Use Docker container for SQLCipher extraction"
    ),
    docker_image: str = Option(None, help="Docker image to use"),
    print_data: bool = Option(
        False, help="Print extracted DB data and exit (for use by Docker container)"
    ),
    _: bool | None = Option(None, "--version", callback=utils.version_callback),
) -> None:
    """Read the Signal directory and output attachments and chat to DEST directory."""
    logging.verbose = verbose

    if not any((dest, list_chats, print_data)):
        secho("Error: Missing argument 'DEST'", fg=colors.RED)
        raise Exit(code=1)

    if source:
        src = Path(source).expanduser().absolute()
    else:
        src = utils.source_location()
    source = src / "config.json"
    db_file = src / "sql" / "db.sqlite"

    # Read sqlcipher key from Signal config file
    if source.is_file():
        with open(source, encoding="utf-8") as conf:
            key = json.loads(conf.read())["key"]
    else:
        secho(f"Error: {source} not found in directory {src}")
        raise Exit(code=1)

    log(f"Fetching data from {db_file}\n")

    if not use_docker:
        try:
            from pysqlcipher3 import dbapi2 as _  # type: ignore[import] # noqa
        except Exception:
            secho("You set 'no-use-docker' but `pysqlcipher3` not installed properly")
            sys.exit(1)

    if use_docker:
        if not docker_image:
            docker_version = __version__.split(".dev")[0]
            docker_image = f"carderne/sigexport:v{docker_version}"
        secho(
            "Using Docker to extract data, this may take a while the first time!",
            fg=colors.BLUE,
        )
        cmd = [
            "docker",
            "run",
            "--rm",
            f"--volume={src}:/Signal",
            docker_image,
            "--no-use-docker",
            "--print-data",
        ]
        if manual:
            cmd.append("--manual")
        if chats:
            cmd.append(f"--chats={chats}")
        if include_empty:
            cmd.append("--include-empty")
        if verbose:
            cmd.append("--verbose")
        try:
            p = subprocess.run(
                cmd,  # NoQA: S603
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
            )
        except FileNotFoundError:
            secho("Error: using Docker method, but is Docker installed?", fg=colors.RED)
            secho("Try running this from the command line:\ndocker run hello-world")
            raise Exit(1)
        except subprocess.TimeoutExpired:
            secho("Docker process timed out.")
            raise Exit(1)
        try:
            docker_logs_1, data_raw, docker_logs_2 = p.stdout.split(DATA_DELIM)
        except ValueError:
            secho(f"Docker process failed, see logs below:\n{p.stderr}", fg=colors.RED)
            raise Exit(1)
        try:
            data = json.loads(data_raw)
            log(docker_logs_1)
            log(docker_logs_2)
        except json.JSONDecodeError:
            secho("Unable to decode data from Docker, see logs below:", fg=colors.RED)
            secho(p.stdout)
            secho(p.stderr, fg=colors.RED)
            raise Exit(1)
        try:
            convos, contacts = data["convos"], data["contacts"]
        except (KeyError, TypeError):
            secho(
                "Unable to extract convos and contacts from Docker, see data below",
                fg=colors.RED,
            )
            secho(data)
            raise Exit(1)
    else:
        from sigexport.data import fetch_data

        convos, contacts = fetch_data(
            db_file,
            key,
            manual=manual,
            chats=chats,
            include_empty=include_empty,
        )

    if print_data:
        data = {"convos": convos, "contacts": contacts}
        print(DATA_DELIM, json.dumps(data), DATA_DELIM)
        raise Exit()

    if list_chats:
        names = sorted(v["name"] for v in contacts.values() if v["name"] is not None)
        secho(" | ".join(names))
        raise Exit()

    dest = Path(dest).expanduser()
    if not dest.is_dir() or overwrite:
        dest.mkdir(parents=True, exist_ok=True)
    else:
        secho(
            f"Output folder '{dest}' already exists, didn't do anything!", fg=colors.RED
        )
        secho("Use --overwrite (or -o) to ignore existing directory.", fg=colors.RED)
        raise Exit()

    contacts = utils.fix_names(contacts)

    secho("Copying and renaming attachments")
    for att_src, att_dst in copy_attachments(src, dest, convos, contacts):
        try:
            shutil.copy2(att_src, att_dst)
        except FileNotFoundError:
            secho(f"No file to copy at {att_src}, skipping!", fg=colors.MAGENTA)
        except OSError as exc:
            secho(f"Error copying file {att_src}, skipping!\n{exc}", fg=colors.MAGENTA)

    secho("Creating markdown files")
    for md_path, md_text in create_markdown(dest, convos, contacts, quote, newlines):
        with md_path.open("a", encoding="utf-8") as md_file:
            print(md_text, file=md_file)
    if old:
        secho(f"Merging old at {old} into output directory")
        secho("No existing files will be deleted or overwritten!")
        merge_with_old(dest, Path(old))
    if html:
        secho("Creating HTML files")
        if paginate <= 0:
            paginate = int(1e20)
        for ht_path, ht_text in create_html(dest, msgs_per_page=paginate):
            with ht_path.open("w", encoding="utf-8") as ht_file:
                print(ht_text, file=ht_file)
    secho("Done!", fg=colors.GREEN)


def cli() -> None:
    """cli."""
    run(main)


if __name__ == "__main__":
    cli()
