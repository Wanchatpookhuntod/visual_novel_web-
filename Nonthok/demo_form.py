import pygame
import pygame_gui
import json

class MyForm:
    def __init__(self, manager, container_rect, bg_color=(220, 220, 220),
                 border_color=(0, 0, 0), border_width=2):
        self.manager = manager
        self.container_rect = container_rect
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.container_rect,
            manager=self.manager
        )

        self.name_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((20, 20), (200, 30)),
            manager=self.manager,
            container=self.panel
        )
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((230, 20), (100, 30)),
            text='Name',
            manager=self.manager,
            container=self.panel
        )
        self.image_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((20, 60), (200, 30)),
            manager=self.manager,
            container=self.panel
        )
        self.image_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((230, 60), (100, 30)),
            text='Image File',
            manager=self.manager,
            container=self.panel
        )
        self.file_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((340, 60), (100, 30)),
            text='Browse',
            manager=self.manager,
            container=self.panel
        )
        self.add_dialog_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 100), (150, 30)),
            text='Add Dialog',
            manager=self.manager,
            container=self.panel
        )
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((180, 100), (150, 30)),
            text='Save',
            manager=self.manager,
            container=self.panel
        )

        panel_width = self.container_rect.width
        self.dialog_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 140), (panel_width, 200)),
            manager=self.manager,
            container=self.panel
        )

        self.dialog_rows = []
        self.dialog_row_height = 40
        self.dialog_spacing = 10

        self.file_dialog = None

        self.dragging_row_index = None
        self.drag_offset_y = 0

    def update_scroll_area(self):
        new_total_height = len(self.dialog_rows) * (self.dialog_row_height + self.dialog_spacing)
        self.dialog_container.set_scrollable_area_dimensions(
            (self.dialog_container.relative_rect.width, new_total_height)
        )
        if hasattr(self.dialog_container, 'horizontal_scroll_bar'):
            self.dialog_container.horizontal_scroll_bar.hide()

    def update_dialog_labels(self):
        panel_width = self.container_rect.width
        total_used = int(panel_width * 0.90)
        left_margin = int((panel_width - total_used) / 2)
        label_width = int(panel_width * 0.10)
        speaker_width = int(panel_width * 0.20)
        text_width = int(panel_width * 0.45)
        remove_width = int(panel_width * 0.15)

        for i, row in enumerate(self.dialog_rows):
            new_y = i * (self.dialog_row_height + self.dialog_spacing)
            row['label'].set_text(f"{i + 1}")
            row['label'].set_relative_position((left_margin, new_y + 5))
            row['label'].set_dimensions((label_width, 30))
            row['speaker_entry'].set_relative_position((left_margin + label_width, new_y + 5))
            row['speaker_entry'].set_dimensions((speaker_width, 30))
            row['text_entry'].set_relative_position((left_margin + label_width + speaker_width, new_y + 5))
            row['text_entry'].set_dimensions((text_width, 30))
            row['remove_button'].set_relative_position((left_margin + label_width + speaker_width + text_width, new_y + 5))
            row['remove_button'].set_dimensions((remove_width, 30))

    def reset_form(self):
        self.name_entry.set_text("")
        self.image_entry.set_text("")
        for row in self.dialog_rows:
            row['label'].kill()
            row['speaker_entry'].kill()
            row['text_entry'].kill()
            row['remove_button'].kill()
        self.dialog_rows.clear()
        self.update_scroll_area()

    def get_form_data(self):
        data = {
            "name": self.name_entry.get_text(),
            "image_file": self.image_entry.get_text(),
            "dialogs": [
                {
                    "speaker": row['speaker_entry'].get_text(),
                    "text": row['text_entry'].get_text()
                }
                for row in self.dialog_rows
            ]
        }
        return data

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, row in enumerate(self.dialog_rows):
                if row['label'].get_abs_rect().collidepoint(event.pos):
                    self.dragging_row_index = i
                    self.drag_offset_y = event.pos[1] - row['label'].get_abs_rect().y
                    break

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_row_index is not None:
                container_abs_y = self.dialog_container.get_abs_rect().y
                new_y = event.pos[1] - self.drag_offset_y - container_abs_y
                row = self.dialog_rows[self.dragging_row_index]
                offset = 5
                row['label'].set_relative_position((row['label'].relative_rect.x, new_y + offset))
                row['speaker_entry'].set_relative_position((row['speaker_entry'].relative_rect.x, new_y + offset))
                row['text_entry'].set_relative_position((row['text_entry'].relative_rect.x, new_y + offset))
                row['remove_button'].set_relative_position((row['remove_button'].relative_rect.x, new_y + offset))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_row_index is not None:
                dropped_row = self.dialog_rows[self.dragging_row_index]
                new_y = dropped_row['label'].relative_rect.y
                new_index = int(new_y / (self.dialog_row_height + self.dialog_spacing))
                new_index = max(0, min(new_index, len(self.dialog_rows) - 1))
                if new_index != self.dragging_row_index:
                    row = self.dialog_rows.pop(self.dragging_row_index)
                    self.dialog_rows.insert(new_index, row)
                self.update_dialog_labels()
                self.update_scroll_area()
                self.dragging_row_index = None

        elif event.type == pygame.MOUSEWHEEL:
            current_scroll = self.dialog_container.vert_scroll_bar.scroll_position
            new_scroll = current_scroll - event.y * 20
            self.dialog_container.vert_scroll_bar.scroll_position = new_scroll

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.file_button:
                self.file_dialog = pygame_gui.windows.UIFileDialog(
                    pygame.Rect(100, 50, 440, 500),
                    self.manager,
                    window_title='Select Image File',
                    initial_file_path='.'
                )
            elif event.ui_element == self.add_dialog_button:
                panel_width = self.container_rect.width
                total_used = int(panel_width * 0.90)
                left_margin = int((panel_width - total_used) / 2)
                label_width = int(panel_width * 0.10)
                speaker_width = int(panel_width * 0.20)
                text_width = int(panel_width * 0.45)
                remove_width = int(panel_width * 0.15)
                row_y = len(self.dialog_rows) * (self.dialog_row_height + self.dialog_spacing)
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((left_margin, row_y + 5), (label_width, 30)),
                    text=f"{len(self.dialog_rows)+1}",
                    manager=self.manager,
                    container=self.dialog_container
                )
                speaker_entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((left_margin + label_width, row_y + 5), (speaker_width, 30)),
                    manager=self.manager,
                    container=self.dialog_container
                )
                text_entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((left_margin + label_width + speaker_width, row_y + 5), (text_width, 30)),
                    manager=self.manager,
                    container=self.dialog_container
                )
                remove_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((left_margin + label_width + speaker_width + text_width, row_y + 5), (remove_width, 30)),
                    text='Remove',
                    manager=self.manager,
                    container=self.dialog_container
                )
                self.dialog_rows.append({
                    'label': label,
                    'speaker_entry': speaker_entry,
                    'text_entry': text_entry,
                    'remove_button': remove_button,
                    'y': row_y
                })
                self.update_scroll_area()
                self.update_dialog_labels()
            elif event.ui_element == self.save_button:
                data = self.get_form_data()
                json_data = json.dumps(data, indent=4, ensure_ascii=False)
                print("----- Save Form Data (JSON) -----")
                print(json_data)
                print("----------------------------------")
                self.reset_form()
            else:
                for idx, row in enumerate(self.dialog_rows):
                    if event.ui_element == row['remove_button']:
                        row['label'].kill()
                        row['speaker_entry'].kill()
                        row['text_entry'].kill()
                        row['remove_button'].kill()
                        self.dialog_rows.pop(idx)
                        self.update_scroll_area()
                        self.update_dialog_labels()
                        break

        elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if self.file_dialog is not None and event.ui_element == self.file_dialog:
                self.image_entry.set_text(event.text)
                self.file_dialog.kill()
                self.file_dialog = None

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.container_rect)
        pygame.draw.rect(surface, self.border_color, self.container_rect, self.border_width)
        self.manager.draw_ui(surface)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((800, 600))
    form_width, form_height = 600, 400
    form_rect = pygame.Rect((800 - form_width) // 2, (600 - form_height) // 2, form_width, form_height)
    form = MyForm(manager, form_rect, bg_color=(220, 220, 220), border_color=(0, 0, 0), border_width=2)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            form.process_event(event)
            manager.process_events(event)
        form.update(time_delta)
        screen.fill(pygame.Color('#000000'))
        form.draw(screen)
        pygame.display.update()
    pygame.quit()
