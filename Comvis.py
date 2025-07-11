import pycparser
from pycparser import plyparser
from objects.function import Function
from ast              import parse
from os               import sep
from typing           import Any, List, Tuple
from pycparser        import parse_file, c_ast
from math             import dist, log2
from rich.console     import Console
from rich.columns     import Columns
from rich.table       import Table
from rich             import box
from rich.style       import Style

class ParsedCode(c_ast.NodeVisitor):
    """docstring for ParsedCode class"""
    def __init__(self, filename: str, file_dir: str = "Examples") -> None:
        """
        :param filename: Name of the file to be analyzed, without extension. 
        :param file_dir: Path to the file_dir.
        """
        #--> File <-- #########################################################
        self.filename   : str = filename                           # Raw file name
        self.file_dir   : str = self.treat_file_dir(file_dir)      # Dir with the source file and the pre-compiled file
        self.file_path  : str = f"{self.file_dir}{self.filename}"  # File path without sufix
        self.file_clean : str = f"{self.file_path}.i"              # Path to the pre-compiled file
        self.file_source: str = f"{self.file_path}.c"              # Path to the source code

        #--> Global states <-- ################################################
        self.has_errors: bool = False

        self.current_node_type: str      | None = None
        self.current_func: Function | None = None  

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

        #--> Metrics <-- ######################################################

        #==> Functions Complexity <==#
        self.functions          : set[Function] = set()
        self.number_of_functions: int           = len(self.functions)
        self.distict_func_calls : set[str]      = set()
        self.total_func_calls   : int           = 0

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
        self.vocabulary    : int   = 0  # Program vocabulary (n).
        self.length        : int   = 0  # Program lenght (N).
        self.estimated_len : float = 0  # Estimated program length (^N).
        self.volume        : float = 0  # Volume (V).
        self.difficulty    : float = 0  # Difficulty (D).
        self.level         : float = 0  # Program level of abstraction. (L)
        self.intelligence  : float = 0  # Intelligence Content. "Independet of language" (I)
        self.effort        : float = 0  # Effort (E).
        self.time_required : float = 0  # Time required to program (T).
        self.delivered_bugs: float = 0  # Estimated number of bugs (B).

        self.avg_line_volume: float = 0

        #==> Not implemented yet <==#
        self.cognitive_statement_weight: dict[str, int | float] = {
            "Sequencial": 0,
            "Break"     : 0,
            "Continue"  : 0,
            "Return"    : 0,
            "If"        : 0,
            "Switch"    : 0,
            "If-Else"   : 0,
            "For"       : 0,
            "While"     : 0,
            "Do-While"  : 0,
            "UDF"       : 0,
            "Recursion" : 0,
            "Exception" : 0,

        }
        self.total_cognitive_complexity: int = 0

        #--> Initialization <-- ###################################################
        self.run_parser()

        #==> Calculate Metrics <==#

