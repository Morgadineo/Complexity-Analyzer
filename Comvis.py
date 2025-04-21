from ast import operator, parse
from typing    import List, Tuple
from pycparser import parse_file, c_ast
from math      import log2
from tabulate  import tabulate

class ParsedCode(c_ast.NodeVisitor):
    """docstring for ParsedCode class"""
    def __init__(self, filename: str) -> None:
        """
        :param filename: Name of the file to be analyzed, without extension. 
        """

        #--> File <-- #########################################################
        self.filename: str = filename                               # Raw file name
        self.file_dir   : str = "Examples"                          # Dir with the source file and the pre-compiled file
        self.file_path  : str = f"{self.file_dir}/{self.filename}"  # File path without sufix
        self.file_clean : str = f"{self.file_path}.i"               # Path to the pre-compiled file
        self.file_source: str = f"{self.file_path}.c"               # Path to the source code

        #--> Global states <-- ################################################
        self.actual_binary_operator: str = ""

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
        self.distict_func_calls: set[str] = set()

        # |> Halstead Metrics <| #
        self.n1            : int   = 0  # Number of distinct operators (n1).
        self.n2            : int   = 0  # Number of distinct operands (n2).
        self.N1            : int   = 0  # Total number of operators (N1).
        self.N2            : int   = 0  # Total number of operands (N2).
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


        #--> Iniciation <-- ###################################################
        self.ast: c_ast.FileAST = parse_file(self.file_clean, use_cpp=False)
        self.visit(self.ast)

##=== ===|> Methods <|=== === #################################################

    ## ==> Auxiliar methods <== ###########################################

    def show_tree(self) -> None:
        """
        Show the Abstract Syntax Tree.
        """

        self.ast.show(showcoord = True)

    def print_operators(self):
        """
        Print the operators dictionary
        """
        for operator in self.operators.keys():
            print(f"{operator}: {self.operators[operator]}")


    def print_operands(self):
        """
        Print the operand dictionary
        """
        for operand in self.operands.keys():
            print(f"{operand}: {self.operands[operand]}")

    def append_operator(self, node: c_ast.Node) -> int:
        """
        Extract the operator from a node and adds the operator and its 
        ocurrence line to the operator dictionary.

        The operator dictionary stores the operator as the key and a list of
        the ocurrence lines as the key.

        :returns: 1 if is a valid node for a operator.
                  0 if is not a valid node.

        """
        valid_nodes: list[str] = ["BinaryOp", "UnaryOp", "TypeDecl"]

        if self.get_node_type(node) in valid_nodes:
            operator: str = self.get_node_value(node)
            line    : int = self.get_node_line(node)

            if self.get_node_type(node) == "TypeDecl":
                operator = "="

            if operator in self.operators.keys():
                self.operators[operator].append(line)
            else:
                self.operators.update({operator: [line]})
            return 1
        return 0

    def append_operand(self, node: c_ast.Node) -> int:
        """
        Extract the operand from a node an adds the operand and its occurrence 
        line to the operand dictionary.

        Only Constant, ID, TypeDecl nodes can have a operand.

        The operand dictionary stores the operand as the key and a list of the 
        occurrence lines of the operator as the key.

        :returns: 1 if is a valid node for a operand.
                  0 if is not a valid node.
        """
        valid_nodes: list[str] = ["Constant", "ID", "TypeDecl", "FuncCall"]

        if self.get_node_type(node) in valid_nodes:
            operand: str = self.get_node_value(node)
            line   : int = self.get_node_line(node)

            if operand in self.operands.keys(): # Only append the line ocurrency.
                self.operands[operand].append(line)
            else:
                self.operands.update({operand: [line]}) # Create a register.

            return 1
        
        return 0

    def count_dict_values(self, dict: dict[str, list[int]]) -> int:
        """
        Count the number of values present in the operands and operators dictionary.

        :param dict: A dict with a list with int as values.

        :return: The total len of values in every register.
        """
        total = 0
        for value in dict.values():
            total += len(value)
        
        return total

    def calculate_halstead_metrics(self) -> None:
        """
        Procedure to calculate the Halstead metrics.
        """

        self.n1: int = len(self.operators.keys())
        self.n2: int = len(self.operands.keys())
        self.N1: int = self.count_dict_values(self.operators)
        self.N2: int = self.count_dict_values(self.operands)

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
            self.delivered_bugs = self.effort ** (2 / 3) / 3000                      # Calculate number of delivered bugs.


    ## ==> Visit nodes <== ################################################

    def visit_Decl(self, node: c_ast.Node) -> None:
        """
        This function is called when a Declaration node is visited.

        :param node: A c_ast node type.
        """
        
        # |> As variable DECLaration
        if node.init is not None:
            self.append_operator(node.type)
            self.append_operand(node.init)
            self.append_operand(node.type)

        self.generic_visit(node)

    def visit_UnaryOp(self, node: c_ast.Node) -> None:
        """
        This function is called when a binary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node)

        self.generic_visit(node)

    def visit_BinaryOp(self, node: c_ast.Node) -> None:
        """
        This function is called when a binary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node)

        self.generic_visit(node)


    def visit_Constant(self, node: c_ast.Node) -> None:
        """
        This function is called when a constant node is visited.
        A constant node, is a node that represent a constant value, as a string or literal
        
        :param node: A c_ast node type.

        """
        
        # |=> Constant as operand:
        self.append_operand(node)

        self.generic_visit(node)

    def visit_FuncCall(self, node: c_ast.Node) -> None:
        """
        This function is called when a function_call node is visited.

        What he does:
            * add the function name in the distinct funcs call set.
            * do generic visit for the rest nodes.

        """
        self.distict_func_calls.add(self.get_node_value(node))

        self.generic_visit(node)

    def visit_ID(self, node: c_ast.Node) -> None:
        """
        This function is called when a ID node is visited.
        A identifier (ID) can be the name of a function or a variable.

        What he does:
            * Verify if is a func_call, if not, add has a operand.
            * visit node

        """
        # |=> As operand:
        if not self.get_node_value(node) in self.distict_func_calls:
            self.append_operand(node)

        self.generic_visit(node)

## ==>  Utils Node Methods <==#############################################
    def get_node_line(self, node: c_ast.Node) -> int:
        """
        Get the node line of occurrency.

        :param node: The node.

        :return: The line of ocurrecy.
        """
        brute_coord : str       = str(node.coord)
        sliced_coord: list[str] = brute_coord.split(":") 

        #-> Infos <-#
        line_coord   : int = int(sliced_coord[1])
        # collumn_coord: int = int(sliced_coord[2])

        return line_coord

    def get_node_type(self, node: c_ast.Node) -> str:
        """
        Get the node type.

        :param node: Node to be analyzed

        :return: A string withe the node type.
        """
        return node.__class__.__name__


    def get_node_value(self, node: c_ast.Node) -> str:
        """Get the node object name.
        Example: The object name of a FuncCall node, is the function 
        called name.

        :param node: The node that the name will be extracted.

        :return: A string with the node name.
        """

        match(self.get_node_type(node)):

            case "FuncCall":
                return node.name.name

            case "ID":
                return node.name

            case "Constant":
                return node.value

            case "UnaryOp":
                return node.op

            case "TypeDecl":
                return node.declname

            case "BinaryOp":
                return node.op
            
            case "FuncCall":
                return node.name
            case _:
                raise ValueError("Not Defined Yet")

if __name__ == "__main__":
    code = "codigo_1"

    code = ParsedCode(code)
    code.print_operators()
    print("\n\n")
    code.print_operands()
