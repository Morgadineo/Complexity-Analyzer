import os
from os.path import isdir
from Compsta import Compsta
from rich.console import Console
from rich.style import Style
import csv

class Comclass:
    def __init__(self):
        self.all_mean_metrics = []  # Armazenará as médias de todas as pastas
        self.dir_names = []         # Nomes das pastas analisadas

    def parse_folder(self, dir_name: str):
        """Analisa todas as subpastas e coleta métricas"""
        for file in os.listdir(dir_name):
            file_path = os.path.join(dir_name, file)
            if os.path.isdir(file_path):
                file_path = f"{file_path}/"
                compsta = Compsta(file_path)
                
                # Adiciona métricas médias à lista
                self.all_mean_metrics.append(compsta.mean_metrics)
                self.dir_names.append(file.capitalize())
                
                Console().print(f"Processed {file.capitalize()}", style="bold green")

        # Exporta tudo para um único CSV após processar todas as pastas
        self.export_consolidated_metrics(dir_name)

    def export_consolidated_metrics(self, base_dir: str):
        """Exporta todas as médias para um único CSV"""
        if not self.all_mean_metrics:
            return

        # Cria cabeçalho baseado nas keys do primeiro item
        header = ["Folder"] + list(self.all_mean_metrics[0].keys())

        # Prepara os dados
        data = [header]
        for name, metrics in zip(self.dir_names, self.all_mean_metrics):
            row = [name] + list(metrics.values())
            data.append(row)

        # Define o nome do arquivo baseado na pasta principal
        csv_name = os.path.join("./csvs/", "consolidated_mean_metrics.csv")

        # Escreve o arquivo
        with open(csv_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

        Console().print(f"\nCREATE consolidated_mean_metrics.csv", style="bold green")

if __name__ == "__main__":
    comclass = Comclass()

    folder = "./Examples/EstruturaDeDadosI/Lista02/"

    comclass.parse_folder(folder)

