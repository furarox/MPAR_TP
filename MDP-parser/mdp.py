from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from mdp_syntax import gramSyntax
from drawgraph import graphDrawer


class gramPrintListener(gramListener):

    def __init__(self):
        pass

    def enterDefstates(self, ctx):
        print("States: %s" % str([str(x) for x in ctx.ID()]))

    def enterDefactions(self, ctx):
        print("Actions: %s" % str([str(x) for x in ctx.ID()]))

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        print("Transition from " + dep + " with action " + act +
              " and targets "
              + str(ids) + " with weights " + str(weights))

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        print("Transition from " + dep + " with no action and targets "
              + str(ids) + " with weights " + str(weights))


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = gramLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    state = gramSyntax()
    walker.walk(state, tree)
    print(state.states)
    print(state.actions)
    print(state.trans_act)
    print(state.trans_noact)
    state.init_run('S0')
    graphDrawer(state)
    while True:
        a = input()
        if a == '':
            state.run()
        else:
            state.run(a)
        graphDrawer(state)


if __name__ == '__main__':
    main(sys.argv)
