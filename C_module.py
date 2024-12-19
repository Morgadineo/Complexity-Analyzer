from pycparser import parse_file, c_ast
from math import log2, pow
from tabulate import tabulate

class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self, filename):
        ##########-- UTILS VARIABLES --########################################
        ##-- FILE --##
        self.filename = filename                             # Raw filename
        self.file_dir = "Examples"                           # Dir with the source file and the pre-compiled file
        self.file_path = f"{self.file_dir}/{self.filename}"  # File path without sufix
        self.file_clean = f"{self.file_path}_pre_limpo.c"    # Path to the pre-compiled file
        self.file_source = f"{self.file_path}.c"             # Path to the source code

        ##########-- CODE INFOS --#############################################

        # VARIABLE: functions_info -> Dict -> STRING: ARRAY
        #  Store functions informations in array in order:
        #      * [0] STRING[] -> "Parameters type" [X]
        #      * [1] STRING -> "Return type"
        #      * [2] INT -> Line of definition
        #      * [3] INT[] -> Lines of calls
        self.functions_info = {}

        # VARIABLE: functions_complexities -> Dict -> STRING: ARRAY
        #  Store functions complexitites in a array with order:
        #      * [0] INT -> Cyclomatic Number 
        #      * [1] INT -> Cognitive Number
        self.functions_complexities = {}

        ##########-- LENGHT COMPLEXITY --######################################
        self.total_lines = 0      # Total lines of code
        self.effective_lines = 0  # Total of effective lines of code

        ##########-- CYCLOMATIC COMPLEXITY --##################################
        self.cyclomatic_complexity = 0        # Individual complexity.
        self.total_cyclomatic_complexity = 0  # Total McCabe.
        # self.functions_complexities[]         # Store the CC in...
        self.current_function = None          # Current visiting function.

        ##########-- HALSTEAD COMPLEXITY --####################################
        self.operators = set()   # Set of operators.
        self.operands = set()    # Set of operands.
        self.operator_count = 0  # Operator count.
        self.operand_count = 0   # Operand count.
        self.n1 = 0              # Number of distinct operators (n1).
        self.n2 = 0              # Number of distinct operands (n2).
        self.N1 = 0              # Total number of operators (N1).
        self.N2 = 0              # Total number of operands (N2).
        self.vocabulary = 0      # Program vocabulary (n).
        self.lenght = 0          # Program lenght (N).
        self.estimated_len = 0   # Estimated program lenght (^N).
        self.volume = 0          # Volume (V).
        self.difficulty = 0      # Difficulty (D).
        self.level = 0           # Program level.
        self.effort = 0          # Effort (E).
        self.time_required = 0   # Time required to program (T).
        self.delivered_bugs = 0  # Estimated number of bugs (errors).

        ##########-- COGNITIVE COMPLEXITY --###################################
        self.total_cognitive_complexity = 0  # Total cognitive complexity.
        self.current_depth = 0               # Actual deph level.
        self.weights = {                     # Weight of statements and structures (Based on the article).
            "sequence": 1,
            "atomic": 1,
            "if": 2,
            "case": 3,
            "for": 3,
            "while": 3,
            "do-while": 3,
            "nested": 4,
            "constant": 1,
            "array": 2,
            "pointer": 3,
            "complex_pointer": 4
        }
    
    ###*********************************************************************###
    ##                           FUNCTIONS                                   ##
    ###*********************************************************************###

    ###-- UTILS FUNCTIONS --###################################################

    def print_analyse(self):
        """## Main function of the class. Call all the complexity functions and print the results."""
        ast = parse_file(self.file_clean, use_cpp=False)   # Create the AST using the pre-compiled and clean file.
        self.visit(ast)
        self.count_lines()
        self.calculate_halstead_volume()    # Halstead Volume - Calculate the Halstead Volume.
        self.print_complexities()
        self.__print_operators__()
        self.__print_operands__()

    def analyse(self):
            """## Main function of the class. Call all the complexity calculate functions."""
            ast = parse_file(self.file_clean, use_cpp=False)   # Create the AST using the pre-compiled and clean file.
            self.visit(ast)
            self.count_lines()
            self.calculate_halstead_volume()

    def print_complexities(self):
        header = ["Complexity", "Value"]
        data = [["Effective lines", self.effective_lines],
                ["Total lines", self.total_lines],
                ["HALSTEAD COMPLEXITY"],
                ["Distinct Operators (n1)", self.n1],
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
                ["CYCLOMATIC COMPLEXITY"],
                ["Total Cyclomatic Complexity", self.total_cyclomatic_complexity]
                ]
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))
        self.print_functions_complexities()

    def __debug_analyse__(self):
        ast = parse_file(self.file_clean, use_cpp=False)
        self.visit(ast)
        print(self.functions_info)

    ###-- COGNITIVE COMPLEXITY --##############################################
    

    ###-- CODE LENGHT --#######################################################
    def print_lenght(self):
        headers = ["CODE INFOS", "VALUE"]
        data = [["Effective lines", self.effective_lines],
                ["Total lines", self.total_lines]]
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

    def count_lines(self):
        """Count the total lines and the effective lines (non-empty and not comments)."""
        with open(self.file_source) as file:
            lines = file.readlines()
            self.total_lines = len(lines)
            in_block_comment = False
            for line in lines:
                stripped_line = line.strip()
                if in_block_comment:
                    if "*/" in stripped_line:
                        in_block_comment = False
                    continue

                if "/*" in stripped_line:
                    in_block_comment = True
                    continue

                if not stripped_line or stripped_line.startswith("//"):
                    continue

                self.effective_lines += 1

            

    ###-- HALSTEAD COMPLEXITY --###################################################

    def calculate_halstead_volume(self):  # Used for Halstead Volume
        """## Procedure to calculate the Halstead volume.
        """
        self.n1 = len(self.operators)  # Distinct operators.
        self.n2 = len(self.operands)   # Distinct operands.
        self.N1 = self.operator_count  # Total operators.
        self.N2 = self.operand_count   # Total operands.

        self.vocabulary = self.n1 + self.n2                                    # Calculate vocabulary.
        self.lenght = self.N1 + self.N2                                        # Calculate length.
        self.estimated_len = self.n1 * log2(self.n1) + self.n2 * log2(self.n2) # Calculate estimative length.
        self.volume = self.lenght * log2(self.vocabulary)                      # Calculate volume.
        self.difficulty = (self.n1 / 2) * (self.N2 / self.n2)                  # Calculate difficulty.
        self.level = 1 / self.difficulty                                       # Calculate program level
        self.effort = self.difficulty * self.volume                            # Calculate effort.
        self.time_required = self.effort / 18                                  # Calculate time to program (seconds).
        self.delivered_bugs = self.effort**(2/3) / 3000                        # Calculate number of delivered bugs.

    def print_halstead_volume(self):      # Used for Halstead Volume
        headers = ["Halstead Volume", "Value"]
        data = [["Distinct Operators (n1)", self.n1],
                ["Distinct Operands (n2)", self.n2],
                ["Total Operators (N1)", self.N1],
                ["Total Operands (N2)", self.N2],
                ["Program vocabulary", self.vocabulary],
                ["Program Lenght", self.lenght],
                ["Estimated Length", self.estimated_len],
                ["Volume", self.volume],
                ["Difficulty", self.difficulty],
                ["Program level", self.level],
                ["Effort", self.effort],
                ["Required time to program", self.time_required],
                ["Delivered bugs", self.delivered_bugs],
                ]
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))


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

    ###-- CYCLOMATIC COMPLEXITY --#############################################
    
    def print_functions_complexities(self):  # UTIL
        """## Print all the function name and his respective complexity"""
        headers = ["Function Name", "Cyclomatic Complexity", "Cognitive Complexity"]
        data = []
        for func_name in self.functions_complexities.keys():
            data.append([func_name, self.functions_complexities[func_name][0], self.functions_complexities[func_name][1]])
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

    #####-- VISIT NODE MODULES --##############################################

    def visit_Decl(self, node):           # Used for Halstead Volume
        """## Procedure called when a declaration is inicialized.
        This is necessary because pycparser library does not identify inicializations as a Assignment node."""
        if node.init is not None:
            self.operators.add('=')
            self.operator_count += 1
            self.visit(node.init)
        else:
            self.generic_visit(node)

    def visit_FuncDecl(self, node):
        self.current_function = node.type.declname
        if not (node.type.declname in self.functions_info):
            self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                        self.__get_func_return_type__(node),
                                                        0, 
                                                        []]
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

    def visit_FuncDef(self, node):        # Used for McCabe Complexity and Cognitive Complexity
        """## Procedure called when a FUNCTION DEFINITION node is find.
        When a function is visited, self.current_function is defined with the function name and the function is
        add in the dictionary. With function complexity is analysed separated.
        """
        self.current_function = node.decl.name  # Get the module name

        self.functions_complexities[self.current_function] = [0, 0]  # Initialize complexities dict

        if self.current_function in self.functions_info:
            self.functions_info[self.current_function][2] = self.__get_line__(node)
        else:
            self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                        self.__get_func_return_type__(node),
                                                        self.__get_line__(node), 
                                                        []]
            
        self.cyclomatic_complexity = 1          # Module cyclomatic complexity number
        self.generic_visit(node)                # Visit all the modules nodes
        self.total_cyclomatic_complexity += self.cyclomatic_complexity
        self.functions_complexities[self.current_function] = [self.cyclomatic_complexity, 0]

    def __get_line__(self, node):
        """Function to get line number of a node.
        Consider the distances in the 'file'_pre_limpo.c."""
        return int(str(node.coord).split(':')[1]) - 220

    def __get_func_parameters_type__(self, node):
        types = []
        try:                            # IF is a FuncDef
            args = node.decl.type.args
        except AttributeError:          # If is a FuncDecl
            args = node.args.params
        if args != None:
            for i in args:
                types.append(i.type.type.names[0])
        else:
            return None
        return types

    def __get_func_return_type__(self, node):
        try:
            return node.decl.type.type.type.names[0]
        except AttributeError:
            return node.type.type.names[0]

    def visit_FuncCall(self, node):
        """Registra chamadas de funções."""
        if node.name.name in self.functions_info:
            self.functions_info[node.name.name][3].append(self.__get_line__(node))
        self.generic_visit(node)

    def visit_If(self, node):             # Used for McCabe Complexity
        """## Procedure called when an IF node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1                                       # Cyclomatic Complexity
        self.generic_visit(node)

    def visit_For(self, node):            # Used for McCabe Complexity
        """## Procedure called when a FOR node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1                                        # Cyclomatic Complexity                                             # Cognitive Complexity
        self.generic_visit(node)

    def visit_While(self, node):          # Used for McCabe Complexity
        """## Procedure called when a WHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1                                          # Cyclomatic Complexity
        self.generic_visit(node)

    def visit_DoWhile(self, node):        # Used for McCabe Complexity
        """## Procedure called when a DoWHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1                                          # Cyclomatic Complexity
        self.generic_visit(node)

    def visit_Switch(self, node):         # Used for McCabe Complexity
        """## Procedure called when a SWITCH node is visited.
        *cyclomatic_complexity += (quantity of case statements)*
        """
        if node.stmt.block_items:
            self.cyclomatic_complexity += len(node.stmt.block_items) - 1
        self.generic_visit(node)


    # DEBUG
    def print_ast(self):
        ast = parse_file(self.file_clean, use_cpp=False)   # Create the AST using the pre-compiled and clean file.
        ast.show()                      # Show the AST with the coordnates