##=== ===|> Methods <|=== === #################################################

    def run_parser(self):
        """
        Method to run the parser class.
        """
        try:
            self.ast: c_ast.FileAST = parse_file(self.file_clean, use_cpp=False)
            self.visit(self.ast)
            self.calculate_metrics()

        except plyparser.ParseError:
            Console().print(f"PARSE ERROR IN '{self.file_path}' - IGNORING",
                            style="bold red")
            self.has_errors = True
            raise

    ## ==> Metric methods <== #############################################

    def calculate_metrics(self):
        """
        Method to call all the others calculate metrics functions
        """
        self.count_lines()
        self.calculate_halstead()
        self.calculate_total_McC()

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
        self.n1, self.N1    = self.count_total_operators()
        self.n2, self.N2    = self.count_total_operands()
        self.vocabulary     = self.n1 + self.n2                                  # Calculate vocabulary.
        self.length         = self.N1 + self.N2                                  # Calculate length.
        self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
        self.volume         = self.length * log2(self.vocabulary)                # Calculate volume.
        self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)                # Calculate difficulty.
        self.level          = 1 / self.difficulty                                # Calculate program level.
        self.intelligence   = self.level * self.volume                           # Calculate program intelligence
        self.effort         = self.difficulty * self.volume                      # Calculate effort.
        self.time_required  = self.effort / 18                                   # Calculate time to program (seconds).
        self.delivered_bugs = self.effort ** (2 / 3) / 3000                      # Calculate number of delivered bugs.

        self.avg_line_volume = self.volume / self.effective_lines

        for function in self.functions:
            function.calculate_halstead()

    def calculate_total_McC(self):
        """
        Calculate and set the total number of paths present in the code.
        Is the sum of all functions paths and set the total_mcc variable.

        """

        for function in self.functions:
            self.total_mcc += function.total_mcc
    
    def add_McComplexity(self) -> None:
        """
        Add 1 for the current function
        ciclomatic complexity.

        The add 1 to total ciclomatic complexity is needed when a function
        is initialized, because every block has at least one path.

        """
        if self.current_func != None:
            self.current_func.add_McC()

    def append_operator(self, node: c_ast.Node) -> None:
        """
        Extract the operator and his line number from a node and append him as
        a operator. If the node is inside a function node, the operator is
        storage in the function object.

        The operator dictionary stores the operator as the key and a list of
        the ocurrence lines as the key.

        :param node: The node to extract the operator and append.

        """
        operator, line = self.extract_operator(node)

        #==> If inside a function <==#
        if self.current_func is not None:
            self.current_func.add_operator(operator, line)

        #==> If not <==#
        else:
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
        operand, line = self.extract_operand(node)

        #==> If inside a function <==#
        if self.current_func is not None:
            self.current_func.add_operand(operand, line)

        #==> If not <==#
        else:
            if operand in self.operands.keys():
                self.operands[operand].append(line)
            else:
                self.operands.update({operand: [line]})

    ## ==> Auxiliar methods <== ###############################################

    def print_complexities(self):
        """Print the code complexity table, list of operands, operators and the functions complexities.

        (This function do not calculate the metrics and either generate the AST)
        """
        console = Console()
    
        # Create table
        title: str = f"[bold][#00ffae]{self.filename.upper()}[/]"
        border_style: Style = Style(color="#000000", bold=True,)

        table = Table(title=title,
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold #ffee00",
                      border_style=border_style,
                      )


        table.add_column("Complexity", style="cyan")
        table.add_column("Value", justify="right", style="#1cffa0")
        
        table.add_row("Total lines", str(self.total_lines))
        table.add_row("Effective lines", str(self.effective_lines))
        
        table.add_row("─" * 20, "─" * 10, style="dim")
        
        table.add_row("Distinct Operators (n1)", str(self.n1))
        table.add_row("Distinct Operands (n2)", str(self.n2))
        table.add_row("Total Operators (N1)", str(self.N1))
        table.add_row("Total Operands (N2)", str(self.N2))
        table.add_row("Program vocabulary", str(self.vocabulary))
        table.add_row("Program Length", str(self.length))
        table.add_row("Estimated Length", f"{self.estimated_len:.1f}")
        table.add_row("Volume", f"{self.volume:.1f}")
        table.add_row("Difficulty", f"{self.difficulty:.1f}")
        table.add_row("Program level", f"{self.level:.3f}")
        table.add_row("Content Intelligence", f"{self.intelligence:.1f}")
        table.add_row("Effort", f"{self.effort:.1f}")
        table.add_row("Required time to program", f"{self.time_required:.1f}")
        table.add_row("Delivered bugs", f"{self.delivered_bugs:.1f}")
        
        # Adicionar separador para a complexidade ciclomática
        table.add_row("─" * 20, "─" * 10, style="dim")
        table.add_row("[bold]CYCLOMATIC COMPLEXITY[/]", "")
        table.add_row("Total Cyclomatic Complexity", str(self.total_mcc))

        table.add_row("─" * 20, "─" * 10, style="dim")
        table.add_row("[bold]OTHERS[/]", "")
        table.add_row("Average line volume", str(round(self.avg_line_volume)))

        table.add_row("Number of functions calls", str(self.total_func_calls))

        # Imprimir a tabela
        console.print(table)

    def count_total_operators(self) -> tuple[int, int]:
        """
        Method to count the number of distinct operators and total operators.

        This method return a ordenered pair with [0] the number of distinct operators e [1] the total number of operators.
        """
        total_operators   : int = 0
        distinct_operators: int = 0

        for function in self.functions:
            for operator in function.operators.keys():
                distinct_operators += 1
                total_operators    += len(function.operators[operator])

        return (distinct_operators, total_operators)

    def count_total_operands(self) -> tuple[int, int]:
        """
        Method to count the number of distinct operands and total operands.

        This method return a ordenered pair with [0] the number of distinct operators e [1] the total number of operands.
        """
        total_operands   : int = 0
        distinct_operands: int = 0
        
        for function in self.functions:
            for operand in function.operands.keys():
                distinct_operands += 1
                total_operands    += len(function.operands[operand])

        return (distinct_operands, total_operands)

    def initialize_function(self, func: Function) -> None:
        """
        Method to initialize a function in the functions dictionary.

        :param node: A FuncDef node that contains the node.
        """
        self.functions.add(func)

    def extract_operator(self, node: c_ast.Node) -> tuple[str, int]:
        """
        Extract the operator from a node and return a str with the operator
        and the line of ocurrency.

        :param node: The node to extract the operator.

        :return: A tuple with the name and the line of ocurrency, respectively.
        """
        line     : int = self.get_node_line(node)
        node_type: str = self.get_node_type(node)
        operator : str = str()

        match(node_type):

            case "Typedef":
                operator = "typedef"

            case "TypeDecl" | "Decl":
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

            case "Return":
                operator = "return"

            case _:
                operator: str = self.get_node_value(node)

        return (operator, line)

    def extract_operand(self, node: c_ast.Node) -> tuple[str, int]:
        """
        Extract the operand from a node and return a tuple with the string
        operand and the line of ocurrency.

        :param node: The node to extract the operand.

        :return: A tuple with the string operand and the line of ocurrency,
                 respectively.
        """
        operand: str = self.get_node_value(node)
        line   : int = self.get_node_line(node)

        return (operand, line)

    def print_functions(self) -> None:
        console = Console()

        title: str = "[bold]Functions Complexity Analysis[/]"
        border_style: Style = Style(color="#000000", bold=True,)

        table = Table(title=title,
                      box=box.ROUNDED,
                      show_header=True,
                      header_style="bold #ffee00",
                      border_style=border_style,
                      )
        
        # Add columns
        table.add_column("Function", style="cyan")
        table.add_column("Lines", justify="right", style="#1cffa0")
        table.add_column("Eff.Lines", justify="right", style="#1cffa0")
        table.add_column("n1", justify="right", style="#1cffa0")
        table.add_column("n2", justify="right", style="#1cffa0")
        table.add_column("N1", justify="right", style="#1cffa0")
        table.add_column("N2", justify="right", style="#1cffa0")
        table.add_column("Vocabulary", justify="right", style="#1cffa0")
        table.add_column("length", justify="right", style="#1cffa0")
        table.add_column("Estimated Len", justify="right", style="#1cffa0")
        table.add_column("Volume", justify="right", style="#1cffa0")
        table.add_column("Difficulty", justify="right", style="#1cffa0")
        table.add_column("Level", justify="right", style="#1cffa0")
        table.add_column("Intelligence", justify="right", style="#1cffa0")
        table.add_column("Effort", justify="right", style="#1cffa0")
        table.add_column("Time", justify="right", style="#1cffa0")
        table.add_column("Bugs", justify="right", style="#1cffa0")
        table.add_column("McCabe", justify="right", style="#1cffa0")
        table.add_column("Cognitive", justify="right", style="#1cffa0")

        for function in self.functions:
            table.add_row(
                function.func_name, str(function.total_lines),
                str(function.effective_lines),
                f"{function.n1}",
                f"{function.n2}",
                f"{function.N1}",
                f"{function.N2}",
                f"{function.vocabulary}",
                f"{function.length}",
                f"{function.estimated_len:.1f}",
                f"{function.volume:.1f}",
                f"{function.difficulty:.1f}",
                f"{function.level:.1f}",
                f"{function.intelligence:.1f}",
                f"{function.effort:.1f}",
                f"{function.time_required:.1f}",
                f"{function.delivered_bugs:.1f}",
                str(function.total_mcc),
                str(function.cognitive_complexity),
            )
        
        console.print(table)

        for function in self.functions:
            f_operators: Table = function.table_operators()
            f_operands : Table = function.table_operands()

            console.print(Columns([f_operators, f_operands],
                                  equal=False,
                                  expand=False,
                                  align="left"))

    def show_tree(self) -> None:
        """
        Show the Abstract Syntax Tree.
        """
        self.ast.show(showcoord = True)

    ## ==> Visit nodes <== ################################################

    def visit_Typedef(self, node: c_ast.Typedef) -> None:
        """
        Method called when a Typedef keyword node is visited.

        :param node: A c_ast Typedef node.
        """
        if self.is_real_node(node):
            self.append_operator(node) # Halstaed Metric
            self.append_operand(node)  # Halstead Metric

    def visit_Struct(self, node: c_ast.Struct) -> None:
        """
        Method called when a Struct statement node is visited.
        
        :param node: A c_ast Struct node.
        """
        self.append_operand(node) # Halstead Metric

        #>>> Visit <<<#
        if node.decls != None:
            self.visit(node.decls)

    def visit_Return(self, node: c_ast.Return) -> None:
        """
        Method called when a Return statement node is visited.
        Returns are considered operators and their return as operands.

        :param node: A c_ast.Return node.
        """
        self.append_operator(node) # Halstead Metric

        #=> Can be a empty "return;" node.
        #>>> Visit <<<#
        if node.expr != None:
            self.visit(node.expr)

    def visit_DoWhile(self, node: c_ast.DoWhile) -> None:
        """
        Method called when a doWhile statement node is visited.

        DoWhile are considered operators.

        What the method do:
            1: Add a path to the ciclomatic complexity (McCabe Complexity).
            2: Add the DoWhile as a operator.
            3: Visit the conditional node.
            4: Visit the statement node (body).

        
        :param node: A c_ast DoWhile statement node.
        """
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric
        
        #>>> Visit <<<#
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
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
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
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
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
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.cond)

        if node.iftrue != None:
            self.visit(node.iftrue)
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
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.lvalue)
        self.visit(node.rvalue)

    def visit_ArrayDecl(self, node: c_ast.ArrayDecl) -> None:
        """
        Method called when a ArrayDecl node is visited.

        
        :param node: A c_ast array declaration node.
        """
        self.append_operator(node) # Halstead Metric
        self.append_operand(node)  # Halstead Metric

        #>>> Visit <<<#
        if node.dim is not None:
            self.visit(node.dim)

    def visit_ArrayRef(self, node: c_ast.ArrayRef) -> None:
        """
        Function called when a arrayRef node is visited.

        In ArrayRef, like 'array[i]', the '[]' are considered operators, so,
        the expr inside the brackets and the array, are considered operands.

        :param node: A arrayRef node.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.name)
        self.visit(node.subscript)

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        """
        Function called when a funcdef node is visited.
        When a function definition is visited, the parser store what function
        is he visiting and initialize in the dictionary. This is made for store
        individual function metrics.

        In the pre processing, functions prototype are replaced by the func
        definition.

        :param node: A definition function node.
        """
        function_name: str      = self.get_node_value(node)
        function     : Function = Function(function_name)
        self.current_func = function
        self.initialize_function(function)

        #>>> Visit <<<#
        self.visit(node.body)

    def visit_Decl(self, node: c_ast.Decl) -> None:
        """
        This function is called when a Declaration node is visited.
        Declarations are generic nodes, so they have internal subtypes.

        Types of Decl:
        * TypeDecl: Types of variables.
        * FuncDecl: Function declaration.

        Declarations examples:
        * Declaration of parameters: void func(int decl_var); (TypeDecl)
        * Declaration of functions : void func_decl(int x);   (FuncDecl)

        :param node: A c_ast node type.
        """
        # |> As variable DECLaration
        if self.is_real_node(node):
            self.current_node_type = "Decl"

            #>>> Visit <<<#
            self.visit(node.type)
            
            if not node.init is None: 
                self.append_operator(node)
                self.append_operand(node.type)

                #>>> Visit <<<#
                self.visit(node.init)

        self.current_node_type = ""

    def visit_TypeDecl(self, node: c_ast.TypeDecl) -> None:
        #>>> Visit <<<#
        self.visit(node.type)

    def visit_IdentifierType(self, node: c_ast.IdentifierType) -> None:
        """
        This functions is called when a type identifier node is visited.

        :param node: A c_ast TypeDecl node.
        """
        pass

    def visit_UnaryOp(self, node: c_ast.UnaryOp) -> None:
        """
        This function is called when a unary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.expr)

    def visit_BinaryOp(self, node: c_ast.BinaryOp) -> None:
        """
        This function is called when a binary operator node is visited.

        :param node: A c_ast node type.
        """
        self.append_operator(node) # Halstead Metric
        
        #>>> Visit <<<#
        self.visit(node.left)
        self.visit(node.right)

    def visit_Constant(self, node: c_ast.Constant) -> None:
        """
        This function is called when a constant node is visited.
        A constant node, is a node that represent a constant value, as a string or literal
        
        :param node: A c_ast node type.

        """
        
        # |=> Constant as operand:
        self.append_operand(node) # Halstead Metric

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        """
        This function is called when a function_call node is visited.

        Function calls are considered operators and consequently, their
        arguments are considered operands.

        :param node: A function call node.
        """
        # |> Function call as operator <|
        self.total_func_calls += 1
        self.distict_func_calls.add(self.get_node_value(node))

        self.append_operator(node) # Halstead Metric

        # |> Function call as operand
        if self.current_node_type != "":
            self.append_operand(node) # Halstead Metric

        # |> Function args as operands
        self.current_node_type = "FuncCall"

        #>>> Visit <<<#
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
        self.append_operand(node) # Halstead Metric

