from math import log2
from tabulate import tabulate

class HalsteadCalculator:

	def __init__(self):
		self.n1: float = 0
		self.n2: float = 0
		self.N1: float = 0
		self.N2: float = 0

		self.vocabulary    : float = 0
		self.lenght        : float = 0
		self.estimated_len : float = 0
		self.volume        : float = 0
		self.estimated_vol : float = 0
		self.difficulty    : float = 0
		self.level         : float = 0
		self.effort        : float = 0
		self.time_required : float = 0
		self.delivered_bugs: float = 0


	def calculate_metrics(self):
		self.vocabulary     = self.n1 + self.n2  # Calculate vocabulary.
		self.lenght         = self.N1 + self.N2  # Calculate length.
		self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
		self.volume         = self.lenght * log2(self.vocabulary)  # Calculate volume.
		self.estimated_vol  = (2 + self.n2) * log2(2 + self.n2) # Calculate estimated volume.
		self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)  # Calculate difficulty.
		self.level          = self.estimated_vol / self.volume
		self.effort         = self.difficulty * self.volume  # Calculate effort.
		self.time_required  = self.effort / 4  # Calculate time to program (seconds).
		self.delivered_bugs = self.effort ** (2 / 3) / 3000  # Calculate number of delivered bugs.

	def print_metrics(self):
		header = ["Complexity", "Value"]
		data = [["Distinct Operators (n1)", self.n1],
				["Distinct Operands (n2)", self.n2],
				["Total Operators (N1)", self.N1],
				["Total Operands (N2)", self.N2],
				["Program vocabulary", self.vocabulary],
				["Program Lenght", self.lenght],
				["Estimated Length", f"{self.estimated_len}"],
				["Volume", f"{self.volume}"],
				["Estimated Volume", f"{self.estimated_vol}"],
				["Difficulty", f"{self.difficulty}"],
				["Program level", f"{self.level}"],
				["Effort", f"{self.effort}"],
				["Required time to program", f"{self.time_required}"],
				["Delivered bugs", f"{self.delivered_bugs}"],
				]
		print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

	def calculate_print(self):
		self.n1 = int(input("Distinc operators (n1): "))
		self.n2 = int(input("Distinc operands  (n2): "))
		self.N1 = int(input("Total operators   (N1): "))
		self.N2 = int(input("Total operands    (N2): "))

		self.calculate_metrics()
		self.print_metrics()

hals_calculator = HalsteadCalculator()	
hals_calculator.calculate_print()
print(f"1 - {log2(hals_calculator.n1)}")
print(f"2 - {log2(hals_calculator.n2)}")


