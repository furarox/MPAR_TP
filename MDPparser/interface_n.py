import pathlib
import sys
from tkinter import Tk, Label, Entry, Button, StringVar, Toplevel

from PIL import Image, ImageTk

from MDPparser.drawgraph import graphDrawer
from MDPparser.mdp import init_graph


def main():
    # Initialisation des différentes variables
    state = init_graph(sys.argv)
    chemin = []
    histo_proba = [1]
    alphabet = [state.states]

    # Fenetre principale de Tkinter
    fenetre = Tk()
    fenetre.title(sys.argv[1])

    # Gestion des entrées de l'utilisateur
    first_state = list(state.states.keys())[0]
    text_box = StringVar(value=first_state)
    label = Label(fenetre, text="Etat initial")
    label.pack()

    box_text = Entry(fenetre, textvariable=text_box)
    box_text.pack()

    # Button pour commencer l'application
    button_simulation = Button(fenetre,
                               text="Lancer la simulation",
                               command=lambda: afficher_image(
                                   state,
                                   alphabet,
                                   chemin,
                                   histo_proba,
                                   text_box,
                                   label_image,
                                   label
                               ))
    button_simulation.pack()

    label_image = Label(fenetre)
    label_image.pack()

    button_new_window = Button(fenetre,
                               text="Effectuer des calculs",
                               command=lambda: calculus_window(
                                   fenetre,
                                   state
                               ))
    button_new_window.pack()

    fenetre.mainloop()


def afficher_image(state,
                   alphabet,
                   chemin,
                   histo_proba,
                   text_box,
                   label_image,
                   label
                   ):
    action = text_box.get()
    if action not in alphabet[0]:
        return None

    if action in state.states:
        alphabet[0] = state.init_run(action, chemin)
    else:
        alphabet[0] = state.run(action, chemin, histo_proba)
    graphDrawer(state)

    # Charge l'image avec PIL
    image_pil = Image.open("test.png")
    image_tk = ImageTk.PhotoImage(image_pil)

    label_image.config(image=image_tk)
    label_image.image = image_tk

    if alphabet[0] == [""]:
        label.config(text=f"L'état actuel est probabiliste, le chemin "
                          f"parcouru est {chemin[-10:]}, avec une proba de "
                          f"{proba(histo_proba):e}")
    else:
        label.config(text=f'Veuillez choisir une action parmi {alphabet}, '
                          f'le chemin est {chemin[-10:]}, avec une proba de {proba(histo_proba):e}')

    text_box.set("")


def proba(histo_proba):
    res = 1.
    for el in histo_proba:
        res = res * el
    return res


def calculus_window(main_window, state):
    n_window = Toplevel(main_window)
    n_window.title("Fenêtre de calcul")

    label = Label(n_window, text="Choissisez le calcul à effectuer")
    label.pack()

    button_PCTL = Button(n_window,
                         text="Algorithme PCTL",
                         command=lambda: PCTL_Window(
                             n_window,
                             state
                         ))
    button_PCTL.pack()

    buttonIterVal = Button(n_window,
                           text="Algorithme IterVal",
                           command=lambda: IterValWindow(
                               n_window,
                               state
                           ))
    buttonIterVal.pack()

    button_Qlearning = Button(n_window,
                              text="Algorithme Qlearning",
                              command=lambda: QlearningWindow(
                                  n_window,
                                  state
                              ))
    button_Qlearning.pack()

    button_MC = Button(n_window,
                       text="Algorithme Monte-Carlo",
                       command=lambda: MC_Window(
                           n_window,
                           state
                       ))
    button_MC.pack()

    button_SPRT = Button(n_window,
                         text="Algorithme SPRT",
                         command=lambda: SPRT_Window(
                             n_window,
                             state
                         ))
    button_SPRT.pack()


