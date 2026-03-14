import os
import time


class WumpusGame:
    def __init__(self):
        self.SIZE = 4
        # EXACT MAP FROM YOUR SCREENSHOT (0-indexed, row 0 = lecture row 1 at bottom)
        self.cave = [
            ['.', '.', 'P', '.'],  # Lecture row 1 (bottom)
            ['.', '.', '.', '.'],  # Lecture row 2
            ['W', 'G', 'P', '.'],  # Lecture row 3
            ['.', '.', '.', 'P']  # Lecture row 4 (top)
        ]

        self.agent_x = 0  # Start at lecture [1,1] → array (0,0)
        self.agent_y = 0
        self.has_arrow = True
        self.has_gold = False
        self.wumpus_alive = True
        self.score = 0
        self.game_over = False
        self.visited = [[False] * 4 for _ in range(4)]
        self.visited[0][0] = True

        self.wumpus_pos = (2, 0)  # [3,1]
        self.gold_pos = (2, 1)  # [3,2]
        self.pits = {(0, 2), (2, 2), (3, 3)}

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_percepts(self):
        percepts = []
        x, y = self.agent_x, self.agent_y
        if self.wumpus_alive and (abs(x - self.wumpus_pos[0]) + abs(y - self.wumpus_pos[1]) == 1):
            percepts.append("\033[31mStench\033[0m")
        if any(abs(x - px) + abs(y - py) == 1 for px, py in self.pits):
            percepts.append("\033[34mBreeze\033[0m")
        if (x, y) == self.gold_pos and not self.has_gold:
            percepts.append("\033[33mGlitter\033[0m")
        return percepts or ["None"]

    def print_map(self):
        print("\033[1m📍 WUMPUS WORLD - AGENT'S KNOWLEDGE BASE 📍\033[0m")
        print("     1     2     3     4")
        print("   ┌─────┬─────┬─────┬─────┐")
        for i in range(3, -1, -1):  # Print lecture row 4 at top
            row = []
            for j in range(4):
                if i == self.agent_x and j == self.agent_y:
                    cell = "\033[32m🧍\033[0m"
                elif self.visited[i][j]:
                    cell = "\033[32mV\033[0m"
                else:
                    cell = "\033[37m?\033[0m"
                row.append(f"  {cell}  ")
            print(f" {i + 1} │" + "│".join(row) + "│")
            if i > 0:
                print("   ├─────┼─────┼─────┼─────┤")
        print("   └─────┴─────┴─────┴─────┘")
        print("Legend: 🧍=You   V=Visited   ?=Unknown")

    def print_status(self):
        self.clear()
        print("\033[1;37m╔════════════════════════════════════════════════╗")
        print("║               WUMPUS WORLD - LECTURE MAP       ║")
        print("╚════════════════════════════════════════════════╝\033[0m\n")

        print(f"📍 Position: \033[32m[{self.agent_x + 1}, {self.agent_y + 1}]\033[0m")
        print(f"💰 Score: \033[33m{self.score}\033[0m")
        print(f"👃 Percepts: {' • '.join(self.get_percepts())}")
        print(f"🏹 Arrow: {'✅' if self.has_arrow else '❌'}   🏆 Gold: {'✅' if self.has_gold else '❌'}\n")

        self.print_map()
        print(
            "\n\033[1mCommands:\033[0m up | down | left | right | shoot up | shoot down | shoot left | shoot right | grab | climb | quit")

    def move(self, direction):
        dx, dy = 0, 0
        if direction == 'up':
            dx = 1 
        elif direction == 'down':
            dx = -1
        elif direction == 'left':
            dy = -1
        elif direction == 'right':
            dy = 1

        new_x = self.agent_x + dx
        new_y = self.agent_y + dy

        if 0 <= new_x < 4 and 0 <= new_y < 4:
            self.agent_x = new_x
            self.agent_y = new_y
            self.visited[new_x][new_y] = True
            print(f"\033[32m✅ Successfully moved {direction.upper()}!\033[0m")
        else:
            print("\033[31m🚧 BUMP! You hit the wall.\033[0m")

    def shoot(self, direction):
        if not self.has_arrow:
            print("\033[31m❌ No arrow left!\033[0m")
            return
        self.has_arrow = False
        self.score -= 10
        print(f"🔫 Shooting {direction.upper()}...")

        dx, dy = 0, 0
        if direction == 'up':
            dx = 1
        elif direction == 'down':
            dx = -1
        elif direction == 'left':
            dy = -1
        elif direction == 'right':
            dy = 1

        x, y = self.agent_x + dx, self.agent_y + dy
        while 0 <= x < 4 and 0 <= y < 4:
            if (x, y) == self.wumpus_pos:
                self.wumpus_alive = False
                print("\033[31m💥 SCREAM! You killed the Wumpus!\033[0m")
                return
            x += dx
            y += dy
        print("\033[33mArrow missed the target.\033[0m")

    def grab(self):
        if (self.agent_x, self.agent_y) == self.gold_pos and not self.has_gold:
            self.has_gold = True
            print("\033[33m🎉 GOLD GRABBED! Well done!\033[0m")
        else:
            print("Nothing to grab here.")

    def climb(self):
        if self.agent_x == 0 and self.agent_y == 0:
            self.game_over = True
            if self.has_gold:
                self.score += 1000
                print("\033[1;32m🏆 VICTORY! You escaped with the gold!\033[0m")
            else:
                print("You escaped... but without the gold.")
        else:
            print("\033[31mYou can only climb at the entrance [1,1]!\033[0m")

    def check_death(self):
        if (self.agent_x, self.agent_y) in self.pits:
            self.score -= 1000
            print("\033[31m💀 You fell into a PIT! Game Over.\033[0m")
            self.game_over = True
        elif (self.agent_x, self.agent_y) == self.wumpus_pos and self.wumpus_alive:
            self.score -= 1000
            print("\033[31m💀 Eaten by the Wumpus! Game Over.\033[0m")
            self.game_over = True

    def play(self):
        print("\033[1;35mWelcome to WUMPUS WORLD (Exact Lecture Map)\033[0m")
        time.sleep(1.2)

        while not self.game_over:
            self.print_status()
            cmd = input("\033[1mYour move: \033[0m").strip().lower()

            self.score -= 1

            if cmd in ['up', 'down', 'left', 'right']:
                self.move(cmd)
            elif cmd.startswith('shoot '):
                _, dir = cmd.split()
                if dir in ['up', 'down', 'left', 'right']:
                    self.shoot(dir)
                else:
                    print("Invalid shoot direction.")
                    self.score += 1
            elif cmd == 'grab':
                self.grab()
            elif cmd == 'climb':
                self.climb()
            elif cmd == 'quit':
                self.game_over = True
                print("\033[33mGame quit by player.\033[0m")
            else:
                print("\033[33mInvalid command. Use: up, down, left, right, shoot up, grab, climb, quit\033[0m")
                self.score += 1

            self.check_death()

        self.clear()
        print("\033[1;37m══════════════════════════════════════════════")
        print(f"           GAME OVER - FINAL SCORE: {self.score}")
        print("══════════════════════════════════════════════\033[0m")


if __name__ == "__main__":
    game = WumpusGame()
    game.play()