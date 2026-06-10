from .tokens import Token, Integer, Operation, Declaration, Variable

class Lexer:
    digits = "01"
    letters = "abcdefghijklmnopqrstuvwxyz"
    operations = "+*^~()=,"
    stopwords = [" ", "\n", "\t"]
    declarations = ["make", "inputs", "outputs"]

    def __init__(self, text):
        self.text = text
        self.idx = 0
        self.tokens = []
        self.char = self.text[self.idx]
        self.token = None
    
    def tokenize(self):
        while self.idx < len(self.text):
            if self.char in Lexer.digits:
                self.token = Integer(self.char)
                self.move()
            
            elif self.char in Lexer.operations:
                if self.char == ',':
                    self.move()
                    continue
                else:
                    self.token = Operation(self.char)
                    self.move()
            elif self.char in Lexer.stopwords:
                self.move()
                continue

            elif self.char in Lexer.letters:
                word = self.extract_word()

                if word in Lexer.declarations:
                    self.token = Declaration(word)
                else:
                    self.token = Variable(word)
            
            self.tokens.append(self.token)
        
        self.tokens.append(Token("EOF", None))
        return self.tokens

    def extract_word(self):
        word = ""
        while self.char in Lexer.letters and self.idx < len(self.text):
            word += self.char
            self.move()
        
        return word
    
    def move(self):
        self.idx += 1
        if self.idx < len(self.text):
            self.char = self.text[self.idx]
