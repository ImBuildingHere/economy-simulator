# renderer.py
# Enhanced renderer with daily routine simulation, movement, icons, buildings, trails, needs, and tooltips

import pygame
import math
import time
import random

class Renderer:
    def __init__(self, screen, economy):
        self.screen = screen
        self.economy = economy
        self.font = pygame.font.SysFont(None, 20)
        self.start_time = time.time()
        self.show_stock_market = False
        self.toggle_rect = None
        self.selected_sector = None
        self.show_ubi = False
        self.show_automation = False
        self.show_recession = False
        self.show_transitions = True
        self.show_market_panel = False
        self.industry_positions = self.assign_industry_centers()
        self.agent_trails = {agent.id: [] for agent in economy.agents}

        self.scenario_presets = [
            {
                'name': 'Normal',
                'config': {
                    'spawn_rate': 0.5,
                    'max_population': 200,
                    'ubi_enabled': False,
                    'automation_enabled': False,
                    'recession_enabled': False,
                    'ubi_amount': 600
                }
            },
            {
                'name': '2008 Recession',
                'config': {
                    'spawn_rate': 0.3,
                    'max_population': 180,
                    'ubi_enabled': False,
                    'automation_enabled': False,
                    'recession_enabled': True,
                    'ubi_amount': 600
                }
            },
            {
                'name': 'High Automation',
                'config': {
                    'spawn_rate': 0.4,
                    'max_population': 220,
                    'ubi_enabled': False,
                    'automation_enabled': True,
                    'recession_enabled': False,
                    'ubi_amount': 600
                }
            },
            {
                'name': 'Post-UBI',
                'config': {
                    'spawn_rate': 0.6,
                    'max_population': 250,
                    'ubi_enabled': True,
                    'automation_enabled': True,
                    'recession_enabled': False,
                    'ubi_amount': 1200
                }
            }
        ]

    def render_start_screen(self, selected_scenario_idx):
        font_large = pygame.font.SysFont(None, 50)
        font_small = pygame.font.SysFont(None, 30)
        width, height = self.screen.get_size()

        self.screen.fill((0, 0, 0))
        title_surface = font_large.render("Start Screen - Select Scenario", True, (255, 255, 255))
        self.screen.blit(title_surface, (width // 2 - title_surface.get_width() // 2, 100))

        scenario_name = self.scenario_presets[selected_scenario_idx]['name']
        scenario_surface = font_large.render(f"Scenario: {scenario_name}", True, (255, 255, 0))
        self.screen.blit(scenario_surface, (width // 2 - scenario_surface.get_width() // 2, height // 2))

        instruction_surface = font_small.render("Use LEFT/RIGHT to change, ENTER to start", True, (200, 200, 200))
        self.screen.blit(instruction_surface, (width // 2 - instruction_surface.get_width() // 2, height - 150))

        # Optionally, render toggles for UBI, Automation, Recession here if needed
        # Example:
        # ubi_text = f"UBI: {'ON' if self.economy.ubi_enabled else 'OFF'}"
        # ubi_surface = font_small.render(ubi_text, True, (255, 255, 255))
        # self.screen.blit(ubi_surface, (width // 2 - ubi_surface.get_width() // 2, height // 2 + 50))

        # Centralized UI panel state
        self.panel_rect = pygame.Rect(20, 20, 320, 320)
        self.panel_dragging = False
        self.panel_drag_offset = (0, 0)
        self.panel_hovered = False
        self.panel_last_hover_time = time.time()
        self.panel_auto_hide_delay = 1.2  # seconds

        # Stock market panel state
        self.stock_panel_rect = pygame.Rect(860, 140, 300, 220)
        self.stock_panel_dragging = False
        self.stock_panel_drag_offset = (0, 0)

        self.scenario_presets = [
            {
                'name': 'Normal',
                'config': {
                    'spawn_rate': 0.5,
                    'max_population': 200,
                    'ubi_enabled': False,
                    'automation_enabled': False,
                    'recession_enabled': False,
                    'ubi_amount': 600
                }
            },
            {
                'name': '2008 Recession',
                'config': {
                    'spawn_rate': 0.3,
                    'max_population': 180,
                    'ubi_enabled': False,
                    'automation_enabled': False,
                    'recession_enabled': True,
                    'ubi_amount': 600
                }
            },
            {
                'name': 'High Automation',
                'config': {
                    'spawn_rate': 0.4,
                    'max_population': 220,
                    'ubi_enabled': False,
                    'automation_enabled': True,
                    'recession_enabled': False,
                    'ubi_amount': 600
                }
            },
            {
                'name': 'Post-UBI',
                'config': {
                    'spawn_rate': 0.6,
                    'max_population': 250,
                    'ubi_enabled': True,
                    'automation_enabled': True,
                    'recession_enabled': False,
                    'ubi_amount': 1200
                }
            }
        ]
        self.selected_scenario_idx = 0
        self.selected_generation = None
        self.show_class_overlay = False
        self.show_resource_hud = False
        self.show_housing_afford = False
        self.panel_buttons = self.create_panel_buttons()

    def create_panel_buttons(self):
        # Define button layout and actions with grouping and headings
        btns = []
        y = 40
        spacing = 38

        def add_heading(text):
            nonlocal y
            btns.append({
                'label': lambda t=text: t,
                'rect': lambda: pygame.Rect(20, y, 280, 24),
                'action': lambda: None,
                'tooltip': '',
                'is_heading': True
            })
            y += 30

        def add_button(label_func, action_func, tooltip_text, width=180, x=40):
            nonlocal y
            btns.append({
                'label': label_func,
                'rect': lambda: pygame.Rect(x, y, width, 28),
                'action': action_func,
                'tooltip': tooltip_text,
                'is_heading': False
            })
            y += spacing

        # Scenario Controls
        add_heading("Scenario Controls")
        add_button(lambda: f"Scenario: {self.scenario_presets[self.selected_scenario_idx]['name']}", self.cycle_scenario_preset, "Cycle scenario presets")

        # Economy Toggles
        add_heading("Economy Toggles")
        add_button(lambda: f"UBI: {'ON' if self.economy.ubi_enabled else 'OFF'}", lambda: self.toggle_economy_flag('ubi_enabled'), "Universal Basic Income")
        add_button(lambda: f"Automation: {'ON' if self.economy.automation_enabled else 'OFF'}", lambda: self.toggle_economy_flag('automation_enabled'), "Enable/Disable job automation")
        add_button(lambda: f"Recession: {'ON' if self.economy.recession_enabled else 'OFF'}", lambda: self.toggle_economy_flag('recession_enabled'), "Simulate economic downturn")

        # Renderer Toggles
        add_heading("Renderer Toggles")
        add_button(lambda: f"Market Panel: {'ON' if self.show_market_panel else 'OFF'}", lambda: self.toggle_renderer_flag('show_market_panel'), "Show market demand, stockpile, pricing")
        add_button(lambda: f"Stock Market: {'ON' if self.show_stock_market else 'OFF'}", lambda: self.toggle_renderer_flag('show_stock_market'), "Show/hide stock market panel")
        add_button(lambda: f"Show Class Overlay: {'ON' if self.show_class_overlay else 'OFF'}", lambda: self.toggle_renderer_flag('show_class_overlay'), "Color agents by socioeconomic class")
        add_button(lambda: f"Show Resources: {'ON' if self.show_resource_hud else 'OFF'}", lambda: self.toggle_renderer_flag('show_resource_hud'), "Display steel, water, labor, energy")
        add_button(lambda: f"Show Housing Affordability: {'ON' if self.show_housing_afford else 'OFF'}", lambda: self.toggle_renderer_flag('show_housing_afford'), "Highlight agents with high rent stress")
        add_button(lambda: f"Transitions: {'ON' if self.show_transitions else 'OFF'}", lambda: self.toggle_renderer_flag('show_transitions'), "Highlight agent career transitions")

        # Time and Filters
        add_heading("Time and Filters")
        add_button(lambda: f"Time: {'Paused' if self.economy.paused else f'x{self.economy.time_speed:.2f}'}", self.toggle_time_speed, "Pause/Play, x2, x0.5")
        add_button(lambda: f"Sector: {self.selected_sector if self.selected_sector else 'All'}", self.cycle_sector_filter, "Filter by industry sector")
        add_button(lambda: f"Generation: {self.selected_generation if self.selected_generation is not None else 'All'}", self.cycle_generation_filter, "Filter agents by generation")

        # Save/Load
        add_heading("Save/Load")
        add_button(lambda: "Save World", self.save_world_state, "Export simulation to file", width=90)
        add_button(lambda: "Load World", self.load_world_state, "Import simulation from file", width=90, x=140)

        return btns

    def cycle_scenario_preset(self):
        self.selected_scenario_idx = (self.selected_scenario_idx + 1) % len(self.scenario_presets)
        preset = self.scenario_presets[self.selected_scenario_idx]['config']
        self.economy.apply_config(preset)

    def cycle_generation_filter(self):
        # Find all generations present
        generations = sorted(set(getattr(agent, 'generation', 0) for agent in self.economy.agents))
        if not generations:
            self.selected_generation = None
            return
        if self.selected_generation is None:
            self.selected_generation = generations[0]
        else:
            idx = generations.index(self.selected_generation)
            self.selected_generation = generations[(idx + 1) % len(generations)]

    def save_world_state(self):
        self.economy.export_world_state()

    def load_world_state(self):
        self.economy.import_world_state()

    def toggle_economy_flag(self, flag):
        setattr(self.economy, flag, not getattr(self.economy, flag))

    def toggle_renderer_flag(self, flag):
        setattr(self, flag, not getattr(self, flag))

    def toggle_time_speed(self):
        if self.economy.paused:
            self.economy.paused = False
        elif self.economy.time_speed < 1.0:
            self.economy.time_speed = 1.0
        elif self.economy.time_speed < 2.0:
            self.economy.time_speed = 2.0
        else:
            self.economy.paused = True

    def cycle_sector_filter(self):
        sectors = list(set(agent.industry for agent in self.economy.agents if agent.industry != 'None'))
        if not sectors:
            self.selected_sector = None
            return
        if self.selected_sector not in sectors:
            self.selected_sector = sectors[0]
        else:
            idx = sectors.index(self.selected_sector)
            self.selected_sector = sectors[(idx + 1) % len(sectors)]

    def handle_panel_events(self, mouse_x, mouse_y, mouse_pressed):
        # Check hover and button clicks
        if self.panel_rect.collidepoint(mouse_x, mouse_y):
            self.panel_hovered = True
            self.panel_last_hover_time = time.time()
            for btn in self.panel_buttons:
                rect = btn['rect']()
                btn_rect = pygame.Rect(self.panel_rect.x + rect.x, self.panel_rect.y + rect.y, rect.width, rect.height)
                if btn_rect.collidepoint(mouse_x, mouse_y):
                    if mouse_pressed[0]:
                        btn['action']()
        else:
            self.panel_hovered = False

    def should_show_panel(self):
        # Show if hovered or within delay
        if self.panel_hovered:
            return True
        return (time.time() - self.panel_last_hover_time) < self.panel_auto_hide_delay

    def assign_industry_centers(self):
        width, height = self.screen.get_size()
        industries = list(set(agent.industry for agent in self.economy.agents))
        positions = {}
        for i, industry in enumerate(industries):
            angle = 2 * math.pi * i / len(industries)
            x = width // 2 + int(math.cos(angle) * width * 0.3)
            y = height // 2 + int(math.sin(angle) * height * 0.3)
            positions[industry] = (x, y)
        return positions


    def draw(self):
        self.screen.fill((30, 30, 30))
        mouse_x, mouse_y = pygame.mouse.get_pos()
        elapsed = time.time() - self.start_time
        self.draw_industry_buildings()
        for agent in self.economy.agents:
            if self.selected_sector and agent.industry != self.selected_sector:
                continue

            agent.age += elapsed * 0.01
            agent.health = max(0, agent.health - elapsed * 0.02)
            if agent.has_insurance and agent.health < 100:
                agent.health += elapsed * 0.01
            if agent.age >= agent.retirement_age and not agent.retired:
                agent.retired = True
                agent.job = "Retired"
                agent.income = agent.pension

            # Routine simulation: Morning work, evening home
            routine_phase = (time.time() % 10) / 10
            home_x, home_y = agent.home_coords
            work_x, work_y = self.industry_positions.get(agent.industry, (agent.x, agent.y))
            target_x = work_x if routine_phase < 0.5 else home_x
            target_y = work_y if routine_phase < 0.5 else home_y

            agent.x += int((target_x - agent.x) * 0.02)
            agent.y += int((target_y - agent.y) * 0.02)

            # Update trails
            trail = self.agent_trails.setdefault(agent.id, [])
            trail.append((agent.x, agent.y))
            if len(trail) > 15:
                trail.pop(0)
            for i in range(1, len(trail)):
                pygame.draw.line(self.screen, (60, 60, 90), trail[i - 1], trail[i], 1)

            # Class overlay coloring
            color = agent.get_color_tint_by_career()
            if self.show_class_overlay:
                cls = getattr(agent, 'socioeconomic_class', None)
                if not cls:
                    cls = self.economy.classify_agent(agent)
                if cls == "Lower":
                    color = (120, 120, 120)
                elif cls == "Working":
                    color = (80, 120, 255)
                elif cls == "Middle":
                    color = (80, 255, 120)
                elif cls == "Upper":
                    color = (255, 215, 0)
            if getattr(agent, 'transitioning', False):
                agent.transition_progress += 0.03
                if agent.transition_progress >= 1.0:
                    agent.transitioning = False
                if self.show_transitions:
                    color = (255, 255, 0)

            # Housing affordability overlay
            housing_stressed = False
            if self.show_housing_afford:
                rent = self.economy.housing_market.get('avg_rent', 1200)
                income = getattr(agent, 'income', 1)
                if income > 0 and rent / income > 0.4:
                    housing_stressed = True
            shape = agent.get_shape_by_industry()
            self.draw_agent_shape(agent.x, agent.y, shape, color)
            self.draw_agent_needs(agent)
            if housing_stressed:
                # Blinking red circle or emoji
                if int(time.time() * 2) % 2 == 0:
                    pygame.draw.circle(self.screen, (255, 0, 0), (agent.x, agent.y), 8, 2)
                # Optionally, draw a housing emoji (requires font support)

            if abs(agent.x - mouse_x) < 8 and abs(agent.y - mouse_y) < 8:
                self.draw_tooltip(agent, mouse_x, mouse_y)

    def handle_agent_clicks(self, mouse_pos, mouse_buttons):
        # Detect click and hold on agent to show detailed stats
        if mouse_buttons[0]:
            for agent in self.economy.agents:
                if abs(agent.x - mouse_pos[0]) < 10 and abs(agent.y - mouse_pos[1]) < 10:
                    self.show_agent_stats(agent, mouse_pos)
                    break

    def show_agent_stats(self, agent, pos):
        # Draw a simple stats box near the agent
        stats_text = f"Agent {agent.id}: Talent={agent.talents} Hobbies={agent.hobbies} Path={getattr(agent, 'education_path', 'N/A')} Career={getattr(agent, 'career_path', 'N/A')} Age={agent.age:.1f} Income={agent.income}"
        font_surface = self.font.render(stats_text, True, (255, 255, 255))
        bg_rect = font_surface.get_rect(topleft=(pos[0] + 15, pos[1] + 15))
        pygame.draw.rect(self.screen, (30, 30, 30), bg_rect.inflate(6, 6))
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect.inflate(6, 6), 1)
        self.screen.blit(font_surface, (pos[0] + 15, pos[1] + 15))

        # Resource HUD
        if self.show_resource_hud:
            self.draw_resource_hud(mouse_x, mouse_y)

        self.draw_sector_filter_toggle(mouse_x, mouse_y)
        self.draw_policy_toggles(mouse_x, mouse_y)

        if self.show_stock_market:
            self.draw_stock_market_panel()
        # Market panel HUD
        if self.show_market_panel:
            self.draw_market_panel(mouse_x, mouse_y)

        # Centralized UI panel logic
        mouse_pressed = pygame.mouse.get_pressed()
        self.handle_panel_events(mouse_x, mouse_y, mouse_pressed)
        if self.should_show_panel():
            self.draw_central_panel(mouse_x, mouse_y)

    def draw_central_panel(self, mouse_x, mouse_y):
        # Draw the panel background
        pygame.draw.rect(self.screen, (40, 40, 60), self.panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 180, 220), self.panel_rect, 2, border_radius=8)

        # Draw buttons
        for btn in self.panel_buttons:
            rect = btn['rect']()
            btn_rect = pygame.Rect(self.panel_rect.x + rect.x, self.panel_rect.y + rect.y, rect.width, rect.height)

            # Check hover state
            is_hovered = btn_rect.collidepoint(mouse_x, mouse_y)
            color = (70, 70, 100) if is_hovered else (50, 50, 80)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)

            # Draw label
            label = btn['label']()
            text_surface = self.font.render(label, True, (220, 220, 220))
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)

            # Draw tooltip if hovered
            if is_hovered and 'tooltip' in btn:
                tooltip_text = btn['tooltip']
                tooltip_surface = self.font.render(tooltip_text, True, (255, 255, 255))
                tooltip_rect = tooltip_surface.get_rect(topleft=(btn_rect.right + 10, btn_rect.top))
                pygame.draw.rect(self.screen, (30, 30, 50), tooltip_rect.inflate(6, 4))

    def draw_central_panel(self, mouse_x, mouse_y):
        # Draw the panel background
        pygame.draw.rect(self.screen, (40, 40, 60), self.panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 180, 220), self.panel_rect, 2, border_radius=8)

        # Draw buttons
        for btn in self.panel_buttons:
            rect = btn['rect']()
            btn_rect = pygame.Rect(self.panel_rect.x + rect.x, self.panel_rect.y + rect.y, rect.width, rect.height)

            # Check hover state
            is_hovered = btn_rect.collidepoint(mouse_x, mouse_y)
            color = (70, 70, 100) if is_hovered else (50, 50, 80)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=6)

            # Draw label
            label = btn['label']()
            text_surface = self.font.render(label, True, (220, 220, 220))
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)

            # Draw tooltip if hovered
            if is_hovered and 'tooltip' in btn:
                tooltip_text = btn['tooltip']
                tooltip_surface = self.font.render(tooltip_text, True, (255, 255, 255))
                tooltip_rect = tooltip_surface.get_rect(topleft=(btn_rect.right + 10, btn_rect.top))
                pygame.draw.rect(self.screen, (30, 30, 50), tooltip_rect.inflate(6, 4))

    def draw_resource_hud(self, mouse_x, mouse_y):
        # Draw resource panel at top-right
        width, height = self.screen.get_size()
        panel_rect = pygame.Rect(width - 220, 20, 200, 110)
        pygame.draw.rect(self.screen, (40, 60, 80), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 180, 220), panel_rect, 2, border_radius=8)
        title = self.font.render("Resources", True, (255, 255, 255))
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 8))
        y = panel_rect.y + 32
        for res, val in self.economy.resources.items():
            txt = self.font.render(f"{res.title()}: {val}", True, (220, 220, 220))
            self.screen.blit(txt, (panel_rect.x + 16, y))
            y += 20

    def draw_industry_buildings(self):
        for industry, (x, y) in self.industry_positions.items():
            agent_count = sum(1 for a in self.economy.agents if a.industry == industry)
            size = max(20, min(80, agent_count * 2))
            pygame.draw.rect(self.screen, (80, 100, 140), (x - size//2, y - size//2, size, size), border_radius=4)
            label = self.font.render(industry, True, (255, 255, 255))
            self.screen.blit(label, (x - label.get_width() // 2, y - size // 2 - 15))

    def draw_agent_shape(self, x, y, shape, color):
        if shape == 'circle':
            pygame.draw.circle(self.screen, color, (x, y), 6)
        elif shape == 'square':
            pygame.draw.rect(self.screen, color, pygame.Rect(x - 5, y - 5, 10, 10))
        elif shape == 'triangle':
            points = [(x, y - 6), (x - 6, y + 6), (x + 6, y + 6)]
            pygame.draw.polygon(self.screen, color, points)
        elif shape == 'hexagon':
            points = [
                (x + math.cos(math.radians(angle)) * 6,
                 y + math.sin(math.radians(angle)) * 6)
                for angle in range(0, 360, 60)
            ]
            pygame.draw.polygon(self.screen, color, points)

    def draw_agent_needs(self, agent):
        # Health bar background
        pygame.draw.rect(self.screen, (50, 0, 0), (agent.x - 6, agent.y - 12, 12, 3))
        # Health bar foreground
        health_ratio = max(0.0, min(1.0, agent.health / 100))
        pygame.draw.rect(self.screen, (0, 255, 0), (agent.x - 6, agent.y - 12, int(12 * health_ratio), 3))

    def draw_tooltip(self, agent, x, y):
        info = (
            f"{agent.job} | {agent.education} | ${agent.income} | "
            f"Age: {agent.age:.1f} | Health: {agent.health:.0f}% | "
            f"Cost: ${agent.cost_of_living} | Retired: {'Yes' if agent.retired else 'No'}"
        )
        text_surface = self.font.render(info, True, (255, 255, 255))
        bg_rect = text_surface.get_rect(topleft=(x + 10, y + 10))
        pygame.draw.rect(self.screen, (50, 50, 50), bg_rect.inflate(6, 4))
        self.screen.blit(text_surface, (x + 10, y + 10))

    def draw_stock_market_toggle(self, mouse_x, mouse_y):
        label = "Stock Market"
        text_surface = self.font.render(label, True, (200, 200, 255))
        rect = text_surface.get_rect(topleft=(10, 10))
        pygame.draw.rect(self.screen, (40, 40, 80), rect.inflate(10, 6))
        self.screen.blit(text_surface, rect.topleft)
        if rect.collidepoint(mouse_x, mouse_y):
            if not self.toggle_rect or not self.toggle_rect.collidepoint(mouse_x, mouse_y):
                self.show_stock_market = not self.show_stock_market
            self.toggle_rect = rect

    def draw_sector_filter_toggle(self, mouse_x, mouse_y):
        sectors = list(set(agent.industry for agent in self.economy.agents))[:5]
        for i, sector in enumerate(sectors):
            y = 10 + (i + 1) * 25
            label = sector if sector != self.selected_sector else f"> {sector} <"
            text_surface = self.font.render(label, True, (255, 220, 180))
            rect = text_surface.get_rect(topleft=(150, y))
            pygame.draw.rect(self.screen, (80, 60, 40), rect.inflate(10, 6))
            self.screen.blit(text_surface, rect.topleft)
            if rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                self.selected_sector = None if self.selected_sector == sector else sector

    def draw_policy_toggles(self, mouse_x, mouse_y):
        policies = [
            ("Toggle UBI", self.show_ubi),
            ("Toggle Automation", self.show_automation),
            ("Toggle Recession", self.show_recession)
        ]
        for i, (label, active) in enumerate(policies):
            text = f"[{label}]" if active else label
            text_surface = self.font.render(text, True, (200, 255, 200) if active else (180, 180, 180))
            rect = text_surface.get_rect(topleft=(300, 10 + i * 25))
            pygame.draw.rect(self.screen, (50, 50, 50), rect.inflate(10, 6))
            self.screen.blit(text_surface, rect.topleft)

            if rect.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0]:
                if "UBI" in label:
                    self.show_ubi = not self.show_ubi
                    self.economy.ubi_enabled = self.show_ubi
                elif "Automation" in label:
                    self.show_automation = not self.show_automation
                    self.economy.automation_enabled = self.show_automation
                elif "Recession" in label:
                    self.show_recession = not self.show_recession
                    self.economy.recession_enabled = self.show_recession

    def draw_stock_market_panel(self):
        companies = self.economy.get_company_stats()
        y = self.stock_panel_rect.y + 20
        for name, data in companies.items():
            info = f"{name}: ${data['stock_price']:.2f} ({data['change']:+.2f}%)"
            color = (0, 255, 0) if data['change'] >= 0 else (255, 0, 0)
            text_surface = self.font.render(info, True, color)
            self.screen.blit(text_surface, (self.stock_panel_rect.x + 10, y))
            y += 20

    def draw_market_panel(self, mouse_x, mouse_y):
        # Draw market data for each industry
        width, height = self.screen.get_size()
        panel_rect = pygame.Rect(width - 320, 140, 300, 220)
        pygame.draw.rect(self.screen, (30, 30, 60), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (120, 180, 220), panel_rect, 2, border_radius=8)
        title = self.font.render("Market Data", True, (255, 255, 255))
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 8))
        y = panel_rect.y + 32
        for industry in self.economy.sectors:
            company = None
            for c in self.economy.companies.values():
                if c.industry == industry:
                    company = c
                    break
            if not company:
                continue
            demand = self.economy.demand_shocks.get(industry, 1.0)
            txt = self.font.render(f"{industry}: Price ${company.price} | Stockpile {company.stockpile} | Sold {company.sold_last_tick} | Demand x{demand:.2f}", True, (220, 220, 220))
            self.screen.blit(txt, (panel_rect.x + 16, y))
            y += 24

