from vi import Agent, Simulation, Config
import random


class Grass(Agent):
    def update(self):
        # Static grass
        self.freeze_movement()
        

class Rabbit(Agent):
    def update(self):
        # Random reproduction of rabbits
        if random.random() < 0.003:
            self.reproduce()

        # Rabbit eating grass -> replenish energy
        in_proximity = self.in_proximity_accuracy().filter_kind(Grass)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
            # Add here the energy function from fox
    

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
        image_rotation = True
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/red.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/bird.png'])
    .batch_spawn_agents(5, Grass, images=['assi2/images/green.png'])
    .run()
)