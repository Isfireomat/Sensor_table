import math
import pygame

class Cover:
    def __init__(self, center, width, height, color,angle=0):
        # self.angle = self.set_angle(angle)
        self.set_angle(angle)
        self.center = center
        self.first_center = (center[0], center[1], self.angle)
        self.width = width
        self.height = height
        self.color = color
        # self.angle=0
    def set_angle(self,angle):
        if angle>=360:
            angle%=360
        elif angle<0:
            angle+=360
        self.angle=angle
        
    def update(self):
        self.angle += 1
        if self.angle >= 360:
            self.angle = 0

    def move(self, point):
        self.center = (point[0], point[1])
        self.angle = point[2]

    def draw(self, surface):
        points = self.get_rotated_rect_points()
        pygame.draw.polygon(surface, self.color, points)

    def get_rotated_rect_points(self):
        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        half_width = self.width / 2
        half_height = self.height / 2

        points = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]

        rotated_points = []
        for x, y in points:
            rotated_x = self.center[0] + x * cos_a - y * sin_a
            rotated_y = self.center[1] + x * sin_a + y * cos_a
            rotated_points.append((rotated_x, rotated_y))

        return rotated_points

    def collidepoint(self, point):
        rect_points = self.get_rotated_rect_points()
        return self.point_in_polygon(point, rect_points)

    @staticmethod
    def point_in_polygon(point, polygon):
        x, y = point
        n = len(polygon)
        inside = False
        px, py = polygon[0]
        for i in range(n+1):
            qx, qy = polygon[i % n]
            if y > min(py, qy):
                if y <= max(py, qy):
                    if x <= max(px, qx):
                        if py != qy:
                            xinters = (y - py) * (qx - px) / (qy - py) + px
                        if px == qx or x <= xinters:
                            inside = not inside
            px, py = qx, qy
        return inside

    def scale(self, scale_factor):
        # Calculate the new width and height
        new_width = self.width * scale_factor
        new_height = self.height * scale_factor
        
        # Calculate the center displacement due to scaling
        center_displacement_x = (new_width - self.width) / 2
        center_displacement_y = (new_height - self.height) / 2
        
        # Update width and height
        self.width = new_width
        self.height = new_height
        
        # Update the center
        self.center = (self.center[0] + center_displacement_x, self.center[1] + center_displacement_y)
