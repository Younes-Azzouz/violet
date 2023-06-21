from vi import Agent, Simulation, Config
import random
import datetime
import time


class Grass(Agent):
    def update(self):
        # Static grass
        self.freeze_movement()

class Grass2(Grass):
    pass

class Grass3(Grass):
    pass

        
    
class Rabbit(Agent):
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_bar = 60  
        self.birth_time = time.time()  


    def update(self):
        # Random reproduction of rabbits
        
        if random.random() < 0.003:
            self.reproduce()
            
            
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
                agent.kill()
                agent.change_image(1)
                self.energy_bar += 10
                if self.energy_bar >= 60:
                    self.energy_bar = 60
                print(self.energy_bar)

        in_proximity = self.in_proximity_accuracy().filter_kind(Grass2)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                agent.change_image(1)
                self.energy_bar += 30 
                if self.energy_bar >= 60:
                    self.energy_bar = 60
                print(self.energy_bar)

        in_proximity = self.in_proximity_accuracy().filter_kind(Grass3)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                agent.change_image(1)
                self.energy_bar = 60
                print(self.energy_bar)
                
                
        if random.random() < death_probability:
            self.kill()
            return
        
        if random.random() < reproduction_probability:
            self.reproduce()
                
    

class Fox(Agent):
    def update(self):
        # Fox eating rabbit
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()
        # Random death of fox
        if random.random() < 0.002:
            self.kill()
        

                
(
    Simulation(Config(
        image_rotation = True,
        radius = 15
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/red.png'])
    .batch_spawn_agents(7, Fox, images=['assi2/images/bird.png'])
    .batch_spawn_agents(5, Grass, images=['assi2/images/grass1.png'
                                          ,'assi2/images/white.png'])
    .batch_spawn_agents(5, Grass2, images=['assi2/images/grass2.png'
                                          ,'assi2/images/white.png'])
    .batch_spawn_agents(5, Grass3, images=['assi2/images/grass3.png'
                                          ,'assi2/images/white.png'])
    .run()
)



