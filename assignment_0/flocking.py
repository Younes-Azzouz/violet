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
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.30
    separation_weight: float = 0.5

    delta_time: float = 4
    mass: int = 10

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig


    # super.mass = random.randint(1, FlockingConfig().mass)

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight


    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        
        birds = list(self.in_proximity_accuracy()) # All birds in de proximity


        
        if len(birds) > 0:
            ### ALIGNMENT ###
            velocities = Vector2() 
            for boid, _ in birds: 
                velocities += boid.move 
            Vn = velocities/len(birds) 
            alignment = Vn - self.move 
            alignment = alignment.normalize()


            ### SEPERATION ###
            positions = Vector2() 
            for boid, _ in birds:
                positions += (self.pos - boid.pos)
            seperation = positions/len(birds) 
            seperation = seperation.normalize()


            ### COHESION ###
            bird_positions = Vector2()
            for boid, _ in birds:
                bird_positions += boid.pos
            average_positions = bird_positions/len(birds) 
            cohesion = (average_positions - self.pos) - self.move
            cohesion = cohesion.normalize()

        else:
            alignment = Vector2((0,0))
            seperation = Vector2((0,0))        
            cohesion = Vector2((0,0))   

        # Adding everything together
        a_weight, c_weight, s_weight = self.config.weights()
        max_velocity = 5
        
        Ftotal = ((s_weight * seperation) + (a_weight * alignment) + (c_weight * cohesion)) / self.config.mass # epsilon is beetje random bewegen
        self.move += Ftotal

        if self.move.length() > max_velocity:
            self.move = self.move.normalize() * max_velocity

        self.pos += self.move * self.config.delta_time

        #TEST

        #END CODE -----------------


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
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

        a, c, s = self.config.weights()
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
    .batch_spawn_agents(30, Bird, images=["violet/assignment_0/images/bird.png"])
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