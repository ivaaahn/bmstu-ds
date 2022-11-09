import click

from signature import Signature


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--sign",
    is_flag=True,
    show_default=True,
    default=False,
    help="Sign data.",
)
@click.option(
    "--verify",
    is_flag=True,
    show_default=True,
    default=False,
    help="Sign data.",
)
def run(filename: str, sign: bool = False, verify: bool = False):
    with open(filename, "rb") as f:
        data = f.read()

    if sign:
        Signature.make(data)
    elif verify:
        print()
        if Signature.verify(data):
            click.secho("Verified", fg="green", bold=True)
        else:
            click.secho("Not verified", fg="red", bold=True)


if __name__ == "__main__":
    run()
