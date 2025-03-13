import pygame
import pygame_gui
from form import MyForm

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((800, 600))
    
    running = True
    form = None

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click
                if form is None:  # Create a new form if one doesn't exist
                    form_width, form_height = 600, 400
                    form_rect = pygame.Rect((800 - form_width) // 2, (600 - form_height) // 2, form_width, form_height)
                    form = MyForm(manager, form_rect, bg_color=(220, 220, 220), border_color=(0, 0, 0), border_width=2)

            if form:
                form.process_event(event)
                manager.process_events(event)

        if form:
            form.update(time_delta)

        screen.fill(pygame.Color('#000000'))
        if form:
            form.draw(screen)
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()