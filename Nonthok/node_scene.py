# import pygame
# import sys

# # Initialize Pygame
# pygame.init()

# # Set up the display
# screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
# pygame.display.set_caption("Pygame Window")

# # Set up the clock for controlling the frame rate
# clock = pygame.time.Clock()

# # Main loop
# running = True
# fullscreen = False
# nodes = [pygame.Rect(10, 10, 100, 50)]
# edges = []
# dragging = False
# dragging_node = None
# drawing_edge = False
# start_pos = None
# current_node = None
# input_node = None

# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_f:
#                 fullscreen = not fullscreen
#                 if fullscreen:
#                     screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#                 else:
#                     screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
#         elif event.type == pygame.VIDEORESIZE:
#             screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
#         elif event.type == pygame.MOUSEBUTTONDOWN:
#             if event.button == 1:  # Left mouse button
#                 for node_rect in nodes:
#                     output_circle_pos = (node_rect.right, node_rect.centery)
#                     input_circle_pos = (node_rect.left, node_rect.centery)
#                     if pygame.Rect(output_circle_pos[0] - 5, output_circle_pos[1] - 5, 10, 10).collidepoint(event.pos):
#                         drawing_edge = True
#                         start_pos = output_circle_pos
#                         current_node = node_rect
#                         break
#                     elif pygame.Rect(input_circle_pos[0] - 5, input_circle_pos[1] - 5, 10, 10).collidepoint(event.pos):
#                         input_node = node_rect
#                         break
#                     elif node_rect.collidepoint(event.pos):
#                         dragging = True
#                         dragging_node = node_rect
#                         mouse_x, mouse_y = event.pos
#                         offset_x = node_rect.x - mouse_x
#                         offset_y = node_rect.y - mouse_y
#                         break
#             elif event.button == 3:  # Right mouse button
#                 new_node = pygame.Rect(event.pos[0], event.pos[1], 100, 50)
#                 nodes.append(new_node)
#         elif event.type == pygame.MOUSEBUTTONUP:
#             if event.button == 1:
#                 if drawing_edge:
#                     drawing_edge = False
#                     for node_rect in nodes:
#                         input_circle_pos = (node_rect.left, node_rect.centery)
#                         if pygame.Rect(input_circle_pos[0] - 5, input_circle_pos[1] - 5, 10, 10).collidepoint(event.pos):
#                             edges.append((current_node, node_rect))
#                             break
#                     start_pos = None
#                     current_node = None
#                 dragging = False
#                 dragging_node = None
#         elif event.type == pygame.MOUSEMOTION:
#             if dragging and dragging_node:
#                 mouse_x, mouse_y = event.pos
#                 dragging_node.x = mouse_x + offset_x
#                 dragging_node.y = mouse_y + offset_y

#     # Fill the screen with a color (optional)
#     screen.fill((0, 0, 0))

#     # Draw all edges
#     for edge in edges:
#         start_node, end_node = edge
#         start_pos = (start_node.right, start_node.centery)
#         end_pos = (end_node.left, end_node.centery)
#         pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 2)

#     # Draw all nodes
#     for node_rect in nodes:
#         pygame.draw.rect(screen, (255, 0, 0), node_rect)
#         # Draw a small circle at the right center of each node (output)
#         output_circle_pos = (node_rect.right, node_rect.centery)
#         pygame.draw.circle(screen, (0, 255, 0), output_circle_pos, 5)
#         # Draw a small circle at the left center of each node (input)
#         input_circle_pos = (node_rect.left, node_rect.centery)
#         pygame.draw.circle(screen, (0, 0, 255), input_circle_pos, 5)

#     # Update start_pos if drawing_edge is True
#     if drawing_edge and current_node:
#         start_pos = (current_node.right, current_node.centery)

#     # Draw the edge being drawn
#     if drawing_edge and start_pos:
#         # Check if the mouse is over an input circle
#         for node_rect in nodes:
#             input_circle_pos = (node_rect.left, node_rect.centery)
#             if pygame.Rect(input_circle_pos[0] - 5, input_circle_pos[1] - 5, 10, 10).collidepoint(pygame.mouse.get_pos()):
#                 pygame.draw.line(screen, (255, 255, 255), start_pos, input_circle_pos, 2)
#                 break

