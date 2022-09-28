import click

APP_IS_RUNNING_MSG = "The application is running!"


class Application:
    def run(self) -> None:
        click.secho(APP_IS_RUNNING_MSG, fg="blue", bg="green", bold=True)
