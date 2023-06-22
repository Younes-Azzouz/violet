from vi import Agent, Simulation, Config
import random
import datetime
import time
import polars as pl
import seaborn as sns
from pygame.math import Vector2


class Grass(Agent):
    agents = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.energy = 0
        
    def update(self):
        # Save grass data
        self.save_data('Agent Type', 'Grass')
        # Static grass
        self.freeze_movement()

        # Grass growing
        if self.energy < 50:
            self.energy += 0.1
        self.growing()
        self.move = Vector2((0,0))
        if random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.999:
            self.reproduce().pos = Vector2((random.randint(0, 750), random.randint(0, 750)))

    def growing(self):
        # Change image of grass at certain energy levels of grass
        if self.energy > 10:
            self.change_image(1)
        if self.energy > 30:
            self.change_image(2)


    
class Rabbit(Agent):
    # Init agent with Energybar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer
        self.energy_bar = 60 # Initialize energy bar
        # Set birthtime to current time
        self.birth_time = time.time() 
        # Jerrys imp, unnecessary?
        self.energy = 0 


    def update(self):
        # Save Rabbit data
        self.save_data('Agent Type', 'Rabbit')

        # Unecessary >>>
        #if random.random() < 0.003:
        #   self.kill()
        # NOT REQUIRED ^^^^^^^^^^^^^^^^^^

        # Random reproduction of rabbits
        if random.random() < 0.00262:
          self.reproduce()
            
        # Age implementation
        age = time.time() - self.birth_time
        death_probability = min(0.005 * age, 0.5) 
        reproduction_probability = max(0.003 - 0.0001 * age, 0.001)
        

        # Rabbit eating grass -> replenish energy
        self.energy_bar -= 0.1
        if self.energy_bar <= 0:
            self.kill()
        in_proximity = self.in_proximity_accuracy().filter_kind(Grass)
        for agent, _ in in_proximity:
            if agent.alive():
                self.reproduce()
                agent.kill()
                agent.change_image(1)
                self.energy_bar += 10
                if self.energy_bar >= 60:
                    self.energy_bar = 60
                
        # Random chance of death as age increases      
        if random.random() < death_probability:
            self.kill()
            return
        # Random chance of reproduction as age increases
        if random.random() < reproduction_probability:
            self.reproduce()

                ##### Sexual Reproduction #####
        if self.reproduction_timer > 240:  # Check the timer
            potential_mates = self.in_proximity_accuracy().filter_kind(Rabbit)
            for agent, _ in potential_mates:
                if agent.alive() and agent.gender != self.gender:
                    if random.random() < 0.02:  # Chance to reproduce when encountering an opposite gender rabbit
                        self.reproduce() 
                        self.reproduction_timer = 0  # Reset the timer after reproduction
        self.reproduction_timer += 1  # Increment the timer on each frame
        ###########################################################################
                
    

class Fox(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer

    def update(self):
        # Save Fox data
        self.save_data('Agent Type', 'Fox')
        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()

        # Random probability of fox death
        ### Play with param
        if random.random() < 0.0038569:
            self.kill()

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

# Images for gender specific foxes and rabbits
male_rabbit_images = ['assi2/images/rabbit.png']
female_rabbit_images = ['assi2/images/female_rabbit.png']
male_fox_images = ['assi2/images/fox.png']
female_fox_images = ['assi2/images/female_fox.png']
                

df = (
    Simulation(Config(
        image_rotation = True,
        radius = 30, # Radius if which agents are in proximity
        #duration = 60 * 60, # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second
        seed = 1,
    ))
    #.batch_spawn_agents(35, Rabbit, images=['assi2/images/rabbit.png'])
    #.batch_spawn_agents(25, Fox, images=['assi2/images/fox.png'])
    #.batch_spawn_agents(15, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png'])
    ### UNCOMMENT THE FOLLOWING TO IMPLEMENT GENDER SPECIFIC >>>>
    .batch_spawn_agents(30, Rabbit, images=male_rabbit_images)
    .batch_spawn_agents(30, Rabbit, images=female_rabbit_images)
    .batch_spawn_agents(20, Fox, images=male_fox_images)
    .batch_spawn_agents(20, Fox, images=female_fox_images)
    .batch_spawn_agents(15, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png'])
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
plot = sns.relplot(x=df['frame'], y=df['agent number'], hue=df['Agent Type'], kind='line')
plot.savefig('assi2/Graphs/Extra(1).png', dpi=600)