def SPRT_Window(main_window, state):
    sprt_window = Toplevel(main_window)
    sprt_window.title("SPRT")

    text_deb_state = StringVar()
    text_final_state = StringVar()
    text_nb_simulation = StringVar()
    text_p = StringVar()
    text_eps = StringVar()
    text_alpha = StringVar()
    text_beta = StringVar()

    label_deb_state = Label(sprt_window,
                            text="Choissisez un état de départ de trace")
    label_deb_state.pack()
    box_deb_state = Entry(sprt_window,
                          textvariable=text_deb_state)
    box_deb_state.pack()
    label_end_state = Label(sprt_window,
                            text="choisissez un groupe d'états finaux ("
                                 "séparés par un espace)")
    label_end_state.pack()
    box_final_state = Entry(sprt_window,
                            textvariable=text_final_state)
    box_final_state.pack()
    label_nb_simulation = Label(sprt_window,
                                text="choisissez la longueur des traces")
    label_nb_simulation.pack()
    box_nb_simulation = Entry(sprt_window,
                              textvariable=text_nb_simulation)
    box_nb_simulation.pack()
    label_delta = Label(sprt_window,
                        text="Choisissez une probabilité (on vérifie si >= p)")
    label_delta.pack()
    box_delta = Entry(sprt_window,
                      textvariable=text_p)
    box_delta.pack()
    label_eps = Label(sprt_window,
                      text="Choisissez une précision (eps)")
    label_eps.pack()
    box_eps = Entry(sprt_window,
                    textvariable=text_eps)
    box_eps.pack()
    label_alpha = Label(sprt_window,
                        text="Choix de alpha")
    label_alpha.pack()
    box_alpha = Entry(sprt_window,
                      textvariable=text_alpha)
    box_alpha.pack()
    label_beta = Label(sprt_window,
                       text="Choix de beta")
    label_beta.pack()
    box_beta = Entry(sprt_window,
                     textvariable=text_beta)
    box_beta.pack()
    label_res = Label(sprt_window)
    label_res.pack()

    button_simulation = Button(sprt_window,
                               text="Lancer la simulation",
                               command=lambda: affiche_SPRT(
                                   state,
                                   float(text_p.get()),
                                   float(text_eps.get()),
                                   float(text_alpha.get()),
                                   float(text_beta.get()),
                                   text_deb_state.get(),
                                   text_final_state.get().split(),
                                   int(text_nb_simulation.get()),
                                   label_res
                               ))
    button_simulation.pack()


def affiche_SPRT(state, teta, epsilon,
                 alpha, beta,
                 deb_state, end_state,
                 nb_simulation, label_res):
    res = state.sprt(teta, epsilon, alpha, beta, deb_state, end_state,
                     nb_simulation)
    label_res.config(text=f'Propriété {res}')


def MC_Window(main_window, state):
    mc_window = Toplevel(main_window)
    mc_window.title("Monte-Carlo")

    text_deb_state = StringVar()
    text_final_state = StringVar()
    text_nb_simulation = StringVar()
    text_delta = StringVar()
    text_eps = StringVar()

    label_deb_state = Label(mc_window,
                            text="Choissisez un état de départ de trace")
    label_deb_state.pack()
    box_deb_state = Entry(mc_window,
                          textvariable=text_deb_state)
    box_deb_state.pack()
    label_end_state = Label(mc_window,
                            text="choisissez un groupe d'états finaux ("
                                 "séparés par un espace)")
    label_end_state.pack()
    box_final_state = Entry(mc_window,
                            textvariable=text_final_state)
    box_final_state.pack()
    label_nb_simulation = Label(mc_window,
                                text="choisissez la longueur des traces")
    label_nb_simulation.pack()
    box_nb_simulation = Entry(mc_window,
                              textvariable=text_nb_simulation)
    box_nb_simulation.pack()
    label_delta = Label(mc_window,
                        text="Choisissez une marge d'erreur (delta)")
    label_delta.pack()
    box_delta = Entry(mc_window,
                      textvariable=text_eps)
    box_delta.pack()
    label_eps = Label(mc_window,
                      text="Choisissez une précision (eps)")
    label_eps.pack()
    box_eps = Entry(mc_window,
                    textvariable=text_delta)
    box_eps.pack()

    label_res = Label(mc_window)
    label_res.pack()

    button_mc = Button(mc_window,
                       text="Lancer la simulation",
                       command=lambda: MC_affiche(
                           state,
                           text_deb_state.get(),
                           text_final_state.get().split(),
                           int(text_nb_simulation.get()),
                           float(text_delta.get()),
                           float(text_eps.get()),
                           label_res
                       ))
    button_mc.pack()


