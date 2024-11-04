import tkinter as tk
from tkinter import filedialog, messagebox
from instructions import *  # Importer votre répertoire d'instructions
from compilateur import compile_draw_code, parse_code
import os

class DrawPPIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw++ IDE")
        
        # Création de l'éditeur de texte
        self.text_area = tk.Text(root, wrap='none', undo=True)
        self.text_area.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Création d'une barre de menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
        
        # Menu Fichier
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Exit", command=root.quit)
        
        # Menu Exécution
        self.run_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Run", menu=self.run_menu)
        self.run_menu.add_command(label="Run", command=self.run_draw_code)

        #menu compilation
        self.compile_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Compile", menu=self.compile_menu)
        self.compile_menu.add_command(label="Compile", command=self.compile_draw_code)

        #menu help readme
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.help_menu.add_command(label="Get help", command=self.open_readme)
        self.menu.add_cascade(label="Help", menu=self.help_menu)

        # Drawing aera
        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(side="right", fill="both", expand=True)

    def open_readme(self):
        readme_path="README.md"
        os.system(f'start {readme_path}')
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Draw++ Files", "*.dpp")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.root.title(f"Draw++ IDE - {file_path}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".dpp", filetypes=[("Draw++ Files", "*.dpp")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"Draw++ IDE - {file_path}")

    def run_draw_code(self):
        # Récupérer le code Draw++ dans l'éditeur
        code = self.text_area.get(1.0, tk.END)

        # Effacer la zone de dessin
        self.canvas.delete("all")

        # Interpréter et exécuter les instructions Draw++
        self.interpret_draw_code(code)

    def compile_draw_code(self):
        """Compile le code Draw++ en code C."""
        code = self.text_area.get(1.0, tk.END)

        # Tente de compiler le code
        try:
            compile_draw_code(code)  # Appel à votre fonction de compilation
            messagebox.showinfo("Compilation réussie", "Le code a été compilé avec succès en output.c")
        except Exception as e:
            messagebox.showerror("Erreur de compilation", str(e))

    def interpret_draw_code(self, code):
        # Analyse du code Draw++ pour obtenir les instructions
        instructions = parse_code(code)  # Utilise le parser pour obtenir les instructions

        # Variables pour gérer la position et l'état de dessin
        current_x, current_y = 100, 100  # Position initiale arbitraire

        for instruction in instructions:
            command = instruction[0]

            if command == "move_to":
                x, y = instruction[1], instruction[2]
                current_x, current_y = x, y
            elif command == "line_to":
                x, y = instruction[1], instruction[2]
                self.canvas.create_line(current_x, current_y, x, y)
                current_x, current_y = x, y
            elif command == "set_color":
                color = instruction[1]
                self.canvas.itemconfig("all", fill=color)
            elif command == "circle":
                radius = instruction[1]
                self.canvas.create_oval(current_x - radius, current_y - radius,
                                        current_x + radius, current_y + radius)
            # Ajoutez ici d'autres commandes Draw++ si nécessaire

if __name__ == "__main__":
    root = tk.Tk()
    ide = DrawPPIDE(root)
    root.mainloop()
