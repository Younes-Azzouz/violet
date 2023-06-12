from enum import Enum, auto
import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class AggregationConfig(Config):
    proclivity_leave: float = 0.5
    proclivity_stay: float = 0.3

    delta_time: float = 5
    mass: int = 10

    def weights(self) -> tuple[float, float]:
        return (self.proclivity_leave, self.proclivity_stay)


class Cockroach(Agent):
    config: AggregationConfig

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight

    def update(self):
        self.bump_and_freeze()
        self.change_position()

    def change_position(self):
        self.bounce_back()
        self.pos += self.move * self.config.delta_time
        print(self.move)
        self.bump_and_freeze()
        
    def bump_and_freeze(self):
        for agent in self.in_proximity_accuracy().without_distance():
            if(agent.move == Vector2((0,0))):
                agent.move = Vector2((random.uniform(-1, 1),random.uniform(-1, 1)))
            else:
                agent.move = Vector2((0,0))
    def bounce_back(self):
        changed = False
        margin_x = 10
        margin_y = 10

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

    


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class AggregationLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: AggregationConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        haha = '''
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION
        '''

        leave, stay = self.config.weights()
        # print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

        
(
    AggregationLive(       
        AggregationConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1, 
        )
    )
    .batch_spawn_agents(50, Cockroach, images=["assignment_0/images/bird.png"])
    .spawn_obstacle(image_path="examples/images/site.png", x = 750 // 2 , y = 750 // 2)
    .run()
)


# (
#     # Step 1: Create a new simulation.
#     Simulation(Config(image_rotation=True))
#     # Step 2: Add 100 agents to the simulation.
#     .batch_spawn_agents(100, Agent, images=["images/bird.png"])
#     # Step 3: Profit! 🎉
#     .run()
# )