from vi import Agent, Simulation, Config
import random


class Rabbit(Agent):
    def update(self):
        # Random probability of rabbit death
        ### Play with param
        if random.random() < 0.003:
            self.reproduce()


class Fox(Agent):
    # Init agent with Energybar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_bar = 60 

    def update(self):
        # Decrease energybar by a value every frame (Note that 60 frames per second), if decrease is 0.01 every frame -> 0.6 decrease every second 
        self.energy_bar -= .04
        # If energy is 0 or less kill the agent
        if self.energy_bar <= 0:
            self.kill()
            return

        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce
                self.energy_bar = 60 # Reset energy value to as initalized, because fox ate rabbit


        # This is commented for testing energy bar values atm, uncomment later
        # Random probability of fox death
        ### Play with param
        #if random.random() < 0.002:
        #    self.kill()
        
(
    Simulation(Config(
        image_rotation = True
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/red.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/bird.png'])
    .run()
)