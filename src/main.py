from frontend.lexer import Lexer
from frontend.parser import Parser
from frontend.expand import Expand
from mapping.map import Mapper

with open("example.make", "r") as f:
    source = f.read()

tokens = Lexer(source).tokenize()
print(tokens)
parser = Parser(tokens)

ast = parser.parse()
# print(ast)
expander = Expand(ast, parser.inputs, parser.outputs)
trees = expander.expand()
tree = trees[0]
mapper = Mapper(trees, 3)
res = mapper.map_trees()
root_lut = res[id(tree)][0]
mapper.print_circuit(root_lut)

