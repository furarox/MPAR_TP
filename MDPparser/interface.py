import sys
from tkinter import Tk, Label, Entry, Button, StringVar

from PIL import Image, ImageTk

from drawgraph import graphDrawer
from mdp import init_graph


def afficher_image(texte_boite, alphabet, state, chemin, histo_proba,
                   label_image, label, bouton_afficher):
    action = texte_boite.get()
    if action not in alphabet:
        return None
    alphabet = state.run(action, chemin, histo_proba)
    graphDrawer(state)
    # Fonction pour afficher l'image après avoir cliqué sur le bouton
    # Charge l'image avec PIL
    image_pil = Image.open("test.png")
    # dans la boîte de texte
    image_tk = ImageTk.PhotoImage(image_pil)

    # Met à jour l'image dans le widget Label
    label_image.config(image=image_tk)
    label_image.image = image_tk  # Garde une référence pour éviter la
    # suppression par le ramasse-miettes

    # Change le texte du label et du bouton
    if alphabet == [""]:
        label.config(text=f"L'état actuel est probabiliste, le chemin "
                          f"parcouru est {chemin[-10:]}, avec une proba de "
                          f"{proba(histo_proba):e}")
    else:
        label.config(text=f'Veuillez choisir une action parmi {alphabet}, '
                          f'le chemin est {chemin[-10:]}, avec une proba de {proba(histo_proba):e}')

    bouton_afficher.config(text="Passer au prochain état")
    texte_boite.set("")


def proba(histo_proba):
    res = 1.
    for el in histo_proba:
        res = res * el
    return res


def main():
    state = init_graph(sys.argv)
    # Crée une fenêtre Tkinter
    fenetre = Tk()
    fenetre.title("Affichage d'une image")

    alphabet = None
    chemin = []
    histo_proba = [1]

    # Crée une variable de chaîne pour stocker le texte de la boîte de texte
    texte_boite = StringVar()

    # Crée un label à côté de la boîte de texte
    label = Label(fenetre, text="Choissisez l'état initial")
    label.pack()

    # Crée une boîte de texte (Entry) pour permettre à l'utilisateur d'écrire
    boite_texte = Entry(fenetre, textvariable=texte_boite)
    boite_texte.pack()

    # Crée un widget Label pour afficher l'image
    label_image = Label(fenetre)
    label_image.pack()

    bouton_afficher = Button(fenetre,
                             text="Lancer la simulation",
                             command=lambda: afficher_image(texte_boite,
                                                            alphabet,
                                                            state, chemin,
                                                            histo_proba,
                                                            label_image,
                                                            label,
                                                            bouton_afficher))
    bouton_afficher.pack()
    # Lance la boucle principale de la fenêtre Tkinter
    fenetre.mainloop()


if __name__ == '__main__':
    main()
