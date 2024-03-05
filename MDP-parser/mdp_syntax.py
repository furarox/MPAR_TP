from random import random
from gramListener import gramListener


class gramSyntax(gramListener):

    def __init__(self):
        self.states = {}
        self.actions = []
        self.trans_act = {}
        self.trans_noact = {}
        self.c_state = None
        self.states_action = {}

    def enterDefstates(self, ctx):
        for x in ctx.ID():
            self.states[str(x)] = 0
            self.states_action[str(x)] = []

        if len(self.states) != len(set(self.states)):
            raise ValueError("Un même état est défini plusieurs fois")

    def enterDefactions(self, ctx):
        self.actions = [str(x) for x in ctx.ID()]
        if len(self.states) != len(set(self.states)):
            raise ValueError("Une même action est définie plusieurs fois")

    def enterTransact(self, ctx):
        tmp = [str(x) for x in ctx.ID()]
        dep = tmp.pop(0)
        act = tmp.pop(0)
        weight = [int(str(x)) for x in ctx.INT()]

        if dep not in self.states:
            raise ValueError("Une transition a été declaré avec "
                             "un état non existant")
        elif self.states[dep] == 1:
            raise ValueError("Une transition possède à la fois des transitions "
                             "avec action et avec probabilité")

        if self.states[dep] == 0:
            self.states[dep] = 2

        if act not in self.actions:
            raise ValueError("Une transition a été déclarée avec une action hors "
                             "de l'alphabet")

        s = sum(weight)
        if (dep, act) in self.trans_act:
            raise ValueError("Une transition avec action sur un même état a été déclaré deux fois")
        self.states_action[dep].append(act)
        self.trans_act[(dep, act)] = []

        for a, w in zip(tmp, weight):
            self.trans_act[(dep, act)].append((a, w / s))

    def enterTransnoact(self, ctx):
        tmp = [str(x) for x in ctx.ID()]
        dep = tmp.pop(0)
        weight = [int(str(x)) for x in ctx.INT()]

        if dep not in self.states:
            raise ValueError("Une transition a été declaré avec "
                             "un état non existant")
        elif self.states[dep] == 1:
            raise ValueError("Une transition possède à la fois des transitions "
                             "avec action et avec probabilité")

        if self.states[dep] == 0:
            self.states[dep] = 1

        s = sum(weight)
        if dep in self.trans_noact:
            raise ValueError("Une transition sur un même état a été déclaré deux fois")
        self.trans_noact[dep] = []

        for a, w in zip(tmp, weight):
            if w < 0:
                raise ValueError("Un poids a été défini négatif")
            self.trans_noact[dep].append((a, w / s))

    def run(self, action=""):
        if action != "" and action not in self.states_action[self.c_state]:
            raise ValueError("L'action choisie n'est pas dans l'alphabet déclaré")

        if self.states[self.c_state] == 1:
            rnd = random()
            iterator = iter(self.trans_noact[(self.c_state)])
            d, w = next(iterator)
            rnd = rnd - w
            while rnd > 0:
                d, w = next(iterator)
                rnd = rnd - w

            print(f"Transition entre l'état {self.c_state} et l'état {d}")
            self.c_state = d

        elif self.states[self.c_state] == 2:
            rnd = random()
            iterator = iter(self.trans_act[(self.c_state, action)])
            d, w = next(iterator)
            rnd = rnd - w
            while rnd > 0:
                d, w = next(iterator)
                rnd = rnd - w

            print(f"Transition entre l'état {self.c_state} et l'état {d}")
            self.c_state = d

        if self.states[self.c_state] == 1:
            print("L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")

    def init_run(self, state):
        self.c_state = state
        if self.states[self.c_state] == 1:
            print("L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")

    def check(self):
        for v in self.states:
            if v == 0:
                raise ValueError("Un état n'a pas de transitions définies")
