import os
from os.path import isdir
from Compsta import Compsta
from rich.console import Console
from rich.style import Style
import csv

class Comclass:
    def __init__(self):
        self.all_mean_metrics = []
        self.dir_names = []

    def parse_folder(self, dir_name: str, csv_name: str):
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

        self.export_consolidated_metrics(dir_name, csv_name)

    def export_consolidated_metrics(self, base_dir: str, csv_name: str):
        """Exporta todas as médias para um único CSV"""
        if not self.all_mean_metrics:
            return

        header = ["Index" ,"Folder"] + list(self.all_mean_metrics[0].keys())

        data = [header]
        for name, metrics in zip(self.dir_names, self.all_mean_metrics):
            row = [ name[:2], name] + list(metrics.values())
            data.append(row)

        os.makedirs(csv_name, exist_ok=True)

        with open(csv_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)

        Console().print(f"\nCREATE {csv_name}.csv", style="bold green")

