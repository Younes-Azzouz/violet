from vi import Agent, Simulation, Config
import random
import time


class Rabbit(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer

    def update(self):
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



        if random.random() < 0.0003:
            self.kill()

class Fox(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gender = random.choice(["male", "female"]) # Choose random a gender
        self.reproduction_timer = 0  # Initialize the timer
    def update(self):
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

        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()

        if random.random() < 0.0002:
            self.kill()

# Defining the images for each gender of each species
male_rabbit_images = ['assi2/images/rabbit.png']
female_rabbit_images = ['assi2/images/female_rabbit.png']
male_fox_images = ['assi2/images/fox.png']
female_fox_images = ['assi2/images/female_fox.png']

simulation = Simulation(Config(image_rotation=True, radius=20, duration=60*60))

# Spawning the agents with their respective images
simulation.batch_spawn_agents(5, Rabbit, images=male_rabbit_images)
simulation.batch_spawn_agents(5, Rabbit, images=female_rabbit_images)
simulation.batch_spawn_agents(5, Fox, images=male_fox_images)
simulation.batch_spawn_agents(5, Fox, images=female_fox_images)

results = simulation.run()
# print(results.snapshots.groupby(['frame','id', 'Agent Type']))