## ==>  Utils Node Methods <==#################################################
    def is_real_node(self, node: c_ast.Node) -> bool:
        """
        Determines whether a given AST node is artificially generated (fake) rather than 
        originating from the actual C source code.

        A node is considered 'fake' when:
        - It was inserted by preprocessor directives rather than being part of the original source
        - It originates from pycparser's fake headers (which include artificial typedefs)

        :param node: A c_ast Node to be validated.

        :return: True if it comes from genuine source code
                 False if the node is compiler-generated/injected (fake).
        """
        node_file: str = str(node.coord).split(":")[0]

        if node_file == self.file_source:
            return True

        else:
            return False

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

            case "Typedef":
                return node.name

            case "Struct" | "ID" | "Decl":
                return node.name

            case "FuncCall":
                return node.name.name

            case "Constant":
                return node.value

            case "UnaryOp" | "BinaryOp" | "Assignment":
                return node.op

            case "TypeDecl":
                return node.declname

            case "FuncDef":
                return node.decl.name
            
            case "PtrDecl" | "ArrayDecl":
                return node.type.declname

            case _:
                raise ValueError(f"Node of type '{self.get_node_type(node)}' is not defined yet")

## ==> Debug methods <==#######################################################

    def is_operand_parsed(self, operand: str) -> bool:
        """
        Debug function to verify whether a given operand was successfully parsed 
        and added to the operands dictionary. If the operand was successfuly
        parsed, print lines when the operad was found and return true. A empty
        list is printed if the operand was not found and return false.

        :param operand: The operand string to check for existence in the parser's dictionary.
        
        :return: True if the operand was successfully identified and stored; 
                 False if the operand was not found.
        """
        print(f"Checking operand '{operand}' |=>", end=" ")

        if operand in self.operands.keys():
            print(self.operands[operand])
            return True

        else:
            print("[]")
            return False

    def is_operator_parsed(self, operator: str) -> bool:
        """
        Debug function to verify whether a given operator was sucessfully
        parsed and added to the operands dictionary. If the operand was
        successfuly parsed, print lines when the operator was found and return
        true. A empty list is printed if the operator was not found and false 
        is returned.

        :param operator: The operator string to check for existence in 
                         parser's dictionary.

        :return: True if the operator was sucessfully identified and stored;
                 False if the operand was not found.
        """
        print(f"Checking operator '{operator}' |=>", end=" ")

        if operator in self.operators.keys():
            print(self.operators[operator])
            return True
        else:
            print("[]")
            return False

## ==> Treatment methods <==###################################################

    def treat_file_dir(self, file_dir: str) -> str:
        """
        Treat the dir path of the file.
        Is commom to use './'ExampleDir/ to represent local folder, but
        pycparser does not use in the node coords. So, to treat that, is
        verified if the path is using ./ and remove it.

        :param file_dir: The dir path to be treat (if necessary).

        :return: The treated path (if the treat is necessary) or the same path
                 (if the treat is not necessary).
        """
        file_dir = file_dir.strip() # Remove left and right spaces.

        if file_dir[:2] == './':
            return file_dir[2:]

        return file_dir


if __name__ == "__main__":
    dirs = "Examples/EstruturaDeDadosI/arredondar/"
    code = "alyssongodinho3@gmail.com_1_arredondar"

    code = ParsedCode(code, dirs)

    if not code.has_errors:
        code.print_complexities()
        code.print_functions()

