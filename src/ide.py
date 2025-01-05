import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from instructions import *  # Importer votre répertoire d'instructions
from compilateur import compile_draw_code
from parser import load_grammar, parse_code
import os
import subprocess
import math

class DrawPPIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ IDE")
        
        # Charger la grammaire
        self.grammar = load_grammar('src/grammar.bnf')
        self.new_file_counter = 1
        self.modified_tabs = {}
        self.cursor_state = {}
        self.selected_item = None
        self.selection_rectangle = None
        self.start_x = None
        self.start_y = None
        self.move_start_x = None
        self.move_start_y = None  # Stocker l'objet actuellement sélectionné
        self.objects = {}
        # Création de la barre de menus
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
        
        # Menu Fichier
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Tab", command=self.new_tab)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Exit", command=root.quit)
        
        # Menu Exécution
        #self.run_menu = tk.Menu(self.menu, tearoff=0)
        #self.menu.add_cascade(label="Run", menu=self.run_menu)
        #self.run_menu.add_command(label="Run", command=self.run_draw_code)

        # Menu Compilation
        self.compile_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Execute", menu=self.compile_menu)
        self.compile_menu.add_command(label="Execute", command=self.compile_draw_code)

        #menu help readme
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.help_menu.add_command(label="Get help", command=self.open_readme)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        
        # Création du Notebook (onglets)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
        
        # Initialisation de la zone de dessin
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.select_object)  # Lier l'événement clic gauche
        
        # Ajout d'un onglet par défaut "New File"
        self.new_tab()
        
        # Zone de sortie pour afficher les résultats de l'exécution
        self.output_area = tk.Text(root, height=10, state="disabled", bg="#f0f0f0")
        self.output_area.pack(fill='x')
        # Événements pour la sélection multiple
        self.canvas.bind("<Button-1>", self.start_selection)  # Clic gauche
        self.canvas.bind("<B1-Motion>", self.update_selection)  # Glissement
        self.canvas.bind("<ButtonRelease-1>", self.complete_selection)  # Relâchement du bouton
        self.canvas.bind("<Button-2>", self.start_drag)  # Clic central pour démarrer le déplacement
        self.canvas.bind("<B2-Motion>", self.drag_objects)  # Glisser avec le clic central maintenu
        self.canvas.bind("<ButtonRelease-2>", self.stop_drag)  # Relâcher le clic central
        
    def select_object(self, event):
        clicked_items = self.canvas.find_withtag("current")  # Objets sous le clic
        self.clear_selection()

        if clicked_items:
            self.selected_item = clicked_items[0]
            # Récupérer les tags de l'objet
            tags = self.canvas.gettags(self.selected_item)
            print(f"Objet sélectionné avec tags : {tags}")

            # Vérifier le type d'objet et appliquer une mise en surbrillance adaptée
            item_type = self.canvas.type(self.selected_item)
            if item_type in ("rectangle", "oval", "polygon"):  # Types d'objets qui supportent "outline"
                self.canvas.itemconfig(self.selected_item, outline="blue", width=2)
            elif item_type == "line":  # Les lignes n'ont pas de "outline", mais ont une largeur
                self.canvas.itemconfig(self.selected_item, width=3, fill="blue")


    def start_selection(self, event):
        """Commence un rectangle de sélection."""
        self.start_x = event.x
        self.start_y = event.y
        # Supprime les sélections existantes
        self.clear_selection()
        # Dessine un rectangle de sélection temporaire
        self.selection_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="black", dash=(4, 4), tags="selection_rectangle"
        )

    def update_selection(self, event):
        """Met à jour le rectangle de sélection."""
        if self.selection_rectangle:
            self.canvas.coords(self.selection_rectangle, self.start_x, self.start_y, event.x, event.y)

    def complete_selection(self, event):
        """Complète la sélection et met en évidence les objets sélectionnés."""
        if self.selection_rectangle:
            # Obtenir les coordonnées du rectangle
            end_x, end_y = event.x, event.y
            x1, y1, x2, y2 = self.normalize_coordinates(self.start_x, self.start_y, end_x, end_y)

            # Trouver les objets dans la zone
            overlapping_items = self.canvas.find_enclosed(x1, y1, x2, y2)
            selectable_items = [item for item in overlapping_items if "selectable" in self.canvas.gettags(item)]

            # Mettre en évidence les objets sélectionnés
            self.highlight_selection(selectable_items)

            # Supprime le rectangle de sélection temporaire
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None

    def normalize_coordinates(self, x1, y1, x2, y2):
        """Retourne les coordonnées dans le bon ordre (haut-gauche à bas-droite)."""
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def highlight_selection(self, items):
        """Met en évidence les objets sélectionnés."""
        self.clear_selection()  # Réinitialise toute sélection précédente
        self.selected_item = items  # Met à jour la sélection actuelle
        for item in items:
            item_type = self.canvas.type(item)
            if item_type in ("rectangle", "oval", "polygon"):
                self.canvas.itemconfig(item, outline="blue", width=2)
            elif item_type == "line":
                self.canvas.itemconfig(item, width=3, fill="blue")

    def start_drag(self, event):
        """Déclenche le déplacement des objets sélectionnés."""
        if not self.selected_item:
            return  # Ne rien faire si aucun objet n'est sélectionné
        self.start_x = event.x
        self.start_y = event.y
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, "Déplacement commencé.\n")
        self.output_area.config(state="disabled")

    def drag_objects(self, event):
        """Déplace les objets sélectionnés pendant le glisser."""
        if not self.selected_item:
            return
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        for item in self.selected_item:
            # Déplace chaque objet sélectionné
            self.canvas.move(item, dx, dy)
            new_coords = self.canvas.coords(item)
            self.objects[item] = new_coords  # Mise à jour dans la structure

            print(f"Nouvelles coordonnées pour {item} : {new_coords}")  # Vérification
        self.start_x = event.x
        self.start_y = event.y


    def stop_drag(self, event):
        """Termine le déplacement des objets sélectionnés."""
        self.output_area.config(state="normal")
        self.output_area.insert(tk.END, "Déplacement terminé.\n")
        self.output_area.config(state="disabled")

    def clear_selection(self):
        """Réinitialise la sélection visuelle."""
        if not isinstance(self.selected_item, list):
            self.selected_item = [self.selected_item] if self.selected_item else []

        for item in self.selected_item:
            item_type = self.canvas.type(item)
            if item_type in ("rectangle", "oval", "polygon"):
                self.canvas.itemconfig(item, outline="", width=1)
            elif item_type == "line":
                self.canvas.itemconfig(item, width=1, fill="black")
        self.selected_item = []  # Réinitialise l'état de sélection


    def new_tab(self, title=None):
        if title is None:
            title = f"New File {self.new_file_counter}"
            self.new_file_counter += 1 
        """Créer un nouvel onglet avec un éditeur de texte vierge."""
        
        # Frame de l'onglet
        frame = tk.Frame(self.notebook)
        
        # Bouton "FERMER" dans l'onglet
        close_button = tk.Button(frame, text="FERMER", command=lambda: self.close_tab(frame))
        close_button.pack(anchor='ne', padx=5, pady=5)
        
        # Zone de texte pour l'éditeur
        text_area = tk.Text(frame, wrap='none', undo=True)
        text_area.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        text_area.bind("<<Modified>>", lambda event, tab=title: self.on_text_modified(tab, text_area))
        
        
        # Ajouter l'onglet avec le titre et sélectionner le nouvel onglet
        self.notebook.add(frame, text=title)
        self.notebook.select(frame)
        self.modified_tabs[title] = False

    def on_text_modified(self, tab, text_area):
        """Marque l'onglet comme modifié si des changements sont détectés."""
        if text_area.edit_modified():
            self.modified_tabs[tab] = True
            text_area.edit_modified(False)  # Réinitialiser l'indicateur de modification interne de Tkinter

    def close_tab(self, frame):
    
        tab_text = self.notebook.tab(frame, "text")
    
        # Vérifier si l'onglet a été modifié
        if self.modified_tabs.get(tab_text, False):
            save_before_closing = messagebox.askyesnocancel("Enregistrer avant de fermer",
                                                            "Souhaitez-vous enregistrer les modifications de cet onglet ?")
            if save_before_closing:  # Si l'utilisateur veut enregistrer
                self.save_file()
                self.notebook.forget(frame)
            elif save_before_closing is None:  # Si l'utilisateur annule
                return
            else:  # Si l'utilisateur ne veut pas enregistrer
                self.notebook.forget(frame)
        else:
            self.notebook.forget(frame)

    def get_current_text_widget(self):
        """Récupère l'éditeur de texte de l'onglet actif."""
        current_tab = self.notebook.select()
        current_frame = self.notebook.nametowidget(current_tab)
        for widget in current_frame.winfo_children():
            if isinstance(widget, tk.Text):
                return widget  # Retourne le Text widget dans l'onglet actif

    def open_readme(self):
        readme_path="README.md"
        os.system(f'start {readme_path}')

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Draw++ Files", "*.dpp")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
            self.new_tab(title=os.path.basename(file_path))
            text_area = self.get_current_text_widget()
            text_area.insert(tk.END, content)
            self.modified_tabs[os.path.basename(file_path)] = {'path': file_path, 'modified': False}
            self.root.title(f"Draw++ IDE - {file_path}")

    def save_file(self):
        text_area = self.get_current_text_widget()
        file_path = filedialog.asksaveasfilename(defaultextension=".dpp", filetypes=[("Draw++ Files", "*.dpp")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(text_area.get(1.0, tk.END))
            self.notebook.tab("current", text=os.path.basename(file_path))  # Met à jour le nom de l'onglet
            self.root.title(f"Draw++ IDE - {file_path}")
            self.modified_tabs[text_area] = False

    def get_current_tab_name(self):
        return self.notebook.tab(self.notebook.select(), "text")

    def run_draw_code(self):
        text_area = self.get_current_text_widget()
        code = text_area.get(1.0, tk.END)
        text_area.tag_remove("error", "1.0", tk.END)
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        
        instructions, errors = parse_code(code, self.grammar)

        for line_number, line in errors:
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.{len(line)}"
            text_area.tag_add("error", start_index, end_index)
            text_area.tag_config("error", background="yellow", foreground="red")

        if errors:
            self.output_area.insert(tk.END, "Erreur de syntaxe : vérifiez les lignes en surbrillance.\n")
            self.output_area.config(state="disabled")
            return
        
        self.canvas.delete("all")
        self.cursor_state = {}
        variables = {}

        for command, var_name, *args in instructions:
            if command == "declare":
                if var_name in variables:
                    self.output_area.insert(tk.END, f"Erreur : La variable '{var_name}' est déjà déclarée.\n")
                    continue
                if len(args) != 1:
                    self.output_area.insert(tk.END, f"Erreur : Mauvaise déclaration pour '{var_name}'.\n")
                    continue
                value = args[0]
                variables[var_name] = value

            elif command == "modify":
                new_value = args[0]
                if var_name in variables:
                    variables[var_name] = new_value
                    self.output_area.insert(tk.END, f"Variable '{var_name}' modifiée à {new_value}.\n")
                else:
                    self.output_area.insert(tk.END, f"Erreur : Variable '{var_name}' non déclarée.\n")
                    continue

            if command == "cursor":
                color, x, y = args
                self.cursor_state[var_name] = {"x": x, "y": y, "color": color}
                cursor_size = 5
                # Créez un rectangle pour représenter le curseur sur le canvas
                self.cursor_state[var_name]["id"] = self.canvas.create_rectangle(
                    x - cursor_size, y - cursor_size,
                    x + cursor_size, y + cursor_size,
                    fill=color, outline=color,
                    tags="selectable")
            
            elif command == "move_to":
                x, y = args
                if var_name in self.cursor_state:
                    # Mise à jour visuelle de la position du curseur
                    cursor_info = self.cursor_state[var_name]
                    self.canvas.coords(cursor_info["id"], x - 5, y - 5, x + 5, y + 5)
                    # Mise à jour interne des coordonnées
                    self.cursor_state[var_name]["x"], self.cursor_state[var_name]["y"] = x, y

            elif command == "move_by":
                # Extraire les arguments : angle et distance
                angle, distance = args
                
                # Vérifier si le curseur existe dans l'état des curseurs
                if var_name not in self.cursor_state:
                    self.cursor_state[var_name] = {"x": 0, "y": 0, "id": None}  # Position initiale (0, 0)
                
                # Utiliser la fonction move_by pour calculer la nouvelle position
                current_x, current_y = self.cursor_state[var_name]["x"], self.cursor_state[var_name]["y"]
                new_x, new_y = move_by(self.canvas, current_x, current_y, angle, distance)
                
                # Mettre à jour les coordonnées internes du curseur dans l'état
                self.cursor_state[var_name]["x"], self.cursor_state[var_name]["y"] = new_x, new_y
                
                # Si le curseur n'a pas encore de rectangle, le créer
                if self.cursor_state[var_name]["id"] is None:
                    self.cursor_state[var_name]["id"] = self.canvas.create_rectangle(
                        new_x - 5, new_y - 5, new_x + 5, new_y + 5, fill="blue", outline="blue")
                else:
                    # Mettre à jour les coordonnées du rectangle pour le curseur
                    self.canvas.coords(self.cursor_state[var_name]["id"], 
                                    new_x - 5, new_y - 5, new_x + 5, new_y + 5)
            elif command == "line_to":
                x, y = args
                if var_name in self.cursor_state:
                        cursor_info = self.cursor_state[var_name]
                        cursor_color = cursor_info.get("color", "black")
                        self.canvas.create_line(
                            cursor_info["x"], 
                            cursor_info["y"], x, y,
                            tags="selectable",fill=cursor_color  )
                        # Déplacer le curseur visuellement à la nouvelle position
                        self.canvas.coords(cursor_info["id"], 
                                        x - 5, y - 5, x + 5, y + 5)
                        cursor_info["x"], cursor_info["y"] = x, y

            elif command == "set_color":
                color = args[0]
                if var_name in self.cursor_state:
                    cursor_info = self.cursor_state[var_name]
                    cursor_info["color"] = color
                    # Changez la couleur visuelle du curseur
                    self.canvas.itemconfig(cursor_info["id"], fill=color, outline=color)

            elif command == "circle":
                radius = args[0]
                if var_name in self.cursor_state:
                    cursor_info = self.cursor_state[var_name]
                    x, y = self.cursor_state[var_name]["x"], self.cursor_state[var_name]["y"]
                    cursor_color = cursor_info.get("color", "black")  # Récupérer la couleur actuelle du curseur, noir par défaut
                    # Dessine un cercle autour de la position actuelle du curseur
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, tags="selectable",fill=cursor_color  )

            elif command == "line_by":
                angle, distance = args
                if var_name in self.cursor_state:
                    # Récupérer la position actuelle du curseur et sa couleur
                    cursor_info = self.cursor_state[var_name]
                    current_x, current_y = cursor_info["x"], cursor_info["y"]
                    cursor_color = cursor_info.get("color", "black")  # Récupérer la couleur actuelle du curseur, noir par défaut
                    
                    # Calculer la nouvelle position en utilisant la fonction line_by
                    new_x, new_y = line_by(self.canvas, current_x, current_y, angle, distance)
                    
                    # Tracer une ligne sur le canevas avec la couleur du curseur et le tag 'selectable'
                    self.canvas.create_line(
                        current_x, current_y, new_x, new_y, 
                        tags="selectable",
                        fill=cursor_color  # Utiliser la couleur du curseur pour la ligne
                    )
                    
                    # Mettre à jour la position du curseur dans l'état interne
                    cursor_info["x"], cursor_info["y"] = new_x, new_y
                    
                    # Déplacer le rectangle représentant le curseur
                    self.canvas.coords(cursor_info["id"], new_x - 5, new_y - 5, new_x + 5, new_y + 5)


        self.output_area.insert(tk.END, "Exécution réussie.\n")
        self.output_area.config(state="disabled")

    def compile_draw_code(self): 
        # Fonction qui traduit le code drawpp en C et exécute le fichier C compilé.
        text_area = self.get_current_text_widget()
        tab_name = self.get_current_tab_name()  # Récupérer le nom de l'onglet actif
        code = text_area.get(1.0, tk.END)
        text_area.tag_remove("error", "1.0", tk.END)
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        # Vérifier si le fichier est enregistré
        if tab_name.startswith("New File"):  # Nom temporaire
            self.output_area.insert(tk.END, "Veuillez enregistrer le fichier avant de compiler.\n")
            self.save_file()  # Ouvre une boîte de dialogue pour enregistrer
            return
        # Parse le code en utilisant la grammaire définie
        instructions, errors = parse_code(code, self.grammar)

        # Gestion des erreurs de syntaxe
        for line_number, line in errors:
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.{len(line)}"
            text_area.tag_add("error", start_index, end_index)
            text_area.tag_config("error", background="yellow", foreground="red")
        
        if errors:
            self.output_area.insert(tk.END, "Erreur de syntaxe : le problème est ici.\n")
            self.output_area.config(state="disabled")
            return

        # Étape 1 : Compilation du code drawpp en C
        try:
            c_code = compile_draw_code(code, self.grammar)  # Fonction existante qui retourne le code C
            c_filename = f"src/{tab_name}.c"  # Utiliser le nom de l'onglet pour le fichier C
            with open(c_filename, "w") as c_file:
                c_file.write(c_code)
            self.output_area.insert(tk.END, f"Compilation réussie : code compilé dans {c_filename}\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"Erreur de compilation drawpp -> C : {str(e)}\n")
            self.output_area.config(state="disabled")
            return

        # Étape 2 : Compilation du fichier C en exécutable
        try:
            executable_name = f"bin/{tab_name}_executable"  # Nommer l'exécutable en fonction de l'onglet
            compile_command = [
                "gcc", "-o", executable_name, c_filename, "-Llib", "-lgraphic", "-Iinclude", "-lSDL2"
            ]
            result = subprocess.run(compile_command, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            self.output_area.insert(tk.END, f"Compilation C réussie : exécutable {executable_name} généré.\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"Erreur de compilation C : {str(e)}\n")
            self.output_area.config(state="disabled")
            return

        # Étape 3 : Exécution du fichier compilé
        try:
            execution_command = f"./{executable_name}"
            subprocess.run(execution_command, check=True)
            self.output_area.insert(tk.END, f"Exécution réussie de l'exécutable {executable_name}.\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"Erreur lors de l'exécution de l'exécutable : {str(e)}\n")

        self.output_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    ide = DrawPPIDE(root)
    root.mainloop()
