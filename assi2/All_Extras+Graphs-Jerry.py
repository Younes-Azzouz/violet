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
import pandas as pd
import matplotlib.pyplot as plt

EPS = 10 ** -5



class Grass(Agent):
    agents = []
    switch = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age_count = 0
        Grass.agents.append(self)
        self.energy = 0
############################ FOXKING ################################
        self.reproduce_threshold = 15
        self.life_cycle = 0
        self.move = Vector2((0,-1))
#######################################################################
        
    def update(self):
        # Save grass data
        self.save_data('Agent Type', 'Grass')
####################### FOX KING ################################
        self.calculate_average()
        
        self.age_count += 1/60
        in_proximity_grasses = self.in_proximity_accuracy().filter_kind(Grass)
        self.growing()
        self.sexing(in_proximity_grasses)

        # Grass growing
        if self.energy < 50:
            self.energy += 0.1
        self.growing()
        self.move = Vector2((0,0))
        #if random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.999:
            #self.reproduce().pos = Vector2((random.randint(0, 750), random.randint(0, 750)))
        
        self.calculate_average()

    def sexing(self, in_proximity):
        around = 0

        if self.energy > self.reproduce_threshold:
            
            for agent, dist in in_proximity:
                if dist < 100:
                    around += 1 + 1 / (dist + EPS)
            if around < 1:
                self.reproduce().pos = (self.pos + Vector2(self.rand_seeding(), self.rand_seeding()))

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
        # Generate a random number between -20 and 20
        number = random.randint(-30, 30)
        
        # Check if the number falls in the range from -10 to 10
        while -15 <= number <= 15:
            number = random.randint(-30, 30)
    
        return number

    average_ages = [0]

    def calculate_average(self):
        summa = 0
        alive = 0
        for agent in Grass.agents:
            if agent.alive():
                alive += 1
                summa += agent.age_count
        if alive > 0 and Grass.average_ages[-1] != summa / alive:
            Grass.average_ages.append(summa / alive)
            #self.save_data('Average Grass Age', summa / alive)
        else:
            pass
            #self.save_data('Average Grass Age', 0)

    
class Rabbit(Agent):
    # Init agent with Energybar

    agents = []
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.age_count = 0

        self.gender = random.choice(["male", "female"]) # Choose random a gender
        if self.gender == "male":
            self.change_image(0)
        else:
            self.change_image(1)
        self.reproduction_timer = 0  # Initialize the timer
        self.energy_bar = 60 # Initialize energy bar
        # Set birthtime to current time
        self.birth_time = time.time() 
        # Jerrys imp, unnecessary?
        self.energy = 0 
