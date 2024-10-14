import tkinter as tk

def move_to(canvas, x, y):
    """Déplace le crayon sans dessiner à la position (x, y)."""
    return x, y  # Retourne la nouvelle position

def line_to(canvas, current_x, current_y, x, y):
    """Trace une ligne vers (x, y) depuis la position actuelle."""
    canvas.create_line(current_x, current_y, x, y)
    return x, y  # Retourne la nouvelle position

def set_color(canvas, color):
    """Change la couleur du trait."""
    canvas.itemconfig("all", fill=color)

def circle(canvas, current_x, current_y, radius):
    """Dessine un cercle à la position actuelle avec un rayon donné."""
    canvas.create_oval(current_x - radius, current_y - radius,
                       current_x + radius, current_y + radius)

# Ajoutez d'autres fonctions 
