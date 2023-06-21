from vi import Agent, Simulation, Config

class Rabbit(Agent):
    pass

class Fox(Agent):
    pass

(
    Simulation(Config(
        image_rotation = True
    ))
    .batch_spawn_agents(100, Rabbit, images=['images/cockroach.png'])
    .batch_spawn_agents(100, Fox, images=['images/bird.png'])
    .run()
)