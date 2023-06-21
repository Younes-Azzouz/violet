from vi import Agent, Simulation, Config
import random

class Rabbit(Agent):
    def update(self):
        if random.random() < 0.003:
            self.reproduce()

        for agent, _ in self.in_proximity_accuracy():
            if isinstance(agent, Fox):
                self.kill()
                break
                

class Fox(Agent):
    def update(self):
        if random.random() < 0.002:
            self.kill()
            return

        for agent, _ in self.in_proximity_accuracy():
            if isinstance(agent, Rabbit):
                agent.kill()
                self.reproduce()
                break

(
    Simulation(Config(image_rotation=True))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/red.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/bird.png'])
    .run()
)
