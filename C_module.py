from pycparser import parse_file, c_ast
from math import log2
from tabulate import tabulate
from os import listdir

class ComplexityVisitor(c_ast.NodeVisitor):
	def __init__(self, filename):
		##########-- UTILS VARIABLES --########################################
		self.__DEBUG__ = False
		##-- FILE --##
		self.filename = filename                             # Raw filename
		self.file_dir = "Examples"                           # Dir with the source file and the pre-compiled file
		self.file_path = f"{self.file_dir}/{self.filename}"  # File path without sufix
		self.file_clean = f"{self.file_path}.i"              # Path to the pre-compiled file
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
		# cognitive_modifiers -> DICT
		# [0] -> STR | "Statement name"
		# [1] -> INT | Node coord
		# [2] -> INT | Cognitive Complexity modifiers
		self.cognitive_modifiers = dict() # Stores all the statements that add cognitive complexity
		self.current_statement = None          # The current statement
		self.current_statement_complexity = 0  # The current statement complexity
		self.total_cognitive_complexity = 0    # Total cognitive complexity.
		self.current_depth = 0                 # Actual deph level.
		self.weights = {                       # Weight of statements and structures (Based on the article):
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

	###********************************************************************************************###
	##                           FUNCTIONS                                                                                     ##
	###********************************************************************************************###

	###-- UTILS FUNCTIONS --###################################################

	def print_analyse(self):
		"""## Main function of the class. Call all the complexity functions and print the results."""
		ast = parse_file(self.file_clean, use_cpp=False)
		self.visit(ast)
		self.count_lines()
		self.calculate_halstead_volume()
		self.print_complexities()

	def analyse(self):
		"""## Main function of the class. Call all the complexity calculate functions."""
		ast = parse_file(self.file_clean, use_cpp=False) 
		self.visit(ast)
		self.count_lines()
		self.calculate_halstead_volume()

	def print_complexities(self):
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
				["Effort", f"{self.effort:.1f}"],
				["Required time to program", f"{self.time_required:.1f}"],
				["Delivered bugs", f"{self.delivered_bugs:.1f}"],
				["CYCLOMATIC COMPLEXITY"],
				["Total Cyclomatic Complexity", self.total_cyclomatic_complexity],
				["Cognitive Complexity"],
				["Cognitve Complexity", self.total_cognitive_complexity],
				]
		print(tabulate(data, headers=header, tablefmt="double_grid", numalign="right"))
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

	def print_ast(self):
		ast = parse_file(self.file_clean, use_cpp=False, )  # Create the AST using the pre-compiled and clean file.
		ast.show(showcoord=False)  # Show the AST with the coordnates

	def __debug_analyse__(self):
		self.__DEBUG__ = True
		ast = parse_file(self.file_clean, use_cpp=False)
		self.visit(ast)

	def print_lenght(self):
		headers = ["CODE INFOS", "VALUE"]
		data = [["Effective lines", self.effective_lines],
				["Total lines", self.total_lines]]
		print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))

	def count_lines(self):
		"""Count the total lines and the effective lines (non-empty, not comment and { or })."""
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
				
				# Remove one line block comments
				if stripped_line[:2] == "/*" and stripped_line[-2:] == "*/":
					continue

				if "/*" in stripped_line:
					in_block_comment = True
					continue

				if not stripped_line or stripped_line.startswith("//"):
					continue
				
				if stripped_line == '{' or stripped_line == '}':
					continue
				
				self.effective_lines += 1

	def calculate_halstead_volume(self):
		"""## Procedure to calculate the Halstead volume.
		"""
		self.n1, self.N1 = self.__count_operators__()
		self.n2, self.N2 = self.__count_operands__()

<<<<<<< HEAD
		self.vocabulary     = self.n1 + self.n2  # Calculate vocabulary.
		self.lenght         = self.N1 + self.N2  # Calculate length.
		self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
		self.volume         = self.lenght * log2(self.vocabulary)  # Calculate volume.
		self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)  # Calculate difficulty.
		self.level          = 1 / self.difficulty  # Calculate program level.
		self.effort         = self.difficulty * self.volume  # Calculate effort.
		self.time_required  = self.effort / 18  # Calculate time to program (seconds).
		self.delivered_bugs = self.effort ** (2 / 3) / 3000  # Calculate number of delivered bugs.
=======
		self.vocabulary     = self.n1 + self.n2                                  # Calculate vocabulary.
        self.lenght         = self.N1 + self.N2                                  # Calculate length.
		self.estimated_len  = self.n1 * log2(self.n1) + self.n2 * log2(self.n2)  # Calculate estimative length.
		self.volume         = self.lenght * log2(self.vocabulary)                # Calculate volume.
		self.difficulty     = (self.n1 / 2) * (self.N2 / self.n2)                # Calculate difficulty.
		self.level          = 1 / self.difficulty                                # Calculate program level.
		self.effort         = self.difficulty * self.volume                      # Calculate effort.
		self.time_required  = self.effort / 18                                   # Calculate time to program (seconds).
		self.delivered_bugs = self.effort ** (2 / 3) / 3000                      # Calculate number of delivered bugs.
