from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from mdp_syntax import gramSyntax


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


def init_graph(argv):
    # Init phase
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

    return state


if __name__ == '__main__':
    state = init_graph(sys.argv)
    S0, S1, S = state.calc_S0_S1_S('S1')
    print(S0)
    print(S1)
    print(S)
    A, b = state.calc_A_b_mdp(S, S1)
    print(A)
    print(b)
    res = state.calc_final_state_mdp('S1')
    print(res.x)
