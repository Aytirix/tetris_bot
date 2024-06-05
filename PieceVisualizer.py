import matplotlib.pyplot as plt
import numpy as np

class PieceVisualizer:
    def __init__(self, pieces):
        self.pieces = pieces
        self.current_piece = 1
        self.current_rotation = 0
        self.grid_size = (20, 10)
        self.fig, self.ax = plt.subplots()

    def plot_piece(self):
        self.ax.clear()
        grid = np.zeros(self.grid_size)
        shape = self.pieces[self.current_piece][self.current_rotation]
        for x, y in shape:
            grid[x, y] = 1
        self.ax.imshow(grid, cmap='gray', extent=[0, 10, 0, 20])
        self.ax.set_xticks(np.arange(0, 11, 1))
        self.ax.set_yticks(np.arange(0, 21, 1))
        self.ax.grid(True)
        self.ax.set_title(f"Piece {self.current_piece} - Rotation {self.current_rotation}")
        plt.draw()

    def next_rotation(self, event):
        self.current_rotation = (self.current_rotation + 1) % len(self.pieces[self.current_piece])
        self.plot_piece()

    def previous_rotation(self, event):
        self.current_rotation = (self.current_rotation - 1) % len(self.pieces[self.current_piece])
        self.plot_piece()

    def next_piece(self, event):
        self.current_piece = (self.current_piece % len(self.pieces)) + 1
        self.current_rotation = 0
        self.plot_piece()

    def previous_piece(self, event):
        self.current_piece = (self.current_piece - 2) % len(self.pieces) + 1
        self.current_rotation = 0
        self.plot_piece()

    def show(self):
        self.plot_piece()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.show()

    def on_key(self, event):
        if event.key == 'right':
            self.next_rotation(event)
        elif event.key == 'left':
            self.previous_rotation(event)
        elif event.key == 'up':
            self.next_piece(event)
        elif event.key == 'down':
            self.previous_piece(event)

pieces = {
			1: [  # T shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 6)],  # Original
				[(1, 5), (2, 5), (3, 5), (2, 6)],   # 270 degrees
				[(1, 5), (1, 6), (1, 7), (2, 6)],  # 180 degrees
				[(1, 6), (2, 6), (3, 6), (2, 5)]  # 90 degrees
			],
			2: [  # L shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 7)],  # Original
				[(1, 5), (2, 5), (3, 5), (3, 6)],  # 90 degrees
				[(1, 5), (1, 6), (1, 7), (2, 5)],  # 180 degrees
				[(1, 5), (1, 6), (2, 6), (3, 6)]   # 270 degrees
			],
			3: [  # J shape rotations
				[(2, 5), (2, 6), (2, 7), (1, 5)],  # Original
				[(1, 5), (2, 5), (3, 5), (1, 6)],   # 270 degrees
				[(1, 5), (1, 6), (1, 7), (2, 7)],  # 180 degrees
				[(1, 6), (2, 6), (3, 6), (3, 5)]  # 90 degrees
			],
			4: [  # O shape (only one rotation)
				[(1, 5), (1, 6), (2, 5), (2, 6)]   # Original
			],
			5: [  # I shape rotations
				[(1, 5), (2, 5), (3, 5), (4, 5)],  # Original
				[(1, 5), (1, 6), (1, 7), (1, 8)]   # 90 degrees
			],
			6: [  # S shape rotations
				[(2, 5), (2, 6), (1, 6), (1, 7)],  # Original
				[(1, 5), (2, 5), (2, 6), (3, 6)]   # 90 degrees
			],
			7: [  # Z shape rotations
				[(1, 5), (1, 6), (2, 6), (2, 7)],  # Original
				[(1, 6), (2, 6), (2, 5), (3, 5)]   # 90 degrees
			]
		}

visualizer = PieceVisualizer(pieces)
visualizer.show()
