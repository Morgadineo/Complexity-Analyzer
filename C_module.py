from pycparser import parse_file, c_ast
from math import log2, pow
from tabulate import tabulate

class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.total_lines = 0      # Lenght Complexity - Total lines of code
        self.effective_lines = 0  # Lenght Complexity - Total of effective lines of code
        self.cyclomatic_complexity = 0        # McCabe Complexity - Individual complexity.
        self.total_cyclomatic_complexity = 0  # McCabe Complexity - Total McCabe.
        self.functions = {}                   # McCabe Complexity - Dict of the functions.
        self.current_function = None          # McCabe Complexity - Current visiting function.
        self.operators = set()   # Halstead Volume - Set of operators.
        self.operands = set()    # Halstead Volume - Set of operands.
        self.operator_count = 0  # Halstead Volume - Operator count.
        self.operand_count = 0   # Halstead Volume - Operand count.
        self.n1 = 0              # Halstead Volume - the number of distinct operators (n1).
        self.n2 = 0              # Halstead Volume - the number of distinct operands (n2).
        self.N1 = 0              # Halstead Volume - the total number of operators (N1).
        self.N2 = 0              # Halstead Volume - the total number of operands (N2).
        self.vocabulary = 0      # Halstead Volume - Program vocabulary (n).
        self.lenght = 0          # Halstead Volume - Program lenght (N).
        self.estimated_len = 0   # Halstead Volume - Estimated program lenght (^N).
        self.volume = 0          # Halstead Volume - Volume (V).
        self.difficulty = 0      # Halstead Volume - Difficulty (D).
        self.effort = 0          # Halstead Volume - Effort (E).
        self.time_required = 0   # Halstead Volume - Time required to program (T).
        self.delivered_bugs = 0  # Halstead Volume - Estimated number of bugs (errors). 

    def print_analyse(self, filename):
        """## Main function of the class. Call all the complexity functions and print the results."""
        path = f"Examples/{filename}"                 # Path
        file = f"{path}.c"         
        file_clean = f"{path}_pre_limpo.c"            # Path to pre-compiled and cleaned file.

        ast = parse_file(file_clean, use_cpp=False)   # Create the AST using the pre-compiled and clean file.
        self.visit(ast)
        self.count_lines(file)
        self.print_lenght()
        self.calculate_halstead_volume()    # Halstead Volume - Calculate the Halstead Volume.
        self.print_halstead_volume()        # Halstead Volume - Print the results of halstead.
        self.print_cyclomatic_complexity()  # McCabe Complexity - Print the results of cc.

    def analyse(self, filename):
            """## Main function of the class. Call all the complexity calculate functions."""
            path = f"Examples/{filename}"                 # Path
            file = f"{path}.c"         
            file_clean = f"{path}_pre_limpo.c"            # Path to pre-compiled and cleaned file.

            ast = parse_file(file_clean, use_cpp=False)   # Create the AST using the pre-compiled and clean file.
            self.visit(ast)
            self.count_lines(file)
            self.calculate_halstead_volume()

        
    # CODE LENGHT
    def print_lenght(self):
        print("== Code Infos ===================")
        print(f"Effective lines: {self.effective_lines}")
        print(f"Total lines:     {self.total_lines}")

    def count_lines(self, filename):
        """## Procedure to count he quantity of lines of code.
        Count the total lines and the effectives lines."""
        with open(filename) as file:
            lines = file.readlines()
            self.total_lines = len(lines)
            for line in lines:
                if line.strip():
                    self.effective_lines += 1
            

    # HALSTEAD VOLUME
    def visit_Decl(self, node):           # Used for Halstead Volume
        """## Procedure called when a variable is inicialized.
        This is necessary because pycparser library does not identify inicializations as a Assignment node."""
        if node.init is not None:
            self.operators.add('=')
            self.operator_count += 1
            self.visit(node.init)
        self.generic_visit(node)

    def visit_Assignment(self, node):     # Used for Halstead Volume
        """## Procedure called when a assignment operator node is visited.
        Visit assignment operations like =, +=, -=.
        """
        self.operators.add("=")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_BinaryOp(self, node):       # Used for Halstead Volume
        """## Procedure called when a binary operator node is visited.
        Called when visit binary operations like +, -, *, /.
        """
        self.operators.add(node.op)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node):        # Used for Halstead Volume
        """## Procedure called when a unary operator node is visited.
        Visit unary operations like -, ++, --.
        """
        self.operators.add(node.op)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_ID(self, node):             # Used for Halstead Volume
        """## Procedure called when a variable node is visited.
        Visit identifiers (variables).
        """
        self.operands.add(node.name)
        self.operand_count += 1

    def visit_Constant(self, node):       # Used for Halstead Volume
        """## Procedure called when a constant/literal node is visited.
        Visit constants (literals).
        """
        self.operands.add(node.value)
        self.operand_count += 1

    def calculate_halstead_volume(self):  # Used for Halstead Volume
        """## Procedure to calculate the Halstead volume.
        """
        self.n1 = len(self.operators)  # Distinct operators.
        self.n2 = len(self.operands)   # Distinct operands.
        self.N1 = self.operator_count  # Total operators.
        self.N2 = self.operand_count   # Total operands.

        self.vocabulary = self.n1 + self.n2                                    # Calculate vocabulary.
        self.lenght = self.N1 + self.N2                                        # Calculate length.
        self.estimated_len = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
        self.volume = self.vocabulary * log2(self.vocabulary)                  # Calculate volume.
        self.difficulty = (self.n1 / 2) * (self.N2 / self.n2)                  # Calculate difficulty.
        self.effort = self.difficulty * self.volume                            # Calculate effort.
        self.time_required = self.effort / 18                                  # Calculate time to program (seconds).
        self.delivered_bugs = self.volume / 3000                               # Calculate number of delivered bugs.

    def print_halstead_volume(self):      # Used for Halstead Volume
        print("== HALSTEAD VOLUME ===============================")
        print(f"Distinct Operators (n1): {self.n1}")
        print(f"Distinct Operands (n2):  {self.n2}")
        print(f"Total Operators (N1):    {self.N1}")
        print(f"Total Operands (N2):     {self.N2}")
        print(f"Program Vocabulary:      {self.vocabulary}")
        print(f"Program Lenght:          {self.lenght}")
        print(f"Estimated Lenght:        {self.estimated_len:.1f}")
        print(f"Volume:                  {self.volume:.1f}")
        print(f"Difficulty:              {self.difficulty:.1f}")
        print(f"Effort:                  {self.effort:.1f}")
        print(f"Required time program:   {self.time_required:.1f} seconds")
        print(f"Delivered bugs:          {self.delivered_bugs:.1f}")


    def __print_operators__(self):  # UTIL
        """## Print the set of operators in the code.
        """
        text = "Operators:"
        for operator in self.operators:
            text += " " + operator + ","
        print(text)

    def __print_operands__(self):   # UTIL
        """## Print the set of operands in the code.
        """
        text = "Operands:"
        for operand in self.operands:
            text += " " + operand + ","
        print(text)

    # CYCLOMATIC COMPLEXITY
    def visit_FuncDef(self, node):        # Used for McCabe Complexity
        """## Procedure called when a FUNCTION node is find.
        When a function is visited, self.current_function is defined with the function name and the function is
        add in the dictionary. With function complexity is analysed separated.
        """
        self.current_function = node.decl.name  # Get the module name
        self.cyclomatic_complexity = 1          # Module cyclomatic complexity
        self.generic_visit(node)                # Visit all the modules nodes
        self.total_cyclomatic_complexity += self.cyclomatic_complexity     # Total cyclomatic complexity equal sum of
                                                                           # the modules complexity
        self.functions[self.current_function] = self.cyclomatic_complexity # Store the module complexity

    def visit_If(self, node):             # Used for McCabe Complexity
        """## Procedure called when an IF node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):            # Used for McCabe Complexity
        """## Procedure called when a FOR node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):          # Used for McCabe Complexity
        """## Procedure called when a WHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_DoWhile(self, node):        # Used for McCabe Complexity
        """## Procedure called when a DoWHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_Switch(self, node):         # Used for McCabe Complexity
        """## Procedure called when a SWITCH node is visited.
        *cyclomatic_complexity += (quantity of case statements)*
        """
        if node.stmt.block_items:
            self.cyclomatic_complexity += len(node.stmt.block_items) - 1
        self.generic_visit(node)

    def get_functions(self):                # UTIL
        """## Return the dictionary containing complexities of each function."""
        return self.functions

    def print_cyclomatic_complexity(self):  # UTIL
        """## Print all the function name and his respective complexity"""
        print(f"\n== COMPLEXIDADE CICLOMÁTICA ===========================")
        complexities = self.get_functions()
        for func_name, complexity in complexities.items():
            print(f"Função '{func_name}' complexidade: {complexity}")
        print(f"Complexidade total: {self.total_cyclomatic_complexity}")

