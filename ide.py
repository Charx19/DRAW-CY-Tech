import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
class SimpleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Python IDE")
        
        # Création de l'éditeur de texte
        self.text_area = tk.Text(root, wrap='none', undo=True)
        self.text_area.pack(fill='both', expand=True)
        
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
        self.run_menu.add_command(label="Run", command=self.run_code)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.root.title(f"Simple Python IDE - {file_path}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"Simple Python IDE - {file_path}")

    def run_code(self):
        # Sauvegarde du code actuel dans un fichier temporaire pour l'exécution
        code = self.text_area.get(1.0, tk.END)
        temp_file = "temp_code.py"
        with open(temp_file, 'w') as file:
            file.write(code)
        
        # Exécution du code Python et récupération de la sortie ou des erreurs
        result = subprocess.run(["python", temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            messagebox.showinfo("Output", result.stdout)
        else:
            messagebox.showerror("Error", result.stderr)
        
        # Suppression du fichier temporaire après exécution
        os.remove(temp_file)

if __name__ == "__main__":
    root = tk.Tk()
    ide = SimpleIDE(root)
    root.mainloop()
