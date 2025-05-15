import pygame

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# RGB Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize Pygame
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers with Scoring and Kinging')

# Try to load crown icon (optional)
try:
    CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (44, 25))
except:
    CROWN = None

class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king and CROWN:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

class Board:
    def __init__(self):
        self.board = []
        self.selected = None
        self.valid_moves = {}
        self.turn = WHITE
        self.score = {RED: 0, WHITE: 0}
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row < 3 and (row + col) % 2 == 1:
                    self.board[row].append(Piece(row, col, RED))
                elif row > 4 and (row + col) % 2 == 1:
                    self.board[row].append(Piece(row, col, WHITE))
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)
        self.highlight_valid_moves(win)
        self.draw_score(win)

    def get_piece(self, row, col):
        return self.board[row][col]

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
        if (piece.color == WHITE and row == 0) or (piece.color == RED and row == ROWS - 1):
            piece.make_king()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        else:
            piece = self.get_piece(row, col)
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.get_valid_moves(piece)

    def _move(self, row, col):
        piece = self.selected
        if (row, col) in self.valid_moves:
            self.move(piece, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board[skipped.row][skipped.col] = 0
                self.score[self.turn] += 1
            self.change_turn()
            return True
        return False

    def get_valid_moves(self, piece):
        moves = {}
        directions = [-1, 1] if piece.king else ([-1] if piece.color == WHITE else [1])
        for d in directions:
            for dx in [-1, 1]:
                r = piece.row + d
                c = piece.col + dx
                if 0 <= r < ROWS and 0 <= c < COLS:
                    target = self.get_piece(r, c)
                    if target == 0:
                        moves[(r, c)] = None
                    elif target.color != piece.color:
                        r2 = r + d
                        c2 = c + dx
                        if 0 <= r2 < ROWS and 0 <= c2 < COLS and self.get_piece(r2, c2) == 0:
                            moves[(r2, c2)] = target
        return moves

    def highlight_valid_moves(self, win):
        for move in self.valid_moves:
            r, c = move
            pygame.draw.circle(win, BLUE, (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.turn = RED if self.turn == WHITE else WHITE

    def draw_score(self, win):
        font = pygame.font.SysFont('arial', 30)
        red_score = font.render(f'Red: {self.score[RED]}', True, RED)
        white_score = font.render(f'White: {self.score[WHITE]}', True, WHITE)
        win.blit(red_score, (10, 10))
        win.blit(white_score, (WIDTH - 150, 10))

def get_row_col_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def main():
    run = True
    clock = pygame.time.Clock()
    board = Board()

    while run:
        clock.tick(60)
        board.draw(WIN)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                board.select(row, col)

    pygame.quit()

if __name__ == "__main__":
    main()