import pygame
import sys
import math
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load music
music_path = "/Users/muneebmushtaq/custom_questions/Iou_game/assests/music.mp3"
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
else:
    print("Missing music file in assets/sf_theme.mp3")

# Screen settings
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BBox Arena - Visualizer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Constants
SPEED = 5
HANDLE_SIZE = 10
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 128, 255)
PURPLE = (150, 0, 150)

initial_box1 = pygame.Rect(100, 100, 150, 100)
initial_box2 = pygame.Rect(400, 300, 150, 100)
box1 = initial_box1.copy()
box2 = initial_box2.copy()

selected_box = None
resize_mode = None
mouse_offset = (0, 0)

def draw_text(text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def iou(a, b):
    xA, yA = max(a.left, b.left), max(a.top, b.top)
    xB, yB = min(a.right, b.right), min(a.bottom, b.bottom)
    inter_w, inter_h = max(0, xB - xA), max(0, yB - yA)
    inter = inter_w * inter_h
    union = a.width * a.height + b.width * b.height - inter + 1e-6
    return inter / union, inter

def giou(a, b, i):
    xC, yC = min(a.left, b.left), min(a.top, b.top)
    xD, yD = max(a.right, b.right), max(a.bottom, b.bottom)
    convex = (xD - xC) * (yD - yC)
    inter = i * (a.width * a.height + b.width * b.height - i)
    union = a.width * a.height + b.width * b.height - inter
    return i - (convex - union) / (convex + 1e-6)

def diou(a, b, i):
    cxA, cyA = a.center
    cxB, cyB = b.center
    center_dist = (cxA - cxB) ** 2 + (cyA - cyB) ** 2
    xC, yC = min(a.left, b.left), min(a.top, b.top)
    xD, yD = max(a.right, b.right), max(a.bottom, b.bottom)
    diag = (xD - xC) ** 2 + (yD - yC) ** 2
    return i - center_dist / (diag + 1e-6), math.sqrt(center_dist)

def ciou(a, b, d):
    w1, h1 = a.width, a.height
    w2, h2 = b.width, b.height
    v = (4 / math.pi ** 2) * (math.atan(w2 / h2) - math.atan(w1 / h1)) ** 2
    alpha = v / (1 - d + v + 1e-6) if v != 0 else 0
    return d - alpha * v

def draw_resize_handles(rect, color):
    pygame.draw.rect(screen, color, rect, 2)
    for x in [rect.left, rect.right - HANDLE_SIZE]:
        for y in [rect.top, rect.bottom - HANDLE_SIZE]:
            pygame.draw.rect(screen, color, (x, y, HANDLE_SIZE, HANDLE_SIZE))

def get_resize_handle(rect, pos):
    mx, my = pos
    corners = {
        'tl': pygame.Rect(rect.left, rect.top, HANDLE_SIZE, HANDLE_SIZE),
        'tr': pygame.Rect(rect.right - HANDLE_SIZE, rect.top, HANDLE_SIZE, HANDLE_SIZE),
        'bl': pygame.Rect(rect.left, rect.bottom - HANDLE_SIZE, HANDLE_SIZE, HANDLE_SIZE),
        'br': pygame.Rect(rect.right - HANDLE_SIZE, rect.bottom - HANDLE_SIZE, HANDLE_SIZE, HANDLE_SIZE),
    }
    for key, area in corners.items():
        if area.collidepoint(mx, my):
            return key
    return None

def resize_box(rect, mode, mouse_pos):
    if mode == 'tl':
        rect.width += rect.left - mouse_pos[0]
        rect.height += rect.top - mouse_pos[1]
        rect.left = mouse_pos[0]
        rect.top = mouse_pos[1]
    elif mode == 'tr':
        rect.width = mouse_pos[0] - rect.left
        rect.height += rect.top - mouse_pos[1]
        rect.top = mouse_pos[1]
    elif mode == 'bl':
        rect.width += rect.left - mouse_pos[0]
        rect.left = mouse_pos[0]
        rect.height = mouse_pos[1] - rect.top
    elif mode == 'br':
        rect.width = mouse_pos[0] - rect.left
        rect.height = mouse_pos[1] - rect.top

def draw_bar(name, val, y, color):
    pygame.draw.rect(screen, WHITE, (750, y, 220, 20), 2)
    fill = min(1, max(0, val)) * 216
    pygame.draw.rect(screen, color, (752, y+2, fill, 16))
    draw_text(f"{name}: {val:.3f}", 750, y - 20)

mouse_down = False
music_paused = False

while True:
    screen.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                box1 = initial_box1.copy()
                box2 = initial_box2.copy()
            elif event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True
            for box in [box1, box2]:
                mode = get_resize_handle(box, (mx, my))
                if mode:
                    selected_box = box
                    resize_mode = mode
                    break
            else:
                if box1.collidepoint(mx, my):
                    selected_box = box1
                    mouse_offset = (mx - box1.x, my - box1.y)
                elif box2.collidepoint(mx, my):
                    selected_box = box2
                    mouse_offset = (mx - box2.x, my - box2.y)
                else:
                    selected_box = None
                    resize_mode = None

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
            selected_box = None
            resize_mode = None

    if mouse_down and selected_box:
        if resize_mode:
            resize_box(selected_box, resize_mode, (mx, my))
        else:
            selected_box.topleft = (mx - mouse_offset[0], my - mouse_offset[1])

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: box1.x -= SPEED
    if keys[pygame.K_RIGHT]: box1.x += SPEED
    if keys[pygame.K_UP]: box1.y -= SPEED
    if keys[pygame.K_DOWN]: box1.y += SPEED
    if keys[pygame.K_a]: box2.x -= SPEED
    if keys[pygame.K_d]: box2.x += SPEED
    if keys[pygame.K_w]: box2.y -= SPEED
    if keys[pygame.K_s]: box2.y += SPEED

    # Draw Boxes & Overlap
    draw_resize_handles(box1, GREEN)
    draw_resize_handles(box2, RED)

    # Overlap visualization
    xA, yA = max(box1.left, box2.left), max(box1.top, box2.top)
    xB, yB = min(box1.right, box2.right), min(box1.bottom, box2.bottom)
    if xB > xA and yB > yA:
        pygame.draw.rect(screen, PURPLE, (xA, yA, xB - xA, yB - yA), 0)

    # Metrics
    iou_val, inter_area = iou(box1, box2)
    giou_val = giou(box1, box2, iou_val)
    diou_val, center_dist = diou(box1, box2, iou_val)
    ciou_val = ciou(box1, box2, diou_val)

    # Center visualization
    pygame.draw.circle(screen, WHITE, box1.center, 5)
    pygame.draw.circle(screen, WHITE, box2.center, 5)
    pygame.draw.line(screen, BLUE, box1.center, box2.center, 2)
    draw_text(f"Center Distance: {center_dist:.1f}px", 10, 130)

    # Metric text
    draw_text(f"Intersection Area: {inter_area:.1f}px²", 10, 100)
    draw_text("Press R = Reset | M = Mute", 10, HEIGHT - 30)

    # Draw metric bars
    draw_bar("IoU", iou_val, 200, (0, 255, 0))
    draw_bar("GIoU", giou_val, 250, (255, 255, 0))
    draw_bar("DIoU", diou_val, 300, (255, 128, 0))
    draw_bar("CIoU", ciou_val, 350, (255, 0, 0))

    pygame.display.flip()
    clock.tick(60)
