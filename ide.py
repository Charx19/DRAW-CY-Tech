import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from instructions import *  # Importer votre répertoire d'instructions
from compilateur import compile_draw_code
from parser import load_grammar, parse_code
import os

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
        # Effacer les anciennes erreurs et la sortie précédente
        text_area.tag_remove("error", "1.0", tk.END)
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        
        # Analyser le code et obtenir les instructions et les erreurs
        instructions, errors = parse_code(code, self.grammar)

        # Afficher les erreurs de syntaxe
        for line_number, line in errors:
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.{len(line)}"
            text_area.tag_add("error", start_index, end_index)
            text_area.tag_config("error", background="yellow", foreground="red")

        if errors:
            self.output_area.insert(tk.END, "Erreur de syntaxe : vérifiez les lignes en surbrillance.\n")
            self.output_area.config(state="disabled")
            return
        
        # Initialiser la position et effacer la zone de dessin
        current_x, current_y = 100, 100
        self.canvas.delete("all")
        
        # Exécuter les instructions
        for command, *args in instructions:
            if command == "move_to":
                x, y = args
                self.canvas.create_line(current_x, current_y, x, y)
                current_x, current_y = x, y
            elif command == "line_to":
                x, y = args
                self.canvas.create_line(current_x, current_y, x, y)
                current_x, current_y = x, y
            elif command == "set_color":
                color = args[0]
                self.canvas.itemconfig("all", fill=color)
            elif command == "circle":
                radius = args[0]
                self.canvas.create_oval(current_x - radius, current_y - radius,
                                        current_x + radius, current_y + radius)

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
