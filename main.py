# main.py
# Entry point for the economic simulation game

import pygame
from economy import Economy
from renderer import Renderer
from agents import Agent

# Config constants (inlined)
WIDTH, HEIGHT = 1920, 1080
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evolving Economy Simulator")
clock = pygame.time.Clock()

# Create simulation core
economy = Economy()
renderer = Renderer(screen, economy)

# Add agents
for _ in range(100):
    economy.add_agent(Agent.random())

# Start screen loop for adjustments before simulation starts
def start_screen():
    selecting = True
    selected_scenario_idx = 0
    font = pygame.font.SysFont(None, 40)
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    selecting = False
                elif event.key == pygame.K_RIGHT:
                    selected_scenario_idx = (selected_scenario_idx + 1) % len(renderer.scenario_presets)
                elif event.key == pygame.K_LEFT:
                    selected_scenario_idx = (selected_scenario_idx - 1) % len(renderer.scenario_presets)

        renderer.render_start_screen(selected_scenario_idx)

        pygame.display.flip()
        clock.tick(FPS)

    # Apply selected scenario config to economy
    preset = renderer.scenario_presets[selected_scenario_idx]['config']
    economy.apply_config(preset)

start_screen()

# Main simulation loop
running = True
paused = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_UP:
                economy.time_speed *= 2
            elif event.key == pygame.K_DOWN:
                economy.time_speed = max(0.25, economy.time_speed / 2)

    if not paused:
        economy.update()

    renderer.draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
