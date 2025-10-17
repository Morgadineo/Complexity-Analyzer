import pycparser
from pycparser        import plyparser
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
    """A class for parsing C code files and calculating software metrics.
    
    This class extends pycparser's NodeVisitor to traverse the AST of C code
    and collect various software metrics including Halstead metrics, 
    cyclomatic complexity, and line counts.
    
    Attributes:
        filename: Name of the file to be analyzed without extension.
        file_dir: Directory path containing the source file.
        file_fullpath: Full file path without suffix.
        file_pre_compiled: Path to the pre-compiled file.
        file_source: Path to the source code file.
        has_errors: Boolean indicating if parsing encountered errors.
        current_node_type: Type of the current node being visited.
        current_func: Current function being processed.
        operands: Dictionary storing operands and their occurrence lines.
        operators: Dictionary storing operators and their occurrence lines.
        functions: Set of Function objects representing parsed functions.
        number_of_functions: Total count of functions in the code.
        distict_func_calls: Set of distinct function call names.
        total_func_calls: Total count of function calls.
        total_mcc: Total McCabe cyclomatic complexity.
        total_lines: Total lines in the source file.
        effective_lines: Count of non-empty, non-comment lines.
        Various Halstead metrics (n1, n2, N1, N2, vocabulary, length, etc.)
        cognitive_statement_weight: Dictionary for cognitive complexity weights.
        total_cognitive_complexity: Total cognitive complexity score.
        ast: Abstract Syntax Tree representation of the parsed code.
    """
    
    def __init__(self, filename: str, file_dir: str = "Examples") -> None:
        """Initializes the ParsedCode object and starts the parsing process.
        
        Args:
            filename: Name of the file to be analyzed, without extension.
            file_dir: Path to the directory containing the file.
        """
        #--> File <-- #########################################################
        self.filename         : str = filename                         
        self.file_dir         : str = self.treat_file_dir(file_dir)   
        self.file_fullpath    : str = f"{self.file_dir}{self.filename}"
        self.file_pre_compiled: str = f"{self.file_fullpath}.i"           
        self.file_source      : str = f"{self.file_fullpath}.c"          

        #--> Global states <-- ################################################
        self.has_errors: bool = False

        self.current_node_type: str | None = None
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
        self.number_of_functions: int           = 0
        self.distict_func_calls : set[str]      = set()
        self.total_func_calls   : int           = 0

        #==> Ciclomatic Complexity <==#
        self.total_mcc: int = 0 # Total McCabe Complexity

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
        self.level          : float = 0  # Program level of abstraction. (L)
        self.estimated_level: float = 0  # Estimated program level (L')
        self.intelligence   : float = 0  # Intelligence Content. "Independet of language" (I)
        self.effort         : float = 0  # Effort (E).
        self.time_required  : float = 0  # Time required to program (T).
        self.delivered_bugs : float = 0  # Estimated number of bugs (B).

        self.avg_line_volume: float = 0

        #--> Initialization <-- ###############################################
        self.run_parser()

        #==> Calculate Metrics <==#