#     # Update the display
#     pygame.display.flip()

#     # Cap the frame rate at 60 frames per second
#     clock.tick(60)

# # Quit Pygame
# pygame.quit()
# sys.exit()

import pygame
import pygame_gui
import sys
import math
import time

# --------------------------------------------------
# Utils
# --------------------------------------------------
class Utils:
    zoom = 1.0
    pan_offset = [0, 0]

    @staticmethod
    def world_to_screen(point):
        return (point[0] * Utils.zoom + Utils.pan_offset[0],
                point[1] * Utils.zoom + Utils.pan_offset[1])

    @staticmethod
    def screen_to_world(point):
        return ((point[0] - Utils.pan_offset[0]) / Utils.zoom,
                (point[1] - Utils.pan_offset[1]) / Utils.zoom)

    @staticmethod
    def cubic_bezier(p0, p1, p2, p3, steps=30):
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
            points.append((x, y))
        return points

# --------------------------------------------------
# Node class
# --------------------------------------------------
class Node:
    node_counter = 0

    def __init__(self, pos, name=None, width=100, height=50):
        if name is None:
            Node.node_counter += 1
            self.name = f"Node {Node.node_counter}"
        else:
            self.name = name
        # เก็บตำแหน่งใน world coordinate
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.rect_color = (200, 200, 200)
        self.border_color = (0, 0, 0)
        self.circle_color = (255, 0, 0)
        self.input = (self.rect.left, self.rect.centery)
        self.output = (self.rect.right, self.rect.centery)
        # เก็บชื่อของ Node ที่เชื่อมต่อกัน
        self.next_nodes = []       # ชื่อของ Node ที่เชื่อมต่อจาก output
        self.previous_nodes = []   # ชื่อของ Node ที่เชื่อมเข้ามาที่ input

    def update_io_positions(self):
        self.input = (self.rect.left, self.rect.centery)
        self.output = (self.rect.right, self.rect.centery)

    def draw(self, surface, zoom, pan_offset, is_selected=False):
        self.update_io_positions()
        tr = pygame.Rect(
            self.rect.x * zoom + pan_offset[0],
            self.rect.y * zoom + pan_offset[1],
            self.rect.width * zoom,
            self.rect.height * zoom
        )
        pygame.draw.rect(surface, self.rect_color, tr)
        if is_selected:
            pygame.draw.rect(surface, (0, 255, 0), tr, 3)
        else:
            pygame.draw.rect(surface, self.border_color, tr, 2)
        in_pos = Utils.world_to_screen(self.input)
        out_pos = Utils.world_to_screen(self.output)
        radius = max(3, int(5 * zoom))
        pygame.draw.circle(surface, self.circle_color, (int(in_pos[0]), int(in_pos[1])), radius)
        pygame.draw.circle(surface, self.circle_color, (int(out_pos[0]), int(out_pos[1])), radius)
        font_size = max(12, int(16 * zoom))
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(self.name, True, (0, 0, 0))
        surface.blit(text_surface, (tr.x + 5, tr.y + 5))

    def is_over_output(self, world_pos):
        self.update_io_positions()
        return math.hypot(world_pos[0] - self.output[0], world_pos[1] - self.output[1]) <= 5

    def is_over_input(self, world_pos):
        self.update_io_positions()
        return math.hypot(world_pos[0] - self.input[0], world_pos[1] - self.input[1]) <= 5

# --------------------------------------------------
# NodeForm class (แยกส่วนการสร้าง form)
# --------------------------------------------------
class NodeForm:
    def __init__(self, manager, position):
        """
        สร้างฟอร์มสำหรับสร้าง Node ใหม่
        :param manager: pygame_gui.UIManager
        :param position: ตำแหน่งใน world coordinate ที่ Node จะถูกสร้าง
        """
        # กำหนดตำแหน่งของ form window (ใช้ค่าคงที่สำหรับ rect ใน screen)
        self.window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect(250, 200, 300, 150),
            manager=manager,
            window_display_title="Create Node"
        )
        self.text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(50, 40, 200, 30),
            manager=manager,
            container=self.window
        )
        self.text_entry.set_text("")
        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 90, 100, 40),
            text="Submit",
            manager=manager,
            container=self.window
        )
        self.position = position  # ตำแหน่งใน world ที่จะสร้าง Node

    def get_node_data(self):
        """คืนค่าข้อมูลสำหรับสร้าง Node (ตำแหน่ง, ชื่อ)"""
        return self.position, self.text_entry.get_text()

    def kill(self):
        self.window.kill()

