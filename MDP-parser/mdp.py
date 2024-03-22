from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from mdp_syntax import gramSyntax


class gramPrintListener(gramListener):

    def __init__(self):
        pass

    def enterDefstates_no_rewards(self, ctx: gramParser.Defstates_no_rewardsContext):
        print("States: %s" % str([str(x) for x in ctx.ID()]))

    def enterDefstates_rewards(self, ctx:gramParser.Defstates_rewardsContext):
        print("States: %s" % str([str(x) for x in ctx.ID()]))
        print("Reward %s" % str([str(x) for x in ctx.INT()]))

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
    state.c_state = list(state.states.keys())[0]
    print(state.states)
    print(state.actions)
    print(state.trans_act)
    print(state.trans_noact)
    print(state.reward)

    return state


if __name__ == '__main__':
    state = init_graph(sys.argv)
    print(state.iter_val())
    Q_f, best_opponent = state.Q_learning()
    print(Q_f)
    for key, act in best_opponent.items():
        print(f'Action selected in state {key} : {act}')
