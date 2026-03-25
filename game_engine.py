import pygame
from game_objects import snake, food, wall, Direction
from storage import Storage
import sys


class GameEngine:

    def __init__(self):
        pygame.init()

        self.width = 600
        self.height = 405

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        self.cell_size = 15
        self.start_x = (self.width // self.cell_size) // 2
        self.start_y = (self.height // self.cell_size) // 2

        # game objects
        self.snake = snake(self.start_x, self.start_y, self.cell_size)
        self.food = food(self.width, self.height, self.cell_size)
        self.walls = []

        # game state
        self.state = "menu"
        self.level = 1
        self.speed = 8
        self.player_name = ""

        # storage
        self.storage = Storage("scores.json")

        # fonts
        self.font_big = pygame.font.SysFont("Helvetica, Arial, sans-serif", 48)
        self.font_medium = pygame.font.SysFont("Helvetica, Arial, sans-serif", 30)
        self.font_small = pygame.font.SysFont("Helvetica, Arial, sans-serif", 20)

    # main loop
    def run(self):
        """Main loop will run until player quit"""
        while True:
            if self.state == "menu":
                self.show_menu()

            elif self.state == "playing":
                self.play()

            elif self.state == "game_over":
                self.show_game_over()

            elif self.state == "high_scores":
                self.show_high_scores()

    # menu screen
    def show_menu(self):
        """Display main menu."""
        while self.state == "menu":
            self.screen.fill((0, 0, 0))

            title = self.font_big.render("SNAKE GAME", True, (0, 255, 0))
            opt1 = self.font_medium.render("1 - Start Game", True, (255, 255, 255))
            opt2 = self.font_medium.render("2 - High Scores", True, (255, 255, 255))
            opt3 = self.font_medium.render("3 - Quit", True, (255, 255, 255))

            self.screen.blit(title, (self.width // 2 - 140, 50))  # 160
            self.screen.blit(opt1, (self.width // 2 - 100, 150))  # 200
            self.screen.blit(opt2, (self.width // 2 - 100, 200))  # 200
            self.screen.blit(opt3, (self.width // 2 - 100, 250))  # 200

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.start_new_game()
                    elif event.key == pygame.K_2:
                        self.state = "high_scores"
                    elif event.key == pygame.K_3:
                        self.quit_game()

    def get_wall_positions(self):
        """get wall positions as (x, y)"""
        positions = []
        for block in self.walls:
            positions.append(block.get_position())
        return positions

    def play(self):
        while self.state == "playing":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(Direction.UP)

                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(Direction.DOWN)

                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(Direction.LEFT)

                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(Direction.RIGHT)

            self.snake.move()

            # check food collision
            if self.snake.get_position() == self.food.get_position():
                self.snake.grow(self.food.points)
                self.food.respawn(self.snake.body, self.get_wall_positions())

            self.check_level_up()

            # check death
            if self.snake.hitself():
                self.state = "game_over"
            if self.snake.hitWall(self.width, self.height):
                self.state = "game_over"
            if self.hit_wall_block():
                self.state = "game_over"

            self.draw_game()
            self.clock.tick(self.speed)

    def show_game_over(self):
        """Show game over and ask for player name."""
        self.player_name = ""
        typing = True

        while self.state == "game_over":
            self.screen.fill((0, 0, 0))

            over_text = self.font_big.render("GAME OVER", True, (255, 0, 0))

            score_text = self.font_medium.render(
                f"Score: {self.snake.score}  Level: {self.level}", True, (255, 255, 255)
            )

            if typing:
                name_text = self.font_medium.render(
                    f"Name: {self.player_name}_", True, (255, 255, 0)
                )

                hint = self.font_small.render(
                    "Type your name, press ENTER to save", True, (150, 150, 150)
                )
            else:
                name_text = self.font_medium.render("Score saved!", True, (0, 255, 0))

                hint = self.font_small.render(
                    "Press M for Menu or Q to Quit", True, (150, 150, 150)
                )

            self.screen.blit(over_text, (self.width // 2 - 120, 50))  # 180
            self.screen.blit(score_text, (self.width // 2 - 140, 130))  # 160
            self.screen.blit(name_text, (self.width // 2 - 120, 200))  # 180
            self.screen.blit(hint, (self.width // 2 - 150, 260))  # 150

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if typing:
                        if event.key == pygame.K_RETURN:
                            self.storage.add_score(
                                self.player_name, self.snake.score, self.level
                            )
                            typing = False

                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]

                        else:
                            if len(self.player_name) < 15:
                                self.player_name += event.unicode

                    else:
                        if event.key == pygame.K_m:
                            self.state = "menu"

                        elif event.key == pygame.K_q:
                            self.quit_game()

    # ---- HIGH SCORES ----

    def show_high_scores(self):
        """display top scores from storage"""
        while self.state == "high_scores":
            self.screen.fill((0, 0, 0))

            title = self.font_big.render("HIGH SCORES", True, (255, 215, 0))
            self.screen.blit(title, (self.width // 2 - 130, 20))  # 170

            top_scores = self.storage.get_top_scores(5)

            if not top_scores:
                empty = self.font_medium.render("No scores yet!", True, (150, 150, 150))
                self.screen.blit(empty, (self.width // 2 - 80, 150))  # 220

            else:
                for i, record in enumerate(top_scores):
                    line = (
                        f"{i + 1}. {record['player_name']}"
                        f" - {record['score']} pts"
                        f" (Lvl {record['level']})"
                    )
                    text = self.font_small.render(line, True, (255, 255, 255))
                    self.screen.blit(text, (100, 80 + i * 35))

            summary = self.storage.get_summary()
            if summary:
                sum_text = self.font_small.render(
                    f"Total Games: {summary['total_games']}"
                    f"  |  Avg Score: {summary['average_score']}",
                    True,
                    (100, 200, 100),
                )
                self.screen.blit(sum_text, (80, 370))

            back = self.font_small.render("Press B to go Back", True, (150, 150, 150))
            self.screen.blit(back, (self.width // 2 - 80, 340))  # 220

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        self.state = "menu"

    # start new game
    def start_new_game(self):
        """resets everything and starts playing"""
        self.snake.reset(self.start_x, self.start_y)
        self.level = 1
        self.speed = 8
        self.walls = []
        self.food.respawn(self.snake.body, self.get_wall_positions())
        self.state = "playing"

    def check_level_up(self):
        """increase level when score reaches threshold"""
        if self.snake.score >= self.level * 50:
            self.level += 1
            self.speed += 3

            if self.level == 2:
                self.walls = wall.createBorderwall(self.width, self.height)

            elif self.level >= 3:
                # border_walls = wall.createBorderwall(self.width, self.height)
                random_walls = wall.createRandomWalls(self.width, self.height, count=20)
                self.walls = random_walls

            self.food.respawn(self.snake.body, self.get_wall_positions())

    def hit_wall_block(self):
        """check if snake hits any wall block."""
        head = self.snake.get_position()
        for wall in self.walls:
            if head == wall.get_position():
                return True
        return False

    def draw_game(self):
        """draw all objects on screen"""
        self.screen.fill((0, 0, 0))

        for wall in self.walls:
            wall.draw(self.screen)
        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        score_text = self.font_small.render(
            f"Score: {self.snake.score}  Level: {self.level}", True, (255, 255, 255)
        )
        self.screen.blit(score_text, (10, 10))

        if self.food.foodtype == "bonus":
            bonus_text = self.font_small.render("BONUS FOOD!", True, (255, 215, 0))
            self.screen.blit(bonus_text, (self.width - 150, 10))

        pygame.display.flip()

    def quit_game(self):
        """exit the game"""
        pygame.quit()
        sys.exit()
