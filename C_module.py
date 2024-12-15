from pycparser import parse_file, c_ast

class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.cyclomatic_complexity = 0        # McCabe Complexity - Individual complexity.
        self.total_cyclomatic_complexity = 0  # McCabe Complexity - Total McCabe.
        self.functions = {}                   # McCabe Complexity - Dict of the functions.
        self.current_function = None          # McCabe Complexity - Current visiting function.
        self.operators = set()   # Halstead Volume - Set of operators.
        self.operands = set()    # Halstead Volume - Set of operands.
        self.operator_count = 0  # Halstead Volume - Operator count.
        self.operand_count = 0   # Halstead Volume - Operand count.
        self.n1 = 0              # Halstead Volume - Distinct operators.
        self.n2 = 0              # Halstead Volume - Distinct operands.
        self.N1 = 0              # Halstead Volume - Total operators.
        self.N2 = 0              # Halstead Volume - Total operands.
        self.vocabulary = 0      # Halstead Volume - Vocabulary.
        self.length = 0          # Halstead Volume - length.
        self.volume = 0          # Halstead Volume - volume.

    def analyse(self, filename):
            """## Main function of the class. Call all the functions."""
            ast = parse_file(filename, use_cpp=False)  # Carregar o arquivo pré-processado e criar a AST.
            self.visit(ast)
            self.calculate_halstead_volume()    # Halstead Volume - Calculate the Halstead Volume.
            self.print_halstead_volume()        # Halstead Volume - Print the results of halstead.
            self.print_cyclomatic_complexity()  # McCabe Complexity - Print the results of cc.

        
    # HALSTEAD VOLUME
    def visit_Decl(self, node):   # Used for Halstead Volume
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
        self.n1 = len(self.operators)  # Distinct operators
        self.n2 = len(self.operands)   # Distinct operands
        self.N1 = self.operator_count  # Total operators
        self.N2 = self.operand_count   # Total operands

        self.vocabulary = self.n1 + self.n2  # Calculate vocabulary
        self.length = self.N1 + self.N2      # Calculate length
        self.volume = self.length * (self.vocabulary and (self.vocabulary.bit_length() or 1))  # Calculate volume

    def print_halstead_volume(self):      # Used for Halstead Volume
        print(f"Distinct Operators (n1): {self.n1}")
        print(f"Distinct Operands (n2): {self.n2}")
        print(f"Total Operators (N1): {self.N1}")
        print(f"Total Operands (N2): {self.N2}")
        print(f"Program Vocabulary: {self.vocabulary}")
        print(f"Program Length: {self.length}")
        print(f"Volume: {self.volume}")

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
        complexities = visitor.get_functions()
        for func_name, complexity in complexities.items():
            print(f"A complexidade ciclomática da função '{func_name}' é: {complexity}")
        print(f"Complexidade total do código é: {self.total_cyclomatic_complexity}")



if __name__ == "__main__":
    filename = "exercicio_3"
    file = f"Examples/{filename}_pre_limpo.c"  # Arquivo pré-processado e limpo
    visitor = ComplexityVisitor()              # Define a classe
    visitor.analyse(file)
    visitor.__print_operators__()
    visitor.__print_operands__()