# --------------------------------------------------
# NodeEditor class
# --------------------------------------------------
class NodeEditor:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.nodes = []      # List of Node objects
        self.edges = []      # List of tuples (source, target)
        self.selected_node = None
        self.current_edge = None
        self.dragging_node = False
        self.panning = False
        self.drag_offset = (0, 0)
        self.pan_start = (0, 0)
        self.pan_start_offset = Utils.pan_offset.copy()

        # สำหรับสร้าง Node ผ่านฟอร์ม
        self.node_form = None
        self.node_form_position = None

        # สำหรับตรวจจับ double‑click manual
        self.last_click_time = 0
        self.last_click_pos = (0, 0)
        self.double_click_threshold = 0.4  # วินาที
        self.click_distance_threshold = 10  # พิกเซล (ใน screen)

    def process_event(self, event):
        # ให้ pygame_gui จัดการ event ของ UI ก่อน
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Submit" and self.node_form is not None:
                pos, node_name = self.node_form.get_node_data()
                new_node = Node(pos, name=node_name if node_name != "" else None)
                self.nodes.append(new_node)
                self.node_form.kill()
                self.node_form = None
            return

        if event.type == pygame.QUIT:
            sys.exit()

        # Manual double-click detection
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            current_time = time.time()
            dx = event.pos[0] - self.last_click_pos[0]
            dy = event.pos[1] - self.last_click_pos[1]
            distance = math.hypot(dx, dy)
            if (current_time - self.last_click_time) < self.double_click_threshold and distance < self.click_distance_threshold:
                print("Manual double-click detected at", event.pos)
                world_pos = Utils.screen_to_world(event.pos)
                handled = False
                # ตรวจสอบ double-click บนจุด input
                for node in self.nodes:
                    if node.is_over_input(world_pos):
                        if node.previous_nodes:
                            prev_name = node.previous_nodes[0]
                            self.edges = [edge for edge in self.edges if not (edge[0].name == prev_name and edge[1] == node)]
                            node.previous_nodes.remove(prev_name)
                            prev_node = next((n for n in self.nodes if n.name == prev_name), None)
                            if prev_node and node.name in prev_node.next_nodes:
                                prev_node.next_nodes.remove(node.name)
                            print(f"Deleted edge from {prev_name} to {node.name} (input side)")
                            handled = True
                            break
                if not handled:
                    for node in self.nodes:
                        if node.is_over_output(world_pos):
                            if node.next_nodes:
                                next_name = node.next_nodes[0]
                                self.edges = [edge for edge in self.edges if not (edge[0] == node and edge[1].name == next_name)]
                                node.next_nodes.remove(next_name)
                                next_node = next((n for n in self.nodes if n.name == next_name), None)
                                if next_node and node.name in next_node.previous_nodes:
                                    next_node.previous_nodes.remove(node.name)
                                print(f"Deleted edge from {node.name} to {next_name} (output side)")
                                handled = True
                                break
                self.last_click_time = 0
                return
            else:
                self.last_click_time = current_time
                self.last_click_pos = event.pos

        # Zoom
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            world_before = Utils.screen_to_world(mouse_pos)
            Utils.zoom *= 1.1 ** event.y
            new_pan_x = mouse_pos[0] - world_before[0] * Utils.zoom
            new_pan_y = mouse_pos[1] - world_before[1] * Utils.zoom
            Utils.pan_offset = [new_pan_x, new_pan_y]

        # Mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                # เปิด NodeForm เมื่อคลิกขวา
                if self.node_form is not None:
                    self.node_form.kill()
                    self.node_form = None
                self.node_form_position = Utils.screen_to_world(event.pos)
                self.node_form = NodeForm(self.manager, self.node_form_position)
            elif event.button == 1:
                world_pos = Utils.screen_to_world(event.pos)
                for node in reversed(self.nodes):
                    if node.is_over_output(world_pos):
                        self.current_edge = {"source": node, "start": node.output, "end": world_pos}
                        break
                if self.current_edge is None:
                    found = False
                    for node in reversed(self.nodes):
                        if node.rect.collidepoint(world_pos):
                            self.selected_node = node
                            self.dragging_node = True
                            self.drag_offset = (world_pos[0] - node.rect.x, world_pos[1] - node.rect.y)
                            found = True
                            break
                    if not found:
                        self.selected_node = None
                        self.dragging_node = False
                        self.panning = True
                        self.pan_start = event.pos
                        self.pan_start_offset = Utils.pan_offset.copy()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                world_pos = Utils.screen_to_world(event.pos)
                if self.current_edge is not None:
                    for node in reversed(self.nodes):
                        if node.is_over_input(world_pos) and node != self.current_edge["source"]:
                            self.edges.append((self.current_edge["source"], node))
                            self.current_edge["source"].next_nodes.append(node.name)
                            node.previous_nodes.append(self.current_edge["source"].name)
                            break
                    self.current_edge = None
                self.dragging_node = False
                self.panning = False
        elif event.type == pygame.MOUSEMOTION:
            if self.panning:
                dx = event.pos[0] - self.pan_start[0]
                dy = event.pos[1] - self.pan_start[1]
                Utils.pan_offset = [self.pan_start_offset[0] + dx, self.pan_start_offset[1] + dy]
            if self.dragging_node and self.selected_node is not None:
                world_pos = Utils.screen_to_world(event.pos)
                self.selected_node.rect.x = world_pos[0] - self.drag_offset[0]
                self.selected_node.rect.y = world_pos[1] - self.drag_offset[1]
            if self.current_edge is not None:
                world_pos = Utils.screen_to_world(event.pos)
                self.current_edge["end"] = world_pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                if self.selected_node is not None:
                    self.edges = [edge for edge in self.edges if edge[0] != self.selected_node and edge[1] != self.selected_node]
                    if self.selected_node in self.nodes:
                        self.nodes.remove(self.selected_node)
                    self.selected_node = None

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw(self):
        self.screen.fill((30, 30, 30))
        # Draw all edges
        for edge in self.edges:
            source, target = edge
            source.update_io_positions()
            target.update_io_positions()
            p0_world = source.output
            p3_world = target.input
            offset = 50
            p1_world = (p0_world[0] + offset, p0_world[1])
            p2_world = (p3_world[0] - offset, p3_world[1])
            p0 = Utils.world_to_screen(p0_world)
            p1 = Utils.world_to_screen(p1_world)
            p2 = Utils.world_to_screen(p2_world)
            p3 = Utils.world_to_screen(p3_world)
            bezier_points = Utils.cubic_bezier(p0, p1, p2, p3, steps=30)
            pygame.draw.lines(self.screen, (255, 255, 255), False, bezier_points, 2)
        # Draw current edge if dragging
        if self.current_edge is not None:
            source = self.current_edge["source"]
            source.update_io_positions()
            p0_world = source.output
            p3_world = self.current_edge["end"]
            offset = 50
            p1_world = (p0_world[0] + offset, p0_world[1])
            p2_world = (p3_world[0] - offset, p3_world[1])
            p0 = Utils.world_to_screen(p0_world)
            p1 = Utils.world_to_screen(p1_world)
            p2 = Utils.world_to_screen(p2_world)
            p3 = Utils.world_to_screen(p3_world)
            bezier_points = Utils.cubic_bezier(p0, p1, p2, p3, steps=30)
            pygame.draw.lines(self.screen, (200, 200, 0), False, bezier_points, 2)
            radius = max(3, int(5 * Utils.zoom))
            pygame.draw.circle(self.screen, (200, 200, 0), (int(p3[0]), int(p3[1])), radius)
        # Draw nodes
        for node in self.nodes:
            node.draw(self.screen, Utils.zoom, Utils.pan_offset, is_selected=(node == self.selected_node))
        self.manager.draw_ui(self.screen)

# --------------------------------------------------
# Main function
# --------------------------------------------------
def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Structured Node Editor")
    manager = pygame_gui.UIManager(screen.get_size())
    # manager = pygame_gui.UIManager((800, 600))
    editor = NodeEditor(screen, manager)
    clock = pygame.time.Clock()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            editor.process_event(event)
        editor.update(time_delta)
        editor.draw()
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
