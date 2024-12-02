import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from instructions import *  # Importer votre répertoire d'instructions
from compilateur import compile_draw_code
from parser import load_grammar, parse_code
import os
import math

class DrawPPIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ IDE")
        
        # Charger la grammaire
        self.grammar = load_grammar('grammar.bnf')
        self.new_file_counter = 1
        self.modified_tabs = {}
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
        self.run_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(label="Run", command=self.run_draw_code)

        # Menu Compilation
        self.compile_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Compile", menu=self.compile_menu)
        self.compile_menu.add_command(label="Compile", command=self.compile_draw_code)

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
        
        # Ajout d'un onglet par défaut "New File"
        self.new_tab()
        
        # Zone de sortie pour afficher les résultats de l'exécution
        self.output_area = tk.Text(root, height=10, state="disabled", bg="#f0f0f0")
        self.output_area.pack(fill='x')

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
        cursor_state = {}

        for command, var_name, *args in instructions:
            if command == "cursor":
                color, x, y = args
                cursor_state[var_name] = {"x": x, "y": y, "color": color}
                cursor_size = 5
                # Créez un rectangle pour représenter le curseur sur le canvas
                cursor_state[var_name]["id"] = self.canvas.create_rectangle(
                    x - cursor_size, y - cursor_size,
                    x + cursor_size, y + cursor_size,
                    fill=color, outline=color)
            
            elif command == "move_to":
                x, y = args
                if var_name in cursor_state:
                    # Mise à jour visuelle de la position du curseur
                    cursor_info = cursor_state[var_name]
                    # Déplacer le rectangle représentant le curseur
                    self.canvas.coords(cursor_info["id"], 
                                    x - 5, y - 5, x + 5, y + 5)
                    cursor_info["x"], cursor_info["y"] = x, y  # Mettre à jour la position interne

            elif command == "move_by":
                # Extraire les arguments : angle et distance
                angle, distance = args
                
                # Vérifier si le curseur existe dans l'état des curseurs
                if var_name not in cursor_state:
                    cursor_state[var_name] = {"x": 0, "y": 0, "id": None}  # Position initiale (0, 0)
                
                # Utiliser la fonction move_by pour calculer la nouvelle position
                current_x, current_y = cursor_state[var_name]["x"], cursor_state[var_name]["y"]
                new_x, new_y = move_by(self.canvas, current_x, current_y, angle, distance)
                
                # Mettre à jour les coordonnées internes du curseur dans l'état
                cursor_state[var_name]["x"], cursor_state[var_name]["y"] = new_x, new_y
                
                # Si le curseur n'a pas encore de rectangle, le créer
                if cursor_state[var_name]["id"] is None:
                    cursor_state[var_name]["id"] = self.canvas.create_rectangle(
                        new_x - 5, new_y - 5, new_x + 5, new_y + 5, fill="blue", outline="blue")
                else:
                    # Mettre à jour les coordonnées du rectangle pour le curseur
                    self.canvas.coords(cursor_state[var_name]["id"], 
                                    new_x - 5, new_y - 5, new_x + 5, new_y + 5)
            elif command == "line_to":
                x, y = args
                if var_name in cursor_state:
                        cursor_info = cursor_state[var_name]
                        self.canvas.create_line(cursor_info["x"], cursor_info["y"], x, y)
                        # Déplacer le curseur visuellement à la nouvelle position
                        self.canvas.coords(cursor_info["id"], 
                                        x - 5, y - 5, x + 5, y + 5)
                        cursor_info["x"], cursor_info["y"] = x, y

            elif command == "set_color":
                color = args[0]
                if var_name in cursor_state:
                    cursor_info = cursor_state[var_name]
                    cursor_info["color"] = color
                    # Changez la couleur visuelle du curseur
                    self.canvas.itemconfig(cursor_info["id"], fill=color, outline=color)

            elif command == "circle":
                radius = args[0]
                if var_name in cursor_state:
                    x, y = cursor_state[var_name]["x"], cursor_state[var_name]["y"]
                    # Dessine un cercle autour de la position actuelle du curseur
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius)
            elif command == "line_by":
                angle, distance = args
                if var_name in cursor_state:
                    # Récupérer la position actuelle du curseur
                    cursor_info = cursor_state[var_name]
                    current_x, current_y = cursor_info["x"], cursor_info["y"]
                    
                    # Appeler la fonction line_by pour tracer la ligne et obtenir la nouvelle position
                    new_x, new_y = line_by(self.canvas, current_x, current_y, angle, distance)
                    
                    # Mettre à jour la position du curseur dans l'état interne
                    cursor_info["x"], cursor_info["y"] = new_x, new_y
                    
                    # Déplacer le rectangle représentant le curseur
                    self.canvas.coords(cursor_info["id"], new_x - 5, new_y - 5, new_x + 5, new_y + 5)

        
        self.output_area.insert(tk.END, "Exécution réussie.\n")
        self.output_area.config(state="disabled")

    def compile_draw_code(self):
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

        try:
            compile_draw_code(code, self.grammar)
            self.output_area.insert(tk.END, "Compilation réussie : code compilé dans output.c\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"Erreur de compilation : {str(e)}\n")
        
        self.output_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    ide = DrawPPIDE(root)
    root.mainloop()
