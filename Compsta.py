from ast import parse
from sys import exception
from typing import final, Any
from Comvis import ParsedCode
from pathlib import Path
import os
from os import listdir, makedirs
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from rich import box
from rich.style import Style
import csv

class Compsta:
    """A comprehensive class for batch analysis and export of code metrics from multiple files.
    
    This class processes directories containing preprocessed C files (.i extension) and
    calculates aggregate software metrics across all files. It provides functionality
    for displaying metrics in formatted tables and exporting to CSV files.
    
    Attributes:
        dir_name: Directory containing preprocessed `.i` files.
        ATTRIBUTES: List of metric attribute names to calculate means for.
        parsed_files: List of ParsedCode objects for each processed file.
        number_of_files: Count of successfully parsed files.
        metrics: Human-readable names for CSV export columns.
        mean_metrics: Dictionary containing mean values of all metrics.
    """
    
    ATTRIBUTES: list[str] = [
        "effective_lines",
        "number_of_functions",
        "total_mcc",
        "n1",
        "n2", 
        "N1",
        "N2",
        "vocabulary",
        "length",
        "estimated_len",
        "volume", 
        "difficulty",
        "estimated_level",
        "intelligence",
        "effort",
        "time_required", 
        "delivered_bugs",
        "avg_line_volume",
        "total_func_calls", 
        ]

    def __init__(self, dir_name: str):
        """Initialize Compsta with a directory path and load preprocessed files.
        
        Args:
            dir_name: Directory path containing preprocessed `.i` files.
        """
        self.dir_name: str = dir_name

        # ==> Files <======================================================== #
        self.parsed_files: list[ParsedCode] = list()
        self.number_of_files: int = 0

        #==> Metrics <==#
        self.metrics: list[str] = [
            "Index",
            "Filename",
            "Effective Lines",
            "Number of distinct operators (n1)",
            "Number of distinct operands (n2)",
            "Total number of operators (N1)",
            "Total number of operands (N2)",
            "Vocabulary",
            "Length",
            "Estimated length",
            "Volume",
            "Difficulty",
            "Estimated level",
            "Intelligence",
            "Effort",
            "Time Required",
            "Delivered bugs",
            "Total McCabe",
            "Average line volume",
            "Functions Call",
            "Number of Functions",
        ]

        self.mean_metrics: dict[str, Any] = dict()

        #==> Run <==#
        self.parse_files()
        self.parse_mean()

    #==> Methods <==###########################################################

    def parse_files(self) -> None:
        """Parse all precompiled files in the directory.
        
        This method populates the parsed_files list with ParsedCode objects
        for each valid `.i` file found in the directory.
        """
        self.parsed_files = self.get_precompiled_files()
        self.number_of_files = len(self.parsed_files)

    def parse_mean(self) -> None:
        """Computes the average values of software metrics across all parsed files.

        This method calculates the mean of a predefined list of static code metrics 
        (e.g., Halstead metrics, cyclomatic complexity, effective lines of code) 
        extracted from each ParsedCode object stored in `self.parsed_files`. 
        The results are stored in the `self.mean_metrics` dictionary using 
        `snake_case` keys prefixed with 'mean_'.

        If `self.number_of_files` is zero, the method exits without performing any calculation.

        Metrics computed include:
            - effective_lines
            - number_of_functions
            - total_mcc (cyclomatic complexity)
            - Halstead metrics (n1, n2, N1, N2, vocabulary, length, estimated_len, etc.)
            - avg_line_volume
            - total_func_calls

        Side Effects:
            - Modifies `self.mean_metrics` in-place.
        """
        #######################################################################
        # This implementation is slower than the previous version because for 
        # each attribute, it needs to loop through the entire list of objects.
        # For readability and scalability reasons, I'll keep this version.
        #######################################################################
        if self.number_of_files > 0:
            for attr in self.ATTRIBUTES:
                ###############################################################
                # variable: total
                #
                # For the current attr, it loops through all the 
                # files in the list and adds the corresponding attribute to the
                # variable.                
                ###############################################################
                total: float = sum(getattr(parsed_file, attr) for parsed_file in self.parsed_files)

                self.mean_metrics[f"mean_{attr}"] = total / self.number_of_files

    def get_precompiled_files(self) -> list[ParsedCode]:
        """Scan the directory for `.i` files and parse them into `ParsedCode` objects.

        Returns:
            List of parsed files with extracted metrics.
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
                    Console().print(f"ERROR PROCESSING '{filename}': {str(e)}",
                                    style="bold yellow")
        return parsed_files

    def print_files_metrics(self) -> None:
        """Display a formatted table of code metrics using Rich.
        
        Shows a comprehensive table with all metrics for each parsed file
        using abbreviated column headers for better readability.
        """
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
        table.add_column("V", justify="left", style="#1cffa0")   # Program Volume
        table.add_column("D", justify="left", style="#1cffa0")   # Difficulty
        table.add_column("L*", justify="left", style="#1cffa0")  # Estimated level
        table.add_column("I", justify="left", style="#1cffa0")   # Intelligence
        table.add_column("E", justify="left", style="#1cffa0")   # Effort
        table.add_column("T", justify="left", style="#1cffa0")   # Time Required
        table.add_column("B", justify="left", style="#1cffa0")   # Delivered Bugs
        table.add_column("CC", justify="left", style="#1cffa0")  # McCabe Complexity
        table.add_column("LC", justify="left", style="#1cffa0")  # Avg Line Volume
        table.add_column("FC", justify="left", style="#1cffa0")  # Number of funtions calls
        

        # Populate rows
        nDigits: int = 2
        for file in self.parsed_files:
            table.add_row(
                file.filename,
                str(file.effective_lines),
                str(file.n1),
                str(file.n2),
                str(file.N1),
                str(file.N2),
                str(round(file.vocabulary, nDigits)),
                str(round(file.length, nDigits)),
                str(round(file.estimated_len, nDigits)),
                str(round(file.volume, nDigits)),
                str(round(file.difficulty, nDigits)),
                str(round(file.estimated_level, nDigits)),
                str(round(file.intelligence, nDigits)),
                str(round(file.effort, nDigits)),
                str(round(file.time_required, nDigits)),
                str(round(file.delivered_bugs, nDigits)),
                str(file.total_mcc),
                str(round(file.avg_line_volume, nDigits)),
                str(file.total_func_calls),
            )
        
        console.print(table)

    def print_mean_metrics(self) -> None:
        """Display a formatted table of mean metrics using Rich.
        
        Shows the average values of all metrics across all parsed files
        in a clean, readable table format.
        """
        console     : Console = Console()
        title       : str     = f"[bold][#00ffae]Average Metrics for {self.dir_name}[/]"
        border_style: Style   = Style(color="#000000", bold=True)

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

        for key, metric_value in self.mean_metrics.items():
            metric_name: str = key.replace("_", " ").title()
            mean_table.add_row(metric_name, f"{metric_value:.1f}")

        console.print(mean_table)

    def export_csv(self, dir: str, filename: str) -> None:
        """Export individual file metrics to a CSV file.
        
        Creates a CSV file with detailed metrics for each parsed file,
        including an index and filename for reference.

        Args:
            dir: Output directory path.
            filename: Output filename without extension.
        """
        data = [self.metrics]  # Header row
        file_name: str = f"{dir}{filename}"
        index = 0

        for file in self.parsed_files:
            # Ordem reorganizada para seguir exatamente a mesma ordem do print
            row = [
                index,
                file.filename,
                file.effective_lines,           # EL
                file.n1,                        # n1
                file.n2,                        # n2
                file.N1,                        # N1
                file.N2,                        # N2
                file.vocabulary,                # Vocabulary
                file.length,                    # Length
                file.estimated_len,             # Estimated length
                file.volume,                    # Volume
                file.difficulty,                # Difficulty
                file.estimated_level,           # Estimated level
                file.intelligence,              # Intelligence
                file.effort,                    # Effort
                file.time_required,             # Time Required
                file.delivered_bugs,            # Delivered bugs
                file.total_mcc,                 # Total McCabe (CC)
                file.avg_line_volume,           # Average line volume (LC)
                file.total_func_calls,          # Functions Call (FC)
                file.number_of_functions,       # Number of Functions
            ]
            data.append(row)
            index += 1

        makedirs(dir, exist_ok=True)

        with open(f"{file_name}.csv", mode="w", newline="") as file:
            csv.writer(file).writerows(data)

        Console().print(f"Create CSV: {file_name}", style="bold green")

    def export_mean_csv(self, dir: str, filename: str) -> None:
        """Export mean metrics to a CSV file with metrics as columns.
        
        Creates a CSV file where each column header is a metric name and
        the single row contains the mean values for all metrics.

        Args:
            dir: Output directory path.
            filename: Output filename without extension.
        """
        file_name: str = f"{dir}{filename}_mean"
        
        # Prepare headers (cleaning 'mean_' prefix)
        headers = [metric.replace("mean_", "") for metric in self.mean_metrics.keys()]
        
        # Prepare values row (formatted to 2 decimal places)
        values = [f"{value:.2f}" for value in self.mean_metrics.values()]
        
        # Create directory if it doesn't exist
        makedirs(dir, exist_ok=True)
        
        # Write to CSV
        with open(f"{file_name}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write metrics as column headers
            writer.writerow(values)   # Write values in a single row
        
        Console().print(f"Created mean CSV: {file_name}", style="bold green")

    @staticmethod
    def process_directory(base_input_dir: str, base_output_dir: str) -> None:
        """Process all exercise directories recursively and generate CSV files.
        
        This static method walks through a directory tree, processes all
        subdirectories containing `.i` files, and generates CSV exports
        for each directory.

        Args:
            base_input_dir: Base directory containing the exercise folders.
            base_output_dir: Base output directory for CSV files.
        """
        console = Console()
        
        # Ensure the base output directory exists
        Path(base_output_dir).mkdir(parents=True, exist_ok=True)
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(base_input_dir):
            # Skip directories that don't contain .i files
            if not any(f.endswith('.i') for f in files):
                continue
                
            # Process each directory with .i files
            relative_path = os.path.relpath(root, base_input_dir)
            output_dir = os.path.join(base_output_dir, relative_path)
            
            # Create Compsta instance for this directory
            try:
                console.print(f"\nProcessing: [bold cyan]{root}[/]", style="bold")
                compsta = Compsta(root + "/")  # Ensure trailing slash
                
                # Generate CSV name from directory name
                csv_name = os.path.basename(root)
                
                # Print metrics and export CSVs
                compsta.print_files_metrics()
                compsta.print_mean_metrics()
                compsta.export_csv(output_dir + "/", csv_name)
                compsta.export_mean_csv(output_dir + "/", csv_name)
                
                console.print(f"Successfully processed [green]{root}[/]", style="bold")
            except Exception as e:
                console.print(f"Error processing {root}: {str(e)}", style="bold red")

if __name__ == "__main__":
    # With /
    file_dir: str = "./Examples/"
    
    input_base = "./Examples/"
    output_base = "./csvs/"
    
    Compsta.process_directory(input_base, output_base)
