from pycparser import parse_file, c_ast
from math import log2
from tabulate import tabulate


class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self, filename):
        ##########-- UTILS VARIABLES --########################################
        self.__DEBUG__ = False

        ##-- FILE --##
        self.filename = filename                             # Raw filename
        self.file_dir = "Examples"                           # Dir with the source file and the pre-compiled file
        self.file_path = f"{self.file_dir}/{self.filename}"  # File path without sufix
        self.file_clean = f"{self.file_path}_limpo_pre.c"    # Path to the pre-compiled file
        self.file_source = f"{self.file_path}.c"             # Path to the source code

        ##########-- CODE INFOS --#############################################

        # VARIABLE: functions_info -> Dict -> STRING: ARRAY
        #  Store functions information in array in order:
        #      * [0] STRING[] -> "Parameters type"
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
        self.cyclomatic_complexity = 0            # Individual complexity.
        self.total_cyclomatic_complexity = 0      # Total McCabe.
        # self.functions_complexities[]           # Store the CC in...
        self.current_function = None  # Current visiting function.

        ##########-- HALSTEAD COMPLEXITY --####################################

        # Operators informations
        # OPERATOR -> ()
        # [0] -> Count of uses
        # [1] -> Lines used
        self.operators_info = dict()
        self.operands = set()    # Set of operands.

        # Operands informations
        # OPERAND -> {}
        # [0] -> Count of uses
        # [1] -> Lines used
        self.operands_info = dict()
        self.n1 = 0              # Number of distinct operators (n1).
        self.n2 = 0              # Number of distinct operands (n2).
        self.N1 = 0              # Total number of operators (N1).
        self.N2 = 0              # Total number of operands (N2).
        self.vocabulary = 0      # Program vocabulary (n).
        self.lenght = 0          # Program lenght (N).
        self.estimated_len = 0   # Estimated program lenght (^N).
        self.volume = 0          # Volume (V).
        self.difficulty = 0      # Difficulty (D).
        self.level = 0           # Program level of abstraction.
        self.inteligence = 0     # Intelligence Content. "Independet of language"
        self.effort = 0          # Effort (E).
        self.time_required = 0   # Time required to program (T).
        self.delivered_bugs = 0  # Estimated number of bugs (errors).

        ##########-- COGNITIVE COMPLEXITY --###################################
        self.current_statement = None        # The current statement
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

    ###********************************************************************************************###
    ##                           FUNCTIONS                                   																 ##
    ###********************************************************************************************###

    ###-- UTILS FUNCTIONS --###################################################

    def print_analyse(self):
        """## Main function of the class. Call all the complexity functions and print the results."""
        ast = parse_file(self.file_clean, use_cpp=False)  # Create the AST using the pre-compiled and clean file.
        self.visit(ast)
        self.count_lines()
        self.calculate_halstead_volume()  # Halstead Volume - Calculate the Halstead Volume.
        self.print_complexities()

    def analyse(self):
        """## Main function of the class. Call all the complexity calculate functions."""
        ast = parse_file(self.file_clean, use_cpp=False)  # Create the AST using the pre-compiled and clean file.
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
        print(tabulate(data, headers=header, tablefmt="grid", numalign="right"))
        self.print_functions_complexities()
        self.print_operators()
        self.print_operands()

    def print_operands(self):
        header = ["Operand", "Total uses", "Used lines"]
        data = []
        for op in self.operands_info:
            data.append([op, len(self.operands_info[op]), self.operands_info[op]])
        print("\n")
        print(tabulate(data, headers=header, tablefmt="grid", numalign="right"))

    def print_operators(self):
        header = ["Operator", "Total uses", "Used lines"]
        data = []
        for op in self.operators_info:
            data.append([op, len(self.operators_info[op]), self.operators_info[op]])
        print("\n")
        print(tabulate(data, headers=header, tablefmt="grid", numalign="right"))


    def __debug_analyse__(self):
        self.__DEBUG__ = True
        ast = parse_file(self.file_clean, use_cpp=False)
        self.visit(ast)

    ###-- COGNITIVE COMPLEXITY --###############################################
    """
		ITS A SIMPLE VERSION OF THE COGNITIVE COMPLEXITY.
	"""

    ###-- CODE LENGHT --########################################################
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

    ###-- HALSTEAD COMPLEXITY --################################################

    def calculate_halstead_volume(self):  # Used for Halstead Volume
        """## Procedure to calculate the Halstead volume.
		"""
        self.n1, self.N1 = self.__count_operators__()
        self.n2, self.N2 = self.__count_operands__()

        self.vocabulary = self.n1 + self.n2  # Calculate vocabulary.
        self.lenght = self.N1 + self.N2  # Calculate length.
        self.estimated_len = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
        self.volume = self.lenght * log2(self.vocabulary)  # Calculate volume.
        self.difficulty = (self.n1 / 2) * (self.N2 / self.n2)  # Calculate difficulty.
        self.level = 1 / self.difficulty  # Calculate program level.
        self.effort = self.difficulty * self.volume  # Calculate effort.
        self.time_required = self.effort / 18  # Calculate time to program (seconds).
        self.delivered_bugs = self.effort ** (2 / 3) / 3000  # Calculate number of delivered bugs.

    def print_halstead_volume(self):  # Used for Halstead Volume
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

    ###-- CYCLOMATIC COMPLEXITY --#############################################

    def print_functions_complexities(self):  # UTIL
        """## Print all the function name and his respective complexity"""
        headers = ["Function Name", "Cyclomatic Complexity", "Cognitive Complexity"]
        data = []
        for func_name in self.functions_complexities.keys():
            data.append(
                [func_name, self.functions_complexities[func_name][0], self.functions_complexities[func_name][1]])
        print("\n")
        print(tabulate(data, headers=headers, tablefmt="grid", numalign="right"))

    ###-- VISIT NODE MODULES --################################################
    def __count_operands__(self):
        distinct_operands = 0
        total_operands = 0
        for op in self.operands_info:
            distinct_operands += 1
            total_operands += len(self.operands_info[op])
        return distinct_operands, total_operands

    def __count_operators__(self):
        distinct_operators = 0
        total_operators = 0
        for op in self.operators_info:
            distinct_operators += 1
            total_operators += len(self.operators_info[op])
        return distinct_operators, total_operators

    def __add_operator__(self, node, node_op):
        """Function to add a operator and initialize the array of calls, or
        append the call."""
        if not node_op in self.operators_info.keys():
            self.operators_info[node_op] = [self.__get_line__(node)]
        else:
            self.operators_info[node_op].append(self.__get_line__(node))

    def __add_node_operands__(self, node):
        node_name = node.__class__.__name__
        node_op = None

        match node_name:
            case "ID":
                node_op = node.name
            case "ArrayRef":
                node_op = node.lvalue.name.name
            case "Constant":
                node_op = node.value

        if not node_op in self.operands_info.keys():
            self.operands_info[node_op] = [self.__get_line__(node)]
        else:
            self.operands_info[node_op].append(self.__get_line__(node))

    def visit_Assignment(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, node.op)
            self.__add_node_operands__(node)
            # Get assignment lvalue operand

            self.generic_visit(node)

    def visit_Decl(self, node):  # Used for Halstead Volume
        """## Procedure called when a declaration is inicialized.
		This is necessary because pycparser library does not identify inicializations as a Assignment node."""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if node.init is not None:
                self.__add_operator__(node, '=')
                self.visit(node.init)
            else:
                self.generic_visit(node)

    def visit_FuncDecl(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.current_function = node.type.declname
            if not (node.type.declname in self.functions_info):
                self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                              self.__get_func_return_type__(node),
                                                              0,
                                                              []]
        self.generic_visit(node)

    def visit_BinaryOp(self, node):  # Used for Halstead Volume
        """## Procedure called when a binary operator node is visited.
		Called when visit binary operations like +, -, *, /.
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, node.op)
            self.generic_visit(node)

    def visit_UnaryOp(self, node):  # Used for Halstead Volume
        """## Procedure called when a unary operator node is visited.
		Visit unary operations like -, ++, --.
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, node.op)
            self.generic_visit(node)

    def visit_ID(self, node):
        self.__add_node_operands__(node)

    def visit_Constant(self, node):  # Used for Halstead Volume

        """## Procedure called when a constant/literal node is visited.
		Visit constants (literals).
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_node_operands__(node)

    def visit_FuncDef(self, node):  # Used for McCabe Complexity and Cognitive Complexity
        """## Procedure called when a FUNCTION DEFINITION node is find.
		When a function is visited, self.current_function is defined with the function name and the function is
		add in the dictionary. With function complexity is analysed separated.
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.current_function = node.decl.name  # Get the module name

            self.functions_complexities[self.current_function] = [0, 0]  # Initialize complexities dict

            if self.current_function in self.functions_info:
                self.functions_info[self.current_function][2] = self.__get_line__(node)
            else:
                self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                              self.__get_func_return_type__(node),
                                                              self.__get_line__(node),
                                                              []]

            self.cyclomatic_complexity = 1  # Module cyclomatic complexity number
            self.generic_visit(node)  # Visit all the modules nodes
            self.total_cyclomatic_complexity += self.cyclomatic_complexity
            self.functions_complexities[self.current_function] = [self.cyclomatic_complexity, 0]

    def __get_line__(self, node):
        """Function to return the node line in the 'file'_limpo_pre.c."""
        return int(str(node.coord).split(':')[1])

    def __get_func_parameters_type__(self, node):
        types = []
        try:  # IF is a FuncDef=
            args = node.decl.type.args
        except AttributeError:  # If is a FuncDecl
            args = node.args.params
        if args != None:
            for i in args:
                try:
                    types.append(i.type.type.names[0])
                except AttributeError:
                    types.append(i.type.type.type.names[0])

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
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if node.name.name in self.functions_info:
                self.functions_info[node.name.name][3].append(self.__get_line__(node))
            self.__add_operator__(node, node.name.name)
            self.generic_visit(node)

    def visit_If(self, node):  # Used for McCabe Complexity
        """## Procedure called when an IF node is visited.
		*cyclomatic_complexity += 1*
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1  # Cyclomatic Complexity
            self.__add_operator__(node, 'if')
            self.generic_visit(node)

    def visit_For(self, node):  # Used for McCabe Complexity
        """## Procedure called when a FOR node is visited.
		*cyclomatic_complexity += 1*
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1  # Cyclomatic Complexity                                             # Cognitive Complexity
            self.__add_operator__(node, 'for')
            self.generic_visit(node)

    def visit_While(self, node):  # Used for McCabe Complexity
        """## Procedure called when a WHILE node is visited.
		*cyclomatic_complexity += 1*
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1  # Cyclomatic Complexity
            self.__add_operator__(node, 'while')

            self.generic_visit(node)

    def visit_DoWhile(self, node):
        # Used for McCabe Complexity
        """## Procedure called when a DoWHILE node is visited.
		*cyclomatic_complexity += 1*
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1
            self.__add_operator__(node, 'do while')
            self.generic_visit(node)  # FFFFFF

    def visit_Switch(self, node):  # Used for McCabe Complexity
        """## Procedure called when a SWITCH node is visited.
		*cyclomatic_complexity += (quantity of case statements)*
		"""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if node.stmt.block_items:
                self.cyclomatic_complexity += len(node.stmt.block_items) - 1
            self.generic_visit(node)

    def visit_Case(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, 'case')

        # DEBUG

    def print_ast(self):
        ast = parse_file(self.file_clean, use_cpp=False, )  # Create the AST using the pre-compiled and clean file.
        ast.show(showcoord=True)  # Show the AST with the coordnates


