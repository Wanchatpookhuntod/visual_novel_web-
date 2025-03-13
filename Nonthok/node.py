import pygame
import pygame_gui
import sys
import math
import time

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Node Editor - Double Click Delete Edge Only")
clock = pygame.time.Clock()

manager = pygame_gui.UIManager(screen.get_size())

# --- ฟังก์ชันแปลงพิกัดระหว่าง world กับ screen ---
zoom = 1.0
pan_offset = [0, 0]

def world_to_screen(point):
    return (point[0] * zoom + pan_offset[0],
            point[1] * zoom + pan_offset[1])

def screen_to_world(point):
    return ((point[0] - pan_offset[0]) / zoom,
            (point[1] - pan_offset[1]) / zoom)

# --- ฟังก์ชันคำนวณ cubic Bézier curve ---
def cubic_bezier(p0, p1, p2, p3, steps=30):
    points = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]
        points.append((x, y))
    return points

# --- Node Class (เก็บ next_nodes และ previous_nodes เป็นชื่อของโหนด) ---
node_counter = 0
class Node:
    def __init__(self, pos, name=None, width=100, height=50):
        global node_counter
        if name is None:
            node_counter += 1
            self.name = f"Node {node_counter}"
        else:
            self.name = name
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.rect_color = (200, 200, 200)
        self.border_color = (0, 0, 0)
        self.circle_color = (255, 0, 0)
        self.input = (self.rect.left, self.rect.centery)
        self.output = (self.rect.right, self.rect.centery)
        # เก็บชื่อของโหนดที่เชื่อมต่อ (เป็น string)
        self.next_nodes = []       # ชื่อของโหนดที่เชื่อมต่อจาก output
        self.previous_nodes = []   # ชื่อของโหนดที่เชื่อมเข้ามาที่ input
        
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
        in_pos = world_to_screen(self.input)
        out_pos = world_to_screen(self.output)
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

# --- เก็บข้อมูล Node และ Edge ---
allNode = []
edges = []  # เก็บเป็น tuple (source, target)

# --- ตัวแปรควบคุมการโต้ตอบ ---
selected_node = None
dragging_node = False
drag_offset = (0, 0)
current_edge = None

panning = False
pan_start = (0, 0)
pan_start_offset = (0, 0)

# --- ตัวแปรสำหรับ pygame_gui form ---
node_form_window = None
node_form_position = None
node_name_entry = None

# --- ตัวแปรสำหรับตรวจจับ double-click manual ---
last_click_time = 0
double_click_threshold = 0.4  # 400 ms
last_click_pos = (0, 0)
click_distance_threshold = 10  # pixels (screen coordinate)

fullscreen = False

