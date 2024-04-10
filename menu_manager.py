import json
import os

import pygame


class MenuItem:
    def __init__(self, name, item_type, text_size, function=None, data_location=None, options=None):
        self.name = name
        self.type = item_type
        self.text_size = text_size
        self.function = function
        self.data_location = data_location
        self.options = options if options else []

        # Additional attributes for selection type
        self.selected_index = 0  # Default selected index
        self.input_active = False  # Default input activation state
        self.input_text = ""  # Initialize input text to an empty string

        # Additional attribute for toggle type
        self.toggle_state = False  # Default toggle state
        self.modified = False  # Default modification state


class MenuManager:
    def __init__(self, directory, current_menu):
        self.directory = directory
        self.menus = {}
        self.current_menu = current_menu
        self.previous_menu = None
        self.cursor_position = [0, 0]
        self.num_rows = None
        self.num_columns = None
        self.num_items = None

    def load_menus(self):
        for filename in os.listdir(self.directory):
            if filename.endswith('.json'):
                menu_name = os.path.splitext(filename)[0]
                with open(os.path.join(self.directory, filename), 'r') as file:
                    try:
                        menu_data = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error loading menu '{menu_name}'. Invalid JSON format.")
                        continue
                items = []
                for item_data in menu_data.get('items', []):
                    item = MenuItem(
                        item_data.get('name'),
                        item_data.get('type'),
                        item_data.get('text_size'),
                        item_data.get('function'),
                        item_data.get('data_location'),
                        item_data.get('options')  # Pass options to MenuItem
                    )
                    if (item.type == 'input' or item.type == 'selection') and item.data_location:
                        self.load_input_data(item)
                    elif item.type == 'toggle' and item.data_location:
                        self.load_toggle_state(item)
                    items.append(item)
                menu_data['items'] = items
                self.menus[menu_name] = menu_data

    def load_input_data(self, item):
        if item.data_location and 'file' in item.data_location and 'key' in item.data_location:
            file_path = item.data_location['file']
            key = item.data_location['key']
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if key in data:
                        if item.type == 'selection':  # Only load input data for selection type items
                            try:
                                item.selected_index = item.options.index(data[key])
                                print(f"{item.selected_index}")
                            except Exception as e:
                                item.selected_index = 0
                                print(f"Set to {item.selected_index} because: {e}")
                        else:
                            item.input_text = data[key]
            except FileNotFoundError:
                pass

    def load_toggle_state(self, item):
        if item.data_location and 'file' in item.data_location and 'key' in item.data_location:
            file_path = item.data_location['file']
            key = item.data_location['key']
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if key in data:
                        item.toggle_state = data[key]
            except FileNotFoundError:
                pass

    def update(self, events):
        if self.current_menu in self.menus:
            menu_data = self.menus[self.current_menu]
            self.num_rows = menu_data.get('rows', {}).get('count', 1)
            self.num_columns = menu_data.get('columns', {}).get('count', 1)
            self.num_items = len(menu_data.get('items', []))

            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if any(item.input_active for item in menu_data.get('items', [])):
                        for item in menu_data['items']:
                            if item.input_active and item.type == "input":
                                for event in events:
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_RETURN:
                                            item.input_active = False
                                            if item.input_text != "":
                                                item.modified = True
                                                self.save_input_data(item)
                                        elif event.key == pygame.K_BACKSPACE:
                                            item.input_text = item.input_text[:-1]
                                        elif hasattr(event, 'unicode'):
                                            item.input_text += event.unicode
                            elif item.input_active and item.type == "selection":
                                if event.key == pygame.K_LEFT:
                                    item.selected_index = (item.selected_index - 1) % len(item.options)
                                elif event.key == pygame.K_RIGHT:
                                    item.selected_index = (item.selected_index + 1) % len(item.options)
                                elif event.key == pygame.K_RETURN:
                                    item.input_active = False  # Leave selection item
                                    print(f"Selected option for {item.name}: {item.options[item.selected_index]}")
                                    self.save_input_data(item)  # Save selection
                                    item.modified = True
                    else:
                        self.handle_menu_navigation(event, menu_data)

        else:
            print(f"Menu '{self.current_menu}' not found.")

    def save_input_data(self, item):
        if item.data_location and 'file' in item.data_location and 'key' in item.data_location:
            file_path = item.data_location['file']
            key = item.data_location['key']
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}
            data[key] = item.input_text
            with open(file_path, 'w') as file:
                json.dump(data, file)

    def save_toggle_state(self, item):
        if item.data_location and 'file' in item.data_location and 'key' in item.data_location:
            file_path = item.data_location['file']
            key = item.data_location['key']
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}
            data[key] = item.toggle_state
            with open(file_path, 'w') as file:
                json.dump(data, file)

    def handle_menu_navigation(self, event, menu_data):
        if event.key == pygame.K_UP:
            self.cursor_position = self.move_cursor(self.cursor_position, [0, -1])
        elif event.key == pygame.K_DOWN:
            self.cursor_position = self.move_cursor(self.cursor_position, [0, 1])
        elif event.key == pygame.K_LEFT:
            self.cursor_position = self.move_cursor(self.cursor_position, [-1, 0])
        elif event.key == pygame.K_RIGHT:
            self.cursor_position = self.move_cursor(self.cursor_position, [1, 0])
        elif event.key == pygame.K_RETURN:
            self.handle_item_selection(menu_data)

    def handle_item_selection(self, menu_data):
        index = self.cursor_position[1] * self.num_columns + self.cursor_position[0]
        if index < self.num_items:
            item = menu_data.get('items', [])[index]
            if item.type == 'input':
                item.input_active = True
            elif item.type == 'toggle':
                item.toggle_state = not item.toggle_state
                print(f"Toggle state of {item.name} changed to {item.toggle_state}")
                self.save_toggle_state(item)  # Save toggle state
            elif item.type == 'button':
                self.handle_button_function(item)
            elif item.type == 'selection':  # Handle selection type
                item.input_active = True
                item.selected_index = (item.selected_index) % len(item.options)  # Move to next option
                print(f"Selected option for {item.name}: {item.options[item.selected_index]}")
                self.save_input_data(item)  # Save selection

    def handle_button_function(self, item):
        function_name = item.function.get('name')
        if function_name == 'exit':
            self.quit_game()
        elif function_name == 'game':
            self.game()
        elif function_name == 'return':
            self.current_menu = self.previous_menu or self.current_menu
            self.cursor_position = [0, 0]
        else:
            next_menu = item.function.get('next_menu')
            if next_menu:
                print(f"Changing to {next_menu}")
                self.previous_menu = self.current_menu
                self.current_menu = next_menu
                self.cursor_position = [0, 0]

    def quit_game(self):
        pygame.quit()
        exit()

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

    def game(self):
        self.write_current_game_state("current_state", "game")  # Example usage

    def move_cursor(self, coord, increment):
        print("Current cursor position:", coord)
        print("Increment:", increment)
        print("self.num_columns:", self.num_columns)
        print("self.num_rows:", self.num_rows)
        if 0 <= coord[0] + increment[0] < self.num_columns and 0 <= coord[1] + increment[1] < self.num_rows:
            coord[0] += increment[0]
            coord[1] += increment[1]
        else:
            print("Cursor movement out of bounds")
        print("New cursor position:", coord)
        return coord

    def draw(self, screen):
        if self.current_menu in self.menus:
            menu_data = self.menus[self.current_menu]
            num_columns = menu_data.get('columns', {}).get('count', 1)
            spacing_columns = menu_data.get('columns', {}).get('spacing', 1)
            num_rows = menu_data.get('rows', {}).get('count', 1)
            spacing_rows = menu_data.get('rows', {}).get('spacing', 1)

            item_width = 200
            item_height = 50
            total_width = num_columns * item_width + (num_columns - 1) * spacing_columns
            total_height = num_rows * item_height + (num_rows - 1) * spacing_rows

            left_padding = (screen.get_width() - total_width) // 2
            top_padding = (screen.get_height() - total_height) // 2

            background_rect = pygame.Rect(left_padding, top_padding, total_width, total_height)
            pygame.draw.rect(screen, (255, 255, 255), background_rect)

            font = pygame.font.Font(None, 36)

            for i, item in enumerate(menu_data.get('items', [])):
                column = i % num_columns
                row = i // num_columns

                text_color = (0, 0, 0)
                if item.type == 'toggle':
                    if item.toggle_state:
                        text_color = (0, 255, 0)
                    else:
                        text_color = (255, 0, 0)
                if item.modified:
                    text = font.render(item.input_text, True, text_color)
                else:
                    text = font.render(item.name, True, text_color)
                text_rect = text.get_rect(center=(left_padding + item_width // 2 + column * (item_width + spacing_columns),
                                                  top_padding + item_height // 2 + row * (item_height + spacing_rows)))

                if self.cursor_position == [column, row]:
                    pygame.draw.rect(screen, (0, 0, 255), text_rect, 2)
                if item.input_active and item.type == "input":
                    pygame.draw.rect(screen, (255, 255, 255), text_rect)  # Draw input box
                    text = font.render(item.input_text, True, (0, 0, 0))
                    text_rect = text.get_rect(
                        center=(left_padding + item_width // 2 + column * (item_width + spacing_columns),
                                top_padding + item_height // 2 + row * (item_height + spacing_rows)))
                if item.input_active and item.type == "selection":
                    item.input_text = item.options[item.selected_index]
                    display_text = "< " + item.input_text + " >"
                    text = font.render(display_text, True, text_color)
                    text_rect = text.get_rect(
                        center=(left_padding + item_width // 2 + column * (item_width + spacing_columns),
                                top_padding + item_height // 2 + row * (item_height + spacing_rows)))
                else:
                    if self.cursor_position == [column, row]:
                        pygame.draw.rect(screen, (0, 0, 255), text_rect, 2)
                screen.blit(text, text_rect)
            # Draw menu title
            font = pygame.font.Font(None, 48)  # You can adjust the font size as needed
            title_text = font.render(menu_data['title'], True, (255, 255, 255))  # White color for text
            title_rect = title_text.get_rect(center=(screen.get_width() // 2, top_padding // 2))
            screen.blit(title_text, title_rect)

        else:
            print(f"Menu '{self.current_menu}' not found.")
