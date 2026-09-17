import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
center = (screen_width / 2, screen_height / 2)
pygame.display.set_caption("Advanced Symmetrical Particle Layers")

# Surface for alpha blending
trail_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

# Layer class to manage shapes and particles
class Layer:
    def __init__(self, center, num_shapes, base_distance, base_radius):
        self.s = 0.1  # Starting scale
        self.s_min = 0.1
        self.s_max = 3.0
        self.scale_speed = 0.15  # Scale units per second, decreased to double the lifespan
        self.rotation = 0
        self.rotation_speed = 0.6 if random.random() < 0.5 else -0.6  # Radians per second
        self.center = center
        self.num_sides = random.randint(3, 8)  # Random number of sides for shapes
        self.angles = [2 * math.pi * i / num_shapes for i in range(num_shapes)]
        self.base_distance = base_distance
        self.base_radius = base_radius
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.opacity = 255  # Start fully opaque

    def update(self, dt):
        """Update scale, rotation, and opacity; return False if layer should be removed."""
        self.s += self.scale_speed * dt
        self.rotation += self.rotation_speed * dt
        if self.s > self.s_max:
            return False
        # Linearly decrease opacity from 255 to 0 as s goes from s_min to s_max
        self.opacity = max(0, int(255 * (1 - (self.s - self.s_min) / (self.s_max - self.s_min))))
        return True

    def draw(self, surface, num_particles_per_side):
        """Draw all particles in the layer along the polygonal shapes."""
        for angle in self.angles:
            # Shape center moves outward with scale
            shape_center_x = self.center[0] + math.cos(angle) * self.base_distance * self.s
            shape_center_y = self.center[1] + math.sin(angle) * self.base_distance * self.s
            # Shape radius grows with scale
            shape_radius = self.base_radius * self.s
            # Calculate vertices with rotation
            vertices = []
            for i in range(self.num_sides):
                theta = 2 * math.pi * i / self.num_sides + self.rotation
                vx = shape_center_x + math.cos(theta) * shape_radius
                vy = shape_center_y + math.sin(theta) * shape_radius
                vertices.append((vx, vy))
            # Place particles along each side of the polygon
            for j in range(self.num_sides):
                start = vertices[j]
                end = vertices[(j + 1) % self.num_sides]
                for k in range(num_particles_per_side):
                    t = k / (num_particles_per_side - 1) if num_particles_per_side > 1 else 0
                    px = start[0] + t * (end[0] - start[0])
                    py = start[1] + t * (end[1] - start[1])
                    # Apply layer’s opacity and keep particle size constant
                    color_with_alpha = self.color + (self.opacity,)
                    particle_radius = 2  # Constant size
                    pygame.draw.circle(surface, color_with_alpha, (int(px), int(py)), particle_radius)

# Constants
fps = 144
spawn_interval = 0.5  # Seconds
num_particles_per_side = 10  # Changed to 10 particles per side

# Main loop
clock = pygame.time.Clock()
layers = []
spawn_timer = 0
running = True
while running:
    dt = clock.tick(fps) / 1000.0  # Delta time in seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Spawn new layer every 0.5 seconds
    spawn_timer += dt
    while spawn_timer >= spawn_interval:
        num_shapes = random.randint(3, 6)
        base_distance = random.uniform(50, 150)
        base_radius = random.uniform(10, 30)
        new_layer = Layer(center, num_shapes, base_distance, base_radius)
        layers.append(new_layer)
        spawn_timer -= spawn_interval

    # Update all layers and remove expired ones
    layers = [layer for layer in layers if layer.update(dt)]

    # Clear the trail surface
    trail_surface.fill((0, 0, 0, 0))

    # Draw all layers
    for layer in layers:
        layer.draw(trail_surface, num_particles_per_side)

    # Render to screen
    screen.fill((0, 0, 0))  # Black background
    screen.blit(trail_surface, (0, 0))
    pygame.display.flip()

pygame.quit()