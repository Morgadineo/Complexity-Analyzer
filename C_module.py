from pycparser import parse_file, c_ast

class ComplexityVisitor(c_ast.NodeVisitor):
    def __init__(self):
        self.cyclomatic_complexity = 0        # Individual McCabe
        self.total_cyclomatic_complexity = 0  # Total McCabe
        self.functions = {}                   # Dict of the func 
        self.current_function = None          # Current visiting function

    def visit_FuncDef(self, node):
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

    def visit_If(self, node):
        """Procedure called when an IF node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        """Procedure called when a FOR node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        """Procedure called when a WHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_DoWhile(self, node):
        """Procedure called when a DoWHILE node is visited.
        *cyclomatic_complexity += 1*
        """
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_Switch(self, node):
        """Procedure called when a SWITCH node is visited.
        *cyclomatic_complexity += (quantity of case statements)*
        """
        if node.stmt.block_items:
            self.cyclomatic_complexity += len(node.stmt.block_items) - 1
        self.generic_visit(node)

    def analyse(self, filename):
        """Main function of the class. Call all the functions."""
        ast = parse_file(filename, use_cpp=False)  # Carregar o arquivo pré-processado e criar a AST
        self.visit(ast)
        
    def get_functions(self):
        """Return the dictionary containing complexities of each function."""
        return self.functions
    
    def get_funcs_complexity(self):
        """## Print all the function name and his respective complexity"""
        complexities = visitor.get_functions()
        for func_name, complexity in complexities.items():
            print(f"A complexidade ciclomática da função '{func_name}' é: {complexity}")
        print(f"Complexidade total do código é: {self.total_cyclomatic_complexity}")


if __name__ == "__main__":
    filename = "cash"
    path = f"Examples/{filename}_pre_limpo.c"  # Arquivo pré-processado e limpo
    visitor = ComplexityVisitor()              # Define a classe
    visitor.analyse(path)            
    visitor.get_funcs_complexity()