>>>>>>> 1123caf (Update code)

	def print_halstead_volume(self):  
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

	def print_functions_complexities(self): 
		"""## Print all the function name and his respective complexity"""
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
			case "Decl":
				node_op = node.name
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

	def __get_line__(self, node):
		"""Function to return the node line in the 'file'_limpo_pre.c."""
		return int(str(node.coord).split(':')[1])

	def __get_func_parameters_type__(self, node):
		types = []
		args = None
		try:  # IF is a FuncDef=
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

	def __get_func_return_type__(self, node):
		try:
			return node.decl.type.type.type.names[0]
		except AttributeError:
			return node.type.type.names[0]

<<<<<<< HEAD
=======
	def __add_statement_modifier__(self, statement, node):
		"""  Function to add the statement in the self.cognitive_modifier dict  """
        self.cognitive_modifiers

>>>>>>> 1123caf (Update code)
	def __add_statement_cog_c__(self, statement, node):
		"""Add the statement cognitive complexity in the function"""
		cognitive_modifier = self.weights[statement] + self.current_statement_complexity # Statement Weight + Nested Weight
		
<<<<<<< HEAD
		# Declaration and func_call do not alter the nested weight.
=======
		# Declaration and func_call do not alter the nested weight.	
>>>>>>> 1123caf (Update code)
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
			self.current_function = node.type.declname
			if not (node.type.declname in self.functions_info):
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
			self.functions_complexities[self.current_function][0] = self.cyclomatic_complexity

	def visit_FuncCall(self, node):
		"""Registra chamadas de funções."""
		if self.__DEBUG__:
			print(f"=============================================================\n{node}")
		else:
			if node.name.name in self.functions_info:
				self.functions_info[node.name.name][3].append(self.__get_line__(node))
			self.__add_operator__(node, node.name.name)
			
			if (self.__verify_recursion__(node.name.name)):
				self.__add_statement_cog_c__("recursion", node)
			else:
				self.__add_statement_cog_c__("func_call", node)
			
			self.generic_visit(node)

	def visit_If(self, node):
		"""## Procedure called when an IF node is visited.
		*cyclomatic_complexity += 1*
		"""
		if self.__DEBUG__:
			print(f"=============================================================\n{node}")
		else:
			self.cyclomatic_complexity += 1  # Cyclomatic Complexity
			
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
			self.cyclomatic_complexity += 1  # Cyclomatic Complexity 
			
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


###-- OUT CLASS --###########################################################
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

	headers = ["Metric", f"{filename1[:5]}", f"{filename2[:5]}", f"{filename2[:5]} has"]
	data = [["Total lines", visitor1.total_lines, visitor2.total_lines, (visitor2.total_lines - visitor1.total_lines)],
			["Effective lines", visitor1.effective_lines, visitor2.effective_lines,
			(visitor2.effective_lines - visitor1.effective_lines)],
			["Count of distinct operators", visitor1.n1, visitor2.n1,
			 (visitor2.n1 - visitor1.n1)],
			["Count of distinct operands", visitor1.n2, visitor2.n2,
			 (visitor2.n2 - visitor1.n2)],
			["Total operators", visitor1.N1, visitor2.N1, (visitor2.N1 - visitor1.N1)],
			["Total operands", visitor1.N2, visitor2.N2, (visitor2.N2 - visitor1.N2)],
			["Program vocabulary", visitor1.vocabulary, visitor2.vocabulary,
			 (visitor2.vocabulary - visitor1.vocabulary)],
			["Program lenght", f"{visitor1.lenght:.2f}", f"{visitor2.lenght:.2f}",
			 f"{(visitor2.lenght - visitor1.lenght):.2f}"],
			["Estimated program length", f"{visitor1.estimated_len:.2f}", f"{visitor2.estimated_len:.2f}",
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

def analyse_all(debug=0):
	for filename in listdir("Examples"):
		if filename[-2:] == ".i":
			pure_filename = filename[:-2]
			if not debug:
				individual_analyse(pure_filename)
			else:
				debuged_analyse(pure_filename)

def compare_to_all(f1):
	for filename in listdir("Examples"):
		if filename[-2:] == ".i":
			pure_filename = filename[:-2]
			print(f"==================/ {f1} compared to {pure_filename}\\================================")
			compare(f1, pure_filename)
			print("\n\n\n")

if __name__ == "__main__":
    gabarito= "abrantesasf@computacaoraiz.com.br_1_temperatura"
    f1 = "arthur.fabres@gmail.com_1_temperatura"
    # show_tree("cod_2")
    #compare (f1, "c")
    # compare_to_all(gabarito)
    # debuged_analyse(
    # individual_analyse(f1)
    analyse_all()
