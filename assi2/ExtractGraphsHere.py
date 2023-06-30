from vi import Agent, Simulation, Config, HeadlessSimulation
from vi.config import Config, dataclass, deserialize
import random
import datetime
import time
import math
import polars as pl
import seaborn as sns
from pygame.math import Vector2
import pygame as pg

EPS = 10 ** -5

class Grass(Agent):
    agents = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.energy = 0
        self.reproduce_threshold = 15
        self.life_cycle = 0
        self.move = Vector2((0,-1))
        self.move = Vector2((0,0))
        
    def update(self):
        self.save_data('Agent Type', 'Grass')
        self.growing()
        around = 0
        
        # Random grass spawn in specific area
        if self.energy > self.reproduce_threshold and random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.97:
            in_proximity = self.in_proximity_accuracy().filter_kind(Grass)
            for agent, dist in in_proximity:
                around += 1 + 1 / (dist + EPS)
            if around < 1:
                self.reproduce().pos = (self.pos + Vector2(self.rand_seeding(), self.rand_seeding()))

        # Grass growing
        if self.energy < 50:
            self.energy += 0.1
        self.growing()
        self.move = Vector2((0,0))
        if random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.999:
            self.reproduce().pos = Vector2((random.randint(0, 750), random.randint(0, 750)))

    def growing(self):
        self.life_cycle += 0.1
        if self.life_cycle > 10:
            self.energy = self.life_cycle
            self.change_image(1)
        if self.life_cycle > 30:
            self.energy = self.life_cycle
            self.change_image(2)
        if self.life_cycle > 50:
            self.change_image(3)
            self.energy = abs(self.energy - 1)
        if self.life_cycle > 80:
            self.kill()

    def rand_seeding(self):
        number = random.randint(-30, 30)
        # Check if the number falls in the range from -10 to 10
        while -15 <= number <= 15:
            number = random.randint(-30, 30)
        return number

class Rabbit(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer
        self.energy_bar = 60 # Initialize energy bar
        # Set birthtime to current time
        self.birth_time = time.time() 
        self.energy = 0 
        self.reproduce_threshold = 30
        #Rabbit.agents.append(self) ####### UNCOMMENT? > ERROR
        self.accelerate = False
        self.decelerate = True
        self.hop_magnitude = 12
        self.hop = random.randint(0, self.hop_magnitude)
        self.hop_direction = Vector2((random.randint(-1, 1), random.randint(-1, 1))) # a normalized vector

    def generate_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        direction = Vector2(math.cos(angle), math.sin(angle))  # Convert angle to direction vector
        return direction

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight

    def closest_grass(self):
        grasses = list(self.in_proximity_accuracy().filter_kind(Grass))
        closest = 500
        ret = None
        for agent, dist in grasses:
            if dist < closest:
                    ret = (self.move + agent.pos).normalize()
                    closest = dist
        return ret

    
    def eating(self):
         grasses = list(self.in_proximity_accuracy().filter_kind(Grass))
         for agent, dist in grasses:
             if agent.alive() and dist < 10:
                  self.energy_bar = 60
                  agent.kill()
                  if self.energy_bar > self.reproduce_threshold:
                     self.reproduce().move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()
    
    def hoppity(self):
        move_to_grass = self.closest_grass()
        if self.decelerate:
            self.move *= 1.15
        elif self.accelerate:
            self.move *= (1 / 1.15)
        self.hop += 1
        if self.hop > self.hop_magnitude:
            self.move *= 0.6
            if self.hop > int(self.hop_magnitude * 2):
                if self.accelerate:
                    if move_to_grass is None:
                        self.hop_direction = Vector2((random.randint(-1, 1), random.randint(-1, 1))) # a normalized vector
                        self.move = self.hop_direction
                    else:
                        self.move = move_to_grass
                    self.hop_magnitude = random.randint(1, 12)
                self.accelerate = not self.accelerate
                self.decelerate = not self.decelerate
                self.hop = 0
    
    def running_away(self):
        in_proximity = list(self.in_proximity_accuracy().filter_kind(Fox))
        closest = 500
        for agent, dist in in_proximity:
            if dist < closest and agent.died_time == 0:
                #self.move = (self.pos - agent.pos).normalize()
                self.move = agent.move + Vector2((random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)))
                closest = dist
        self.move *= 0.9

    def update(self):
        self.save_data('Agent Type', 'Rabbit')
        
        age = time.time() - self.birth_time
        death_probability = min(0.001 * age, 0.5) 
        reproduction_probability = max(0.003 - 0.0001 * age, 0.001)
        # Random reproduction of rabbits
        if random.random() < reproduction_probability:
           self.reproduce()
        
        # Random chance of death as age increases, higher chance of death as age increases      
        if random.random() < death_probability:
            self.kill()
            return

                ##### Sexual Reproduction #####
        if self.reproduction_timer > 240:  # Check the timer
            potential_mates = self.in_proximity_accuracy().filter_kind(Rabbit)
            for agent, _ in potential_mates:
                if agent.alive() and agent.gender != self.gender:
                    if random.random() < 0.02:  # Chance to reproduce when encountering an opposite gender rabbit
                        self.reproduce() 
                        self.reproduction_timer = 0  # Reset the timer after reproduction
        self.reproduction_timer += 1  # Increment the timer on each frame
        
        # Run away from fox, or eat/hop
        if self.in_proximity_accuracy().filter_kind(Fox).count() > 1:
            self.running_away()
        else:
            self.hoppity()
            self.eating()

