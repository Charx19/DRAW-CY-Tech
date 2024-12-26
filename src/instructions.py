import tkinter as tk
import math

class DrawppInterpreter:
    def __init__(self, canvas):
        self.canvas = canvas
        self.cursors = {}  # Dictionnaire pour stocker les curseurs avec des noms
        self.cursor_positions = {}  # Dictionnaire pour stocker les positions des curseurs

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

def cursor(canvas, x, y, color="blue"):
    """Dessine un curseur à la position (x, y) avec une couleur spécifiée."""
    cursor_size = 5  # Taille du curseur visuel
    # Dessiner un petit carré représentant le curseur
    cursor_item = canvas.create_rectangle(x - cursor_size, y - cursor_size,
                                           x + cursor_size, y + cursor_size,
                                           fill=color, outline=color)
    return cursor_item

def move_by(canvas, current_x, current_y, angle, distance):
    """Déplace le curseur de 'distance' pixels dans la direction de 'angle' (en degrés)."""
    
    # Convertir l'angle en radians (car les fonctions trigonométriques en Python utilisent des radians)
    angle_rad = math.radians(angle)
    
    # Calculer les déplacements en x et y
    delta_x = math.cos(angle_rad) * distance
    delta_y = math.sin(angle_rad) * distance
    
    # Calculer la nouvelle position du curseur
    new_x = current_x + delta_x
    new_y = current_y + delta_y
    
    return new_x, new_y  # Retourner les nouvelles coordonnées

def line_by(canvas, current_x, current_y, angle, distance):
    """Trace une ligne de la position (current_x, current_y) selon un angle et une distance."""
    
    # Convertir l'angle en radians
    angle_rad = math.radians(angle)
    
    # Calculer les déplacements en x et y
    delta_x = math.cos(angle_rad) * distance
    delta_y = math.sin(angle_rad) * distance
    
    # Calculer la nouvelle position
    new_x = current_x + delta_x
    new_y = current_y + delta_y
    
    # Retourner la nouvelle position
    return new_x, new_y