def MC_affiche(state, deb_state, end_state,
               nb_simulation, delta, eps,
               window_label):
    res = state.monte_carlo(delta, eps, deb_state, end_state, nb_simulation)
    window_label.config(text=f"La probabilité d'atteindre les états finaux "
                             f"est de {res}")


def QlearningWindow(main_window, state):
    qlearningwindow = Toplevel(main_window)
    qlearningwindow.title('Qlearning')

    nb_simulation = StringVar()
    label_nb_simulation = Label(qlearningwindow,
                                text="Choisissez un nombre de simulation")
    label_nb_simulation.pack()
    box_nb_simulation = Entry(qlearningwindow,
                              textvariable=nb_simulation)
    box_nb_simulation.pack()

    button_simulation = Button(qlearningwindow,
                               text="Lancer la simulation",
                               command=lambda: Qlearning_affiche(
                                   qlearningwindow,
                                   state,
                                   int(nb_simulation.get())
                               ))

    button_simulation.pack()


def Qlearning_affiche(main_window, state, nb_simulation):

    total_reward, opponent, Qf = state.Q_learning(n_tot=nb_simulation)

    text = "Q value pour les différents couples état.action : \n"
    for state_ in list(state.states.keys()):
        if state.states[state_] == 2:
            for action in state.states_action[state_]:
                text += f'Q({state_}, {action}) : {Qf[state_, action]}\n '
        elif state.states[state_] == 1:
            action = None
            text += f'Q({state_}, {action}) : {Qf[state_, action]}, '

    text += "\nLe meilleur adversaire retenu est le suivant : \n"
    for state_, act in opponent.items():
        text += f'{state_}.{act}\n'

    text += f'La récompense totale obtenue sur la simulation est {total_reward}'

    label = Label(main_window,
                  text=text)
    label.pack()


def IterValWindow(main_window, state):
    window_iterval = Toplevel(main_window)
    window_iterval.title("IterVal")

    V, opponent = state.iter_val()

    text = ("L'algorithme IterVal trouves les valeurs suivantes pour la "
            "fonction d'espérance : \n")
    states = list(state.reward.keys())
    for state_, v in zip(states, V):
        text += f"{state_}: {v} \n"

    text += "Et trouve comme meilleur adversaire le suivant : \n"
    for state_, act in zip(states, opponent):
        text += f'{state_}.{act}\n'

    label = Label(window_iterval,
                  text=text)
    label.pack()


def PCTL_Window(main_window, state):
    window_PCTL = Toplevel(main_window)
    window_PCTL.title("PCTL")
    label = Label(window_PCTL, text="choisissez les états finaux (écrire les "
                                    "états finaux separés par un espace)")
    label.pack()

    text_box = StringVar()
    box_text = Entry(window_PCTL, textvariable=text_box)
    box_text.pack()

    start_button = Button(window_PCTL,
                          text="Lancer le calcul",
                          command=lambda: affiche_PCTL(
                              state,
                              label,
                              text_box
                          ))
    start_button.pack()


def affiche_PCTL(state,
                 label,
                 text_box
                 ):
    final_states = text_box.get().split()
    states = list(state.states.keys())
    for state_ in final_states:
        if state_ not in states:
            return None

    test_mc = True
    for state_value in state.states.values():
        if state_value == 2:
            test_mc = False

    if test_mc:
        S, res = state.calc_prob_final_state_mc(final_states)
        text = (f"La probabilité (non triviale) d'atteindre un des états "
                f"finaux depuis les états suivants: \n")
        for state_, p in zip(S, res):
            text += f'{state_}: {p}\n'
    else:
        S, res = state.calc_final_state_mdp(final_states)
        res = res.x
        text = (f"La probabilité (non triviale) d'atteindre un des états "
                f"finaux depuis les états suivants en suivant la meilleure "
                f"action (non calculée): \n")
        for state_, p in zip(S, res):
            text += f'{state_}: {p}\n'

    label.config(text=text)


def wrapper_main():
    try:
        main()
    finally:
        path = pathlib.Path.cwd()
        path = path / "test.png"
        if path.exists():
            path.unlink()


if __name__ == '__main__':
    wrapper_main()