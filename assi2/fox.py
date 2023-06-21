from vi import Agent, Simulation, Config
import random

class Rabbit(Agent):
    def update(self):
        if random.random() < 0.003:
            self.reproduce()
    

class Fox(Agent):
    def update(self):
        in_proximity = list(self.in_proximity_accuracy())
        for agent, _ in in_proximity:
            if agent.__class__ == Rabbit: # type: ignore
                agent.kill()
                self.reproduce()
(
    Simulation(Config(
        image_rotation = True
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/red.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/bird.png'])
    .run()
)