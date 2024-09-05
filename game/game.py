from queue import Queue
import pygame
import random
import copy
from game.button import Button


class GridGame:
    def __init__(
        self,
        send_victory_callback,
        grid,
        entity_position,
        entity_direction,
        solution_path=None,  # Solution path added here
        event_queue: Queue = Queue(),
        move_interval=30,
    ):
        pygame.init()
        self.width = 1200
        self.height = 1200
        self.input_data = (
            grid,
            tuple(entity_position),
            entity_direction,
            solution_path,
        )  # Store solution path
        assert len(grid) == len(grid[0])
        self.grid_size = len(grid)
        self.cell_size = self.width // self.grid_size
        self.border_size = 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grid Game with Arrow Entity")
        self.move_interval = move_interval
        self.game_over = False
        self.send_victory_callback = send_victory_callback
        self.history = []  # Stack to keep track of previous moves (for undo)
        self.autoplay = False  # Control variable for autoplay

        self.grid = copy.deepcopy(grid)
        self.entity_position = copy.deepcopy(tuple(entity_position))
        self.entity_direction = copy.deepcopy(entity_direction)
        self.solution_path = copy.deepcopy(solution_path)  # Store the solution path

        self.autoplay_index = 0  # Index for autoplaying solution

        self.entity_color = (255, 255, 255)  # White color for the arrow
        self.tick_count = 0
        self.moves_done = [self.entity_position]

        self.font = pygame.font.Font(None, 36)
        # Define buttons with improved graphics
        self.buttons = [
            Button(
                rect=(50, self.height - 100, 150, 50),
                color=(255, 0, 0),
                hover_color=(200, 0, 0),
                text="Undo",
                text_color=(255, 255, 255),
                font=self.font,
            ),
            Button(
                rect=(250, self.height - 100, 150, 50),
                color=(0, 255, 0),
                hover_color=(0, 200, 0),
                text="Checkpoint",
                text_color=(255, 255, 255),
                font=self.font,
            ),
            Button(
                rect=(450, self.height - 100, 200, 50),
                color=(0, 0, 255),
                hover_color=(0, 0, 200),
                text="Load Checkpoint",
                text_color=(255, 255, 255),
                font=self.font,
            ),
        ]
        self.won = False
        self.set_checkpoint()
        self.event_queue = event_queue
        self.messages = []

    def restart_game(self):
        self.color = self.get_random_color()
        self.entity_color = (255, 255, 255)
        self.tick_count = 0
        self.game_over = False
        self.moves_done = self.moves_done[:1]  # keep starting position for reduction
        self.autoplay = False
        self.autoplay_index = 0  # Reset autoplay index
        self.grid, self.entity_position, self.entity_direction, self.solution_path = (
            copy.deepcopy(self.input_data)
        )
        self.history = []
        self.set_checkpoint()

    def set_checkpoint(self):
        # Save the checkpoint (current grid and entity position)
        self.checkpoint_position = copy.deepcopy(self.entity_position)
        self.checkpoint_grid = copy.deepcopy(self.grid)
        self.checkpoint_moves = copy.deepcopy(self.moves_done)

    def load_checkpoint(self):
        # Load the checkpoint if it exists
        if self.checkpoint_position and self.checkpoint_grid:
            self.entity_position = copy.deepcopy(self.checkpoint_position)
            self.grid = copy.deepcopy(self.checkpoint_grid)
            self.moves_done = copy.deepcopy(self.checkpoint_moves)

    def undo_move(self):
        if self.history:
            # Pop the last move from history and restore the state
            self.grid, self.entity_position = self.history.pop()
        if len(self.moves_done) > 1:
            self.moves_done.pop()

    def get_random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def draw_arrow(self, position, direction):
        x, y = position
        center = (
            x * self.cell_size + self.cell_size // 2,
            y * self.cell_size + self.cell_size // 2,
        )
        size = self.cell_size // 2 - self.border_size
        directions = {
            "north": [
                (
                    center,
                    (center[0] - size, center[1] + size),
                    (center[0] + size, center[1] + size),
                )
            ],
            "south": [
                (
                    center,
                    (center[0] - size, center[1] - size),
                    (center[0] + size, center[1] - size),
                )
            ],
            "east": [
                (
                    center,
                    (center[0] - size, center[1] - size),
                    (center[0] - size, center[1] + size),
                )
            ],
            "west": [
                (
                    center,
                    (center[0] + size, center[1] - size),
                    (center[0] + size, center[1] + size),
                )
            ],
        }
        pygame.draw.polygon(self.screen, self.entity_color, directions[direction][0])

    def update_entity_position(self):
        if self.game_over:
            return
        dx, dy = 0, 0
        if self.entity_direction == "north":
            dy = -1
        elif self.entity_direction == "south":
            dy = 1
        elif self.entity_direction == "east":
            dx = 1
        elif self.entity_direction == "west":
            dx = -1

        new_x = self.entity_position[0] + dx
        new_y = self.entity_position[1] + dy

        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.moves_done.append((new_x, new_y))
            # print(self.moves_done)
            # Save the current state before moving (for undo)
            self.history.append(
                (copy.deepcopy(self.grid), copy.deepcopy(self.entity_position))
            )

            self.grid[self.entity_position[1]][self.entity_position[0]] = None
            self.entity_position = (new_x, new_y)

            if self.grid[new_y][new_x] is None:
                self.game_over = True

    def autoplay_solution(self):
        # Autoplay the solution path
        if self.autoplay and self.autoplay_index < len(self.solution_path):
            next_position = self.solution_path[self.autoplay_index]
            self.entity_position = next_position
            self.autoplay_index += 1

    def draw_buttons(self):
        for button in self.buttons:
            button.check_hover(pygame.mouse.get_pos())
            button.draw(self.screen)

    def draw_grid(self):
        self.screen.fill((0, 0, 0))  # Clear the screen
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                color = self.grid[row][col]
                if color:
                    pygame.draw.rect(
                        self.screen,
                        color,
                        (
                            col * self.cell_size + self.border_size,
                            row * self.cell_size + self.border_size,
                            self.cell_size - self.border_size * 2,
                            self.cell_size - self.border_size * 2,
                        ),
                    )
                if col == self.entity_position[0] and row == self.entity_position[1]:
                    self.draw_arrow((col, row), self.entity_direction)

        self.draw_buttons()

    def display_game_over(self):
        font = pygame.font.Font(None, 60)
        text = font.render("Game Over! Press R to restart", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def process_event_queue(self):
        while not self.event_queue.empty():
            message = self.event_queue.get()
            self.messages.append((message, pygame.time.get_ticks() + 3000))  # 3 seconds

    def display_messages(self):
        current_ticks = pygame.time.get_ticks()
        self.messages = [
            msg for msg in self.messages if msg[1] > current_ticks
        ]  # Filter out expired messages

        y_offset = 50  # Start 50 pixels down from the top
        for message, _ in self.messages:
            font = pygame.font.Font(None, 40)
            text = font.render(message, True, (255, 255, 0))  # Yellow text
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40

    def check_victory(self):
        for row in self.grid:
            if any(cell is not None for cell in row):  # Check if any cell is not empty
                return False
        return True

    def display_victory(self):
        font = pygame.font.Font(None, 72)
        text = font.render("Victory! Press R to restart", True, (0, 255, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle the QUIT event
                pygame.quit()
                exit()
            if self.won:
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.entity_direction = "north"
                    self.update_entity_position()
                elif event.key == pygame.K_DOWN:
                    self.entity_direction = "south"
                    self.update_entity_position()
                elif event.key == pygame.K_LEFT:
                    self.entity_direction = "west"
                    self.update_entity_position()
                elif event.key == pygame.K_RIGHT:
                    self.entity_direction = "east"
                    self.update_entity_position()
                elif event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_c:  # Save checkpoint
                    self.set_checkpoint()
                elif event.key == pygame.K_l:  # Load checkpoint
                    self.load_checkpoint()
                elif event.key == pygame.K_u:  # Undo the last move
                    self.undo_move()
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_s and self.solution_path:  # Start autoplay
                    self.autoplay = True
                    self.autoplay_index = 0  # Reset autoplay index

            # Handle mouse clicks on buttons
            if mouse_click[0]:  # Left mouse button click
                for button in self.buttons:
                    if button.check_click(mouse_pos):
                        if button.text == "Undo":
                            self.undo_move()
                        elif button.text == "Checkpoint":
                            self.set_checkpoint()
                        elif button.text == "Load Checkpoint":
                            self.load_checkpoint()

    def run(self):
        running = True
        clock = pygame.time.Clock()
        self.draw_grid()
        while running:
            self.process_event_queue()  # Process any new messages in the queue
            self.handle_input()
            self.draw_grid()
            self.display_messages()

            if not self.game_over:
                if self.autoplay:
                    self.autoplay_solution()  # Autoplay the solution if enabled
                pygame.display.flip()
            else:
                if self.check_victory():  # Display victory message if won
                    self.display_victory()
                    if not self.won:
                        self.won = True
                        self.send_victory_callback(
                            copy.deepcopy(self.input_data[0]), self.moves_done[:-1]
                        )
                else:
                    self.display_game_over()

            clock.tick(60)

        pygame.quit()
