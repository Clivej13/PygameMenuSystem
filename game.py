import json
import pygame


class Game:
    def __init__(self):
        pass

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check if Escape key is pressed
                    self.menu()  # Open the menu

    def draw(self, screen):
        pass

    def write_current_game_state(self, key, value):
        try:
            with open("current_game_state.json", "r+") as file:
                data = json.load(file)
                data[key] = value
                file.seek(0)  # Move the file pointer to the beginning
                json.dump(data, file, indent=4)
                file.truncate()  # Remove any remaining content after writing
                print(f"Game state updated: {key} = {value}")
        except FileNotFoundError:
            print("File 'current_game_state.json' not found.")

    def menu(self):
        self.write_current_game_state("current_state", "menu")  # Example usage
