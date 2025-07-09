import os
from os.path import isdir
from Compsta import Compsta
from rich.console import Console
from rich.style import Style

class Comclass:
    """
    Class for analyse classes or folder representing classes.
    """
    def __init__(self):
        pass

    def parse_folder(self, dir_name: str):
        for file in os.listdir(dir_name):
            file_path: str = os.path.join(dir_name, file)
            if os.path.isdir(file_path):
                file_path = f"{file_path}/"
                compsta: Compsta = Compsta(file_path)

                compsta.export_csv(f"csvs/{file.capitalize()}")
                Console().print(f"CREATE {file.capitalize()}.csv",
                            style="bold green")

if __name__ == "__main__":
    comclass = Comclass()

    folder = "./Examples/EstruturaDeDadosI/"

    comclass.parse_folder(folder)

