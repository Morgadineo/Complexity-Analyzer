from math import log2
from tabulate import tabulate

class HalsteadCalculator:

	def __init__(self):
		self.n1 = 0
		self.n2 = 0
		self.N1 = 0
		self.N2 = 0

		self.vocabulary     = 0
		self.lenght         = 0
		self.estimated_len  = 0
		self.volume         = 0
		self.difficulty     = 0
		self.level          = 0
		self.effort         = 0
		self.time_required  = 0
		self.delivered_bugs = 0


	def calculate_metrics(self):
		self.vocabulary     = self.n1 + self.n2  # Calculate vocabulary.
		self.lenght         = self.N1 + self.N2  # Calculate length.
		self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
		self.volume         = self.lenght * log2(self.vocabulary)  # Calculate volume.
		self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)  # Calculate difficulty.
		self.level          = 1 / self.difficulty  # Calculate program level.
		self.effort         = self.difficulty * self.volume  # Calculate effort.
		self.time_required  = self.effort / 18  # Calculate time to program (seconds).
		self.delivered_bugs = self.effort ** (2 / 3) / 3000  # Calculate number of delivered bugs.

	def print_metrics(self):
		header = ["Complexity", "Value"]
		data = [["Distinct Operators (n1)", self.n1],
				["Distinct Operands (n2)", self.n2],
				["Total Operators (N1)", self.N1],
				["Total Operands (N2)", self.N2],
				["Program vocabulary", self.vocabulary],
				["Program Lenght", self.lenght],
				["Estimated Length", f"{self.estimated_len:.1f}"],
				["Volume", f"{self.volume:.1f}"],
				["Difficulty", f"{self.difficulty:.1f}"],
				["Program level", f"{self.level:.1f}"],
				["Effort", f"{self.effort:.1f}"],
				["Required time to program", f"{self.time_required:.1f}"],
				["Delivered bugs", f"{self.delivered_bugs:.1f}"],
				]
		print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

	def calculate_print(self):
		self.n1 = int(input("Distinc operators (n1): "))
		self.n2 = int(input("Distinc operands  (n2): "))
		self.N1 = int(input("Total operators   (N1): "))
		self.N2 = int(input("Total operands    (N2): "))

		self.calculate_metrics()
		self.print_metrics()

if __name__ == "__main__":
	hals_calculator = HalsteadCalculator()
	
	hals_calculator.calculate_print()