###-- OUT CLASS --#########################################################
def debuged_analyse(filename):
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

    headers = ["Metric", f"{filename1[:6]}", f"{filename2[:6]}", f"{filename2[:6]} - {filename1[:6]}"]
    data = [["Total lines", visitor1.total_lines, visitor2.total_lines, (visitor2.total_lines - visitor1.total_lines)],
            ["Effective lines", visitor1.effective_lines, visitor2.effective_lines,
             (visitor2.effective_lines - visitor1.effective_lines)],
            ["Operator count", visitor1.operator_count, visitor2.operator_count,
             (visitor2.operator_count - visitor1.operator_count)],
            ["Operand count", visitor1.operand_count, visitor2.operand_count,
             (visitor2.operand_count - visitor1.operand_count)],
            ["Count of distinct operators", visitor1.n1, visitor2.n1, (visitor2.n1 - visitor1.n1)],
            ["Count of distinct operands", visitor1.n2, visitor2.n2, (visitor2.n2 - visitor1.n2)],
            ["Program vocabulary", visitor1.vocabulary, visitor2.vocabulary,
             (visitor2.vocabulary - visitor1.vocabulary)],
            ["Program lenght", f"{visitor1.lenght:.2f}", f"{visitor2.lenght:.2f}",
             f"{(visitor2.lenght - visitor1.lenght):.2f}"],
            ["Estimated program lenght", f"{visitor1.estimated_len:.2f}", f"{visitor2.estimated_len:.2f}",
             f"{(visitor2.estimated_len - visitor1.estimated_len):.2f}"],
            ["Volume", f"{visitor1.volume:.2f}", f"{visitor2.volume:.2f}",
             f"{(visitor2.volume - visitor1.volume):.2f}"],
            ["Difficulty", f"{visitor1.difficulty:.2f}", f"{visitor2.difficulty:.2f}",
             f"{(visitor2.difficulty - visitor1.difficulty):.2f}"],
            ["Level", f"{visitor1.level:.2f}", f"{visitor2.level:.2f}", f"{(visitor2.level - visitor1.level):.2f}"],
            ["Effort", f"{visitor1.effort:.2f}", f"{visitor2.effort:.2f}",
             f"{(visitor2.effort - visitor1.effort):.2f}"],
            ["Time required to program", f"{visitor1.time_required:.2f}", f"{visitor2.time_required:.2f}",
             f"{(visitor2.time_required - visitor1.time_required):.2f}"],
            ["Estimated number of bugs", f"{visitor1.delivered_bugs:.2f}", f"{visitor2.delivered_bugs:.2f}",
             f"{(visitor2.delivered_bugs - visitor1.delivered_bugs):.2f}"],
            ["Total cyclomatic complexity", visitor1.total_cyclomatic_complexity, visitor2.total_cyclomatic_complexity,
             (visitor2.total_cyclomatic_complexity - visitor1.total_cyclomatic_complexity)]
            ]
    print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))
    visitor1.print_functions_complexities()
    visitor2.print_functions_complexities()


def individual_analyse(filename):
    visitor = ComplexityVisitor(filename)
    visitor.print_analyse()


if __name__ == "__main__":
    filename = "teste"
    filename4 = "abrantesasf@computacaoraiz.com.br_1_credit"
    filename2 = "lucaslucklux@gmail.com_4_credit"
    filename3 = "augustolm06@gmail.com_4_credit"
    # show_tree(filename)
    # compare(filename, filename2)
    # debuged_analyse(filename)
    individual_analyse(filename)
