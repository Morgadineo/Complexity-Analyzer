from ast import operator, parse
from os import linesep, sep
from typing    import Any, List, Tuple
from pycparser import parse_file, c_ast
from math      import dist, log2
from tabulate  import simple_separated_format, tabulate

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
        self.current_node: str | None = None
        self.current_func: str | None = None  

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
        self.operators         : dict[str, list[int]]      = dict()
        self.distict_func_calls: set[str]                  = set()
        self.functions         : dict[str, dict[str, int]] = dict()

        #--> Metrics <-- ######################################################
        #==> Ciclomatic Complexity <==#
        self.total_mcc: int = 0 # Total McCabe Complexity

        #==> Number of lines <==#
        self.total_lines    : int = 0
        self.effective_lines: int = 0

        #==> Halstead Metric <==#
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

        #--> Iniciation <-- ###################################################
        self.ast: c_ast.FileAST = parse_file(self.file_clean, use_cpp=False)
        self.visit(self.ast)

        #==> Calculate Metrics <==#
        self.count_lines()
        self.calculate_halstead()


##=== ===|> Methods <|=== === #################################################

    ## ==> Metric methods <== #############################################
    def count_lines(self) -> None:
        """
        Count the total lines and the effective lines (non-empty, not comment
        and not only '{' or '}').

        Store the total number of lines and effective in self.total_lines and self.effective_lines.
        """
        with open(self.file_source) as file:
            lines            = file.readlines()
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

    def calculate_halstead(self) -> None:
        """
        Calculate the Maurice Halstead metrics.

        This method has to be called after the visit of the ast.
        """
        self.n1, self.N1    = self.count_operators()
        self.n2, self.N2    = self.count_operands()
        self.vocabulary     = self.n1 + self.n2                    # Calculate vocabulary.
        self.lenght         = self.N1 + self.N2                    # Calculate length.
        self.volume         = self.lenght * log2(self.vocabulary)  # Calculate volume.
        self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)  # Calculate difficulty.
        self.level          = 1 / self.difficulty                  # Calculate program level.
        self.intelligence   = self.level * self.volume             # Calculate program intelligence
        self.effort         = self.difficulty * self.volume        # Calculate effort.
        self.time_required  = self.effort / 18                     # Calculate time to program (seconds).
        self.delivered_bugs = self.effort ** (2 / 3) / 3000        # Calculate number of delivered bugs.
    
    def add_McComplexity(self) -> None:
        """
        Add 1 to total ciclomatic complexity and 1 for the current function
        ciclomatic complexity.

        The add 1 to total ciclomatic complexity is needed when a function
        is initialized, because every block has at least one path.

        """
        if self.current_func != None:
            self.total_mcc += 1
            self.functions[self.current_func]["McC"] += 1

    ## ==> Auxiliar methods <== ###############################################
    def print_complexities(self):
        """Print the code complexity table, list of operands, operators and the functions complexities.

        (This function do not calculate the metrics and either generate the AST)
        """
        print(f"==================/ {self.filename} \\===================================")
        header = ["Complexity"                  , "Value"]
        data   = [["Total lines"                , self.total_lines],
                  ["Effective lines"            , self.effective_lines],
                  ["Distinct Operators (n1)"    , self.n1],
                  ["Distinct Operands (n2)"     , self.n2],
                  ["Total Operators (N1)"       , self.N1],
                  ["Total Operands (N2)"        , self.N2],
                  ["Program vocabulary"         , self.vocabulary],
                  ["Program Lenght"             , self.lenght],
                  ["Estimated Length"           , f"{self.estimated_len:.1f}"],
                  ["Volume"                     , f"{self.volume:.1f}"],
                  ["Difficulty"                 , f"{self.difficulty:.1f}"],
                  ["Program level"              , f"{self.level:.1f}"],
                  ["Content Intelligence"       , f"{self.intelligence}"],
                  ["Effort"                     , f"{self.effort:.1f}"],
                  ["Required time to program"   , f"{self.time_required:.1f}"],
                  ["Delivered bugs"             , f"{self.delivered_bugs:.1f}"],
                  ["CYCLOMATIC COMPLEXITY"]     ,
                  ["Total Cyclomatic Complexity", self.total_mcc],
                  ]
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))
        
        self.print_operators()
        self.print_operands()

    def count_operators(self) -> tuple[int, int]:
        """
        Method to count the number of distinct operators and total operators.

        This method return a ordenered pair with [0] the number of distinct operators e [1] the total number of operators.
        """
        total_operators   : int = 0
        distinct_operators: int = 0

        for operator in self.operators.keys():
            distinct_operators += 1
            total_operators    += len(self.operators[operator])

        return (distinct_operators, total_operators)

    def count_operands(self) -> tuple[int, int]:
        """
        Method to count the number of distinct operands and total operands.

        This method return a ordenered pair with [0] the number of distinct operators e [1] the total number of operands.
        """
        total_operands   : int = 0
        distinct_operands: int = 0

        for operand in self.operands.keys():
            distinct_operands += 1
            total_operands    += len(self.operands[operand])

        return (distinct_operands, total_operands)

    def initialize_function(self, node: c_ast.FuncDef) -> None:
        """
        Method to initialize a function in the functions dictionary.

        :param node: A FuncDef node that contains the node.
        """
        #--> Functions Metrics 
        functions_info: list[str] = ["McC"]  

        func_name: str = self.get_node_value(node)
        self.functions.update({func_name: dict()})

        for func_info in functions_info:
            self.functions[func_name].update({func_info: 0})
            
        # McComplexity start with 1 path
        self.functions[func_name]["McC"] += 1 
        self.total_mcc += 1

    def print_operators(self) -> None:
        """
        Print the operators dictionary in a table format.
        """
        header = ["Operator", "Total uses", "Used lines"]
        data = []
        
        for op in self.operators:
            data.append([op, len(self.operators[op]), self.operators[op]])
        
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

    def print_operands(self) -> None:
        """Print the operands dictionary in a table format."""
        header = ["Operand", "Total uses", "Appeared line"]
        data   = []

        for op in self.operands:
            data.append([op, len(self.operands[op]), self.operands[op]])
        
        print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))

    def print_functions(self) -> None:
        print(self.functions)

    def show_tree(self) -> None:
        """
        Show the Abstract Syntax Tree.
        """

        self.ast.show(showcoord = True)

    def append_operator(self, node: c_ast.Node) -> None:
        """
        Extract the operator from a node and adds the operator and its 
        ocurrence line to the operator dictionary.

        The operator dictionary stores the operator as the key and a list of
        the ocurrence lines as the key.

        :returns: 1 if is a valid node for a operator.
                  0 if is not a valid node.

        """
        line     : int = self.get_node_line(node)
        node_type: str = self.get_node_type(node)

        match(node_type):

            case "TypeDecl":
                operator = "="

            case "ArrayRef":
                operator = "[]"

            case "If":
                operator = "if"

            case "For":
                operator = "for"

            case "While":
                operator = "while"

            case "DoWhile":
                operator = "doWhile"

            case "ArrayDecl":
                operator = "[]"

            case "Decl":
                operator = "="

            case "Return":
                operator = "return"

            case _:
                operator: str = self.get_node_value(node)


        if operator in self.operators.keys():
            self.operators[operator].append(line)
        else:
            self.operators.update({operator: [line]})

    def append_operand(self, node: c_ast.Node) -> None:
        """
        Extract the operand from a node an adds the operand and its occurrence 
        line to the operand dictionary.

        Only Constant, ID, TypeDecl nodes can have a operand.

        The operand dictionary stores the operand as the key and a list of the 
        occurrence lines of the operator as the key.

        :returns: 1 if is a valid node for a operand.
                  0 if is not a valid node.
        """
        operand: str = self.get_node_value(node)
        line   : int = self.get_node_line(node)

        if operand in self.operands.keys(): # Only append the line ocurrency.
            self.operands[operand].append(line)
        else:
            self.operands.update({operand: [line]}) # Create a register.

    ## ==> Visit nodes <== ################################################

    def visit_Return(self, node: c_ast.Return) -> None:
        self.append_operator(node)

        self.visit(node.expr)

    def visit_DoWhile(self, node: c_ast.DoWhile) -> None:
        """
        Method called when statement a doWhile node is visited.

        DoWhile are considered operators.

        What the method do:
            1: Add a path to the ciclomatic complexity (McCabe Complexity).
            2: Add the DoWhile as a operator.
            3: Visit the conditional node.
            4: Visit the statement node (body).

        
        :param node: A c_ast DoWhile statement node.
        """
        self.add_McComplexity()

        self.append_operator(node)
        
        self.visit(node.cond)
        self.visit(node.stmt)

    def visit_While(self, node: c_ast.While) -> None:
        """
        Method called when a while statement node is visited.

        While statement is considered a operator.

        What the method do:
            1: Add a path to the ciclomatic complexity (McCabe Complexity).
            2: Add the While statement as operator.
            3: Visit the conditional node.
            4: Visit the statement node (body).

        :param node: A c_ast While statement node.
        """
        self.add_McComplexity()

        self.append_operator(node)

        self.visit(node.cond)
        self.visit(node.stmt) 

    def visit_For(self, node: c_ast.For) -> None:
        """
        Method called when a for statement node is visited.

        For statement nodes are considered operators.

        What the method do:
            1: Add a path to the cicomatic complexity (McCabe Complexity).
            2: Add the For statement as operator.
            3: Visit the initialize.
            4: Visit the conditional node.
            5: Visit the next node (increment).
            6: Visit the statement node (body).

        :param node: A c_ast For statement node.
        """
        self.add_McComplexity()

        self.append_operator(node)

        self.visit(node.init)
        self.visit(node.cond)
        self.visit(node.next)
        self.visit(node.stmt)

    def visit_If(self, node: c_ast.If) -> None:
        """
        Method called when a if node is visited.

        If are considered operators.

        What the method do:
            1: Add a path to the ciclomatic complexity (McCabe Complexity).
            2: Add the If statement as operator.
            3: Visit the if conditional statement.
            4: Visit the true if block.
            5: If has a false if block, visit it.

        :param node: A c_ast if statement node.
        """
        self.add_McComplexity()
        self.append_operator(node)

        #--> Visits <--#
        self.visit(node.cond)
        self.visit(node.iftrue)
        # Verify if has a else statement.
        if node.iffalse != None:
            self.visit(node.iffalse)

    def visit_Assignment(self, node: c_ast.Assignment) -> None:
        """
        Function called when a assignment node is visited.

        A Assigment node is a node that have a lvalue = rvalue.
        Assignment nodes has the '=' operator.

        What the method do:
            1: Add the assignment node as '=' operator.
            2: Visit the lvalue.
            3: Visit the rvalue.

        :param node: A assignment node.
        """
        self.append_operator(node)
        self.visit(node.lvalue)
        self.visit(node.rvalue)

    def visit_ArrayDecl(self, node: c_ast.ArrayDecl) -> None:
        """
        Method called when a ArrayDecl node is visited.

        
        :param node: A c_ast array declaration node.
        """
        self.append_operator(node)

        self.append_operand(node)

        self.visit(node.dim)

    def visit_ArrayRef(self, node: c_ast.ArrayRef) -> None:
        """
        Function called when a arrayRef node is visited.

        In ArrayRef, like 'array[i]', the '[]' are considered operators, so,
        the expr inside the brackets and the array, are considered operands.

        :param node: A arrayRef node.
        """
        self.append_operator(node)

        self.visit(node.name)
        self.visit(node.subscript)

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        """
        Function called when a funcdef node is visited.

        :param node: A definition function node.
        """
        self.current_func = self.get_node_value(node)
        self.initialize_function(node)

        self.visit(node.body)

    def visit_Decl(self, node: c_ast.Decl) -> None:
        """
        This function is called when a Declaration node is visited.

        :param node: A c_ast node type.
        """
        self.current_node_type = "Decl"

        # |> As variable DECLaration
        if self.get_node_value(node) != "_Value":
            self.visit(node.type)
            
            if not node.init is None: 
                self.append_operator(node)
                self.append_operand(node.type)
                self.visit(node.init)

        self.current_node_type = ""

    def visit_UnaryOp(self, node: c_ast.UnaryOp) -> None:
        """
        This function is called when a binary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node)

        self.visit(node.expr)

    def visit_BinaryOp(self, node: c_ast.BinaryOp) -> None:
        """
        This function is called when a binary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node)
        self.visit(node.left)
        self.visit(node.right)

    def visit_Constant(self, node: c_ast.Constant) -> None:
        """
        This function is called when a constant node is visited.
        A constant node, is a node that represent a constant value, as a string or literal
        
        :param node: A c_ast node type.

        """
        
        # |=> Constant as operand:
        self.append_operand(node)

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        """
        This function is called when a function_call node is visited.
        """
        # |> Function call as operator
        self.distict_func_calls.add(self.get_node_value(node))
        self.append_operator(node)

        # |> Function call as operand
        if self.current_node_type != "":
            self.append_operand(node)

        # |> Function args as operands
        self.current_node_type = "FuncCall"
        if node.args != None:
            for arg in node.args:
                self.visit(arg)

        self.current_node_type = ""

    def visit_ID(self, node: c_ast.ID) -> None:
        """
        This function is called when a ID node is visited.
        A identifier (ID) can be the name of a function or a variable.
        """
        # |=> As operand:
        self.append_operand(node)

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

            case "FuncDef":
                return node.decl.name
            
            case "PtrDecl":
                return node.type.declname

            case "Assignment":
                return node.op

            case "Decl":
                return node.name
                
            case "ArrayDecl":
                return node.type.declname

            case _:
                raise ValueError(f"Node of type '{self.get_node_type(node)}' is not defined yet")

if __name__ == "__main__":
    code = "euclids_gcd"

    code = ParsedCode(code)
    code.print_complexities()
