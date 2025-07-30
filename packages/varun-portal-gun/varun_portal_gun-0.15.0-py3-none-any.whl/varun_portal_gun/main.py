import typer
from pathlib import Path
from typing import Optional

from typing_extensions import Annotated
import os
app = typer.Typer()


@app.callback()
def callback():
    pass

@app.command()
def predict(path: Annotated[str, typer.Option()] = None):
    print("Here are your input files: " + path)

    for filename in os.listdir(path):
        print(filename)


@app.command()
def tester(config: Annotated[Optional[Path], typer.Option()] = None):
    if config is None:
        print("No config file")
        raise typer.Abort()
    if config.is_file():
        text = config.read_text()
        print(f"Config file contents: {text}")
    elif config.is_dir():
        print("Config is a directory, will use all its config files")
    elif not config.exists():
        print("The config doesn't exist")