# economy.py
# Handles agent updates, job assignment, company performance, UBI, automation, and macro events

import random
import time

class Company:
    def __init__(self, name, industry):
        self.name = name
        self.industry = industry
        self.employees = []
        self.revenue = random.randint(100000, 1000000)
        self.stock_price = round(random.uniform(10, 100), 2)
        self.growth = random.uniform(-0.05, 0.05)
        # Market simulation fields
        self.products_produced = 0
        self.resources_required = self.get_resources_required()
        self.price = 100
        self.stockpile = 0
        self.sold_last_tick = 0
        self.cycle_phase = "neutral"  # Add this

    def get_resources_required(self):
        # Example mapping by industry
        mapping = {
            "Tech": {"steel": 10, "energy": 20, "labor": 5},
            "Healthcare": {"water": 5, "labor": 10, "energy": 5},
            "Retail": {"labor": 8, "energy": 5},
            "Finance": {"energy": 3, "labor": 2},
            "Education": {"labor": 10, "energy": 2}
        }
        return mapping.get(self.industry, {"labor": 5, "energy": 2})

    def produce_and_sell(self, economy, market_demand, demand_multiplier=1.0, policy=None):
        if policy is None:
            policy = {
                'stimulus': 0.0,
                'corporate_tax_rate': 0.2,
                'price_controls_enabled': False,
                'price_ceiling': 200
            }

        prod_factor = 1.0
        price_factor = 1.0
        if self.cycle_phase == "boom":
            prod_factor = 1.2
            price_factor = 1.1
        elif self.cycle_phase == "bust":
            prod_factor = 0.7
            price_factor = 0.8

        if policy.get('stimulus', 0) > 0:
            prod_factor += policy['stimulus']
        if policy.get('corporate_tax_rate', 0) > 0:
            price_factor -= policy['corporate_tax_rate'] * 0.01
        if policy.get('price_controls_enabled', False):
            self.price = min(self.price, policy.get('price_ceiling', self.price))

        for res, amt in self.resources_required.items():
            if economy.resources.get(res, 0) < amt * prod_factor:
                economy.log_event(f"{self.name} shortage of {res}")
                return 0

        for res, amt in self.resources_required.items():
            economy.resources[res] -= int(amt * prod_factor)
        produced = int(10 * prod_factor)
        self.products_produced += produced
        self.stockpile += produced

        effective_demand = int(market_demand * demand_multiplier)
        sold = min(self.stockpile, effective_demand)
        net_income = sold * int(self.price * price_factor)
        net_income = int(net_income * (1 - policy.get('corporate_tax_rate', 0.2)))
        self.revenue += net_income
        self.sold_last_tick = sold
        self.stockpile -= sold

        if sold < effective_demand * 0.5:
            self.price = max(10, int(self.price * 0.95))
            economy.log_event(f"{self.name} price dropped due to oversupply")
        elif sold > effective_demand * 0.9:
            self.price = int(self.price * 1.05)
            economy.log_event(f"{self.name} price spiked due to high demand")

        return sold

    # Company scaffolding for layoffs/hiring
    def layoff(self, percent=0.1):
        n = int(len(self.employees) * percent)
        for _ in range(n):
            if self.employees:
                agent = self.employees.pop()
                agent.job = "Unemployed"
                agent.income = 0
    def hire(self, agent):
        self.employees.append(agent)
        agent.job = self.name
        agent.income = random.randint(3000, 12000)
        agent.industry = self.industry
        agent.employer = self.name
    def update(self):
        performance = random.uniform(-0.03, 0.03) + self.growth
        self.stock_price = max(1.0, self.stock_price * (1 + performance))
        self.revenue = max(10000, self.revenue * (1 + performance))
        self.growth += random.uniform(-0.005, 0.005)

