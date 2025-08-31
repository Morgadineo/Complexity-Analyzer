from math import log2
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from rich.style import Style

class HalsteadCalculator:

	def __init__(self):
		self.n1: float = 0
		self.n2: float = 0
		self.N1: float = 0
		self.N2: float = 0

		self.vocabulary    : float = 0
		self.length        : float = 0
		self.estimated_len : float = 0
		self.volume        : float = 0
		self.difficulty    : float = 0
		self.estimated_level : float = 0
		self.intelligence  : float = 0
		self.effort        : float = 0
		self.time_required : float = 0
		self.delivered_bugs: float = 0

	def calculate_metrics(self):
		self.vocabulary      = self.n1 + self.n2                                  
		self.length          = self.N1 + self.N2
		self.estimated_len   = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)
		self.volume          = self.length * log2(self.vocabulary)             
		self.difficulty      = (self.n1 / 2) * (self.N2 / self.n2)            
		self.estimated_level = 1 / self.difficulty
		self.intelligence    = self.estimated_level * self.volume
		self.effort          = self.difficulty * self.volume               
		self.time_required   = self.effort / 18                         
		self.delivered_bugs  = self.effort ** (2 / 3) / 3000             

	def print_metrics(self):
		"""Print the code complexity metrics using Rich."""
		
		console = Console()

		# Create table
		title: str = f"[bold][#00ffae]CODE COMPLEXITY METRICS[/]"
		border_style: Style = Style(color="#000000", bold=True)

		table = Table(
			title=title,
			box=ROUNDED,
			show_header=True,
        header_style="bold #ffee00",
        border_style=border_style,
		)

		table.add_column("Complexity", style="cyan")
		table.add_column("Value", justify="right", style="#1cffa0")
		
		# Add metrics rows
		table.add_row("Distinct Operators (n1)", str(self.n1))
		table.add_row("Distinct Operands (n2)", str(self.n2))
		table.add_row("Total Operators (N1)", str(self.N1))
		table.add_row("Total Operands (N2)", str(self.N2))
		
		table.add_row("Program vocabulary", str(self.vocabulary))
		table.add_row("Program Length", str(self.length))
		table.add_row("Estimated Length", f"{self.estimated_len:.1f}")
		table.add_row("Volume", f"{self.volume:.1f}")
		table.add_row("Difficulty", f"{self.difficulty:.1f}")
		table.add_row("Estimated Program level", f"{self.estimated_level:.3f}")
		table.add_row("Content Intelligence", f"{self.intelligence:.1f}")
		table.add_row("Effort", f"{self.effort:.1f}")
		table.add_row("Required time to program", f"{self.time_required:.1f}")
		table.add_row("Delivered bugs", f"{self.delivered_bugs:.1f}")

		# Print the table
		console.print(table)
	def calculate_print(self):
		self.n1 = int(input("Distinc operators (n1): "))
		self.n2 = int(input("Distinc operands  (n2): "))
		self.N1 = int(input("Total operators   (N1): "))
		self.N2 = int(input("Total operands    (N2): "))

		self.calculate_metrics()
		self.print_metrics()

hals_calculator = HalsteadCalculator()	
hals_calculator.calculate_print()