class Fox(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer
        Grass.agents.append(self)
        self.energy_bar = 50
        self.died_time = 0
        self.birth_time = time.time() 
        too_full_threshold = 80

    def hunting_fox(self):
        if self.died_time == 0:
            in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
            closest = 500
            for agent, dist in in_proximity:
                if dist < closest:
                    self.move = (agent.pos - self.pos).normalize() * 1.05
                    closest = dist
                if agent.alive() and dist < 25:
                    self.energy_bar = 50 # no inheriting the rabbit energy
                    agent.kill()
                    self.reproduce()

    
    def too_full(self):
        if self.energy_bar > too_full_threshold:
            pass

    def dying_fox(self):
        if self.energy_bar < 0:
            self.move = Vector2((0,-1))
            self.change_image(1)
            self.died_time += 0.1
        if self.died_time > 0:
            self.died_time += 0.1
        if self.died_time % 2 > 1 and self.died_time != 0:
            self.change_image(2)
        else:
            if self.died_time != 0:
                self.change_image(1)
        if self.died_time > 30:
            self.kill()


    def update(self):
        self.save_data('Agent Type', 'Fox')
        self.hunting_fox()
        self.energy_bar -= 0.1
        self.dying_fox()


        age = time.time() - self.birth_time
        death_probability = min(0.010 * age, 0.5) 
        
        # Random chance of death as age increases, higher chance of death as age increases      
        if random.random() < death_probability:
            self.kill()
            return

                ##### Sexual Reproduction #####
        self.reproduction_timer += 1  # Increment the timer on each frame
        if self.reproduction_timer > 240:  
            potential_mates = self.in_proximity_accuracy().filter_kind(Fox)
            for agent, _ in potential_mates:
                if agent.alive() and agent.gender != self.gender:
                    if random.random() < 0.02:  # Chance to reproduce when encountering an opposite gender fox
                        self.reproduce()  
                        self.reproduction_timer = 0  # Reset the timer after reproduction


df = (
    Simulation(Config(
        image_rotation = True,
        radius = 30, # Radius if which agents are in proximity
        duration = 300 * 60, # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second (SET TO 5 MINUTES)
        seed = 1,
    ))
    .batch_spawn_agents(100, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(100, Rabbit, images=['assi2/images/female_rabbit.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/fox.png', 'assi2/images/dead_fox1.png', 'assi2/images/dead_fox2.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/female_fox.png', 'assi2/images/dead_fox1.png', 'assi2/images/dead_fox2.png'])
    .batch_spawn_agents(200, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png', 'assi2/images/dead_grass.png'])
    .run()).snapshots.groupby(['frame','Agent Type']).agg(pl.count('id').alias('Population Count')).sort(['frame', 'Agent Type'])

print(df)
plot = sns.relplot(x=df['frame'], y=df['Population Count'], hue=df['Agent Type'], kind='line')
plot.savefig('assi2/Graphs/Presentation(1).png', dpi=600)
df.write_csv('assi2/CSV Graphs/Test.csv')