##=== ===|> Methods <|=== === #################################################

    def run_parser(self) -> None:
        """Runs the parser to generate AST and process the code.
        
        This method attempts to parse the pre-compiled file and visit all nodes
        in the AST. If parsing fails, it sets the has_errors flag and prints
        an error message.
        """
        try:
            self.ast: c_ast.FileAST = parse_file(self.file_pre_compiled, use_cpp=False)
            self.visit(self.ast)
            self.calculate_metrics()
            self.number_of_functions = len(self.functions)

        except plyparser.ParseError as e:
            Console().print(f"PARSE ERROR IN '{self.file_fullpath}': {e} - FILE IGNORED",
                            style="bold red")
            self.has_errors = True

    ## ==> Metric methods <== #############################################

    def calculate_metrics(self) -> None:
        """Calculates all software metrics for the parsed code.
        
        This method coordinates the calculation of line counts, Halstead metrics,
        and McCabe cyclomatic complexity.
        """
        self.count_lines()
        self.calculate_halstead()
        self.calculate_total_McC()

    def count_lines(self) -> None:
        """Counts total lines and effective lines of code.
        
        Effective lines exclude empty lines, comments, and lines containing
        only braces. Stores results in total_lines and effective_lines attributes.
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
        """Calculates all Halstead metrics for the parsed code.
        
        This method must be called after visiting the AST as it relies on
        collected operator and operand data. Calculates vocabulary, length,
        volume, difficulty, level, intelligence, effort, time, and bugs metrics.
        """
        nDigits: int = 2

        self.n1, self.N1     = self.count_total_operators()
        self.n2, self.N2     = self.count_total_operands()
        self.vocabulary      = self.n1 + self.n2                                  
        self.length          = self.N1 + self.N2                                 
        self.estimated_len   = round(self.n1 * log2(self.n1) + self.n2 *
                                     log2(self.n2), nDigits)
        self.volume          = round(self.length * log2(self.vocabulary),
                                     nDigits)             
        self.difficulty      = round((self.n1 / 2) * (self.N2 / self.n2),
                                     nDigits)
        self.estimated_level = round(1 / self.difficulty, nDigits)
        self.intelligence    = round(self.estimated_level * self.volume,
                                     nDigits)
        self.effort          = round(self.difficulty * self.volume,
                                     nDigits)
        self.time_required   = round(self.effort / 18, nDigits)
        self.delivered_bugs  = round(self.effort ** (2 / 3) / 3000,
                                     nDigits)

        self.avg_line_volume = round(self.volume / self.effective_lines,
                                     nDigits)

        for function in self.functions:
            function.calculate_halstead()

    def calculate_total_McC(self) -> None:
        """Calculates the total McCabe cyclomatic complexity.
        
        Sums the cyclomatic complexity of all functions in the code
        and stores the result in total_mcc attribute.
        """
        for function in self.functions:
            self.total_mcc += function.total_mcc
    
    def add_McComplexity(self) -> None:
        """Increments the cyclomatic complexity for the current function.
        
        Adds 1 to the current function's McCabe complexity. This is needed
        because every function block has at least one path.
        """
        if self.current_func != None:
            self.current_func.add_McC()

    def append_operator(self, node: c_ast.Node) -> None:
        """Extracts and stores an operator from a node.
        
        Extracts the operator and its line number from a node and stores it
        in the operators dictionary. If inside a function, stores it in the
        function's operator dictionary.
        
        Args:
            node: The AST node to extract the operator from.
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
        """Extracts and stores an operand from a node.
        
        Extracts the operand and its line number from a node and stores it
        in the operands dictionary. Only works for Constant, ID, and TypeDecl nodes.
        If inside a function, stores it in the function's operand dictionary.
        
        Args:
            node: The AST node to extract the operand from.
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

    def print_complexities(self) -> None:
        """Prints a formatted table of code complexity metrics.
        
        Displays Halstead metrics, cyclomatic complexity, line counts, and
        other complexity measures in a rich formatted table.
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
        table.add_row("Program estimated level", f"{self.estimated_level:.4f}")
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
        """Counts distinct and total operators in the code.
        
        Counts operators both in global scope and within functions.
        
        Returns:
            A tuple containing (distinct_operators, total_operators).
        """
        distinct_operators: int = len(self.operators.keys())
        total_operators   : int = 0

        for line_list in self.operators.values():
            total_operators += len(line_list)

        for function in self.functions:
            distinct_operators += len(function.operators.keys())
            for line_list in function.operators.values():
                total_operators += len(line_list)

        return (distinct_operators, total_operators)

    def count_total_operands(self) -> tuple[int, int]:
        """Counts distinct and total operands in the code.
        
        Counts operands both in global scope and within functions.
        
        Returns:
            A tuple containing (distinct_operands, total_operands).
        """
        distinct_operands: int = len(self.operands.keys())
        total_operands   : int = 0

        for line_list in self.operands.values():
            total_operands += len(line_list)
        
        for function in self.functions:
            distinct_operands += len(function.operands.keys())
            for line_list in function.operands.values():
                total_operands += len(line_list)

        return (distinct_operands, total_operands)

    def initialize_function(self, func: Function) -> None:
        """Adds a function to the functions set.
        
        Args:
            func: The Function object to add to the functions set.
        """
        self.functions.add(func)

    def extract_operator(self, node: c_ast.Node) -> tuple[str, int]:
        """Extracts the operator string and line number from a node.
        
        Args:
            node: The AST node to extract the operator from.
            
        Returns:
            A tuple containing (operator_string, line_number).
        """
        line     : int = self.get_node_line(node)
        node_type: str = self.get_node_type(node)
        operator : str = str()

        match(node_type):

            case "StructRef":
                operator = "->"

            case "Cast":
                # Cast for a simple type
                if isinstance(node.to_type.type.type, c_ast.IdentifierType):
                    operator = node.to_type.type.type.names[0]

                # Cast for a pointer
                elif isinstance(node.to_type.type, c_ast.PtrDecl):
                    operator = node.to_type.type.type.type.names[0] + '*'

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

            case "PtrDecl":
                operator = "*"

            case "Return":
                operator = "return"

            case "Sizeof":
                operator = "sizeof"

            case _:
                operator: str = self.get_node_value(node)

        return (operator, line)

    def extract_operand(self, node: c_ast.Node) -> tuple[str, int]:
        """Extracts the operand string and line number from a node.
        
        Args:
            node: The AST node to extract the operand from.
            
        Returns:
            A tuple containing (operand_string, line_number).
        """
        operand: str = self.get_node_value(node)
        line   : int = self.get_node_line(node)

        return (operand, line)

    def print_functions(self) -> None:
        """Prints a formatted table of function-level complexity metrics.
        
        Displays Halstead metrics and McCabe complexity for each function
        in the code, along with operator and operand tables for each function.
        """
        if self.number_of_functions == 0:
            return

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
        table.add_column("n1", justify="right", style="#1cffa0")
        table.add_column("n2", justify="right", style="#1cffa0")
        table.add_column("N1", justify="right", style="#1cffa0")
        table.add_column("N2", justify="right", style="#1cffa0")
        table.add_column("Vocabulary", justify="right", style="#1cffa0")
        table.add_column("length", justify="right", style="#1cffa0")
        table.add_column("Estimated Len", justify="right", style="#1cffa0")
        table.add_column("Volume", justify="right", style="#1cffa0")
        table.add_column("Difficulty", justify="right", style="#1cffa0")
        table.add_column("Estimated Level", justify="right", style="#1cffa0")
        table.add_column("Intelligence", justify="right", style="#1cffa0")
        table.add_column("Effort", justify="right", style="#1cffa0")
        table.add_column("Time", justify="right", style="#1cffa0")
        table.add_column("Bugs", justify="right", style="#1cffa0")
        table.add_column("McCabe", justify="right", style="#1cffa0")

        # table.add_column("Cognitive", justify="right", style="#1cffa0") ==>
        # Not Implemented yeet

        for function in self.functions:
            table.add_row(
                f"{function.func_name}",
                f"{function.n1}",
                f"{function.n2}",
                f"{function.N1}",
                f"{function.N2}",
                f"{function.vocabulary}",
                f"{function.length}",
                f"{function.estimated_len:.1f}",
                f"{function.volume:.1f}",
                f"{function.difficulty:.1f}",
                f"{function.estimated_level:.4f}",
                f"{function.intelligence:.1f}",
                f"{function.effort:.1f}",
                f"{function.time_required:.1f}",
                f"{function.delivered_bugs:.1f}",
                str(function.total_mcc),
                # str(function.cognitive_complexity),
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
        """Displays the Abstract Syntax Tree with coordinate information."""
        self.ast.show(showcoord = True)

    ## ==> Visit nodes <== ################################################

    def visit_FileAST(self, node: c_ast.FileAST) -> None:
        self.visit(node.ext)

    def visit_StructRef(self, node: c_ast.StructRef) -> None:

        self.append_operator(node)

        self.visit(node.name)
        self.visit(node.field)

    def visit_Typedef(self, node: c_ast.Typedef) -> None:
        """Visits a Typedef node and processes it for metrics.
        
        Args:
            node: A c_ast.Typedef node representing a typedef statement.
        """
        if self.is_real_node(node):
            self.append_operator(node) # Halstaed Metric
            self.append_operand(node)  # Halstead Metric

    def visit_Struct(self, node: c_ast.Struct) -> None:
        """Visits a Struct node and processes it for metrics.
        
        Args:
            node: A c_ast.Struct node representing a struct definition.
        """
        self.append_operand(node) # Halstead Metric

        #>>> Visit <<<#
        if node.decls != None:
            self.visit(node.decls)

    def visit_Return(self, node: c_ast.Return) -> None:
        """Visits a Return node and processes it for metrics.
        
        Return statements are considered operators, and their expressions
        are considered operands.
        
        Args:
            node: A c_ast.Return node representing a return statement.
        """
        self.append_operator(node) # Halstead Metric

        #=> Can be a empty "return;" node.
        #>>> Visit <<<#
        if node.expr != None:
            self.visit(node.expr)

    def visit_DoWhile(self, node: c_ast.DoWhile) -> None:
        """Visits a DoWhile node and processes it for metrics.
        
        DoWhile statements are considered operators and contribute to
        cyclomatic complexity.
        
        Args:
            node: A c_ast.DoWhile node representing a do-while loop.
        """
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric
        
        #>>> Visit <<<#
        self.visit(node.cond)
        self.visit(node.stmt)

    def visit_While(self, node: c_ast.While) -> None:
        """Visits a While node and processes it for metrics.
        
        While statements are considered operators and contribute to
        cyclomatic complexity.
        
        Args:
            node: A c_ast.While node representing a while loop.
        """
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.cond)
        self.visit(node.stmt) 

    def visit_For(self, node: c_ast.For) -> None:
        """Visits a For node and processes it for metrics.
        
        For statements are considered operators and contribute to
        cyclomatic complexity.
        
        Args:
            node: A c_ast.For node representing a for loop.
        """
        self.add_McComplexity() # McCabe Complexity

        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        if not node.init is None:
            self.visit(node.init)

        if not node.cond is None:
            self.visit(node.cond)

        if not node.next is None:
            self.visit(node.next)

        self.visit(node.stmt)

    def visit_If(self, node: c_ast.If) -> None:
        """Visits an If node and processes it for metrics.
        
        If statements are considered operators and contribute to
        cyclomatic complexity.
        
        Args:
            node: A c_ast.If node representing an if statement.
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
        """Visits an Assignment node and processes it for metrics.
        
        Assignment nodes contain the '=' operator.
        
        Args:
            node: A c_ast.Assignment node representing an assignment.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.lvalue)
        self.visit(node.rvalue)

    def visit_ArrayDecl(self, node: c_ast.ArrayDecl) -> None:
        """Visits an ArrayDecl node and processes it for metrics.
        
        Args:
            node: A c_ast.ArrayDecl node representing an array declaration.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.type)

        if node.dim is not None:
            self.visit(node.dim)

    def visit_ArrayRef(self, node: c_ast.ArrayRef) -> None:
        """Visits an ArrayRef node and processes it for metrics.
        
        In array references like 'array[i]', the '[]' are considered operators,
        and the array and index expressions are considered operands.
        
        Args:
            node: A c_ast.ArrayRef node representing an array reference.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.name)
        self.visit(node.subscript)

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        """Visits a FuncDef node and processes it for metrics.
        
        When a function definition is visited, the parser stores which function
        is being visited and initializes it in the functions dictionary for
        individual function metrics.
        
        Args:
            node: A c_ast.FuncDef node representing a function definition.
        """
        function_name: str      = self.get_node_value(node)
        function     : Function = Function(function_name)
        self.current_func = function
        self.initialize_function(function)

        #>>> Visit <<<#
        self.visit(node.body)

    def visit_PtrDecl(self, node: c_ast.PtrDecl) -> None:
        """Visits a PtrDecl node and processes it for metrics.
        
        Pointer declarations contain the '*' operator.
        
        Args:
            node: A c_ast.PtrDecl node representing a pointer declaration.
        """
        #==> Append * operator <==#
        self.append_operator(node)

        #>>> Visit <<<#
        self.visit(node.type)

    def visit_Cast(self, node: c_ast.Cast) -> None:
        """Visits a Cast node and processes it for metrics.
        
        Cast operations are considered operators.
        
        Args:
            node: A c_ast.Cast node representing a type cast.
        """
        self.append_operator(node)

        #>>> Visit <<<#
        self.visit(node.to_type)
        self.visit(node.expr)

    def visit_Decl(self, node: c_ast.Decl) -> None:
        """Visits a Decl node and processes it for metrics.
        
        Declaration nodes are generic and can have internal subtypes:
        - TypeDecl: Variable type declarations
        - FuncDecl: Function declarations
        
        Args:
            node: A c_ast.Decl node representing a declaration.
        """
        # |> As variable DECLaration
        if self.is_real_node(node):
            self.current_node_type = "Decl"

            #>>> Visit <<<#
            self.visit(node.type)

            if not node.init is None: 
                self.append_operator(node)

                #>>> Visit <<<#
                self.visit(node.init)

        self.current_node_type = ""

    def visit_TypeDecl(self, node: c_ast.TypeDecl) -> None:
        """Visits a TypeDecl node and processes it for metrics.
        
        TypeDecl nodes represent variable type declarations and are
        considered operands.
        
        Args:
            node: A c_ast.TypeDecl node representing a type declaration.
        """
        if node.declname == None:
            return

        self.append_operand(node)

        #>>> Visit <<<#
        ###############################################
        # This will visit the type node of a variable #
        ###############################################
        self.visit(node.type)

    def visit_IdentifierType(self, node: c_ast.IdentifierType) -> None:
        """Visits an IdentifierType node.
        
        Args:
            node: A c_ast.IdentifierType node representing an identifier type.
        """
        pass

    def visit_UnaryOp(self, node: c_ast.UnaryOp) -> None:
        """Visits a UnaryOp node and processes it for metrics.
        
        Unary operators are considered operators.
        
        Args:
            node: A c_ast.UnaryOp node representing a unary operation.
        """
        self.append_operator(node) # Halstead Metric

        #>>> Visit <<<#
        self.visit(node.expr)

    def visit_BinaryOp(self, node: c_ast.BinaryOp) -> None:
        """Visits a BinaryOp node and processes it for metrics.
        
        Binary operators are considered operators.
        
        Args:
            node: A c_ast.BinaryOp node representing a binary operation.
        """
        self.append_operator(node) # Halstead Metric
        
        #>>> Visit <<<#
        self.visit(node.left)
        self.visit(node.right)

    def visit_Constant(self, node: c_ast.Constant) -> None:
        """Visits a Constant node and processes it for metrics.
        
        Constant nodes represent literal values and are considered operands.
        
        Args:
            node: A c_ast.Constant node representing a constant value.
        """
        # |=> Constant as operand:
        self.append_operand(node) # Halstead Metric

    def visit_FuncCall(self, node: c_ast.FuncCall) -> None:
        """Visits a FuncCall node and processes it for metrics.
        
        Function calls are considered operators, and their arguments
        are considered operands.
        
        Args:
            node: A c_ast.FuncCall node representing a function call.
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
        """Visits an ID node and processes it for metrics.
        
        Identifier nodes represent variable or function names and are
        considered operands.
        
        Args:
            node: A c_ast.ID node representing an identifier.
        """
        # |=> As operand:
        self.append_operand(node) # Halstead Metric

## ==>  Utils Node Methods <==#################################################
    def is_real_node(self, node: c_ast.Node) -> bool:
        """Determines if a node comes from genuine source code.
        
        A node is considered 'fake' when:
        - It was inserted by preprocessor directives
        - It originates from pycparser's fake headers (artificial typedefs)
        
        Args:
            node: A c_ast.Node to be validated.
            
        Returns:
            True if the node comes from genuine source code,
            False if the node is compiler-generated/injected.
        """
        node_file: str = str(node.coord).split(":")[0]

        if node_file == self.file_source:
            return True

        else:
            return False

    def get_node_line(self, node: c_ast.Node) -> int:
        """Extracts the line number where a node occurs.
        
        Args:
            node: The AST node to extract the line number from.
            
        Returns:
            The line number where the node occurs.
        """
        brute_coord : str       = str(node.coord)
        sliced_coord: list[str] = brute_coord.split(":") 

        #-> Infos <-#
        line_coord   : int = int(sliced_coord[1])

        return line_coord

    def get_node_type(self, node: c_ast.Node) -> str:
        """Gets the type name of a node.
        
        Args:
            node: The AST node to get the type of.
            
        Returns:
            A string representing the node type.
        """
        return node.__class__.__name__

    def get_node_value(self, node: c_ast.Node) -> str:
        """Extracts the value/name from a node.
        
        For different node types, extracts appropriate values:
        - IdentifierType: type name
        - Typedef: typedef name
        - Struct/ID/Decl: name
        - FuncCall: function name
        - Constant: constant value
        - UnaryOp/BinaryOp/Assignment: operator
        - TypeDecl/PtrDecl/ArrayDecl: declaration name
        - FuncDef: function name
        
        Args:
            node: The AST node to extract the value from.
            
        Returns:
            A string representing the node's value/name.
            
        Raises:
            ValueError: If the node type is not yet implemented.
        """
        match(self.get_node_type(node)):

            case "IdentifierType":
                return node.names[0]

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

            case "PtrDecl":
                return node.declname

            case "ArrayDecl":
                return node.type.declname

            case "FuncDef":
                return node.decl.name
            
            case _:
                raise ValueError(f"Node of type '{self.get_node_type(node)}' is not defined yet")

## ==> Debug methods <==#######################################################

    def is_operand_parsed(self, operand: str) -> bool:
        """Debug function to check if an operand was successfully parsed.
        
        Args:
            operand: The operand string to check for existence.
            
        Returns:
            True if the operand was found, False otherwise.
        """
        print(f"Checking operand '{operand}' |=>", end=" ")

        if operand in self.operands.keys():
            print(self.operands[operand])
            return True

        else:
            print("[]")
            return False

    def is_operator_parsed(self, operator: str) -> bool:
        """Debug function to check if an operator was successfully parsed.
        
        Args:
            operator: The operator string to check for existence.
            
        Returns:
            True if the operator was found, False otherwise.
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
        """Treats the directory path for compatibility with pycparser.
        
        Removes './' prefix if present, as pycparser doesn't use it in node coordinates.
        
        Args:
            file_dir: The directory path to be treated.
            
        Returns:
            The treated path without './' prefix if it was present.
        """
        file_dir = file_dir.strip() # Remove left and right spaces.

        if file_dir[:2] == './':
            return file_dir[2:]

        return file_dir


