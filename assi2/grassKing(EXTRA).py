from vi import Agent, Simulation, Config
import random
import seaborn as sns
import polars as pl
from pygame.math import Vector2

class FoxRabbitConfig(Config):
    reproduce_threshold: int = 10

    def weights(self) -> tuple[float, float]:
        return (self.Pjoin, self.Pleave)

class Rabbit(Agent):
    agents = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Rabbit.agents.append(self)
        self.energy = 0

    def update(self):
        self.eating()
    def eating(self):
        grasses = self.in_proximity_accuracy().filter_kind(Grass)
        for agent, _ in grasses:
            if agent.alive():
                self.energy += agent.energy
                print("RABBIT ATE")
                agent.kill()
                self.reproduce()
                
                

class Fox(Agent):
    def update(self):
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()
                
class Grass(Agent):

    agents = []


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Grass.agents.append(self)
        self.energy = 0

    def update(self):
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

                
df = (
    Simulation(Config(
        image_rotation = True
    ))
    .batch_spawn_agents(1, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(1, Fox, images=['assi2/images/fox.png', 'assi2/images/dead_fox.png'])
    .batch_spawn_agents(10, Grass, images=['assi2/images/grass1.png', 'assi2/images/grass2.png', 'assi2/images/grass3.png'])
    .run()

    .snapshots # Init dataframe

    # Replay file? Uncomment >>>
    #.write_parquet("agents.parquet") 

    #.groupby(["frame","image_index"]) # Combine all agents into one row of that specific frame, image_index wether in prox or not
    #.agg(pl.count("id").alias("agents")) # Count total number of agents
    #.sort(["frame", "image_index"]) # Sort first by frame then by image_index
)

print(df)

plot = sns.relplot(x=df["frame"], y=df["agents"], hue=df["image_index"], kind="line")
plot.savefig("foxrabbit-fig.png", dpi=600)