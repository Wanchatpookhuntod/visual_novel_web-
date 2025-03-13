import pygame
import sys
import math

# กำหนดค่าเริ่มต้นของ Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Node Editor with 90° Edges")
clock = pygame.time.Clock()

# ตัวนับสำหรับสร้างชื่อโหนดอัตโนมัติ
node_counter = 0

def get_right_angle_points(p0, p3):
    """
    สร้าง polyline แบบมุม 90 องศา
    โดยคำนวณจุดกลางในแนวแกน x จากนั้น
    วาดเส้นจาก p0 -> (x_mid, p0.y) -> (x_mid, p3.y) -> p3
    """
    x_mid = (p0[0] + p3[0]) / 2
    return [p0, (x_mid, p0[1]), (x_mid, p3[1]), p3]

# คลาสสำหรับโหนด
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
        # กำหนดตำแหน่งเริ่มต้นของ input (ด้านซ้าย) และ output (ด้านขวา)
        self.input = (self.rect.left, self.rect.centery)
        self.output = (self.rect.right, self.rect.centery)

    def update_io_positions(self):
        self.input = (self.rect.left, self.rect.centery)
        self.output = (self.rect.right, self.rect.centery)

    def draw(self, surface):
        self.update_io_positions()
        pygame.draw.rect(surface, self.rect_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        pygame.draw.circle(surface, self.circle_color, self.input, 5)
        pygame.draw.circle(surface, self.circle_color, self.output, 5)
        font = pygame.font.SysFont("Arial", 16)
        text_surface = font.render(self.name, True, (0, 0, 0))
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def is_over_output(self, pos):
        self.update_io_positions()
        distance = math.hypot(pos[0] - self.output[0], pos[1] - self.output[1])
        return distance <= 5

    def is_over_input(self, pos):
        self.update_io_positions()
        distance = math.hypot(pos[0] - self.input[0], pos[1] - self.input[1])
        return distance <= 5

# ตัวแปรสำหรับเก็บโหนดและ edge
allNode = []
# edges เก็บคู่ (source, target)
edges = []

# ตัวแปรสำหรับจัดการการลากโหนดและลาก edge
selected_node = None
drag_offset = (0, 0)
current_edge = None  # เก็บข้อมูล edge แบบชั่วคราวเมื่อกำลังลากจาก output

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # คลิกขวาเพื่อสร้างโหนดใหม่
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                pos = pygame.mouse.get_pos()
                new_node = Node(pos)
                allNode.append(new_node)
            # ปุ่มซ้ายสำหรับเริ่มลาก edge หรือเลือกลากโหนด
            elif event.button == 1:
                pos = pygame.mouse.get_pos()
                # ตรวจสอบว่าคลิกที่จุด output ของโหนดหรือไม่
                for node in reversed(allNode):
                    if node.is_over_output(pos):
                        current_edge = {"source": node, "start": node.output, "end": pos}
                        break
                # หากไม่ได้เริ่มลาก edge ให้ตรวจสอบสำหรับลากโหนด
                if current_edge is None:
                    for node in reversed(allNode):
                        if node.rect.collidepoint(pos):
                            selected_node = node
                            drag_offset = (pos[0] - node.rect.x, pos[1] - node.rect.y)
                            break

        # เมื่อปล่อยปุ่มซ้าย
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pos = pygame.mouse.get_pos()
                # หากกำลังลาก edge อยู่ ให้ตรวจสอบว่าปล่อยบนจุด input ของโหนดเป้าหมาย
                if current_edge is not None:
                    for node in reversed(allNode):
                        if node.is_over_input(pos) and node != current_edge["source"]:
                            edges.append((current_edge["source"], node))
                            break
                    current_edge = None
                selected_node = None

        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            if current_edge is not None:
                current_edge["end"] = pos
            if selected_node is not None:
                selected_node.rect.x = pos[0] - drag_offset[0]
                selected_node.rect.y = pos[1] - drag_offset[1]

    # วาดพื้นหลัง
    screen.fill((30, 30, 30))

    # วาด edge ทั้งหมดที่เชื่อมต่อระหว่างโหนดแบบมุม 90 องศา
    for edge in edges:
        source, target = edge
        source.update_io_positions()
        target.update_io_positions()
        points = get_right_angle_points(source.output, target.input)
        pygame.draw.lines(screen, (255, 255, 255), False, points, 2)

    # หากกำลังลาก edge อยู่ ให้วาด polyline แบบชั่วคราว
    if current_edge is not None:
        source = current_edge["source"]
        points = get_right_angle_points(source.output, current_edge["end"])
        pygame.draw.lines(screen, (200, 200, 0), False, points, 2)

    # วาดโหนดทั้งหมด
    for node in allNode:
        node.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
