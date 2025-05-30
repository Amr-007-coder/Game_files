import pygame, math

pygame.init()

def draw_dashed_circle(surface, center, radius, dash_length, gap_length, color, width):
    circumference = 2 * math.pi * radius
    num_dashes = int(circumference // (dash_length + gap_length))
    angle_step = 2 * math.pi / num_dashes

    for i in range(num_dashes):
        start_angle = i * angle_step
        end_angle = start_angle + (dash_length / radius)

        start_pos = (center[0] + math.cos(start_angle) * radius,
                     center[1] + math.sin(start_angle) * radius)
        end_pos = (center[0] + math.cos(end_angle) * radius,
                   center[1] + math.sin(end_angle) * radius)

        pygame.draw.line(surface, color, start_pos, end_pos, width)

def create_circle_rects(center, radius, rect_size):
    rects = []
    cx, cy = center
    diameter = 2 * radius
    start_x = cx - radius
    start_y = cy - radius

    for y in range(start_y, start_y + diameter, rect_size):
        for x in range(start_x, start_x + diameter, rect_size):
            dist = math.sqrt((x + rect_size / 2 - cx) ** 2 + (y + rect_size / 2 - cy) ** 2)
            if dist <= radius:
                rects.append(pygame.Rect(x, y, rect_size, rect_size))
    
    return rects