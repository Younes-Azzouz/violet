from vi import Agent, Simulation, Config
from vi.config import Config, dataclass, deserialize
import random
import seaborn as sns
import polars as pl
from pygame.math import Vector2
import math

import pygame as pg

EPS = 10 ** -5



class Rabbit(Agent):
    agents = []    

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reproduce_threshold = 30
        Rabbit.agents.append(self)
        self.energy_bar = 60
        
        self.accelerate = False
        self.decelerate = True
        self.hop_magnitude = 12
        self.hop = random.randint(0, self.hop_magnitude)

        self.hop_direction = Vector2((random.randint(-1, 1), random.randint(-1, 1))) # a normalized vector


    def generate_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        direction = Vector2(math.cos(angle), math.sin(angle))  # Convert angle to direction vector
        return direction
    
    

    def update(self):
        self.save_data('Agent Type', 'Rabbit')
        #self.energy_bar -= 0.1
        if self.energy_bar <= 0:
            self.kill()
        
        if self.in_proximity_accuracy().filter_kind(Fox).count() > 1:
            self.running_away()
        else:
            self.hoppity()
            self.eating()
        
        

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
                self.energy_bar += agent.energy if self.energy_bar < 5 else 5
                agent.kill()
                if self.energy_bar > self.reproduce_threshold:
                    pass
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


class Fox(Agent):

    agents = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.energy_bar = 50
        self.died_time = 0

        too_full_threshold = 80

    def update(self):
        self.save_data('Agent Type', 'Fox')
        self.hunting_fox()
        self.energy_bar -= 0.1
        self.dying_fox()

    def hunting_fox(self):
        if self.died_time == 0:
            in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
            closest = 500
            for agent, dist in in_proximity:
                if dist < closest:
                    self.move = (agent.pos - self.pos).normalize() * 1.05
                    closest = dist
                if agent.alive() and dist < 10:
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


class Grass(Agent):

    agents = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.reproduce_threshold = 15
        self.life_cycle = 0
        self.energy = 0
        self.move = Vector2((0,-1))
        self.move = Vector2((0,0))

    def update(self):
        self.save_data('Agent Type', 'Grass')
        self.growing()

        around = 0
        
        if self.energy > self.reproduce_threshold and random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.97:
            in_proximity = self.in_proximity_accuracy().filter_kind(Grass)
            for agent, dist in in_proximity:
                around += 1 + 1 / (dist + EPS)
            if around < 1:
                self.reproduce().pos = (self.pos + Vector2(self.rand_seeding(), self.rand_seeding()))

    def rand_seeding(self):
        # Generate a random number between -20 and 20
        number = random.randint(-30, 30)
        
        # Check if the number falls in the range from -10 to 10
        while -15 <= number <= 15:
            number = random.randint(-30, 30)
    
        return number

    

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


class RabbitFoxSimulation(Simulation):

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        #print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")




df = (
    Simulation(Config(
        image_rotation = True,
        movement_speed=1,
        radius=25,
        seed=1
    ))
    .batch_spawn_agents(40, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(5, Fox, images=['assi2/images/fox.png', 'assi2/images/dead_fox1.png', 'assi2/images/dead_fox2.png'])
    .batch_spawn_agents(10, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png', 'assi2/images/dead_grass.png'])
    .run()
    .snapshots.groupby(['frame','Agent Type']) # Initialize dataframe
    #.groupby(['frame','id', 'Agent Type'])
    #.groupby(['frame','Agent Type'])
    #.agg(pl.count('id').alias('agent number'))
    .agg(pl.count('id').alias('agent number'))
    .sort(['frame', 'Agent Type'])
)
print(df) # Print dataframe
# Plot df
sns.color_palette()
plot = sns.relplot(x=df['frame'], y=df['agent number'], hue=df['Agent Type'], kind='line', palette=['orange', 'green', 'red'])
plot.savefig('assi2/Graphs/grassFoxKing(2).png', dpi=600)