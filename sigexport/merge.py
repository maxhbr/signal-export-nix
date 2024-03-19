import shutil
from pathlib import Path

from typer import colors

from sigexport.logging import log
from sigexport.utils import lines_to_msgs


def merge_attachments(media_new: Path, media_old: Path) -> None:
    """Merge new and old attachments directories."""
    for f in media_old.iterdir():
        if f.is_file():
            try:
                shutil.copy2(f, media_new)
            except shutil.SameFileError:
                log(
                    f"Skipped file {f} as duplicate found in new export directory!",
                    fg=colors.RED,
                )


def merge_chat(path_new: Path, path_old: Path) -> None:
    """Merge new and old chat markdowns."""
    with path_old.open(encoding="utf-8") as f:
        old_raw = f.readlines()
    with path_new.open(encoding="utf-8") as f:
        new_raw = f.readlines()

    try:
        a = old_raw[0][:30]
        b = old_raw[-1][:30]
        c = new_raw[0][:30]
        d = new_raw[-1][:30]
        log(f"\t\tFirst line old:\t{a}")
        log(f"\t\tLast line old:\t{b}")
        log(f"\t\tFirst line new:\t{c}")
        log(f"\t\tLast line new:\t{d}")
    except IndexError:
        log("\t\tNo new messages for this conversation")
        return

    old = lines_to_msgs(old_raw)
    new = lines_to_msgs(new_raw)

    # get rid of duplicates
    msg_dict = {m.comp(): m.repr() for m in old + new}
    merged = list(msg_dict.values())

    with path_new.open("w", encoding="utf-8") as f:
        f.writelines(merged)


def merge_with_old(dest: Path, old: Path) -> None:
    """Main function for merging new and old."""
    for dir_old in old.iterdir():
        if dir_old.is_dir():
            name = dir_old.stem
            log(f"\tMerging {name}")
            dir_new = dest / name
            if dir_new.is_dir():
                merge_attachments(dir_new / "media", dir_old / "media")
                path_new = dir_new / "index.md"
                path_old = dir_old / "index.md"
                try:
                    merge_chat(path_new, path_old)
                except FileNotFoundError:
                    log(f"\tNo old for {name}")
            else:
                shutil.copytree(dir_old, dir_new)
