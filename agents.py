
import random

class Agent:
    def __init__(self, id, parent_id=None, generation=0, parent_talents=None, parent_hobbies=None):
        self.id = id
        self.education = random.choice(["None", "High School", "College"])
        self.age = random.randint(18, 75)
        self.retirement_age = random.randint(65, 75)
        self.retired = self.age >= self.retirement_age
        self.pension = 1000
        self.job = self.assign_job()
        self.income = self.assign_income()
        self.industry = self.assign_industry()
        self.health = random.randint(60, 100)
        if self.retired:
            self.job = "Retired"
            self.income = self.pension
            self.industry = "None"
        self.has_insurance = self.job in ["Doctor", "Engineer", "Teacher"]
        self.cost_of_living = random.randint(800, 2500)
        self.transitioning = False
        self.transition_progress = 0.0
        self.home_coords = (random.randint(100, 700), random.randint(100, 500))
        self.x, self.y = self.home_coords
        self.at_work = False

        # Initialize talents and hobbies
        if parent_talents:
            self.talents = self.mutate_talents(parent_talents)
        else:
            self.talents = self.generate_talents()

        if parent_hobbies:
            self.hobbies = self.mutate_hobbies(parent_hobbies)
        else:
            self.hobbies = self.generate_hobbies()

        # Financial attributes
        self.savings = random.randint(0, 10000)
        self.debt = random.randint(0, 5000)
        self.income_history = [self.income]

        # Bankruptcy flag
        self.bankrupt = False
    def update_finances(self):
        # Update savings/debt each tick
        net = self.income - self.cost_of_living
        self.savings += net * 0.01
        if self.savings < 0:
            self.debt += abs(self.savings) * 0.01
            self.savings = 0
        self.income_history.append(self.income)
        if len(self.income_history) > 120:
            self.income_history.pop(0)
    def retrain(self, economy):
        # Retrain to new career path
        self.transitioning = True
        self.transition_progress = 0.0
        self.decide_career_path(economy)
        self.transitioning = False

    def mutate_talents(self, parent_talents):
        # Slight mutation for each talent
        return {k: min(1.0, max(0.0, v + random.uniform(-0.1, 0.1))) for k, v in parent_talents.items()}

    def mutate_hobbies(self, parent_hobbies):
        # Inherit some hobbies, add random new ones
        hobby_pool = ["Music", "Sports", "Reading", "Coding", "Art", "Gaming", "Cooking", "Travel", "DIY"]
        inherited = random.sample(parent_hobbies, k=min(len(parent_hobbies), random.randint(1, 2))) if parent_hobbies else []
        new_hobbies = random.sample([h for h in hobby_pool if h not in inherited], k=random.randint(0, 2))
        return inherited + new_hobbies

    def generate_talents(self):
        # Logical, Artistic, Social, Physical, Technical
        talents = {
            "logical": random.uniform(0, 1),
            "artistic": random.uniform(0, 1),
            "social": random.uniform(0, 1),
            "physical": random.uniform(0, 1),
            "technical": random.uniform(0, 1)
        }
        return talents

    def generate_hobbies(self):
        hobby_pool = ["Music", "Sports", "Reading", "Coding", "Art", "Gaming", "Cooking", "Travel", "DIY"]
        return random.sample(hobby_pool, k=random.randint(1, 3))

    def decide_career_path(self, economy):
        # Education options
        paths = [
            {
                "name": "No School",
                "years": 0,
                "cost": 0,
                "careers": ["Gig Worker", "Laborer", "Retail", "Delivery"]
            },
            {
                "name": "Trade School",
                "years": 2,
                "cost": 5000,
                "careers": ["Electrician", "Plumber", "Technician", "Driver"]
            },
            {
                "name": "College",
                "years": 4,
                "cost": 40000,
                "careers": ["Doctor", "Lawyer", "Engineer", "Teacher"]
            }
        ]

        # Economic conditions
        recession = getattr(economy, 'recession_enabled', False)
        automation = getattr(economy, 'automation_enabled', False)

        # ROI evaluation for each path
        roi_scores = []
        for path in paths:
            expected_income = self.estimate_career_income(path["careers"], automation)
            roi = self.evaluate_education_roi(path["cost"], path["years"], expected_income, recession)
            # Talent fit bonus
            fit = self.estimate_talent_fit(path["careers"])
            # Recession discourages expensive education
            if recession and path["cost"] > 10000:
                roi *= 0.7
            # Hobbies bonus for certain careers
            hobby_bonus = self.estimate_hobby_bonus(path["careers"])
            total_score = roi + fit + hobby_bonus + random.uniform(-0.2, 0.2)
            roi_scores.append((total_score, path))

        # Pick best path probabilistically
        roi_scores.sort(reverse=True)
        best_path = roi_scores[0][1]
        self.education_path = best_path["name"]
        self.education_years = best_path["years"]
        self.education_cost = best_path["cost"]
        # Pick career from path, weighted by talents/hobbies
        self.career_path = self.pick_career(best_path["careers"], automation)
        self.career_entry_age = self.age + self.education_years
        self.job = self.career_path
        self.income = self.assign_income()
        self.industry = self.assign_industry()
        self.career_decision_debug = f"Agent {self.id}: Talent={self.talents} Hobbies={self.hobbies} Path={self.education_path} Career={self.career_path} Age={self.career_entry_age} Income={self.income}"
        print(self.career_decision_debug)

    def estimate_career_income(self, careers, automation):
        # Map career to income
        job_income = {
            "Engineer": 9000,
            "Doctor": 12000,
            "Lawyer": 11000,
            "Teacher": 4000,
            "Technician": 4500,
            "Clerk": 3000,
            "Driver": 3200,
            "Gig Worker": 2000,
            "Laborer": 2500,
            "Electrician": 5000,
            "Plumber": 5200,
            "Retail": 2800,
            "Delivery": 2600,
            "Unemployed": 0,
            "Displaced": 600,
        }
        # Automation risk: lower expected income for high-risk jobs
        automation_risk = {"Gig Worker": 0.7, "Laborer": 0.6, "Retail": 0.5, "Delivery": 0.8, "Technician": 0.3, "Driver": 0.9}
        incomes = []
        for c in careers:
            base = job_income.get(c, 2000)
            if automation and automation_risk.get(c, 0) > 0.5:
                base *= 0.6
            incomes.append(base)
        return sum(incomes) / len(incomes) if incomes else 2000

    def evaluate_education_roi(self, cost, years, expected_income, recession):
        # ROI = (expected_income * 10 - cost) / (years + 1)
        roi = (expected_income * 10 - cost) / (years + 1)
        if recession:
            roi *= 0.8
        return roi

    def estimate_talent_fit(self, careers):
        # Score based on talents matching career type
        fit = 0.0
        for c in careers:
            if c in ["Engineer", "Technician", "Electrician", "Plumber"]:
                fit += self.talents["technical"]
            if c in ["Doctor", "Teacher", "Lawyer"]:
                fit += self.talents["logical"]
            if c in ["Retail", "Driver", "Delivery"]:
                fit += self.talents["social"]
            if c in ["Laborer"]:
                fit += self.talents["physical"]
            if c in ["Gig Worker"]:
                fit += self.talents["artistic"]
        return fit / max(1, len(careers))

    def estimate_hobby_bonus(self, careers):
        # Bonus if hobby matches career
        bonus = 0.0
        for c in careers:
            if c == "Engineer" and "Coding" in self.hobbies:
                bonus += 0.2
            if c == "Teacher" and "Reading" in self.hobbies:
                bonus += 0.2
            if c == "Electrician" and "DIY" in self.hobbies:
                bonus += 0.2
            if c == "Plumber" and "DIY" in self.hobbies:
                bonus += 0.2
            if c == "Doctor" and "Reading" in self.hobbies:
                bonus += 0.2
            if c == "Gig Worker" and "Gaming" in self.hobbies:
                bonus += 0.2
        return bonus

    def pick_career(self, careers, automation):
        # Weighted pick based on talents/hobbies
        weights = []
        for c in careers:
            w = 1.0
            if c in ["Engineer", "Technician", "Electrician", "Plumber"]:
                w += self.talents["technical"]
            if c in ["Doctor", "Teacher", "Lawyer"]:
                w += self.talents["logical"]
            if c in ["Retail", "Driver", "Delivery"]:
                w += self.talents["social"]
            if c in ["Laborer"]:
                w += self.talents["physical"]
            if c in ["Gig Worker"]:
                w += self.talents["artistic"]
            # Hobby bonus
            if c == "Engineer" and "Coding" in self.hobbies:
                w += 0.2
            if c == "Teacher" and "Reading" in self.hobbies:
                w += 0.2
            if c == "Electrician" and "DIY" in self.hobbies:
                w += 0.2
            if c == "Plumber" and "DIY" in self.hobbies:
                w += 0.2
            if c == "Doctor" and "Reading" in self.hobbies:
                w += 0.2
            if c == "Gig Worker" and "Gaming" in self.hobbies:
                w += 0.2
            # Automation risk
            automation_risk = {"Gig Worker": 0.7, "Laborer": 0.6, "Retail": 0.5, "Delivery": 0.8, "Technician": 0.3, "Driver": 0.9}
            if automation and automation_risk.get(c, 0) > 0.5:
                w *= 0.6
            weights.append(w)
        # Normalize and pick
        total = sum(weights)
        if total == 0:
            return random.choice(careers)
        pick = random.uniform(0, total)
        acc = 0.0
        for c, w in zip(careers, weights):
            acc += w
            if pick <= acc:
                return c
        return careers[-1]
    @staticmethod
    def random(parent_id=None, generation=0, parent_talents=None, parent_hobbies=None):
        return Agent(random.randint(100000, 999999), parent_id, generation, parent_talents, parent_hobbies)

    def assign_job(self):
        if self.education == "College":
            return random.choice(["Engineer", "Doctor", "Lawyer"])
        elif self.education == "High School":
            return random.choice(["Teacher", "Technician", "Clerk", "Driver"])
        else:
            return random.choice(["Gig Worker", "Laborer"])

    def assign_income(self):
        job_income = {
            "Engineer": 9000,
            "Doctor": 12000,
            "Lawyer": 11000,
            "Teacher": 4000,
            "Technician": 4500,
            "Clerk": 3000,
            "Driver": 3200,
            "Gig Worker": 2000,
            "Laborer": 2500,
            "Retired": 1000,
        }
        return job_income.get(self.job, 2000)

    def assign_industry(self):
        return {
            "Engineer": "Tech",
            "Doctor": "Healthcare",
            "Lawyer": "Legal",
            "Teacher": "Education",
            "Clerk": "Retail",
            "Technician": "Tech",
            "Driver": "Logistics",
            "Gig Worker": "Services",
            "Laborer": "Manufacturing",
            "Retired": "None"
        }.get(self.job, "Services")

    def commute_home(self):
        tx, ty = self.home_coords
        self.x += int((tx - self.x) * 0.05)
        self.y += int((ty - self.y) * 0.05)

    def commute_to_work(self):
        if self.industry and self.industry != "None":
            wx, wy = 400, 300  # Default work center
            self.x += int((wx - self.x) * 0.05)
            self.y += int((wy - self.y) * 0.05)
        else:
            self.commute_home()

    def transition_career(self):
        self.transitioning = True
        self.transition_progress = 0.0
        previous_job = self.job
        self.job = self.assign_job()
        self.income = self.assign_income()
        self.industry = self.assign_industry()

    def get_color_tint_by_career(self):
        if self.retired:
            return (180, 180, 180)  # Grey for retired
        level = {
            "Engineer": 3,
            "Doctor": 3,
            "Lawyer": 3,
            "Teacher": 2,
            "Technician": 2,
            "Clerk": 1,
            "Driver": 1,
            "Gig Worker": 0,
            "Laborer": 0
        }.get(self.job, 0)
        base_colors = [
            (120, 120, 255),  # Low
            (100, 255, 150),  # Mid
            (255, 255, 100),  # High
            (255, 180, 50)    # Elite
        ]
        return base_colors[min(level, len(base_colors) - 1)]

    def get_shape_by_industry(self):
        return {
            "Tech": "square",
            "Healthcare": "circle",
            "Legal": "triangle",
            "Education": "hexagon",
            "Retail": "circle",
            "Logistics": "square",
            "Services": "triangle",
            "Manufacturing": "hexagon"
        }.get(self.industry, "circle")

    def get_position(self):
        return self.x, self.y
