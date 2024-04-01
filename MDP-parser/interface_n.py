import sys
from tkinter import Tk, Label, Entry, Button, StringVar, Toplevel

from PIL import Image, ImageTk

from drawgraph import graphDrawer
from mdp import init_graph


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
                         text="PCTL",
                         command=lambda: PCTL_Window(
                             n_window,
                             state
                         ))
    button_PCTL.pack()


def PCTL_Window(main_window, state):
    window_PCTL = Toplevel(main_window)
    label = Label(window_PCTL, text="Choisisez les états finaux (écrire les "
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


if __name__ == '__main__':
    main()

