import tkinter as tk

class Tetris_map(tk.Frame):
    def __init__(self, master=None, title="Tetris"):
        super().__init__(master)
        self.master = master
        self.master.title(title)
        self.grid_size = (10, 20)  # Dimensions de la grille Tetris (largeur, hauteur)
        self.cells = [[None for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]
        self.init_grid()
        self.pack()

    def init_grid(self):
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                cell_frame = tk.Frame(self, width=30, height=30, bg='white', borderwidth=1, relief="solid")
                cell_frame.grid(row=y, column=x, padx=1, pady=1)
                self.cells[y][x] = cell_frame

    def update_grid(self, grid):
        """Mise à jour de la grille à partir d'un tableau bidimensionnel."""
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                color = 'white'  # couleur par défaut
                if grid[y][x] == 1:
                    color = 'purple'
                elif grid[y][x] == 2:
                    color = 'blue'
                elif grid[y][x] == 3:
                    color = 'orange'
                elif grid[y][x] == 4:
                    color = 'yellow'
                elif grid[y][x] == 5:
                    color = 'brown'
                elif grid[y][x] == 6:
                    color = 'red'
                elif grid[y][x] == 7:
                    color = 'green'
                self.cells[y][x].config(bg=color)

    def run_game_update(self):
        """Fonction récurrente pour simuler le jeu (à compléter)."""
        self.master.after(500, self.run_game_update)  # Mettre à jour toutes les 500 ms