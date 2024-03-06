from tkinter import Tk, Label, Entry, Button, StringVar
from PIL import Image, ImageTk
import sys
from mdp import init_graph
from drawgraph import graphDrawer


def afficher_image():
    global alphabet
    action = texte_boite.get()
    if alphabet is None:
        if action not in state.states:
            return None
        else:
            alphabet = state.init_run(action)
    elif action not in alphabet:
        return None
    else:
        alphabet = state.run(action)
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
        label.config(text="L'état actuel est probabiliste")
    else:
        label.config(text=f'Veuillez choisir une action parmi {alphabet}')

    bouton_afficher.config(text="Passer au prochain état")
    texte_boite.set("")


alphabet = None

# Crée une fenêtre Tkinter
fenetre = Tk()
fenetre.title("Affichage d'une image")


# Crée une variable de chaîne pour stocker le texte de la boîte de texte
texte_boite = StringVar()

# Crée un label à côté de la boîte de texte
label = Label(fenetre, text="Choissisez l'état initial")
label.pack()

# Crée une boîte de texte (Entry) pour permettre à l'utilisateur d'écrire
boite_texte = Entry(fenetre, textvariable=texte_boite)
boite_texte.pack()

# Crée un bouton pour afficher l'image en fonction de l'entrée de l'utilisateur

bouton_afficher = Button(fenetre,
                         text="Lancer la simulation",
                         command=afficher_image)

bouton_afficher.pack()

# Crée un widget Label pour afficher l'image
label_image = Label(fenetre)
label_image.pack()


if __name__ == "__main__":
    state = init_graph(sys.argv)

# Lance la boucle principale de la fenêtre Tkinter
fenetre.mainloop()
