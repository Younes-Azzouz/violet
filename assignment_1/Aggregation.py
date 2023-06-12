from enum import Enum, auto
import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize
import random


@deserialize
@dataclass
class FlockingConfig(Config):
    # alignment_weight: float = 0.5
    cohesion_weight: float = 0
    separation_weight: float = 0

    delta_time: float = 2
    mass: int = 10

    def weights(self) -> tuple[float, float]:
        return (self.cohesion_weight, self.separation_weight)


class Cockroach(Agent):
    config: FlockingConfig
    
    
         


    def change_position(self):
        # remove  this and make it finite space
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        if next(self.in_proximity_accuracy().without_distance()) is not None:
             self.freeze_movement()
        
        cockroaches = list(self.in_proximity_accuracy()) # All cockroaches in de proximity
        
        
            

        # ----------------

        if len(cockroaches) > 0:
            # ### ALIGNMENT ### change to join
            # velocities = Vector2() 
            # for boid, _ in cockroaches: 
            #     velocities += boid.move 
            # Vn = velocities/len(cockroaches) 
            # alignment = Vn - self.move 
            # alignment = alignment.normalize()


            ### SEPERATION ### 
            positions = Vector2() 
            for boid, _ in cockroaches:
                positions += (self.pos - boid.pos)
            seperation = positions/len(cockroaches) 
            seperation = seperation.normalize()


            ### COHESION ###
            bird_positions = Vector2()
            for boid, _ in cockroaches:
                bird_positions += boid.pos
            average_positions = bird_positions/len(cockroaches) 
            cohesion = (average_positions - self.pos) - self.move
            cohesion = cohesion.normalize()

        else:
            # alignment = Vector2((0,0))
            seperation = Vector2((0,0))        
            cohesion = Vector2((0,0))   

        # Adding everything together
        c_weight, s_weight = self.config.weights()
        max_velocity = 5
        
        Ftotal = ((s_weight * seperation) + + (c_weight * cohesion)) / self.config.mass # epsilon is beetje random bewegen
        self.move += Ftotal

        if self.move.length() > max_velocity:
            self.move = self.move.normalize() * max_velocity

        self.pos += self.move * self.config.delta_time

        # #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            pass
            # self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

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

        c, s = self.config.weights()
        # print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")

        
(
    FlockingLive(       
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1, 
        )
    )
    .batch_spawn_agents(30, Cockroach, images=["assignment_0/images/bird.png"])
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