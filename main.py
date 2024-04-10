import json

import pygame

from menu_manager import MenuManager
from game import Game


def read_current_game_state(key):
    try:
        with open("current_game_state.json", "r") as file:
            data = json.load(file)
            return data.get(key)
    except FileNotFoundError:
        print("File 'current_game_state' not found.")
        return "menu"  # Return "menu" as default state if file not found or JSON parsing fails


def write_current_game_state(key, value):
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


if __name__ == "__main__":
    write_current_game_state("current_state", "menu")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    manager = MenuManager("menus", "main_menu")
    game = Game()
    manager.load_menus()

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        if read_current_game_state("current_state") == "menu":
            manager.update(events)
            manager.draw(screen)
        else:
            manager.current_menu = "in_game_exit_confirm"
            game.update(events)
            game.draw(screen)

        pygame.display.flip()

    pygame.quit()
