from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from MDPparser.gramLexer import gramLexer
from MDPparser.gramListener import gramListener
from MDPparser.gramParser import gramParser
import sys
from MDPparser.mdp_syntax import gramSyntax


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
    walker = ParseTreeWalker()
    state = gramSyntax()
    walker.walk(state, tree)
    state.c_state = list(state.states.keys())[0]

    return state


if __name__ == '__main__':
    state = init_graph(sys.argv)
    S, res = state.calc_final_state_mdp('W')
    print(res.x)
