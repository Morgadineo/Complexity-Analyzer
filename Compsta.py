from sys import exception
from typing import final
from Comvis import ParsedCode
from os import listdir
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from rich import box
from rich.style import Style
import csv

class Compsta:
    """A class for analyzing and exporting code metrics from preprocessed files.

    :param dir_name: Directory containing preprocessed `.i` files.
    """
    def __init__(self, dir_name: str):
        """Initialize Compsta with a directory path and load preprocessed files."""
        self.dir_name: str = dir_name

        # ==> Files <======================================================== #
        self.parsed_files: list[ParsedCode] = self.get_precompiled_files()

        #==> Metrics <==#
        self.metrics: list[str] = [
            "Index",
            "Filename",
            "Effective Lines",
            "Number of Functions",
            "Total McCabe",
            "Number of distinct operators (n1)",
            "Number of distinct operands (n2)",
            "Total number of operators (N1)",
            "Total number of operands (N2)",
            "Vocabulary",
            "Lenght",
            "Estimated Lenght",
            "Volume",
            "Difficulty",
            "Level",
            "Intelligence",
            "Effort",
            "Time Required",
            "Delivered bugs",
            "Average line volume"
        ]

    def get_precompiled_files(self) -> list[ParsedCode]:
        """Scan the directory for `.i` files and parse them into `ParsedCode` objects.

        :return: List of parsed files with extracted metrics.
        :rtype: list[ParsedCode]
        """
        parsed_files: list[ParsedCode] = []
        for filename in listdir(self.dir_name):
            if filename.endswith(".i"):
                filename = filename[:-2]  # Remove `.i` extension
                
                try:
                    parsed_code = ParsedCode(filename, self.dir_name)

                    if not parsed_code.has_errors:
                        parsed_files.append(parsed_code)
                
                except Exception as e:
                    Console().print(f"ERROR PROCESSING '{filename}': {str(e)} - IGNORING",
                                  style="bold yellow")
                    continue

        return parsed_files

    def print_files_metrics(self) -> None:
        """Display a formatted table of code metrics using Rich."""
        console: Console = Console()
        title: str = f"[bold][#00ffae]{self.dir_name}[/]"
        border_style: Style = Style(color="#000000", bold=True)

        # Initialize table
        table = Table(
            title=title,
            box=box.ROUNDED,
            show_header=True,
            header_style="bold #ffee00",
            border_style=border_style,
        )

        # Define columns (abbreviated for readability)
        table.add_column("Filename", style="cyan", justify="left")
        table.add_column("EL", justify="left", style="#1cffa0")  # Effective Lines
        table.add_column("n1", justify="left", style="#1cffa0")  # Distinct operators
        table.add_column("n2", justify="left", style="#1cffa0")  # Distinct operands
        table.add_column("N1", justify="left", style="#1cffa0")  # Total operators
        table.add_column("N2", justify="left", style="#1cffa0")  # Total operands
        table.add_column("n", justify="left", style="#1cffa0")   # Vocabulary
        table.add_column("N", justify="left", style="#1cffa0")   # Length
        table.add_column("^N", justify="left", style="#1cffa0")  # Estimated Length
        table.add_column("D", justify="left", style="#1cffa0")   # Difficulty
        table.add_column("L", justify="left", style="#1cffa0")   # Level
        table.add_column("I", justify="left", style="#1cffa0")   # Intelligence
        table.add_column("E", justify="left", style="#1cffa0")   # Effort
        table.add_column("T", justify="left", style="#1cffa0")   # Time Required
        table.add_column("B", justify="left", style="#1cffa0")   # Delivered Bugs
        table.add_column("CC", justify="left", style="#1cffa0")  # McCabe Complexity
        table.add_column("LC", justify="left", style="#1cffa0")  # Avg Line Volume

        # Populate rows
        for file in self.parsed_files:
            table.add_row(
                file.filename,
                str(file.effective_lines),
                str(file.n1),
                str(file.n2),
                str(file.N1),
                str(file.N2),
                str(round(file.vocabulary)),
                str(round(file.lenght)),
                str(round(file.estimated_len)),
                str(round(file.difficulty)),
                str(round(file.level)),
                str(round(file.intelligence)),
                str(round(file.effort)),
                str(round(file.time_required)),
                str(round(file.delivered_bugs)),
                str(file.total_mcc),
                str(round(file.avg_line_volume)),
            )
        
        console.print(table)

    def export_csv(self, file_name: str) -> None:
        """Export metrics to a CSV file.

        :param file_name: Output filename (without `.csv` extension).
        :type file_name: str
        :return: None
        """
        data = [self.metrics]  # Header row

        index = 0
        for file in self.parsed_files:
            row = [
                index,
                file.filename,
                file.effective_lines,
                file.number_of_functions,
                file.total_mcc,
                file.n1,
                file.n2,
                file.N1,
                file.N2,
                file.vocabulary,
                file.lenght,
                file.estimated_len,
                file.volume,
                file.difficulty,
                file.level,
                file.intelligence,
                file.effort,
                file.time_required,
                file.delivered_bugs,
                file.avg_line_volume,
            ]
            data.append(row)
            index += 1

        with open(f"{file_name}.csv", mode="w", newline="") as file:
            csv.writer(file).writerows(data)


if __name__ == "__main__":
    compsta = Compsta("./Examples/EstruturaDeDadosI/inverter/")
    compsta.print_files_metrics()
    compsta.export_csv("Inverter")
