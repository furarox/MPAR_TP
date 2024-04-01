import random
import numpy as np
from MDPparser.gramListener import gramListener
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
        self.reward = {}

    def enterDefstates_rewards(self, ctx):
        for x, r in zip(ctx.ID(), ctx.INT()):
            self.states[str(x)] = 0
            self.states_action[str(x)] = []
            self.pred[str(x)] = []
            self.reward[str(x)] = int(str(r))

    def enterDefstates_no_rewards(self, ctx):
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
            raise ValueError(
                "Une transition possède à la fois des transitions "
                "avec action et avec probabilité")

        if self.states[dep] == 0:
            self.states[dep] = 2

        if act not in self.actions:
            raise ValueError(
                "Une transition a été déclarée avec une action hors "
                "de l'alphabet")

        s = sum(weight)
        if (dep, act) in self.trans_act:
            raise ValueError(
                "Une transition avec action sur un même état a été déclaré deux fois")
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
            raise ValueError(
                "Une transition possède à la fois des transitions "
                "avec action et avec probabilité")

        if self.states[dep] == 0:
            self.states[dep] = 1

        s = sum(weight)
        if dep in self.trans_noact:
            raise ValueError(
                "Une transition sur un même état a été déclaré deux fois")
        self.trans_noact[dep] = []

        for a, w in zip(tmp, weight):
            if w < 0:
                raise ValueError("Un poids a été défini négatif")
            self.trans_noact[dep].append((a, w / s))
            self.pred[a].append((dep, w / s))

    def run(self, action, histo_state, histo_proba):
        if action != "" and action not in self.states_action[self.c_state]:
            raise ValueError(
                "L'action choisie n'est pas dans l'alphabet déclaré")

        if action != "":
            histo_state.append(action)

        if self.states[self.c_state] == 1:
            rnd = random.random()
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
            rnd = random.random()
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
            print(
                "L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")
            return [""]

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(
                f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")
            return actions

    def init_run(self, state, chemin):
        self.c_state = state
        chemin.append(state)
        if self.states[self.c_state] == 1:
            print(
                "L'état actuel est probabliste, entrer 'enter' pour passer au prochain état")
            return [""]

        elif self.states[self.c_state] == 2:
            actions = [x[1] for x in self.trans_act if x[0] == self.c_state]
            print(
                f"L'état actuel est décisionnel, entrer l'action à choisir parmi les différentes actions suivantes : {actions}")
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
        if isinstance(last_state, str):
            S1 = [last_state]
        elif isinstance(last_state, list):
            S1 = last_state
        else:
            raise TypeError
        S = []
        for last_state in S1:
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

        res = np.matmul(np.linalg.inv(identity - A), b.reshape((len(S), 1)))
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
                            A[row + ii, col] += p
                        elif next_state in S1:
                            b[row + ii] += p

                    col_state = S.index(state)
                    A[row + ii, col_state] -= 1

        return A, -b

    def calc_final_state_mdp(self, final_state):
        S0, S1, S = self.calc_S0_S1_S(final_state)
        A, b = self.calc_A_b_mdp(S, S1)

        c = [1 for _ in S]

        res = linprog(c, A_ub=A, b_ub=b, bounds=(0, 1))
        return S, res

    def iter_val(self, gamma=0.9, eps=0.01):
        # Initialize V0
        V0 = np.zeros(len(self.states))
        states = list(self.reward.keys())
        rewards = list(self.reward.values())
        for i, rew in enumerate(rewards):
            V0[i] = rew

        V_pred = V0
        V_suiv = np.zeros(len(states))

        # Iter until ||V_suiv - V_pred|| < eps
        cond_fin = False
        while not cond_fin:
            for idx_state, state in enumerate(states):
                if self.states[state] == 1:
                    s = rewards[idx_state]
                    for next_state, p in self.trans_noact[state]:
                        s += gamma * p * V_pred[states.index(next_state)]
                    V_suiv[idx_state] = s

                elif self.states[state] == 2:
                    list_s = []
                    for act in self.states_action[state]:
                        s = rewards[idx_state]
                        for next_state, p in self.trans_act[(state, act)]:
                            s += gamma * p * V_pred[states.index(next_state)]
                        list_s.append(s)

                    V_suiv[idx_state] = max(list_s)

            if np.linalg.norm(V_suiv - V_pred) < eps:
                cond_fin = True

            V_pred = V_suiv

        # Compute the best opponent
        opponent = [None for _ in states]
        for i, state in enumerate(states):
            if self.states[state] == 1:
                pass
            elif self.states[state] == 2:
                list_s = []
                list_action = list(self.states_action[state])
                for act in list_action:
                    s = 0
                    for next_state, p in self.trans_act[(state, act)]:
                        s += gamma * p * V_pred[states.index(next_state)]
                    list_s.append(s)

                idx_act = np.argmax(np.array(list_s))
                opponent[i] = list_action[idx_act]

        return V_pred, opponent

    def select_state(self, state, step):
        return state

    def select_action(self, state, Q):
        p = random.random()
        if p < 0.1:
            if self.states[state] == 1:
                return None
            else:
                rnd_idx = random.randint(0, len(self.states_action[state]) - 1)
                return self.states_action[state][rnd_idx]
        else:
            if self.states[state] == 1:
                return None
            elif self.states[state] == 2:
                idx_max = 0
                l_action = self.states_action[state]
                # First check if we have tested a least once every action
                for action in l_action:
                    if Q[(state, action)] == self.reward[state]:
                        return action
                Q_max = Q[(state, l_action[0])]
                for i, act in enumerate(l_action):
                    if Q[(state, act)] > Q_max:
                        idx_max = i
                        Q_max = Q[(state, act)]
                return self.states_action[state][idx_max]

    def simulate(self, state, action=None):
        if self.states[state] == 1:
            s_and_p = self.trans_noact[state]
        else:
            s_and_p = self.trans_act[(state, action)]

        rnd = random.random()

        iterator = iter(s_and_p)
        d, w = next(iterator)
        rnd = rnd - w
        while rnd > 0:
            d, w = next(iterator)
            rnd = rnd - w

        return d, self.reward[state]

    def Q_learning(self, gamma=1 / 2):

        total_reward = 0
        alpha = {}
        for state, value in self.states.items():
            if value == 1:
                alpha[(state, None)] = 1
            elif value == 2:
                for action in self.states_action[state]:
                    alpha[(state, action)] = 1

        Q_f = self.init_Q()

        for _ in range(10_000):
            Q = self.init_Q()
            last_state = random.choice(list(self.states.keys()))

            for i in range(1, 100):
                last_state = self.select_state(last_state, i)
                action = self.select_action(last_state, Q)
                new_state, reward = self.simulate(last_state, action)
                total_reward += reward

                l_Q = []
                if self.states[new_state] == 1:
                    l_Q.append(Q[new_state, None])
                elif self.states[new_state] == 2:
                    for act in self.states_action[new_state]:
                        l_Q.append(Q[new_state, act])

                dt = reward + gamma * max(l_Q) - Q[last_state, action]
                Q[last_state, action] += dt / alpha[(last_state, action)]
                alpha[(last_state, action)] += 1

                last_state = new_state

            for key, value in Q.items():
                Q_f[key] += value

        best_opponent = {state: None for state in self.states.keys()}
        for state in best_opponent.keys():
            # Choose best action
            if self.states[state] == 1:
                continue

            act_max = self.states_action[state][0]
            Q_max = Q_f[(state, act_max)]
            for act in self.states_action[state][1:]:
                if Q_f[(state, act)] > Q_max:
                    act_max = act
                    Q_max = Q_f[(state, act)]

            best_opponent[state] = act_max

        return total_reward, best_opponent, Q_f

    def init_Q(self) -> dict:
        Q = {}
        for state, value in self.states.items():
            if value == 1:
                Q[(state, None)] = self.reward[state]
            elif value == 2:
                for action in self.states_action[state]:
                    Q[(state, action)] = self.reward[state]

        return Q

    def monte_carlo_rec(self, etat_debut, etat_final, limite_taille,
                        taille_parcours):
        self.c_state = etat_debut
        if self.states[self.c_state] == 2:
            raise ValueError(
                "impossible d'appliquer Monte Carlo ou SPRT à un MDP")
        if self.c_state in etat_final:
            return (1)
        elif taille_parcours == limite_taille:
            return (0)
        else:
            rnd = random.random()
            iterator = iter(self.trans_noact[(self.c_state)])
            d, w = next(iterator)
            rnd = rnd - w
            while rnd > 0:
                d, w = next(iterator)
                rnd = rnd - w
            self.c_state = d
            return (
                self.monte_carlo_rec(self.c_state, etat_final, limite_taille,
                                     taille_parcours + 1))

    def monte_carlo(self, delta, epsilon, etat_debut, etat_final,
                    limite_taille):
        N = int((np.log(2) - np.log(delta)) / (2 * epsilon) ** 2)
        res = 0
        for i in range(N):
            res += self.monte_carlo_rec(etat_debut, etat_final, limite_taille,
                                        0)
        return (res / N)

    def sprt(self, teta, epsilon, alpha, beta, etat_debut, etat_final,
             limite_taille):
        Rm = 1
        borne_A = (1 - beta) / alpha
        borne_B = beta / (1 - alpha)
        gamma_1 = teta - epsilon
        gamma_0 = teta + epsilon
        while Rm > borne_B and Rm < borne_A:
            if self.monte_carlo_rec(etat_debut, etat_final, limite_taille,
                                    0) == 1:
                Rm *= (gamma_1 / gamma_0)
            else:
                Rm *= (1 - gamma_1) / (1 - gamma_0)
        if Rm >= borne_A:
            return "rejetée"
        elif Rm <= borne_B:
            return "acceptée"