class Economy:
    def create_companies(self):
        companies = {}
        # Ensure industries is initialized before calling this
        industries = self.industries if hasattr(self, 'industries') and self.industries else set(["Tech", "Healthcare", "Retail", "Finance", "Education"])
        for industry in industries:
            companies[industry] = Company(industry, industry)
        return companies
    def apply_config(self, config):
        # Apply scenario config to economy
        for k, v in config.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def export_world_state(self, filename='savegame.json'):
        import json
        state = {
            'agents': [self.agent_to_dict(agent) for agent in self.agents],
            'config': {
                'spawn_rate': self.spawn_rate,
                'max_population': self.max_population,
                'ubi_enabled': self.ubi_enabled,
                'automation_enabled': self.automation_enabled,
                'recession_enabled': self.recession_enabled,
                'ubi_amount': self.ubi_amount
            },
            'day_time': self.day_time,
            'time_speed': self.time_speed
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"World state saved to {filename}")

    def import_world_state(self, filename='savegame.json'):
        import json
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
        except Exception as e:
            print(f"Failed to load: {e}")
            return
        self.agents.clear()
        for agent_data in state.get('agents', []):
            from agents import Agent
            agent = Agent(agent_data.get('id', random.randint(100000, 999999)))
            for k, v in agent_data.items():
                setattr(agent, k, v)
            self.add_agent(agent)
        self.apply_config(state.get('config', {}))
        self.day_time = state.get('day_time', 0.0)
        self.time_speed = state.get('time_speed', 1.0)
        print(f"World state loaded from {filename}")

    def agent_to_dict(self, agent):
        # Serialize agent state
        attrs = [
            'id', 'age', 'retirement_age', 'retired', 'pension', 'job', 'income', 'industry', 'health',
            'has_insurance', 'cost_of_living', 'transitioning', 'transition_progress', 'home_coords', 'x', 'y', 'at_work',
            'talents', 'hobbies', 'education_path', 'career_path', 'education_years', 'education_cost', 'career_entry_age',
            'career_decision_debug', 'parent_id', 'generation'
        ]
        return {k: getattr(agent, k, None) for k in attrs}
    def __init__(self):
        self.agents = []
        self.industries = set(["Tech", "Healthcare", "Retail", "Finance", "Education"])
        self.ubi_enabled = False
        self.ubi_amount = 600
        self.automation_enabled = False
        self.recession_enabled = False
        self.event_log = []
        self.day_time = 0.0
        self.time_speed = 1.0
        self.paused = False
        self.sectors = ["Tech", "Healthcare", "Retail", "Finance", "Education"]
        self.companies = self.create_companies()
        # Sprint 7-B: Demand shocks initialization
        self.demand_shocks = {sector: 1.0 for sector in self.sectors}
        self.stimulus_by_industry = {  # targeted economic stimulus
            "Tech": 0.1,
            "Healthcare": 0.05,
            "Retail": 0.0,
            "Finance": -0.05,
            "Education": 0.0
        }
        self.corporate_tax_rate = 0.2
        self.price_controls_enabled = False
        self.price_ceiling = 200
        self.resources = {
            "steel": 1000,
            "water": 1000,
            "labor": 1000,
            "energy": 1000
        }
        self.spawn_enabled = True
        self.last_birth_time = time.time()
        self.spawn_rate = 0.1
        self.max_population = 1000
        self.cycle_timer = 0.0
        self.cycle_length = 100.0
        self.cycle_phase = "boom"
        self.inflation_rate = 0.02

    def produce_and_sell(self, economy, market_demand, demand_multiplier=1.0, policy=None):
        # Sprint 7-B: Demand shocks, boom/bust, policy controls
        if policy is None:
            policy = {
                'stimulus': 0.0,
                'corporate_tax_rate': 0.2,
                'price_controls_enabled': False,
                'price_ceiling': 200
            }
        # Boom/bust cycle
        prod_factor = 1.0
        price_factor = 1.0
        if self.cycle_phase == "boom":
            prod_factor = 1.2
            price_factor = 1.1
        elif self.cycle_phase == "bust":
            prod_factor = 0.7
            price_factor = 0.8
        # Policy controls
        if policy.get('stimulus', 0) > 0:
            prod_factor += policy['stimulus']
        if policy.get('corporate_tax_rate', 0) > 0:
            price_factor -= policy['corporate_tax_rate'] * 0.01
        if policy.get('price_controls_enabled', False):
            self.price = min(self.price, policy.get('price_ceiling', self.price))
        # Consume resources, produce products
        can_produce = True
        for res, amt in self.resources_required.items():
            if economy.resources.get(res, 0) < amt * prod_factor:
                can_produce = False
                economy.log_event(f"{self.name} shortage of {res}")
        if can_produce:
            for res, amt in self.resources_required.items():
                economy.resources[res] -= int(amt * prod_factor)
            produced = int(10 * prod_factor)
            self.products_produced += produced
            self.stockpile += produced
        # Sell products based on market demand and demand shocks
        effective_demand = int(market_demand * demand_multiplier)
        sold = min(self.stockpile, effective_demand)
        net_income = sold * int(self.price * price_factor)
        # Apply corporate tax
        net_income = int(net_income * (1 - policy.get('corporate_tax_rate', 0.2)))
        self.revenue += net_income
        self.sold_last_tick = sold
        self.stockpile -= sold
        # Price elasticity: adjust price if oversupply/undersupply
        if sold < effective_demand * 0.5:
            self.price = max(10, int(self.price * 0.95))
            economy.log_event(f"{self.name} price dropped due to oversupply")
        elif sold > effective_demand * 0.9:
            self.price = int(self.price * 1.05)
            economy.log_event(f"{self.name} price spiked due to high demand")
        return sold

    def seed_population(self):
        # Controlled seeding: one agent per valid job path
        from agents import Agent
        # Pull all careers from decision tree
        job_paths = [
            ("No School", ["Gig Worker", "Laborer", "Retail", "Delivery"]),
            ("Trade School", ["Electrician", "Plumber", "Technician", "Driver"]),
            ("College", ["Doctor", "Lawyer", "Engineer", "Teacher"])
        ]
        for path_name, careers in job_paths:
            for career in careers:
                agent = Agent.random()
                # Force agent to take this path/career
                agent.education_path = path_name
                agent.career_path = career
                agent.job = career
                agent.education_years = 0 if path_name == "No School" else (2 if path_name == "Trade School" else 4)
                agent.education_cost = 0 if path_name == "No School" else (5000 if path_name == "Trade School" else 40000)
                agent.career_entry_age = agent.age + agent.education_years
                agent.income = agent.assign_income()
                agent.industry = agent.assign_industry()
                self.add_agent(agent)

    def update_births(self, current_time):
        # Dynamic birth simulation
        if not self.spawn_enabled:
            return
        if len(self.agents) >= self.max_population:
            return
        # Spawn based on spawn_rate and time
        if current_time - self.last_birth_time >= 1.0 / max(0.01, self.spawn_rate):
            from agents import Agent
            agent = Agent.random()
            self.add_agent(agent)
            self.last_birth_time = current_time
    def update(self):
        if self.paused:
            return
        # Birth simulation
        self.update_births(current_time=time.time())
        self.day_time += 0.01 * self.time_speed
        if self.day_time > 1.0:
            self.day_time = 0.0
        # Macroeconomic cycle update
        self.cycle_timer += 0.01 * self.time_speed
        if self.cycle_timer > self.cycle_length:
            self.cycle_timer = 0.0
            self.advance_economic_cycle()
        # Inflation update
        inflation_monthly = (1 + self.inflation_rate) ** (1/12) - 1
        # Sprint 7-B: Apply demand shocks
        self.apply_demand_shocks()
        # Boom/bust cycle for companies
        for company in self.companies.values():
            # Randomly change cycle phase
            if random.random() < 0.01:
                company.cycle_phase = random.choice(["boom", "bust", "neutral"])
        # Market simulation
        global_market = {
            "Consumer Goods": random.randint(100, 500),
            "Commodities": random.randint(50, 200)
        }
        total_output = 0
        for company in self.companies.values():
            company.update()
            company.revenue *= (1 + inflation_monthly)
            # Simulate product output and sales
            demand = global_market["Consumer Goods"] if company.industry in ["Tech", "Retail", "Healthcare", "Education"] else global_market["Commodities"]
            # Sprint 7-B: Demand shocks, policy controls
            demand_multiplier = self.demand_shocks.get(company.industry, 1.0)
            policy = {
                'stimulus': self.stimulus_by_industry.get(company.industry, 0.0),
                'corporate_tax_rate': self.corporate_tax_rate,
                'price_controls_enabled': self.price_controls_enabled,
                'price_ceiling': self.price_ceiling
            }
            sold = company.produce_and_sell(self, demand, demand_multiplier, policy)
            total_output += sold
        # Regenerate resources each tick
        for res in self.resources:
            regen = 50 if res == "water" else 20
            self.resources[res] += regen
        # Decay unused resources (spoilage)
        for res in self.resources:
            if self.resources[res] > 100000:
                self.resources[res] -= int(self.resources[res] * 0.01)
        self.log_event(f"Total market output: {total_output}")

        for agent in self.agents:
            # UBI
            if self.ubi_enabled:
                agent.income += self.ubi_amount * 0.01

            # Inflation: cost of living and prices
            agent.cost_of_living = int(agent.cost_of_living * (1 + inflation_monthly))

            # Financial update
            agent.update_finances()

            # Bankruptcy detection
            if agent.savings < -agent.debt:
                agent.bankrupt = True
                self.log_event(f"Agent {agent.id} BANKRUPT (Savings: {agent.savings}, Debt: {agent.debt})")

            # Automation/recession events
            if self.automation_enabled and random.random() < 0.001:
                agent.job = "Displaced"
                agent.income *= 0.3
                self.log_event(f"{agent.job} lost job to automation (Agent {agent.id})")

            if self.recession_enabled and random.random() < 0.002:
                agent.job = "Unemployed"
                agent.income = 0
                self.log_event(f"{agent.job} lost job in downturn (Agent {agent.id})")

            # Retraining system
            if agent.job in ["Displaced", "Unemployed"] and random.random() < 0.05:
                agent.retrain(self)
                self.log_event(f"Agent {agent.id} retrained to {agent.job}")

            # Career transitions
            if random.random() < 0.002:
                agent.transition_career()

            # Daily routine cycle
            if self.day_time < 0.33:
                agent.at_work = False
                agent.commute_home()
            elif self.day_time < 0.66:
                agent.at_work = True
                agent.commute_to_work()
            else:
                agent.at_work = False
                agent.commute_home()

    def apply_demand_shocks(self):
        # Randomly adjust demand multipliers per industry
        for sector in self.demand_shocks:
            shock = random.uniform(0.95, 1.05)
            # Occasional big shock
            if random.random() < 0.01:
                shock *= random.choice([0.7, 1.3])
            self.demand_shocks[sector] = max(0.5, min(2.0, self.demand_shocks[sector] * shock))
            # Log major shocks
            if shock < 0.8 or shock > 1.2:
                self.log_event(f"Demand shock in {sector}: {self.demand_shocks[sector]:.2f}")

    def advance_economic_cycle(self):
        # Cycle through boom, recession, stagnation
        if self.cycle_phase == "boom":
            self.cycle_phase = "recession"
            self.inflation_rate = 0.04
        elif self.cycle_phase == "recession":
            self.cycle_phase = "stagnation"
            self.inflation_rate = 0.01
        else:
            self.cycle_phase = "boom"
            self.inflation_rate = 0.02
        self.log_event(f"Economic cycle advanced to {self.cycle_phase} (Inflation: {self.inflation_rate:.2%})")

    def log_event(self, msg):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.event_log.append(f"[{timestamp}] {msg}")

    def toggle_pause(self):
        self.paused = not self.paused

    def set_time_speed(self, speed):
        self.time_speed = speed

    def add_agent(self, agent):
        self.agents.append(agent)

    def get_company_stats(self):
        stats = {}
        for name, company in self.companies.items():
            stats[name] = {
                'stock_price': company.stock_price,
                'change': company.growth * 100  # approximate percentage change
            }
        return stats
