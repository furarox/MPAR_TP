from random import random
import numpy as np
from gramListener import gramListener
from scipy.optimize import linprog


class gramSyntax(gramListener):

    def __init__(self):
        self.states = {}
        self.actions = []
        self.trans_act = {}
        self.trans_noact = {}
        self.c_state = None
        self.states_action = {}
        self.pred = {}

    def enterDefstates(self, ctx):
        for x in ctx.ID():
            self.states[str(x)] = 0
            self.states_action[str(x)] = []
            self.pred[str(x)] = []

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
            self.pred[a].append((dep, w / s))

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
            self.pred[a].append((dep, w / s))

    def run(self, action, histo_state, histo_proba):
        if action != "" and action not in self.states_action[self.c_state]:
            raise ValueError("L'action choisie n'est pas dans l'alphabet déclaré")

        if action != "":
            histo_state.append(action)

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
            histo_state.append(d)
            histo_proba.append(w)

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
            histo_state.append(d)
            histo_proba.append(w)

        if self.states[self.c_state] == 1:
            print("L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")
            return [""]

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")
            return actions

    def init_run(self, state, chemin):
        self.c_state = state
        chemin.append(state)
        if self.states[self.c_state] == 1:
            print("L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")
            return [""]

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")
            return actions

    def check(self):
        for v in self.states:
            if v == 0:
                raise ValueError("Un état n'a pas de transitions définies")

    def calc_S0_S1_S_rec(self, last_state, S1, S):
        pred_explo = []
        for pred, w in self.pred[last_state]:
            if self.states[pred] == 1:
                if pred in S1 or pred in S:
                    continue
                test = True
                for child, p in self.trans_noact[pred]:
                    if child not in S1:
                        test = False
                if test:
                    S1.append(pred)
                else:
                    S.append(pred)

                pred_explo.append(pred)

            elif self.states[pred] == 2:
                if pred in S1 or pred in S:
                    continue
                test = True
                for action in self.states_action[pred]:
                    for child, p in self.trans_act[(pred, action)]:
                        if child not in S1:
                            test = False
                if test:
                    S1.append(pred)
                else:
                    S.append(pred)

                pred_explo.append(pred)

        for pred in pred_explo:
            self.calc_S0_S1_S_rec(pred, S1, S)

    def calc_S0_S1_S(self, last_state):
        S1 = [last_state]
        S = []
        self.calc_S0_S1_S_rec(last_state, S1, S)
        S0 = []
        for state in self.states:
            if state not in S1 and state not in S:
                S0.append(state)

        return S0, S1, S

    def calc_A_b_mc(self, S: list, S1):
        A = np.zeros((len(S), len(S)))
        b = np.zeros(len(S))
        for row, state in enumerate(S):
            next_states = self.trans_noact[state]
            for next_state, p in next_states:
                if next_state in S:
                    col = S.index(next_state)
                    A[row, col] = p

                elif next_state in S1:
                    b[row] += p

        return A, b

    def calc_prob_final_state_mc(self, final_state):
        S0, S1, S = self.calc_S0_S1_S(final_state)
        A, b = self.calc_A_b_mc(S, S1)

        identity = np.eye(len(S))

        res = np.matmul(np.linalg.inv(identity - A),  b.reshape((len(S), 1)))
        print(A.shape)
        print(b.shape)
        print(res.shape)

        return S, res

    def calc_A_b_mdp(self, S, S1):
        action_list = []
        for state in S:
            if self.states[state] == 1:
                action_list.append([None])
            else:
                action_list.append(self.states_action[state])

        A = np.zeros((sum([len(x) for x in action_list]), len(S)))
        print(action_list)
        b = np.zeros(sum([len(x) for x in action_list]))

        for i, state in enumerate(S):
            row = sum([len(x) for x in action_list[:i]])
            if self.states[state] == 1:
                next_states = self.trans_noact[state]
                for next_state, p in next_states:
                    if next_state in S:
                        col = S.index(next_state)
                        A[row, col] += p
                    elif next_states in S1:
                        b[row] += p
                col_state = S.index(state)
                A[row, col_state] -= 1

            elif self.states[state] == 2:
                for ii, act in enumerate(action_list[i]):
                    next_states = self.trans_act[(state, act)]
                    for next_state, p in next_states:
                        if next_state in S:
                            col = S.index(next_state)
                            A[row+ii, col] += p
                        elif next_state in S1:
                            b[row+ii] += p

                    col_state = S.index(state)
                    A[row+ii, col_state] -= 1

        return A, -b

    def calc_final_state_mdp(self, final_state):
        S0, S1, S = self.calc_S0_S1_S(final_state)
        A, b = self.calc_A_b_mdp(S, S1)

        c = [1 for _ in S]

        res = linprog(c, A_ub=A, b_ub=b, bounds=(0, 1))
        return res