##########      NEW FROM GRASSFOXKING.py ############
        self.reproduce_threshold = 30
        Rabbit.agents.append(self)
        self.accelerate = False
        self.decelerate = True
        self.hop_magnitude = 12
        self.hop = random.randint(0, self.hop_magnitude)
        self.hop_direction = Vector2((random.randint(-1, 1), random.randint(-1, 1))) # a normalized vector
        self.age = 0

    def generate_random_direction(self):
        angle = random.uniform(0, 2 * math.pi)  # Random angle in radians
        direction = Vector2(math.cos(angle), math.sin(angle))  # Convert angle to direction vector
        return direction

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight

    def closest_grass(self, in_proximity):
        closest = 500
        ret = None
        for agent, dist in in_proximity:
            if dist < closest:
                    ret = (self.pos + agent.pos).normalize()
                    closest = dist
        return ret

    
    def eating(self, in_proximity_grass, in_proximity_rabbits):
        for agent, dist in in_proximity_grass:
            if agent.alive() and dist < 10:
                self.energy_bar = 60
                agent.kill()
                if self.energy_bar > self.reproduce_threshold and len(in_proximity_rabbits) < 8:
                    self.reproduce().move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()
    
    def hoppity(self, in_proximity):
        move_to_grass = self.closest_grass(in_proximity)
        
        if self.hop > self.hop_magnitude:
            self.move *= 0.6
            if self.hop > int(self.hop_magnitude * 2):
                if self.accelerate:
                    if move_to_grass is None:
                        
                        self.hop_direction = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize() # a normalized vector
                        self.move = self.hop_direction
                    else:
                        self.move = move_to_grass
                    self.hop_magnitude = random.randint(1, 12)
                self.accelerate = not self.accelerate
                self.decelerate = not self.decelerate
                self.hop = 0
        if self.decelerate:
            self.move *= 1.15
        elif self.accelerate:
            self.move *= (1 / 1.15)
        self.hop += 1
    
    def running_away(self, in_proximity):
        closest = 500
        for agent, dist in in_proximity:
            if dist < closest and agent.died_time == 0:
                #self.move = (self.pos - agent.pos).normalize()
                #self.move = agent.move + Vector2((random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)))
                self.move.x = (self.move.x + (agent.pos - self.pos).normalize().x * -1) / 2
                self.move.y = (self.move.y + (self.pos - agent.pos).normalize().y) / 2
                closest = dist

        self.move *= 1.05
    
    def sexing(self, in_proximity):
        ########### Sexual Reproduction ###########
        if self.reproduction_timer > 240:  # Check the timer
            for agent, _ in in_proximity:
                if agent.alive() and agent.gender != self.gender:
                    if random.random() < 0.5:  # Chance to reproduce when encountering an opposite gender rabbit
                        self.reproduce().move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()
                        self.reproduction_timer = 0  # Reset the timer after reproduction
        self.reproduction_timer += 1  # Increment the timer on each frame

    def aging(self, in_proximity_rabbits):
        # Age implementation
        self.age = time.time() - self.birth_time
        death_probability = min(0.001 * self.age, 0.01) 
        reproduction_probability = min(0.005 - 0.0001 * self.age, 0.001)
        
                
        # Random chance of death as age increases, higher chance of death as age increases      
        if random.random() < death_probability:
            self.kill()
            return
        # Random chance of reproduction decreases as age increases, the lower age the higher chance of reproduction
        if random.random() < reproduction_probability:
            self.reproduce().move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()
####################          ####################       #############                  ###############################

    def dont_collide(self, in_proximity):
        for agent, dist in in_proximity:
            if dist < 15:
                self.move = (agent.move + self.move) / 2


    average_ages = [0]

    def calculate_average(self):
        summa = 0
        alive = 0
        for agent in Rabbit.agents:
            if agent.alive():
                alive += 1
                summa += agent.age_count
        if alive > 0 and Rabbit.average_ages[-1] != summa / alive:
            Rabbit.average_ages.append(summa / alive)
            #self.save_data('Average Rabbit Age', summa / alive)
        else:
            pass
            #self.save_data('Average Rabbit Age', 0)

    def update(self):
        # Save Rabbit data
        self.save_data('Agent Type', 'Rabbit')

        self.calculate_average()

        self.age_count += 1/60

        ip_rabbits = list(self.in_proximity_accuracy().filter_kind(Rabbit))
        ip_foxes = list(self.in_proximity_accuracy().filter_kind(Fox))
        ip_grasses = list(self.in_proximity_accuracy().filter_kind(Grass))

        self.sexing(ip_rabbits)
        self.aging(ip_rabbits)

        
        if len(ip_foxes) > 0:
            self.running_away(ip_foxes)
            self.dont_collide(ip_rabbits)
        else:
            self.hoppity(ip_grasses)
            self.eating(ip_grasses, ip_rabbits)

        
                
    

class Fox(Agent):
    agents = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age_count = 0
        self.gender = random.choice(["male", "female"]) # Choose random a gender
        if self.gender == "male":
            self.change_image(0)
        else:
            self.change_image(1)
        self.reproduction_timer = 0  # Initialize the timer
############### NEW FROM FOXKING #####################
        Fox.agents.append(self)
        self.energy_bar = 75
        self.hunt_cycle = 1
        self.died_time = 0

        

    def hunting_fox(self, in_proximity_rabbits, in_proximity_foxes):
        if self.died_time == 0:
            closest = 500
            for agent, dist in in_proximity_rabbits:
                if dist < closest:
                    self.move = (agent.pos - self.pos).normalize() * 1.258
                    closest = dist
                if agent.alive() and dist < 10: # and len(in_proximity_foxes) < 3:
                    self.energy_bar = 75 # no inheriting the rabbit energy
                    self.hunt_cycle = 0
                    agent.kill()
                    self.reproduce().move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()
                    self.move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1))).normalize()


    def dying_fox(self):
        if self.energy_bar < 0:
            self.move = Vector2((0,-1))
            self.change_image(2)
            self.died_time += 0.1
        if self.died_time > 0:
            self.died_time += 0.1
        if self.died_time % 2 > 1 and self.died_time != 0:
            self.change_image(3)
        else:
            if self.died_time != 0:
                self.change_image(2)
        if self.died_time > 14:
            self.kill()