# OUT CLASS
def debuged_analysed(filename):
    visitor = ComplexityVisitor(filename)
    visitor.__debug_analyse__()

def show_tree(filename):
    visitor = ComplexityVisitor(filename)
    visitor.print_ast()

def compare(filename1, filename2):
    visitor1 = ComplexityVisitor(filename1)
    visitor2 = ComplexityVisitor(filename2)
    visitor1.analyse()
    visitor2.analyse()

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
            ["Level", visitor1.level, visitor2.level, (visitor2.level - visitor1.level)],
            ["Effort", visitor1.effort, visitor2.effort, (visitor2.effort - visitor1.effort)],
            ["Time required to program", visitor1.time_required, visitor2.time_required, (visitor2.time_required - visitor1.time_required)],
            ["Estimated number of bugs", visitor1.delivered_bugs, visitor2.delivered_bugs, (visitor2.delivered_bugs - visitor1.delivered_bugs)],
            ["Total cyclomatic complexity", visitor1.total_cyclomatic_complexity, visitor2.total_cyclomatic_complexity, (visitor2.total_cyclomatic_complexity - visitor1.total_cyclomatic_complexity)]
           ]
    print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

def individual_analyse(filename):
    visitor = ComplexityVisitor(filename)
    visitor.print_analyse()

if __name__ == "__main__":
    filename = "teste" 
    individual_analyse(filename)
    

