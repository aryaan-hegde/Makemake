from .ast import Assignment, BinaryOp, UnaryOp, Inputs, Outputs
from .tokens import Variable

class Expand:
    def __init__(self, ast, inputs, outputs):
        self.ast = ast
        self.inputs = inputs
        self.outputs = outputs
        self.assignments = {}

    def expand_var(self, node):
        if isinstance(node, Variable):
            if node.value in self.assignments:
                return self.expand_var(self.assignments[node.value])

            return node

        elif isinstance(node, BinaryOp):
            return BinaryOp(
                self.expand_var(node.left),
                node.op,
                self.expand_var(node.right)
            )

        elif isinstance(node, UnaryOp):
            return UnaryOp(
                node.op,
                self.expand_var(node.operand)
            )

        else:
            return node
    
    def expand(self):
        for statement in self.ast:
            if isinstance(statement, Inputs):
                self.inputs = statement.vars
            elif isinstance(statement, Outputs):
                self.outputs = statement.vars
            elif isinstance(statement, Assignment):
                self.assignments[statement.target.value] = self.expand_var(statement.expr)

        trees = []
        for output in self.outputs:
            trees.append(self.expand_var(Variable(output)))
        
        return trees