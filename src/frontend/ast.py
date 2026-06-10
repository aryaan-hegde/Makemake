class Assignment:
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Inputs:
    def __init__(self, vars):
        self.vars = vars

class Outputs:
    def __init__(self, vars):
        self.vars = vars