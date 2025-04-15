from typing import List, Tuple
from pycparser import parse_file, c_ast
from math import log2
from tabulate import tabulate

class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self, filename):
        ##########-- UTILS VARIABLES --########################################
        self.__DEBUG__: bool = False

        ##-- FILE --###########################################################
        self.filename   : str = filename                            # Raw filename
        self.file_dir   : str = "Examples"                          # Dir with the source file and the pre-compiled file
        self.file_path  : str = f"{self.file_dir}/{self.filename}"  # File path without sufix
        self.file_clean : str = f"{self.file_path}.i"               # Path to the pre-compiled file
        self.file_source: str = f"{self.file_path}.c"               # Path to the source code

        ##########-- CODE INFOS --#############################################
        self.functions_called  : set[str] = set()
        self.qtt_functions_call: int = 0

        # VARIABLE: functions_info -> Dict -> STRING: ARRAY
        #  Store functions information in array in order:
        #      * [0] STRING[] -> "Parameters type"
        #      * [1] STRING -> "Return type"
        #      * [2] INT -> Line of definition
        #      * [3] INT[] -> Lines of calls
        self.functions_info: dict[str, list[int | str]] = {}

        # VARIABLE: functions_complexities -> Dict -> STRING: ARRAY
        #  Store functions complexitites in a array with order:
        #      * [0] INT -> Cyclomatic Number
        #      * [1] INT -> Cognitive Number
        self.functions_complexities: dict[str, list[int]] = {}
        
        ##########-- LENGHT COMPLEXITY --######################################
        self.total_lines    : int = 0  # Total lines of code
        self.effective_lines: int = 0  # Total of effective lines of code

        ##########-- CYCLOMATIC COMPLEXITY --##################################
        self.cyclomatic_complexity      : int = 0   # Individual complexity.
        self.total_cyclomatic_complexity: int = 0   # Total McCabe.
        self.current_function           : str = ""  # Current visiting function.

        ##########-- HALSTEAD COMPLEXITY --####################################
        self.current_func_call: bool = False

        # Operators informations
        # OPERATOR -> ()
        # [0] -> Count of uses
        # [1] -> Lines used
        self.operators_info: dict[str, list[int]] = dict()
        self.operands      : set[str] = set()   

        # Operands informations
        # OPERAND -> {}
        # [0] -> Count of uses
        # [1] -> Lines used
        self.operands_info : dict[str, list[int]] = dict()
        self.n1            : float = 0  # Number of distinct operators (n1).
        self.n2            : float = 0  # Number of distinct operands (n2).
        self.N1            : float = 0  # Total number of operators (N1).
        self.N2            : float = 0  # Total number of operands (N2).
        self.vocabulary    : float = 0  # Program vocabulary (n).
        self.lenght        : float = 0  # Program lenght (N).
        self.estimated_len : float = 0  # Estimated program lenght (^N).
        self.volume        : float = 0  # Volume (V).
        self.difficulty    : float = 0  # Difficulty (D).
        self.level         : float = 0  # Program level of abstraction. (L)
        self.intelligence  : float = 0  # Intelligence Content. "Independet of language" (I)
        self.effort        : float = 0  # Effort (E).
        self.time_required : float = 0  # Time required to program (T).
        self.delivered_bugs: float = 0  # Estimated number of bugs (B).


        ##########-- COGNITIVE COMPLEXITY --###################################
        # cognitive_modifiers -> DICT
        # [0] -> STR | "Statement name"
        # [1] -> INT | Node coord
        # [2] -> INT | Cognitive Complexity modifiers
        self.cognitive_modifiers         : dict[str, list[str | int]] = dict() # Stores all the statements that add cognitive complexity
        self.current_statement           : str = ""          # The current statement
        self.current_statement_complexity: int = 0  # The current statement complexity
        self.total_cognitive_complexity  : int = 0    # Total cognitive complexity.
        self.current_depth               : int = 0                 # Actual deph level.
        self.weights                     : dict[str, int] = {                       # Weight of statements and structures (Based on the article):
            "declaration": 1,                  # "Code Complexity - A New Measure" de Jitender Kumar Chhabra. (ADAPTADO)
            "func_call": 1,
            "if": 2,
            "case": 3,
            "for": 4,
            "while": 3,
            "do while": 3,
            "recursion": 4,
            "constant": 1,
            "array": 2,
            "pointer": 3,
            "complex_pointer": 4
        }

        # Initializing function
        self.analyse()

    ###********************************************************************************************###
    ##                           FUNCTIONS                                                          ##
    ###********************************************************************************************###

    ###-- UTILS FUNCTIONS --###################################################

    def print_analyse(self) -> None:
        """
        Call the analyse function that parse the precompiled C code, make the AST, visit the nodes 
        and get the metric. After that, print the code complexity table.
        """
        self.analyse()             
        self.print_complexities()

    def analyse(self) -> None:
        """This function parse the precompiled C code, generates an Abstract Syntax Tree (AST),
        visit the nodes and get the metrics.

        Halstead Metrics and LOC complexity are called here, while Cyclomatic Complexity is
        obtained when the nodes are visited.
        """
        ast = parse_file(self.file_clean, use_cpp=False) 
        self.visit(ast)
        self.count_lines()
        self.calculate_halstead_metrics()
        
    def print_complexities(self):
        """Print the code complexity table, list of operands, operators and the functions complexities.

        (This function do not calculate the metrics and either generate the AST)
        """
        print(f"==================/ {self.filename} \\===================================")
        header = ["Complexity", "Value"]
        data = [["Total lines", self.total_lines],
                ["Effective lines", self.effective_lines],
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
                ["Content Intelligence", f"{self.intelligence}"],
                ["Effort", f"{self.effort:.1f}"],
                ["Required time to program", f"{self.time_required:.1f}"],
                ["Delivered bugs", f"{self.delivered_bugs:.1f}"],
                ["CYCLOMATIC COMPLEXITY"],
                ["Total Cyclomatic Complexity", self.total_cyclomatic_complexity],
                ["Cognitive Complexity"],
                ["Cognitive Complexity", self.total_cognitive_complexity],
                ]
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))
        
        self.print_functions_complexities()
        self.print_operators()
        self.print_operands()

    def print_operands(self) -> None:
        """Print the operands dictionary in a table format."""
        header = ["Operand", "Total uses", "Appeared line"]
        data = []
        for op in self.operands_info:
            data.append([op, len(self.operands_info[op]), self.operands_info[op]])
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

    def print_operators(self) -> None:
        """Print the operators dictionary in a table format."""
        header = ["Operator", "Total uses", "Used lines"]
        data = []
        for op in self.operators_info:
            data.append([op, len(self.operators_info[op]), self.operators_info[op]])
        print("\n")
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

    def print_ast(self) -> None:
        """Print the Abstract Syntax Tree using the pycparser ast.show function."""
        ast = parse_file(self.file_clean, use_cpp=False, )  
        ast.show(showcoord=False)

    def __debug_analyse__(self) -> None:
        """Make the anaylse using the DEBUG mode.
        DEBUG MODE print the nodes in the visit order.
        """
        self.__DEBUG__ = True
        ast = parse_file(self.file_clean, use_cpp=False)
        self.visit(ast)

    def print_lenght(self) -> None:
        """Print the code lenght complexity in a table format."""
        headers = ["CODE INFOS", "VALUE"]
        data = [["Effective lines", self.effective_lines],
                ["Total lines", self.total_lines]]
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

    def count_lines(self) -> None:
        """Count the total lines and the effective lines (non-empty, not comment
        and not only '{' or '}')."""
        with open(self.file_source) as file:
            lines = file.readlines()
            self.total_lines = len(lines)
            in_block_comment = False
            for line in lines:
                stripped_line = line.strip()
                
                # Stop block comments if in one.
                if in_block_comment:
                    # Found the end of the block comments.
                    if "*/" in stripped_line:
                        in_block_comment = False
                    continue
                
                # Remove one line block comments
                if stripped_line[:2] == "/*" and stripped_line[-2:] == "*/":
                    continue
                
                # Start a block comments.
                if "/*" in stripped_line:
                    in_block_comment = True
                    continue
                # Identify a one line commentary.
                if not stripped_line or stripped_line.startswith("//"):
                    continue
                # Identify lines with just '{' or '}'    
                if stripped_line == '{' or stripped_line == '}':
                    continue
                
                self.effective_lines += 1

    def calculate_halstead_metrics(self) -> None:
        """Procedure to calculate the Halstead metrics."""
        self.n1, self.N1 = self.__count_operators__()
        self.n2, self.N2 = self.__count_operands__()

        self.vocabulary     = self.n1 + self.n2                                  # Calculate vocabulary.
        self.lenght         = self.N1 + self.N2                                  # Calculate length.
        if self.vocabulary == 0:
            self.estimated_len  = 0
            self.volume         = 0
            self.difficulty     = 0
            self.level          = 0
            self.effort         = 0
            self.time_required  = 0
            self.delivered_bugs = 0
        else:
            self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
            self.volume         = self.lenght * log2(self.vocabulary)                # Calculate volume.
            self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)                # Calculate difficulty.
            self.level          = 1 / self.difficulty                                # Calculate program level.
            self.intelligence   = self.level * self.volume                           # Calculate program intelligence
            self.effort         = self.difficulty * self.volume                      # Calculate effort.
            self.time_required  = self.effort / 18                                   # Calculate time to program (seconds).
            self.delivered_bugs = self.effort ** (2 / 3) / 3000
            # Calculate number of delivered bugs.

    def print_halstead_volume(self) -> None:  
        """Print the Halstead metrics atributes.

        OBS: The function only
        print the atributes, no call the function to calculate them.
        """
        
        # Metric table
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
        self.print_operators(); 
        self.print_operands();

    def print_functions_complexities(self): 
        """Print all the function name and his respective cyclomatic and
        cognitive complexity."""
        print(f"=== {self.filename} ===")
        headers = ["Function Name", "Cyclomatic Complexity", "Cognitive Complexity"]
        data = []
        for func_name in self.functions_complexities.keys():
            data.append(
                [func_name, self.functions_complexities[func_name][0], self.functions_complexities[func_name][1]])
        print("\n")
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

    ###-- NODE UTILITIES --#######################################################
    def __count_operands__(self):
        distinct_operands = 0
        total_operands = 0
        for op in self.operands_info:
            distinct_operands += 1
            total_operands += len(self.operands_info[op])
        return distinct_operands, total_operands

    def __count_operators__(self) -> Tuple[int, int]:
        """Function to count the operators present in the code.
        """
        distinct_operators = 0
        total_operators = 0
        for op in self.operators_info:
            distinct_operators += 1
            total_operators += len(self.operators_info[op])
        return distinct_operators, total_operators

    def __add_operator__(self, node, node_op):
        """Function to add a operator and initialize the array of calls, or
        append the call."""
        # The ++ operator is named p++, so remove the p.
        if node_op == 'p++' or node_op == 'p--':
            node_op = node_op[1:] 

        if not node_op in self.operators_info.keys():
            self.operators_info[node_op] = [self.__get_line__(node)]
        else:
            self.operators_info[node_op].append(self.__get_line__(node))

    def get_node_value(self, node):
        """Function to get the inner value of a node.

        Respective output for node type:

        CONSTANT      : (int) constant value;
        ID            : (str) "{variable_name}";
        BinaryOperator: (str) "{node.left} {op} {node.right}";
        ArrayRef      : (str) "vector[index]";
        """
        if isinstance(node, c_ast.BinaryOp):
            return f"{self.get_node_value(node.left)} {node.op} {self.get_node_value(node.right)}"

        elif isinstance(node, c_ast.ArrayRef):
            vector_name = node.name.name
            vector_index = self.get_node_value(node.subscript)

            if type(vector_index) is tuple:
                return f"""{vector_name}[{vector_index[0]} {vector_index[1]} {vector_index[2]}]"""

            return f"{vector_name}[{vector_index}]"

        elif isinstance(node, c_ast.Constant):
            return node.value
        elif isinstance(node, c_ast.UnaryOp):
            return node.expr.name
        elif isinstance(node, c_ast.ID):
            return node.name

    def __add_node_operands__(self, node):
        node_name = node.__class__.__name__
        node_op = self.get_node_value(node)
        
        self.__add_operand_in_dict__(node, node_op)
        
    def __add_operand_in_dict__(self, node, operand):
        if not operand in self.operands_info.keys():
            self.operands_info[operand] = [self.__get_line__(node)]
        else:
            self.operands_info[operand].append(self.__get_line__(node))


    def __get_line__(self, node):
        """Function to return the node line in the 'file'_limpo_pre.c."""
        return int(str(node.coord).split(':')[1])

    def __get_func_parameters_type__(self, node) -> list[str] | None:
        types = []
        args = None
        try:  # IF is a FuncDef
            args = node.decl.type.args
        except AttributeError:  # If is a FuncDecl
            if node.args != None:
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

    def __get_func_return_type__(self, node) -> str | None:
        
        node_type = None
        
        if isinstance(node, c_ast.FuncDef):
            node_type = node.decl.type.type
        elif isinstance(node, c_ast.FuncDecl):
            node_type = node.type

        if isinstance(node_type, c_ast.TypeDecl):
            return node_type.type.names[0]
        elif isinstance(node_type, c_ast.PtrDecl):
            return node_type.type.type.names[0]

    def __add_statement_cog_c__(self, statement, node):
        """Add the statement cognitive complexity in the function."""
        cognitive_modifier = self.weights[statement] + self.current_statement_complexity # Statement Weight + Nested Weight
        
        if not (statement == "declaration" or statement == "func_call"):
            self.current_statement_complexity = self.weights[statement] + self.current_statement_complexity
        
        self.total_cognitive_complexity += cognitive_modifier
        self.functions_complexities[self.current_function][1] += cognitive_modifier

    def __verify_recursion__(self, func_name):
        if func_name == self.current_function:
            return True
        return False
        

    ###-- VISIT NODE MODULES --##################################################

    def visit_Assignment(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\nCOORD = {node.coord}\n{node}\n")
        else:
            self.__add_operator__(node, node.op)
            self.__add_statement_cog_c__("declaration", node)
            # Get assignment lvalue operand

            self.generic_visit(node)
    
    def visit_Decl(self, node):  
        """## Procedure called when a declaration is inicialized.
        This is necessary because pycparser library does not identify inicializations as a Assignment node."""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if node.init is not None:
                self.__add_operator__(node, '=')
                self.__add_node_operands__(node)
                self.__add_statement_cog_c__("declaration", node)
                self.visit(node.init)
            else:
                self.generic_visit(node)

    def visit_FuncDecl(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if isinstance(node.type, c_ast.PtrDecl):
                self.current_function = node.type.type.declname
            else:
                self.current_function = node.type.declname

            if not (self.current_function in self.functions_info):
                self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                              self.__get_func_return_type__(node),
                                                              0,
                                                              []]
        self.generic_visit(node)

    def visit_BinaryOp(self, node):
        """## Procedure called when a binary operator node is visited.
        Called when visit binary operations like +, -, *, /.
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:

            self.__add_operator__(node, node.op)
            self.generic_visit(node)

    def visit_UnaryOp(self, node):
        """## Procedure called when a unary operator node is visited.
        Visit unary operations like -, ++, --.
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, node.op)
            if (node.op == "*"):
                self.__add_statement_cog_c__("pointer", node)
            
            self.generic_visit(node)

    def visit_ID(self, node):
        if not self.current_func_call:
            self.__add_node_operands__(node)

    def visit_Constant(self, node):
        """## Procedure called when a constant/literal node is visited.
        Visit constants (literals).
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_node_operands__(node)

    def visit_FuncDef(self, node):
        """## Procedure called when a FUNCTION DEFINITION node is find.
        When a function is visited, self.current_function is defined with the function name and the function is
        add in the dictionary. With function complexity is analysed separated.
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.current_function = node.decl.name
            
            self.functions_complexities[self.current_function] = [0, 0]

            if self.current_function in self.functions_info:
                self.functions_info[self.current_function][2] = self.__get_line__(node)
            else:
                self.functions_info[self.current_function] = [self.__get_func_parameters_type__(node),
                                                              self.__get_func_return_type__(node),
                                                              self.__get_line__(node),
                                                              []]

            self.cyclomatic_complexity = 1
            self.generic_visit(node)  
            self.total_cyclomatic_complexity += self.cyclomatic_complexity
            self.functions_complexities[self.current_function][0] = self.cyclomatic_complexity

    def visit_FuncCall(self, node):
        """Registra chamadas de funções."""
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.functions_called.add(node.name.name)
            self.qtt_functions_call += 1

            if node.name.name in self.functions_info:
                self.functions_info[node.name.name][3].append(self.__get_line__(node))
            self.__add_operator__(node, node.name.name)
            
            if not node.args is None:
                for param in node.args:
                    if not isinstance(param, c_ast.Constant):
                        param = self.get_node_value(param)
                
                        self.__add_operand_in_dict__(node, param)

            if (self.__verify_recursion__(node.name.name)):
                self.__add_statement_cog_c__("recursion", node)
            else:
                self.__add_statement_cog_c__("func_call", node)

            self.current_func_call = True
            self.generic_visit(node)
            self.current_func_call = False

    def visit_If(self, node):
        """## Procedure called when an IF node is visited.
        *cyclomatic_complexity += 1*
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1
            
            statement = 'if'
            
            self.__add_operator__(node, statement)
            
            self.__add_statement_cog_c__(statement, node)
            
            self.generic_visit(node)
    
            self.current_statement_complexity = 0
        
    def visit_For(self, node):
        """## Procedure called when a FOR node is visited.
        *cyclomatic_complexity += 1*
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1 
            
            statement = 'for'
            
            self.__add_operator__(node, statement)
            self.__add_statement_cog_c__(statement, node)
            
            self.generic_visit(node)
            self.current_statement_complexity = 0
            
    def visit_While(self, node):
        """## Procedure called when a WHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1  # Cyclomatic Complexity
            
            statement = 'while'
            
            self.__add_operator__(node, statement)
            
            self.__add_statement_cog_c__(statement, node)
                
            self.generic_visit(node)
            self.current_statement_complexity = 0

    def visit_DoWhile(self, node):
        """## Procedure called when a DoWHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.cyclomatic_complexity += 1
            
            statement = 'do while'
            
            self.__add_operator__(node, statement)
            
            self.__add_statement_cog_c__(statement, node)
                
            self.generic_visit(node)
            self.current_statement_complexity = 0

    def visit_Switch(self, node):
        """## Procedure called when a SWITCH node is visited.
        *cyclomatic_complexity += (quantity of case statements)*
        """
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            if node.stmt.block_items:
                self.cyclomatic_complexity += len(node.stmt.block_items)
            self.generic_visit(node)

    def visit_Case(self, node):
        if self.__DEBUG__:
            print(f"=============================================================\n{node}")
        else:
            self.__add_operator__(node, 'case')
            
            statement = 'case'
            
            self.__add_statement_cog_c__(statement, node)
            
            self.generic_visit(node)
            self.current_statement_complexity = 0
    
    def visit_ArrayRef(self, node):
        self.current_operator = True

        self.__add_operator__(node, '[]')
        self.__add_node_operands__(node)

        self.generic_visit(node)
        self.current_operator = False

    # ==== PROGRAM EXECUTION =====================
    def debuged_analyse(self):
        visitor = ComplexityVisitor(self.filename)
        visitor.__debug_analyse__()


    def show_tree(self):
        self.print_ast()

    def compare(self, filename2: str):
        self.calculate_halstead_metrics()
        visitor2 = ComplexityVisitor(filename2)
        visitor2.analyse()

        headers = ["Metric", f"{self.filename}", f"{filename2}", f"{filename2} has"]
        data = [["Total lines", self.total_lines, visitor2.total_lines, (visitor2.total_lines - self.total_lines)],
                ["Effective lines", self.effective_lines, visitor2.effective_lines,
                (visitor2.effective_lines - self.effective_lines)],
                ["Count of distinct operators", self.n1, visitor2.n1,
                 (visitor2.n1 - self.n1)],
                ["Count of distinct operands", self.n2, visitor2.n2,
                 (visitor2.n2 - self.n2)],
                ["Total operators", self.N1, visitor2.N1, (visitor2.N1 - self.N1)],
                ["Total operands", self.N2, visitor2.N2, (visitor2.N2 - self.N2)],
                ["Program vocabulary", self.vocabulary, visitor2.vocabulary,
                 (visitor2.vocabulary - self.vocabulary)],
                ["Program lenght", f"{self.lenght:.2f}", f"{visitor2.lenght:.2f}",
                 f"{(visitor2.lenght - self.lenght):.2f}"],
                ["Estimated program length", f"{self.estimated_len:.2f}", f"{visitor2.estimated_len:.2f}",
                 f"{(visitor2.estimated_len - self.estimated_len):.2f}"],
                ["Volume", f"{self.volume:.2f}", f"{visitor2.volume:.2f}",
                 f"{(visitor2.volume - self.volume):.2f}"],
                ["Difficulty", f"{self.difficulty:.2f}", f"{visitor2.difficulty:.2f}",
                 f"{(visitor2.difficulty - self.difficulty):.2f}"],
                ["Level", f"{self.level:.2f}", f"{visitor2.level:.2f}", f"{(visitor2.level - self.level):.2f}"],
                ["Intelligence", f"{self.intelligence}",
                 f"{visitor2.intelligence}", f"{(visitor2.intelligence -
                 self.intelligence)}"],
                ["Effort", f"{self.effort:.2f}", f"{visitor2.effort:.2f}",
                 f"{(visitor2.effort - self.effort):.2f}"],
                ["Time required to program", f"{self.time_required:.2f}", f"{visitor2.time_required:.2f}",
                 f"{(visitor2.time_required - self.time_required):.2f}"],
                ["Estimated number of bugs", f"{self.delivered_bugs:.2f}", f"{visitor2.delivered_bugs:.2f}",
                 f"{(visitor2.delivered_bugs - self.delivered_bugs):.2f}"],
                ["Total cyclomatic complexity", self.total_cyclomatic_complexity, visitor2.total_cyclomatic_complexity,
                 (visitor2.total_cyclomatic_complexity -
                  self.total_cyclomatic_complexity)],
                ["Total Cognitive Complexity", self.total_cognitive_complexity,
                 visitor2.total_cognitive_complexity,
                 (visitor2.total_cognitive_complexity -
                  self.total_cognitive_complexity)]
                ]
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))
        print("\n\n")
        self.print_functions_complexities()
        print("\n")
        visitor2.print_functions_complexities()

if __name__ == "__main__":
    codigo_1 = ComplexityVisitor("codigo_1")
    codigo_1.print_complexities()