running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        manager.process_events(event)
        
        if event.type == pygame.QUIT:
            running = False

        # Manual double-click detection (สำหรับปุ่มซ้าย)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            current_time = time.time()
            dx = event.pos[0] - last_click_pos[0]
            dy = event.pos[1] - last_click_pos[1]
            distance = math.hypot(dx, dy)
            if (current_time - last_click_time) < double_click_threshold and distance < click_distance_threshold:
                print("Manual double-click detected at", event.pos)
                world_pos = screen_to_world(event.pos)
                double_click_handled = False
                # ตรวจสอบ double-click ที่จุด input
                for node in allNode:
                    if node.is_over_input(world_pos):
                        if node.previous_nodes:
                            prev_name = node.previous_nodes[0]
                            # ค้นหา edge ที่เชื่อมระหว่าง prev_node (ชื่อ prev_name) กับ node
                            prev_node = next((n for n in allNode if n.name == prev_name), None)
                            if prev_node is not None:
                                edges[:] = [edge for edge in edges if not (edge[0] == prev_node and edge[1] == node)]
                                node.previous_nodes.remove(prev_name)
                                if node.name in prev_node.next_nodes:
                                    prev_node.next_nodes.remove(node.name)
                                print(f"Deleted edge between {prev_node.name} and {node.name} (input side)")
                                double_click_handled = True
                                break
                if not double_click_handled:
                    # ตรวจสอบ double-click ที่จุด output
                    for node in allNode:
                        if node.is_over_output(world_pos):
                            if node.next_nodes:
                                next_name = node.next_nodes[0]
                                next_node = next((n for n in allNode if n.name == next_name), None)
                                if next_node is not None:
                                    edges[:] = [edge for edge in edges if not (edge[0] == node and edge[1] == next_node)]
                                    node.next_nodes.remove(next_name)
                                    if node.name in next_node.previous_nodes:
                                        next_node.previous_nodes.remove(node.name)
                                    print(f"Deleted edge between {node.name} and {next_node.name} (output side)")
                                    double_click_handled = True
                                    break
                last_click_time = 0
                continue  # ข้าม event อื่น ๆ สำหรับ double-click
            else:
                last_click_time = current_time
                last_click_pos = event.pos

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            world_before = screen_to_world(mouse_pos)
            zoom *= 1.1 ** event.y
            new_pan_x = mouse_pos[0] - world_before[0] * zoom
            new_pan_y = mouse_pos[1] - world_before[1] * zoom
            pan_offset = [new_pan_x, new_pan_y]

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                if node_form_window is not None:
                    node_form_window.kill()
                    node_form_window = None
                    node_name_entry = None
                node_form_position = screen_to_world(event.pos)
                node_form_window = pygame_gui.elements.UIWindow(
                    rect=pygame.Rect(250, 200, 300, 150),
                    manager=manager,
                    window_display_title="Create Node"
                )
                node_name_entry = pygame_gui.elements.UITextEntryLine(
                    relative_rect=pygame.Rect(50, 40, 200, 30),
                    manager=manager,
                    container=node_form_window
                )
                node_name_entry.set_text("")
                node_submit_button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(100, 90, 100, 40),
                    text="Submit",
                    manager=manager,
                    container=node_form_window
                )
            elif event.button == 1:
                world_pos = screen_to_world(event.pos)
                for node in reversed(allNode):
                    if node.is_over_output(world_pos):
                        current_edge = {"source": node, "start": node.output, "end": world_pos}
                        break
                if current_edge is None:
                    found = False
                    for node in reversed(allNode):
                        if node.rect.collidepoint(world_pos):
                            selected_node = node
                            dragging_node = True
                            drag_offset = (world_pos[0] - node.rect.x, world_pos[1] - node.rect.y)
                            found = True
                            break
                    if not found:
                        selected_node = None
                        dragging_node = False
                        panning = True
                        pan_start = event.pos
                        pan_start_offset = pan_offset.copy()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                world_pos = screen_to_world(event.pos)
                if current_edge is not None:
                    for node in reversed(allNode):
                        if node.is_over_input(world_pos) and node != current_edge["source"]:
                            edges.append((current_edge["source"], node))
                            current_edge["source"].next_nodes.append(node.name)
                            node.previous_nodes.append(current_edge["source"].name)
                            break
                    current_edge = None
                dragging_node = False
                panning = False

        elif event.type == pygame.MOUSEMOTION:
            if panning:
                dx = event.pos[0] - pan_start[0]
                dy = event.pos[1] - pan_start[1]
                pan_offset = [pan_start_offset[0] + dx, pan_start_offset[1] + dy]
            if dragging_node and selected_node is not None:
                world_pos = screen_to_world(event.pos)
                selected_node.rect.x = world_pos[0] - drag_offset[0]
                selected_node.rect.y = world_pos[1] - drag_offset[1]
            if current_edge is not None:
                world_pos = screen_to_world(event.pos)
                current_edge["end"] = world_pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                if selected_node is not None:
                    edges = [edge for edge in edges if edge[0] != selected_node and edge[1] != selected_node]
                    if selected_node in allNode:
                        allNode.remove(selected_node)
                    selected_node = None
            elif event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Submit" and node_form_window is not None:
                node_name = node_name_entry.get_text()
                new_node = Node(node_form_position, name=node_name if node_name != "" else None)
                allNode.append(new_node)
                node_form_window.kill()
                node_form_window = None
                node_name_entry = None

    manager.update(time_delta)
    screen.fill((30, 30, 30))
    
    # --- วาด edge (Bézier curve) ---
    for edge in edges:
        source, target = edge
        source.update_io_positions()
        target.update_io_positions()
        p0_world = source.output
        p3_world = target.input
        offset = 50
        p1_world = (p0_world[0] + offset, p0_world[1])
        p2_world = (p3_world[0] - offset, p3_world[1])
        p0 = world_to_screen(p0_world)
        p1 = world_to_screen(p1_world)
        p2 = world_to_screen(p2_world)
        p3 = world_to_screen(p3_world)
        bezier_points = cubic_bezier(p0, p1, p2, p3, steps=30)
        pygame.draw.lines(screen, (255, 255, 255), False, bezier_points, 2)
    
    # --- วาด edge แบบชั่วคราว (ขณะลาก) พร้อมจุดวงกลมปลาย ---
    if current_edge is not None:
        source = current_edge["source"]
        source.update_io_positions()
        p0_world = source.output
        p3_world = current_edge["end"]
        offset = 50
        p1_world = (p0_world[0] + offset, p0_world[1])
        p2_world = (p3_world[0] - offset, p3_world[1])
        p0 = world_to_screen(p0_world)
        p1 = world_to_screen(p1_world)
        p2 = world_to_screen(p2_world)
        p3 = world_to_screen(p3_world)
        bezier_points = cubic_bezier(p0, p1, p2, p3, steps=30)
        pygame.draw.lines(screen, (200, 200, 0), False, bezier_points, 2)
        radius = max(3, int(5 * zoom))
        pygame.draw.circle(screen, (200, 200, 0), (int(p3[0]), int(p3[1])), radius)
    
    # --- วาด Node ทั้งหมด ---
    for node in allNode:
        node.draw(screen, zoom, pan_offset, is_selected=(node == selected_node))
        print(f"Node {node.name} - Next: {node.next_nodes}, Previous: {node.previous_nodes}")
    
    manager.draw_ui(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
