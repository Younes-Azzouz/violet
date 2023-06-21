from vi import Agent, Simulation, Config

class Rabbit(Agent):
    pass

class Fox(Agent):
    def update(self):
        in_proximity = list(self.in_proximity_accuracy())
        for agent, _ in in_proximity:
            if agent.__class__ == Rabbit: # type: ignore
                print('test')

(
    Simulation(Config(
        image_rotation = True
    ))
    .batch_spawn_agents(100, Rabbit, images=['assi2/images/cockroach.png'])
    .batch_spawn_agents(100, Fox, images=['assi2/images/bird.png'])
    .run()
)