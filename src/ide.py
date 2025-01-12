import tkinter as tk
from lexer import Lexer
from parser import Parser
from tkinter import filedialog, messagebox, ttk
from compilateur import ast_to_c
import os
import subprocess
import math
import re

class DrawPPIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ IDE")
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
        
        # Ajout d'un onglet par défaut "New File"
        self.new_tab()
        
        # Zone de sortie pour afficher les résultats de l'exécution
        self.output_area = tk.Text(root, height=10, state="disabled", bg="#f0f0f0")
        self.output_area.pack(fill='x')
        # Événements pour la sélection multiple
       

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

    def compile_draw_code(self): 
        """Fonction qui traduit le code Draw++ en C et exécute le fichier C compilé."""
        # Récupérer le widget texte de l'onglet actif
        text_area = self.get_current_text_widget()
        tab_name = self.get_current_tab_name()  # Nom de l'onglet actif
        code = text_area.get(1.0, tk.END)
        text_area.tag_remove("error", "1.0", tk.END)  # Supprimer les erreurs existantes
        self.output_area.config(state="normal")
        self.output_area.delete(1.0, tk.END)
        errors = []

        if tab_name.startswith("New File"):  
            self.output_area.insert(tk.END, "Veuillez enregistrer le fichier avant de compiler.\n")
            self.save_file()  
            return
        lexer = Lexer(code)
        tokens = lexer.get_tokens()
        for token in tokens:
            print(token)
        try:
            parser = Parser(tokens) 
            instructions = parser.parse()  
            if parser.errors:  
                print("Erreurs de syntaxe détectées :")
                for error_message in parser.errors:
                    print(error_message)
                    match = re.search(r"line (\d+), column (\d+)", error_message)
                    if match:
                        line_number = int(match.group(1))
                        errors.append((line_number, error_message))
                    else:
                        errors.append((1, error_message))
            else:
                print("Instructions générées par le parser :")
                print(instructions)
        except Exception as e:
            error_message = str(e)
            print(f"Erreur critique détectée : {error_message}")
            match = re.search(r"line (\d+), column (\d+)", error_message)
            if match:
                line_number = int(match.group(1))
                errors.append((line_number, error_message))
            else:
                errors.append((1, error_message))

        if errors:
            text_area.tag_config("error", background="yellow", foreground="red")
            for line_number, error_message in errors:
                start_index = f"{line_number}.0"  
                end_index = f"{line_number}.end"  
                text_area.tag_add("error", start_index, end_index)  
            self.output_area.config(state="normal")  
            self.output_area.insert(tk.END, "Erreurs de syntaxe détectées :\n")
            for line_number, error_message in errors:
                self.output_area.insert(tk.END, f"Ligne {line_number}: {error_message}\n")
            self.output_area.config(state="disabled")  
            return  
        
        try:
            print("Début de la génération du code C...")
            c_code = ast_to_c(instructions)
            print("Code C généré avec succès.")

            c_filename = f"{tab_name}.c"  
            print(f"Nom du fichier C : {c_filename}")

            with open(c_filename, "w") as c_file:
                c_file.write(c_code)

            self.output_area.insert(tk.END, f"Compilation réussie : code compilé dans {c_filename}\n")
        except Exception as e:
            self.output_area.insert(tk.END, f"Erreur de compilation drawpp ici -> C : {str(e)}\n")
            self.output_area.config(state="disabled")
            return

        try:
            library_source = "src/graphic.c"
            library_object = "src/graphic.o"
            library_output = "lib/libgraphic.a"
            #compilation bibliothèque graphic
            compile_library_command = ["gcc", "-c", library_source, "-o", library_object, "-Iinclude"]
            result_lib = subprocess.run(compile_library_command, capture_output=True, text=True)
            if result_lib.returncode != 0:
                raise RuntimeError(f"Erreur lors de la compilation de graphic.c : {result_lib.stderr}")
            else:
                print(f"Compilation de graphic.c réussie : {result_lib.stdout}")
            create_library_command = ["ar", "rcs", library_output, library_object]
            result_ar = subprocess.run(create_library_command, capture_output=True, text=True)
            if result_ar.returncode != 0:
                raise RuntimeError(f"Erreur lors de la création de libgraphic.a : {result_ar.stderr}")
            else:
                print(f"Bibliothèque libgraphic.a créée avec succès : {result_ar.stdout}")
            #compilation de l'executable
            executable_name = f"bin/{tab_name}_executable"  
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
