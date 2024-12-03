from project.task11.GraphQueryLangLexer import GraphQueryLangLexer
from project.task11.GraphQueryLangParser import GraphQueryLangParser

import antlr4


class NodeCounter(antlr4.ParseTreeListener):
    def __init__(self):
        self.count = 0

    def enterEveryRule(self, ctx):
        self.count += 1


class ToProgramListener(antlr4.ParseTreeListener):
    def __init__(self) -> None:
        self.tokens = []

    def visitTerminal(self, node):
        self.tokens.append(node.getText())

    def getProgram(self):
        return " ".join(self.tokens)


def program_to_tree(program: str) -> tuple[antlr4.ParserRuleContext, bool]:
    program = program.replace("<EOF>", "EOF")
    lexer = GraphQueryLangLexer(antlr4.InputStream(program))
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = GraphQueryLangParser(token_stream)

    tree = parser.prog()

    if parser.getNumberOfSyntaxErrors() > 0:
        return (None, False)
    return (tree, True)


def nodes_count(tree: antlr4.ParserRuleContext) -> int:
    if tree:
        counter = NodeCounter()
        walker = antlr4.ParseTreeWalker()
        walker.walk(counter, tree)
        return counter.count
    return 0


def tree_to_program(tree: antlr4.ParserRuleContext) -> str:
    if tree:
        listener = ToProgramListener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(listener, tree)
        return listener.getProgram()
    return ""
