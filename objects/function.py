from pycparser import c_ast
from math      import log2
from rich.console import Console
from rich.table   import Table
from rich.style   import Style
from rich         import box

class Function:

    def __init__(self, func_name: str) -> None:
        #==> Function info <==#
        self.func_name: str = func_name
        self.calls    : int = 0

        ####################################################################### 
        # |> variable: self.operands
        #
        # Dictonary to store the operands
        #
        # Keys  : Operand.
        # Values: Lists of operand occurrence lines. 
        #######################################################################
        self.operands : dict[str, list[int]] = dict()

        #######################################################################
        # |> variable: self.operators
        # 
        # Dictionary to store operators
        #
        # Keys  : Operand.
        # Values: Lists of operator ocurrence lines.
        ######################################################################
        self.operators: dict[str, list[int]] = dict()

        #==> Ciclomatic Complexity <==#
        self.total_mcc: int = 1 # Total McCabe Complexity

        #==> Number of lines <==#
        self.total_lines    : int = 0
        self.effective_lines: int = 0

        #==> Halstead Metric <==#
        self.n1             : int   = 0  # Number of distinct operators (n1).
        self.n2             : int   = 0  # Number of distinct operands (n2).
        self.N1             : int   = 0  # Total number of operators (N1).
        self.N2             : int   = 0  # Total number of operands (N2).
        self.vocabulary     : int   = 0  # Program vocabulary (n).
        self.length         : int   = 0  # Program lenght (N).
        self.estimated_len  : float = 0  # Estimated program length (^N).
        self.volume         : float = 0  # Volume (V).
        self.difficulty     : float = 0  # Difficulty (D).
        self.estimated_level: float = 0 # Estimated program level (L')
        self.intelligence   : float = 0  # Intelligence Content. "Independet of language" (I)
        self.effort         : float = 0  # Effort (E).
        self.time_required  : float = 0  # Time required to program (T).
        self.delivered_bugs : float = 0  # Estimated number of bugs (B).

        #==> Cognitive Complexity <==#
        self.cognitive_complexity: int = 0

    #===> Utils Methods <=====================================================#
    def table_operators(self) -> Table:
        """
        Print the table of operators inside the function.
        """
        title: str = f"[bold]Operators of [cyan]{self.func_name}[cyan][/]"
        border_style: Style = Style(color="#000000", bold=True,)

        table = Table(title=title,
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold #ffee00",
                      border_style=border_style,
                      )

        table.add_column("Operator", style="cyan")
        table.add_column("Lines of Ocurrency", style="#1cffa0", justify="right")

        for operator, lines in self.operators.items():
            table.add_row(operator, f"{lines}")

        return table

    def table_operands(self) -> Table:
        """
        Print the table of operands inside the function.
        """
        title: str = f"[bold]Operands of [cyan]{self.func_name}[cyan][/]"
        border_style: Style = Style(color="#000000", bold=True,)

        table = Table(title=title,
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold #ffee00",
                      border_style=border_style,
                      )

        table.add_column("Operands", style="cyan")
        table.add_column("Lines of Ocurrency", style="#1cffa0", justify="right")

        for operand, lines in self.operands.items():
            table.add_row(operand, f"{lines}")

        return table

    #===> Metric Methods <====================================================#

    def add_CoC(self, value: int) -> None:
        self.cognitive_complexity += value

    def calculate_halstead(self) -> None:
        self.vocabulary     = self.n1 + self.n2                                  # Calculate vocabulary.
        self.length         = self.N1 + self.N2                                  # Calculate length.
        self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
        self.volume         = self.length * log2(self.vocabulary)                # Calculate volume.
        self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)                # Calculate difficulty.
        self.estimated_level = 1 / self.difficulty
        self.intelligence   = self.estimated_level * self.volume                           # Calculate program intelligence
        self.effort         = self.difficulty * self.volume                      # Calculate effort.
        self.time_required  = self.effort / 18                                   # Calculate time to program (seconds).
        self.delivered_bugs = self.effort ** (2 / 3) / 3000                      # Calculate number of delivered bugs.
    
    def add_McC(self) -> None:
        self.total_mcc += 1

    def add_operator(self, operator: str, line: int) -> None:
        """
        Add a operator to the function.

        :param operator: The string of operator.
        :param line    : The line of operator ocurrency.
        """

        if operator in self.operators.keys():
            self.operators[operator].append(line)
            self.N1 += 1
        else:
            self.operators.update({operator: [line]})
            self.n1 += 1
            self.N1 += 1

    def add_operand(self, operand: str, line: int) -> None:
        """
        Add a operand to the function.
        
        :param operand: The string of operand.
        :param line   : The line of the operand ocurrency.
        """
        if operand in self.operands.keys():
            self.operands[operand].append(line)
            self.N2 += 1
        else:
            self.operands.update({operand: [line]})
            self.n2 += 1
            self.N2 += 1


