from typer import secho

verbose = False


def log(msg: str, fg: str | None = None) -> None:
    if verbose:
        secho(msg, fg=fg)
