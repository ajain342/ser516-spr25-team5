from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from app.services.javaFileParsingDependencies.java_parser.JavaLexer import JavaLexer
from app.services.javaFileParsingDependencies.java_parser.JavaParser import JavaParser
from app.services.javaFileParsingDependencies.java_parser.JavaParserListener import JavaParserListener


class ParsingException(Exception):
    def __init__(self, message="Parsing Error occurred"):
        self.message = message
        super().__init__(self.message)

class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        offending_token = offendingSymbol if offendingSymbol else "Unknown"
        error_message = (
            f"Syntax Error: Invalid token '{offending_token}' "
            f"at Line {line}, Column {column}. "
            f"Parser expected one of the following: {msg}."
        )
        self.errors.append(error_message)



class Extractor(JavaParserListener):
    def __init__(self, java_code=""):
        self.operators = {}
        self.operands = {}

        if java_code:
            self._analyze(java_code)

    def visitTerminal(self, node):
        if not node or not node.symbol:
            return

        token = node.getText()
        token_type = node.symbol.type

        if token in {"+", "-", "*", "/", "=", ">", "<", "&&", "||", "!", "==", "!="}:
            self.operators[token] = self.operators.get(token, 0) + 1

        if token_type == JavaLexer.IDENTIFIER:
            self.operands[token] = self.operands.get(token, 0) + 1
        elif token_type in {
            JavaLexer.DECIMAL_LITERAL, JavaLexer.HEX_LITERAL, JavaLexer.OCT_LITERAL, JavaLexer.BINARY_LITERAL, JavaLexer.FLOAT_LITERAL
        }:
            self.operands[token] = self.operands.get(token, 0) + 1

    def get_params(self):
        return self.operators, self.operands

    def _analyze(self, java_code):
        try:
            lexer = JavaLexer(InputStream(java_code))
            stream = CommonTokenStream(lexer)
            parser = JavaParser(stream)

            error_listener = SyntaxErrorListener()
            parser.removeErrorListeners()
            parser.addErrorListener(error_listener)

            tree = parser.compilationUnit()

            if error_listener.errors:
                raise ParsingException(f"Parsing Errors in Java Code: {error_listener.errors[0]}")

            walker = ParseTreeWalker()
            walker.walk(self, tree)

        except ParsingException as e:
            raise ParsingException(f"Error occured while parsing file: {str(e)}")

        except Exception as e:
            raise Exception(f"Error occured while parsing file: {str(e)}")
