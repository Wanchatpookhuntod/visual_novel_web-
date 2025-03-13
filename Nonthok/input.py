import pygame

# กำหนดค่าต่างๆ
pygame.init()
WIDTH, HEIGHT = 500, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Input Box in Pygame")

# ตั้งค่าฟอนต์
FONT = pygame.font.Font(None, 32)

# กำหนดค่ากล่องอินพุต
input_box = pygame.Rect(100, 100, 300, 40)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ""
done = False

while not done:
    screen.fill((30, 30, 30))  # พื้นหลังสีดำ

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            # เช็คว่าคลิกที่ input box หรือไม่
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    print("Input:", text)  # แสดงข้อความที่พิมพ์เมื่อกด Enter
                    text = ""  # เคลียร์ช่องข้อความ
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]  # ลบตัวอักษรตัวสุดท้าย
                else:
                    text += event.unicode  # เพิ่มตัวอักษรที่พิมพ์ลงไป

    # วาด Input Box
    pygame.draw.rect(screen, color, input_box, 2)
    
    # แสดงข้อความที่พิมพ์
    txt_surface = FONT.render(text, True, pygame.Color('white'))
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

    pygame.display.flip()

pygame.quit()
