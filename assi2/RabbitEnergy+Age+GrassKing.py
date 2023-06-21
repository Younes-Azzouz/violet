from vi import Agent, Simulation, Config
import random
import datetime
import time
from pygame.math import Vector2


class Grass(Agent):
    agents = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.energy = 0
        
    def update(self):
        # Static grass
        self.freeze_movement()
        if self.energy < 50:
            self.energy += 0.1
        self.growing()
        self.move = Vector2((0,0))
        if random.uniform(0, len(Grass.agents)) >= len(Grass.agents) * 0.999:
            self.reproduce().pos = Vector2((random.randint(0, 750), random.randint(0, 750)))

    def growing(self):
        if self.energy > 10:
            self.change_image(1)
        if self.energy > 30:
            self.change_image(2)


    
class Rabbit(Agent):
    # Init agent with Energybar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_bar = 60  
        # Set birthtime to current time
        self.birth_time = time.time() 
        # Jerrys imp, unnecessary?
        self.energy = 0 


    def update(self):
        # Random probability of rabbit death,  commented for testing
        ### Play with param
        #if random.random() < 0.003:
        #    self.kill()

        # Random reproduction of rabbits, commented for testing
        #if random.random() < 0.003:
        #   self.reproduce()
            
            
        #age = time.time() - self.birth_time
        #death_probability = min(0.005 * age, 0.5) 
        #reproduction_probability = max(0.003 - 0.0001 * age, 0.001)
        

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
        #if random.random() < death_probability:
            #self.kill()
            #return
        # Random chance of reproduction as age increases
        #if random.random() < reproduction_probability:
            #self.reproduce()
                
    

class Fox(Agent):
    def update(self):
        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()

        # Random probability of fox death
        ### Play with param
        if random.random() < 0.002:
            self.kill()

                
(
    Simulation(Config(
        image_rotation = True,
        radius = 15,
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(7, Fox, images=['assi2/images/fox.png'])
    .batch_spawn_agents(15, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png'])
    .run()
)



