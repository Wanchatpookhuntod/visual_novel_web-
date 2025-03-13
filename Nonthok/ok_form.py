import pygame
import pygame_gui
import json  # สำหรับแปลงข้อมูลเป็น JSON

pygame.init()
pygame.display.set_caption('Demo Form with Save JSON and Reset Functionality')
window_surface = pygame.display.set_mode((800, 600))
background = pygame.Surface((800, 600))
background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((800, 600))

# UIScrollingContainer สำหรับ dialog rows (เลื่อนเฉพาะแนวตั้ง)
dialog_container = pygame_gui.elements.UIScrollingContainer(
    relative_rect=pygame.Rect((50, 200), (700, 350)),
    manager=manager,
    container=None
)

# ส่วนฟอร์มด้านบน
name_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 50), (200, 30)),
    manager=manager
)
name_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((260, 50), (100, 30)),
    text='Name',
    manager=manager
)

# ช่อง Image File พร้อมปุ่ม Browse
image_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 100), (200, 30)),
    manager=manager
)
image_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((260, 100), (100, 30)),
    text='Image File',
    manager=manager
)
file_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((370, 100), (100, 30)),
    text='Browse',
    manager=manager
)

# ปุ่มสำหรับเพิ่ม Dialog และปุ่ม Save (Save อยู่ถัดจาก Add Dialog)
add_dialog_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 150), (150, 30)),
    text='Add Dialog',
    manager=manager
)
save_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((210, 150), (150, 30)),
    text='Save',
    manager=manager
)

dialog_rows = []         # รายการเก็บ dialog row แต่ละแถว
dialog_row_height = 40   # ความสูงของแต่ละ dialog row
dialog_spacing = 10      # ระยะห่างระหว่างแต่ละแถว

# ตัวแปรสำหรับเก็บ reference ของ File Dialog
file_dialog = None

# ตัวแปรสำหรับ Drag & Drop
dragging_row_index = None
drag_offset_y = 0

def update_scroll_area():
    new_total_height = len(dialog_rows) * (dialog_row_height + dialog_spacing)
    dialog_container.set_scrollable_area_dimensions(
        (dialog_container.relative_rect.width, new_total_height)
    )
    if hasattr(dialog_container, 'horizontal_scroll_bar'):
        dialog_container.horizontal_scroll_bar.hide()

def update_dialog_labels():
    for i, row in enumerate(dialog_rows):
        new_y = i * (dialog_row_height + dialog_spacing)
        row['label'].set_text(f"{i+1}")
        row['label'].set_relative_position((10, new_y + 5))
        row['speaker_entry'].set_relative_position((50, new_y + 5))
        row['text_entry'].set_relative_position((200, new_y + 5))
        row['remove_button'].set_relative_position((560, new_y + 5))

def reset_form():
    name_entry.set_text("")
    image_entry.set_text("")
    for row in dialog_rows:
        row['label'].kill()
        row['speaker_entry'].kill()
        row['text_entry'].kill()
        row['remove_button'].kill()
    dialog_rows.clear()
    update_scroll_area()

clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Drag & Drop สำหรับ dialog rows
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, row in enumerate(dialog_rows):
                if row['label'].get_abs_rect().collidepoint(event.pos):
                    dragging_row_index = i
                    drag_offset_y = event.pos[1] - row['label'].get_abs_rect().y
                    break

        if event.type == pygame.MOUSEMOTION:
            if dragging_row_index is not None:
                container_abs_y = dialog_container.get_abs_rect().y
                new_y = event.pos[1] - drag_offset_y - container_abs_y
                row = dialog_rows[dragging_row_index]
                offset = 5
                row['label'].set_relative_position((10, new_y + offset))
                row['speaker_entry'].set_relative_position((50, new_y + offset))
                row['text_entry'].set_relative_position((200, new_y + offset))
                row['remove_button'].set_relative_position((560, new_y + offset))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging_row_index is not None:
                dropped_row = dialog_rows[dragging_row_index]
                new_y = dropped_row['label'].relative_rect.y
                new_index = int(new_y / (dialog_row_height + dialog_spacing))
                new_index = max(0, min(new_index, len(dialog_rows) - 1))
                if new_index != dragging_row_index:
                    row = dialog_rows.pop(dragging_row_index)
                    dialog_rows.insert(new_index, row)
                update_dialog_labels()
                update_scroll_area()
                dragging_row_index = None

        if event.type == pygame.MOUSEWHEEL:
            current_scroll = dialog_container.vert_scroll_bar.scroll_position
            new_scroll = current_scroll - event.y * 20
            dialog_container.vert_scroll_bar.scroll_position = new_scroll

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == file_button:
                file_dialog = pygame_gui.windows.UIFileDialog(
                    pygame.Rect(160, 50, 440, 500),
                    manager,
                    window_title='Select Image File',
                    initial_file_path='.'
                )
            elif event.ui_element == add_dialog_button:
                row_y = len(dialog_rows) * (dialog_row_height + dialog_spacing)
                label = pygame_gui.elements.UILabel(
                    relative_rect=pygame.Rect((10, row_y + 5), (40, 30)),
                    text=f"{len(dialog_rows)+1}",
                    manager=manager,
                    container=dialog_container
                )
                speaker_entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((50, row_y + 5), (140, 30)),
                    manager=manager,
                    container=dialog_container
                )
                text_entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect((200, row_y + 5), (350, 30)),
                    manager=manager,
                    container=dialog_container
                )
                remove_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((560, row_y + 5), (100, 30)),
                    text='Remove',
                    manager=manager,
                    container=dialog_container
                )
                dialog_rows.append({
                    'label': label,
                    'speaker_entry': speaker_entry,
                    'text_entry': text_entry,
                    'remove_button': remove_button,
                    'y': row_y
                })
                update_scroll_area()
            elif event.ui_element == save_button:
                # สร้างข้อมูลฟอร์มในรูปแบบ JSON
                form_data = {
                    "name": name_entry.get_text(),
                    "image_file": image_entry.get_text(),
                    "dialogs": [
                        {
                            "speaker": row['speaker_entry'].get_text(),
                            "text": row['text_entry'].get_text()
                        }
                        for row in dialog_rows
                    ]
                }
                json_data = json.dumps(form_data, indent=4, ensure_ascii=False)
                print("----- Save Form Data (JSON) -----")
                print(json_data)
                print("----------------------------------")
                reset_form()
            else:
                for idx, row in enumerate(dialog_rows):
                    if event.ui_element == row['remove_button']:
                        row['label'].kill()
                        row['speaker_entry'].kill()
                        row['text_entry'].kill()
                        row['remove_button'].kill()
                        dialog_rows.pop(idx)
                        update_scroll_area()
                        update_dialog_labels()
                        break

        if event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            if file_dialog is not None and event.ui_element == file_dialog:
                image_entry.set_text(event.text)
                file_dialog.kill()
                file_dialog = None

        manager.process_events(event)

    manager.update(time_delta)
    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)
    pygame.display.update()

pygame.quit()
