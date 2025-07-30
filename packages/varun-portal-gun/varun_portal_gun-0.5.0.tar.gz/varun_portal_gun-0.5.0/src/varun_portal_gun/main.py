import typer
app = typer.Typer()


@app.command()
def predict(file_path: str):
    print("Here are your input files: " + file_path)

    # for filename in os.listdir(file_path):
    #     print("Type: " + type(filename) + ", " + "Name: " + filename)