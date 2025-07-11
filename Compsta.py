from ast import parse
from sys import exception
from typing import final, Any
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
        self.parsed_files: list[ParsedCode] = list()
        self.number_of_files: int = 0

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
            "length",
            "Estimated length",
            "Volume",
            "Difficulty",
            "Level",
            "Intelligence",
            "Effort",
            "Time Required",
            "Delivered bugs",
            "Average line volume",
            "Functions Call",
        ]

        self.mean_metrics: dict[str, Any] = dict()

        #==> Run <==#
        self.parse_files()
        self.parse_mean()

    #==> Methods <==###########################################################

    def parse_files(self):
        self.parsed_files = self.get_precompiled_files()
        self.number_of_files = len(self.parsed_files)

    def parse_mean(self):
        total_effective_lines = 0
        total_number_of_functions = 0
        total_mcc = 0
        total_n1 = 0
        total_n2 = 0
        total_N1 = 0
        total_N2 = 0
        total_vocabulary = 0
        total_length = 0
        total_estimated_len = 0
        total_volume = 0
        total_difficulty = 0
        total_level = 0
        total_intelligence = 0
        total_effort = 0
        total_time_required = 0
        total_delivered_bugs = 0
        total_avg_line_volume = 0
        total_cognitive_complexity = 0
        total_functions_calls = 0


        for parsed_file in self.get_precompiled_files():
            total_effective_lines += parsed_file.effective_lines
            total_number_of_functions += parsed_file.number_of_functions
            total_mcc += parsed_file.total_mcc
            total_n1 += parsed_file.n1
            total_n2 += parsed_file.n2
            total_N1 += parsed_file.N1
            total_N2 += parsed_file.N2
            total_vocabulary += parsed_file.vocabulary
            total_length += parsed_file.length
            total_estimated_len += parsed_file.estimated_len
            total_volume += parsed_file.volume
            total_difficulty += parsed_file.difficulty
            total_level += parsed_file.level
            total_intelligence += parsed_file.intelligence
            total_effort += parsed_file.effort
            total_time_required += parsed_file.time_required
            total_delivered_bugs += parsed_file.delivered_bugs
            total_avg_line_volume += parsed_file.avg_line_volume
            total_cognitive_complexity += parsed_file.total_cognitive_complexity
            total_functions_calls += parsed_file.total_func_calls

        total_effective_lines /= self.number_of_files
        total_number_of_functions /= self.number_of_files
        total_mcc /= self.number_of_files
        total_n1 /= self.number_of_files
        total_n2 /= self.number_of_files
        total_N1 /= self.number_of_files
        total_N2 /= self.number_of_files
        total_vocabulary /= self.number_of_files
        total_length /= self.number_of_files
        total_estimated_len /= self.number_of_files
        total_volume /= self.number_of_files
        total_difficulty /= self.number_of_files
        total_level /= self.number_of_files
        total_intelligence /= self.number_of_files
        total_effort /= self.number_of_files
        total_time_required /= self.number_of_files
        total_delivered_bugs /= self.number_of_files
        total_avg_line_volume /= self.number_of_files
        total_cognitive_complexity /= self.number_of_files
        total_functions_calls /= self.number_of_files

        self.mean_metrics = {
            "Mean Effective Lines": total_effective_lines,
            "Mean Number of Functions": total_number_of_functions,
            "Mean Total McCabe": total_mcc,
            "Mean Number of distinct operators (n1)": total_n1,
            "Mean Number of distinct operands (n2)": total_n2,
            "Mean Total number of operators (N1)": total_N1,
            "Mean Total number of operands (N2)": total_N2,
            "Mean Vocabulary": total_vocabulary,
            "Mean Length": total_length,
            "Mean Estimated length": total_estimated_len,
            "Mean Volume": total_volume,
            "Mean Difficulty": total_difficulty,
            "Mean Level": total_level,
            "Mean Intelligence": total_intelligence,
            "Mean Effort": total_effort,
            "Mean Time Required": total_time_required,
            "Mean Delivered bugs": total_delivered_bugs,
            "Mean Average line volume": total_avg_line_volume,
            "Mean Functions Call": total_functions_calls,
            "Mean Cognitive Complexity": total_cognitive_complexity
        }

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
        table.add_column("FC", justify="left", style="#1cffa0")  # Number of funtions calls
        

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
                str(round(file.length)),
                str(round(file.estimated_len)),
                str(round(file.difficulty)),
                str(round(file.level)),
                str(round(file.intelligence)),
                str(round(file.effort)),
                str(round(file.time_required)),
                str(round(file.delivered_bugs)),
                str(file.total_mcc),
                str(round(file.avg_line_volume)),
                str(file.total_func_calls),
            )
        
        console.print(table)

    def print_mean_metrics(self) -> None:
        console = Console()
        title = f"[bold][#00ffae]Average Metrics for {self.dir_name}[/]"
        border_style = Style(color="#000000", bold=True)

        # Create table for mean metrics
        mean_table = Table(
            title=title,
            box=box.ROUNDED,
            show_header=True,
            header_style="bold #ffee00",
            border_style=border_style,
        )

        # Add columns (matching your original style)
        mean_table.add_column("Metric", style="cyan", justify="left")
        mean_table.add_column("Value", justify="left", style="#1cffa0")
        mean_table.add_column("Description", justify="left", style="#1cffa0")

        # Add mean metrics rows with descriptions
        mean_table.add_row(
            "Effective Lines (EL)",
            f"{self.mean_metrics['Mean Effective Lines']:.2f}",
            "Average executable lines of code"
        )
        mean_table.add_row(
            "Functions",
            f"{self.mean_metrics['Mean Number of Functions']:.2f}",
            "Average number of functions"
        )
        mean_table.add_row(
            "McCabe (CC)",
            f"{self.mean_metrics['Mean Total McCabe']:.2f}",
            "Average cyclomatic complexity"
        )
        mean_table.add_row(
            "Distinct Operators (n1)",
            f"{self.mean_metrics['Mean Number of distinct operators (n1)']:.2f}",
            "Average unique operators"
        )
        mean_table.add_row(
            "Distinct Operands (n2)",
            f"{self.mean_metrics['Mean Number of distinct operands (n2)']:.2f}",
            "Average unique operands"
        )
        mean_table.add_row(
            "Total Operators (N1)",
            f"{self.mean_metrics['Mean Total number of operators (N1)']:.2f}",
            "Average total operators"
        )
        mean_table.add_row(
            "Total Operands (N2)",
            f"{self.mean_metrics['Mean Total number of operands (N2)']:.2f}",
            "Average total operands"
        )
        mean_table.add_row(
            "Vocabulary (n)",
            f"{self.mean_metrics['Mean Vocabulary']:.2f}",
            "Average n1 + n2"
        )
        mean_table.add_row(
            "Length (N)",
            f"{self.mean_metrics['Mean Length']:.2f}",
            "Average N1 + N2"
        )
        mean_table.add_row(
            "Difficulty (D)",
            f"{self.mean_metrics['Mean Difficulty']:.2f}",
            "Average program difficulty"
        )
        mean_table.add_row(
            "Level (L)",
            f"{self.mean_metrics['Mean Level']:.2f}",
            "Average program level"
        )
        mean_table.add_row(
            "Effort (E)",
        f"{self.mean_metrics['Mean Effort']:.2f}",
        "Average programming effort"
        )
        mean_table.add_row(
            "Time (T)",
            f"{self.mean_metrics['Mean Time Required']:.2f}",
            "Average time required"
        )
        mean_table.add_row(
            "Line Volume (LC)",
            f"{self.mean_metrics['Mean Average line volume']:.2f}",
            "Average volume per line"
        )
        mean_table.add_row(
            "Cognitive Complexity",
            f"{self.mean_metrics.get('Mean Cognitive Complexity', 0):.2f}",
            "Average cognitive complexity"
        )

        console.print(mean_table)

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
                file.length,
                file.estimated_len,
                file.volume,
                file.difficulty,
                file.level,
                file.intelligence,
                file.effort,
                file.time_required,
                file.delivered_bugs,
                file.avg_line_volume,
                file.total_func_calls,
            ]
            data.append(row)
            index += 1

        with open(f"{file_name}.csv", mode="w", newline="") as file:
            csv.writer(file).writerows(data)

if __name__ == "__main__":
    file_dir: str = "./Examples/EstruturaDeDadosI/distancia/"
    
    compsta: Compsta = Compsta(file_dir)

    csv_dir  : str = "csvs"
    csv_name : str = "Distancia"
    csv_final: str = f"{csv_dir}/{csv_name}"

    compsta.print_files_metrics()
    compsta.print_mean_metrics()

