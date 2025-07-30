import typer
import os
app = typer.Typer()


@app.callback()
def callback():
    pass

@app.command()
def predict(path: str):
    print("Here are your input files: " + path)

    for filename in os.listdir(path):
        print("Type: " + type(filename) + ", " + "Name: " + filename)