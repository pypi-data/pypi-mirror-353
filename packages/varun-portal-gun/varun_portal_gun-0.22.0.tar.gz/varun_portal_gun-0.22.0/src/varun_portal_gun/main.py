import typer
from pathlib import Path
from typing import Optional

from typing_extensions import Annotated
import os
import joblib
import pandas as pd

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
def run_model():
    print("Loaded Model")
    loaded_model = joblib.load("/Users/vyelluru/Desktop/bdc_power_det_v3.sav")
    X_test = [[1.00000, 17.7500, 4.413225, 1858.00], [1.00000, 17.7500, 4.413225, 1858.00]]
    result = loaded_model.predict(pd.DataFrame(X_test))
    print(result)
    print("Success")