#######################################################


    def update(self):
        # Save Fox data
        self.save_data('Agent Type', 'Fox')
        self.calculate_average()
############# FOXKING ##########################

        self.age_count += 1/60

        in_proximity_rabbits = list(self.in_proximity_accuracy().filter_kind(Rabbit))
        in_proximity_foxes = list(self.in_proximity_accuracy().filter_kind(Fox))
        
        #self.dont_collide(in_proximity_foxes)
        if self.hunt_cycle > 60: # the fox will not be hungry for 60 frames to avoid clumping
            self.hunting_fox(in_proximity_rabbits, in_proximity_foxes)
        self.hunt_cycle += 1
        
        self.energy_bar -= 0.01
        self.dying_fox()
###################################################

        # Random probability of fox death
        ### Play with param
        if random.random() < 0.0038569:
            self.energy_bar = 0

                ##### Sexual Reproduction #####
        self.reproduction_timer += 1  # Increment the timer on each frame
        if self.reproduction_timer > 240:  
            potential_mates = self.in_proximity_accuracy().filter_kind(Fox)
            for agent, _ in potential_mates:
                if agent.alive() and agent.gender != self.gender:
                    if random.random() < 0.02:  # Chance to reproduce when encountering an opposite gender fox
                        self.reproduce()  
                        self.reproduction_timer = 0  # Reset the timer after reproduction
        ###########################################################################

        

    average_ages = [0]

    def calculate_average(self):
        summa = 0
        alive = 0
        for agent in Fox.agents:
            if agent.alive():
                alive += 1
                summa += agent.age_count
        if alive > 0 and Fox.average_ages[-1] != summa / alive:
            Fox.average_ages.append(summa / alive)
            #self.save_data('Average Grass Age', summa / alive)
        else:
            pass
            #self.save_data('Average Grass Age', 0)

# Images for gender specific foxes and rabbits
male_rabbit_images = ['assi2/images/rabbit.png']
female_rabbit_images = ['assi2/images/female_rabbit.png']
male_fox_images = ['assi2/images/fox.png']
female_fox_images = ['assi2/images/female_fox.png']
                

df = (
    Simulation(Config(
        image_rotation = True,
        radius = 50, # Radius if which agents are in proximity
        duration = 300 * 60, # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second
        seed = 500,
    ))
    #.batch_spawn_agents(35, Rabbit, images=['assi2/images/rabbit.png'])
    #.batch_spawn_agents(25, Fox, images=['assi2/images/fox.png'])
    #.batch_spawn_agents(15, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png'])
    ### UNCOMMENT THE FOLLOWING TO IMPLEMENT GENDER SPECIFIC >>>>
    .batch_spawn_agents(40, Rabbit, images=['assi2/images/rabbit.png', 'assi2/images/female_rabbit.png'])
    .batch_spawn_agents(40, Fox, images=['assi2/images/fox.png', 'assi2/images/female_fox.png', 'assi2/images/dead_fox1.png', 'assi2/images/dead_fox2.png'])
    .batch_spawn_agents(40, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png', 'assi2/images/dead_grass.png'])
    .run()
    .snapshots.groupby(['frame','Agent Type']) # Initialize dataframe
    #.groupby(['frame','id', 'Agent Type'])
    #.groupby(['frame','Agent Type'])
    .agg(pl.count('id').alias('agent number'))
    #.agg(pl.count('Agent Type').alias('id'))
    .sort(['frame', 'Agent Type'])
)
#print(df) # Print dataframe
# Plot df
grass_ages = pd.DataFrame(Grass.average_ages)
rabbit_ages = pd.DataFrame(Rabbit.average_ages)
fox_ages = pd.DataFrame(Fox.average_ages)

#hi Younes and Mohammad


plot = sns.relplot(x=df['frame'], y=df['agent number'], hue=df['Agent Type'], kind='line')
plot.savefig('assi2/Graphs/Extra(1).png', dpi=600)

print(grass_ages)
print(rabbit_ages)
print(fox_ages)