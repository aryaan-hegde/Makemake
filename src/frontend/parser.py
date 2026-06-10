from .ast import Assignment, BinaryOp, UnaryOp, Inputs, Outputs

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.token = self.tokens[self.idx]
        self.statements = []
        self.inputs = []
        self.outputs = []
    
    def factor(self):
        if self.token.type == "INT":
            node = self.token
            self.move()
            return node

        elif self.token.type == "VAR":
            node = self.token
            self.move()
            return node

        elif self.token.value == "~":
            op = self.token
            self.move()
            return UnaryOp(op, self.factor())

        elif self.token.value == "(":
            self.move()
            expr = self.expression()
            self.move()
            return expr

    def term(self):
        left = self.factor()

        while self.token.value == "*":
            op = self.token
            self.move()
            right = self.factor()
            left = BinaryOp(left, op, right)

        return left
    
    def expression(self):
        left = self.term()

        while self.token.value in ["+", "^"]:
            op = self.token
            self.move()
            right = self.term()
            left = BinaryOp(left, op, right)

        return left

    def statement(self):
        if self.token.value == 'make':
            self.move()
            target = self.token
            self.move()
            self.move()
            expr = self.expression()

            return Assignment(target, expr)
        elif self.token.value in ('inputs', 'outputs'):
            declaration_value = self.token.value
            self.move()
            while self.token.type not in ("DECL", "EOF"):
                if declaration_value == 'inputs':
                    self.inputs.append(self.token.value)
                else:
                    self.outputs.append(self.token.value)
                self.move()
            return Inputs(self.inputs) if declaration_value == 'inputs' else Outputs(self.outputs)
        else:
            raise Exception("Begin statements with a declaration")

    def parse(self):
        statements = []
        while self.token.type != "EOF":
            statements.append(self.statement())
        self.statements = statements
        return statements

    def print_tree(self, indent=""):
        for node in self.statements:
            self.print_recursive(node, indent)
        
    def print_recursive(self, node, indent):
        if node is None:
            return

        if isinstance(node, Assignment):

            print(indent + "Assignment")
            print(indent + "├── " + str(node.target.value))

            print(indent + "└── Expr")
            self.print_recursive(node.expr, indent + "    ")

        elif isinstance(node, BinaryOp):

            print(indent + f"BinaryOp({node.op.value})")

            print(indent + "├── Left")
            self.print_recursive(node.left, indent + "│   ")

            print(indent + "└── Right")
            self.print_recursive(node.right, indent + "    ")

        elif isinstance(node, UnaryOp):

            print(indent + f"UnaryOp({node.op.value})")

            print(indent + "└── Operand")
            self.print_recursive(node.operand, indent + "    ")

        else:
            print(indent + str(node.value))


    def move(self):
        self.idx += 1

        if self.idx < len(self.tokens):
            self.token = self.tokens[self.idx]