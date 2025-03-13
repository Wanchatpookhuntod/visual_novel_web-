import pygame
import pygame_gui
import sys
import math
import time

# --------------------------------------------------
# Utils: ฟังก์ชันช่วยและ global variables
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
# NodeModel: ข้อมูลและ logic ของโหนด (ไม่เกี่ยวกับการวาด UI)
# --------------------------------------------------
class NodeModel:
    node_counter = 0

    def __init__(self, pos, name=None, width=100, height=50):
        if name is None:
            NodeModel.node_counter += 1
            self.name = f"Node {NodeModel.node_counter}"
        else:
            self.name = name
        # เก็บตำแหน่งใน world coordinate
        self.x, self.y = pos[0], pos[1]
        self.width, self.height = width, height
        # เก็บชื่อของ Node ที่เชื่อมต่อ (เป็น string)
        self.next_nodes = []       # ชื่อของ Node ที่เชื่อมต่อออกจาก output
        self.previous_nodes = []   # ชื่อของ Node ที่เชื่อมเข้ามาที่ input

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_position(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_input_position(self):
        return (self.x, self.y + self.height / 2)

    def get_output_position(self):
        return (self.x + self.width, self.y + self.height / 2)

    def get_data(self):
        """คืนค่าข้อมูลของ Node เป็น dictionary"""
        return {
            "name": self.name,
            "position": (self.x, self.y),
            "width": self.width,
            "height": self.height,
            "next_nodes": self.next_nodes,
            "previous_nodes": self.previous_nodes
        }

# --------------------------------------------------
# NodeView: รับผิดชอบการวาด NodeModel ลงบนหน้าจอ
# --------------------------------------------------
class NodeView:
    def __init__(self, node_model):
        self.model = node_model
        self.rect_color = (200, 200, 200)
        self.border_color = (0, 0, 0)
        self.circle_color = (255, 0, 0)

    def draw(self, surface, zoom, pan_offset, is_selected=False):
        rect = self.model.get_rect()
        tr = pygame.Rect(
            rect.x * zoom + pan_offset[0],
            rect.y * zoom + pan_offset[1],
            rect.width * zoom,
            rect.height * zoom
        )
        pygame.draw.rect(surface, self.rect_color, tr)
        if is_selected:
            pygame.draw.rect(surface, (0, 255, 0), tr, 3)
        else:
            pygame.draw.rect(surface, self.border_color, tr, 2)
        # วาด input และ output
        in_pos = Utils.world_to_screen(self.model.get_input_position())
        out_pos = Utils.world_to_screen(self.model.get_output_position())
        radius = max(3, int(5 * zoom))
        pygame.draw.circle(surface, self.circle_color, (int(in_pos[0]), int(in_pos[1])), radius)
        pygame.draw.circle(surface, self.circle_color, (int(out_pos[0]), int(out_pos[1])), radius)
        # วาดชื่อ Node
        font_size = max(12, int(16 * zoom))
        font = pygame.font.SysFont("Arial", font_size)
        text_surface = font.render(self.model.name, True, (0, 0, 0))
        surface.blit(text_surface, (tr.x + 5, tr.y + 5))

# --------------------------------------------------
# NodeForm: คลาสสำหรับสร้างฟอร์ม UI ในการสร้าง Node ใหม่
# --------------------------------------------------
class NodeForm:
    def __init__(self, manager, position):
        # สร้างหน้าต่างฟอร์ม (ตำแหน่งของหน้าต่างใน screen สามารถปรับได้)
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
        self.position = position  # ตำแหน่งใน world สำหรับสร้าง Node

    def get_node_data(self):
        return self.position, self.text_entry.get_text()

    def kill(self):
        self.window.kill()

# --------------------------------------------------
# NodeEditor: จัดการ NodeModel, NodeView, NodeForm และการโต้ตอบทั้งหมด
# --------------------------------------------------
class NodeEditor:
    def __init__(self, screen, manager):
        self.screen = screen
        self.manager = manager
        self.nodes = []    # List of NodeModel objects
        self.edges = []    # List of tuples (source_model, target_model)
        self.selected_node = None
        self.current_edge = None
        self.dragging_node = False
        self.panning = False
        self.drag_offset = (0, 0)
        self.pan_start = (0, 0)
        self.pan_start_offset = Utils.pan_offset.copy()

        self.node_form = None  # Instance ของ NodeForm

        # สำหรับ manual double‑click detection
        self.last_click_time = 0
        self.last_click_pos = (0, 0)
        self.double_click_threshold = 0.4  # วินาที
        self.click_distance_threshold = 10   # พิกเซล (screen)

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Submit" and self.node_form is not None:
                pos, node_name = self.node_form.get_node_data()
                new_node = NodeModel(pos, name=node_name if node_name != "" else None)
                self.nodes.append(new_node)
                print(f"Created node: {new_node.name}")
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
                # ตรวจจับ double-click บนจุด input
                for node in self.nodes:
                    if math.hypot(world_pos[0] - node.get_input_position()[0],
                                  world_pos[1] - node.get_input_position()[1]) <= 5:
                        if node.previous_nodes:
                            prev_name = node.previous_nodes.pop(0)
                            self.edges = [edge for edge in self.edges if not (edge[0].name == prev_name and edge[1] == node)]
                            prev_node = next((n for n in self.nodes if n.name == prev_name), None)
                            if prev_node and node.name in prev_node.next_nodes:
                                prev_node.next_nodes.remove(node.name)
                            print(f"Deleted edge from {prev_name} to {node.name} (input side)")
                            handled = True
                            break
                if not handled:
                    for node in self.nodes:
                        if math.hypot(world_pos[0] - node.get_output_position()[0],
                                      world_pos[1] - node.get_output_position()[1]) <= 5:
                            if node.next_nodes:
                                next_name = node.next_nodes.pop(0)
                                self.edges = [edge for edge in self.edges if not (edge[0] == node and edge[1].name == next_name)]
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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                if self.node_form is not None:
                    self.node_form.kill()
                    self.node_form = None
                pos = Utils.screen_to_world(event.pos)
                self.node_form = NodeForm(self.manager, pos)
            elif event.button == 1:
                world_pos = Utils.screen_to_world(event.pos)
                for node in reversed(self.nodes):
                    # ตรวจสอบคลิกที่ output
                    if math.hypot(world_pos[0] - node.get_output_position()[0],
                                  world_pos[1] - node.get_output_position()[1]) <= 5:
                        self.current_edge = {"source": node, "start": node.get_output_position(), "end": world_pos}
                        break
                if self.current_edge is None:
                    found = False
                    for node in reversed(self.nodes):
                        if node.get_rect().collidepoint(world_pos):
                            self.selected_node = node
                            self.dragging_node = True
                            self.drag_offset = (world_pos[0] - node.x, world_pos[1] - node.y)
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
                        if math.hypot(world_pos[0] - node.get_input_position()[0],
                                      world_pos[1] - node.get_input_position()[1]) <= 5 and node != self.current_edge["source"]:
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
                self.selected_node.update_position(world_pos[0] - self.drag_offset[0], world_pos[1] - self.drag_offset[1])
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
            p0_world = source.get_output_position()
            p3_world = target.get_input_position()
            offset = 50
            p1_world = (p0_world[0] + offset, p0_world[1])
            p2_world = (p3_world[0] - offset, p3_world[1])
            p0 = Utils.world_to_screen(p0_world)
            p1 = Utils.world_to_screen(p1_world)
            p2 = Utils.world_to_screen(p2_world)
            p3 = Utils.world_to_screen(p3_world)
            bezier_points = Utils.cubic_bezier(p0, p1, p2, p3, steps=30)
            pygame.draw.lines(self.screen, (255, 255, 255), False, bezier_points, 2)
        # Draw current edge if any
        if self.current_edge is not None:
            source = self.current_edge["source"]
            p0_world = source.get_output_position()
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
        # Draw nodes using NodeView for each NodeModel
        for node_model in self.nodes:
            node_view = NodeView(node_model)
            node_view.draw(self.screen, Utils.zoom, Utils.pan_offset, is_selected=(node_model == self.selected_node))
        self.manager.draw_ui(self.screen)

    def get_all_node_data(self):
        """คืนค่าข้อมูลของ NodeModel ทั้งหมดในรูปแบบ list ของ dictionary"""
        return [node.get_data() for node in self.nodes]

# --------------------------------------------------
# Main function
# --------------------------------------------------
def main():
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Structured Node Editor")
    manager = pygame_gui.UIManager(screen.get_size())
    editor = NodeEditor(screen, manager)
    clock = pygame.time.Clock()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            manager.process_events(event)
            editor.process_event(event)
        editor.update(time_delta)
        editor.draw()
        pygame.display.flip()

        node_data = editor.get_all_node_data()
        print(node_data)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    pygame.init()
    main()