def compare(filename1, filename2):
    visitor1 = ComplexityVisitor()
    visitor2 = ComplexityVisitor()
    visitor1.analyse(filename1)
    visitor2.analyse(filename2)

    headers = ["Metric", "Code(1)", "Code(2)", "Code(2) have"]
    data = [["Total lines", visitor1.total_lines, visitor2.total_lines, (visitor2.total_lines - visitor1.total_lines)],
            ["Effective lines", visitor1.effective_lines, visitor2.effective_lines, (visitor2.effective_lines - visitor1.effective_lines)],
            ["Operator count", visitor1.operator_count, visitor2.operator_count, (visitor2.operator_count - visitor1.operator_count)],
            ["Operand count", visitor1.operand_count, visitor2.operand_count, (visitor2.operand_count - visitor1.operand_count)],
            ["Count of distinct operators", visitor1.n1, visitor2.n1, (visitor2.n1 - visitor1.n1)],
            ["Count of distinct operands", visitor1.n2, visitor2.n2, (visitor2.n2 - visitor1.n2)],
            ["Total count of operators", visitor1.N1, visitor2.N1, (visitor2.N1 - visitor1.N1)],
            ["Total count of operands", visitor1.N2, visitor2.N2, (visitor2.N2 - visitor1.N2)],
            ["Program vocabulary", visitor1.vocabulary, visitor2.vocabulary, (visitor2.vocabulary - visitor1.vocabulary)],
            ["Program lenght", visitor1.lenght, visitor2.lenght, (visitor2.lenght - visitor1.lenght)],
            ["Estimated program lenght", visitor1.estimated_len, visitor2.estimated_len, (visitor2.estimated_len - visitor1.estimated_len)],
            ["Volume", visitor1.volume, visitor2.volume, (visitor2.volume - visitor1.volume)],
            ["Difficulty", visitor1.difficulty, visitor2.difficulty, (visitor2.difficulty - visitor1.difficulty)],
            ["Effort", visitor1.effort, visitor2.effort, (visitor2.effort - visitor1.effort)],
            ["Time required to program", visitor1.time_required, visitor2.time_required, (visitor2.time_required - visitor1.time_required)],
            ["Estimated number of bugs", visitor1.delivered_bugs, visitor2.delivered_bugs, (visitor2.delivered_bugs - visitor1.delivered_bugs)],
            ["Total cyclomatic complexity", visitor1.total_cyclomatic_complexity, visitor2.total_cyclomatic_complexity, (visitor2.total_cyclomatic_complexity - visitor1.total_cyclomatic_complexity)]
           ]
    print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))


if __name__ == "__main__":
    filename = "cash" 
    compare(filename, f"{filename}2")
