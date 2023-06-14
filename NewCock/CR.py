from vi import Agent, Simulation, HeadlessSimulation, Config, dataclass, deserialize
from pygame.math import Vector2
from enum import Enum, auto
import polars as pl
import seaborn as sns
import pygame as pg
import random
import numpy as np

class State(Enum):
    WANDERING = auto()
    JOINING = auto()
    STILL = auto()
    LEAVING = auto()

@deserialize
@dataclass
class AggregationConfig(Config):
    Pjoin: float = 0.8
    Pleave: float = 0.5
    Tjoin: int = 10
    Tleave: int = 5
    D: int = 20
    delta_time: float = 1
    range_of_sight: int = 20
    n: int = 2
    def __init__(self, config: AggregationConfig):
        super().__init__(config)
        self.sites = [
            self.spawn_site(image_path=self.site_image_path, x=130, y=375, radius=75),
            self.spawn_site(image_path=self.site_image_path, x=500, y=375, radius=125)
        ]
    def weights(self) -> tuple[float, float]:
        return (self.Pjoin, self.Pleave)
    
    def spawn_site(self, image_path, x, y, radius=100):
        new_site = Site(image_path, x, y, radius)
        return new_site
    
    def before_update(self):
        super().before_update()

        leave, join = self.config.weights()

        for site in self.sites:
            site.draw(self._screen)
        
        for agent in CockRoach.agents:
            for site in self.sites:
                if site.contains(agent.pos):
                    if agent.state == State.WANDERING:
                        if random.random() < self.config.Pjoin:
                            agent.state = State.JOINING
                            agent.timer = self.config.Tjoin + np.random.normal(0, 1)
                    elif agent.state == State.STILL:
                        neighbors_in_sight = agent.get_neighbors_in_sight()
                        
                        # if len(neighbors_in_sight) < self.config.n:
                        if random.random() < self.config.Pleave:
                            agent.state = State.LEAVING
                            for agent in neighbors_in_sight:
                                self.config.Pleave = self.config.Pleave - 1 / len(neighbors_in_sight * 50)
                            agent.timer = self.config.Tleave + np.random.normal(0, 1)
                    elif agent.state == State.JOINING:
                        direction_to_site = (site.pos - agent.pos).normalize()
                        agent.move = direction_to_site
                        
                        
                    elif agent.state == State.LEAVING:
                        direction_to_site = (site.pos - agent.pos).normalize()
                        agent.move = -direction_to_site

class Site:
    def __init__(self, image_path, x, y, radius):
        self.image_path = image_path
        self.pos = Vector2(x, y)
        self.radius = radius
        self.image = pg.image.load(image_path)  

    def contains(self, pos: Vector2) -> bool:
        return (pos - self.pos).length() <= self.radius

    def draw(self, surface):
        surface.blit(self.image, (self.pos.x - self.radius, self.pos.y - self.radius))

class CockRoach(Agent):
    config: AggregationConfig
    state: State = State.WANDERING
    radius: float = 10
    timer: int = 0

    agents = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CockRoach.agents.append(self)

    def check_for_overlap(self):
        for other_agent in CockRoach.agents:
            if other_agent != self:
                distance_between_agents = self.pos.distance_to(other_agent.pos)
                if distance_between_agents < (self.radius + other_agent.radius):
                    if distance_between_agents == 0:  
                        direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) 
                    else:
                        direction = (self.pos - other_agent.pos).normalize()
                    overlap = self.radius + other_agent.radius - distance_between_agents
                    self.pos += overlap / 2 * direction  
                    other_agent.pos -= overlap / 2 * direction

    def update(self):
        self.check_for_overlap() # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # START
        # If agent in proximity of other agent, change color
        if self.in_proximity_accuracy().count() > 0:
            self.change_image(1)
        else:
            self.change_image(0)
        # END

        if self.state == State.WANDERING:
            self.wandering()
        elif self.state == State.JOINING:
            self.joining()
            self.timer -= self.config.delta_time
            if self.timer <= 0:
                self.state = State.STILL
                self.timer = self.config.D
        elif self.state == State.STILL:
            self.still()
            self.timer -= self.config.delta_time
            if self.timer <= 0:
                self.state = State.LEAVING
                self.timer = self.config.Tleave + np.random.normal(0, 1)
        elif self.state == State.LEAVING:
            self.leaving()
            self.timer -= self.config.delta_time
            if self.timer <= 0:
                self.state = State.WANDERING

        self.change_position()

    def wandering(self):
        self.move += Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.move = self.move.normalize()

        neighbors = self.get_neighbors_in_sight()
        
        if len(neighbors) == 0:
            return

        for neighbor in neighbors:
            diff = self.pos - neighbor.pos
            if diff.length_squared() > 0:
                diff.normalize_ip()
                diff /= diff.length()
            self.move += diff
        
        average_heading = sum((neighbor.move for neighbor in neighbors), Vector2())
        average_heading /= len(neighbors)
        self.move += average_heading
        
        average_position = sum((neighbor.pos for neighbor in neighbors), Vector2())
        average_position /= len(neighbors)
        direction_to_average_position = average_position - self.pos

        if direction_to_average_position.length() > 0: 
            direction_to_average_position.normalize_ip()

        self.move += direction_to_average_position

        self.move.normalize_ip()


    def get_neighbors_in_sight(self):
        neighbors = []
        for other_agent in CockRoach.agents:
            if other_agent != self and self.pos.distance_to(other_agent.pos) <= self.config.range_of_sight:
                neighbors.append(other_agent)
        return neighbors
    
    def leaving(self):
        self.move = Vector2((random.uniform(-1, 1), random.uniform(-1, 1)))

    def bounce_back(self):
        changed = False
        margin_x = 5
        margin_y = 5

        if self.pos.x < self._area.left + margin_x:
            changed = True
            self.move.x *= -1

        if self.pos.x > self._area.right - margin_x:
            changed = True
            self.move.x *= -1

        if self.pos.y < self._area.top + margin_y:
            changed = True
            self.move.y *= -1

        if self.pos.y > self._area.bottom - margin_y:
            changed = True
            self.move.y *= -1

        return changed


df = (
    #HeadlessSimulation
    Simulation(AggregationConfig(
        #radius = 20, # Range of Cockroach sight
        duration = 5*60, # Duration of Sim, Seconds * FPS
        seed = 1
    ))
    # Spawn agents
    .batch_spawn_agents(100, CockRoach, images=["images/cockroach.png", 
                                                "images/redroach.png"])
    .run()
    .snapshots # Init dataframe

    # Replay file? Uncomment >>>
    #.write_parquet("agents.parquet") 

    .groupby(["frame","image_index"]) # Combine all agents into one row of that specific frame, image_index wether in prox or not
    .agg(pl.count("id").alias("agents")) # Count total number of agents
    .sort(["frame", "image_index"]) # Sort first by frame then by image_index
)



print(df)

plot = sns.relplot(x=df["frame"], y=df["agents"], hue=df["image_index"], kind="line")
plot.savefig("agents.png", dpi=600)