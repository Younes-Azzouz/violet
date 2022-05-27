from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeVar

import pygame as pg
from pygame.mask import Mask
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface

from .config import BaseConfig
from .metrics import Metrics
from .util import random_angle, random_pos, round_pos

if TYPE_CHECKING:
    from .proximity import ProximityEngine
    from .simulation import Shared


T = TypeVar("T", bound="Agent")


class Agent(Sprite):
    id: int
    """The unique identifier of the agent."""

    _images: list[Surface]
    """A list of images which you can use to change the current image of the agent."""

    _image_index: int
    """The currently selected image."""

    _image_cache: Optional[tuple[int, Surface]] = None

    area: Rect
    """The area in which the agent is free to move."""

    move: Vector2
    """The current angle and speed used for the agent's movement."""

    pos: Vector2
    """The current (centre) position of the agent."""

    __previous_move: Optional[Vector2] = None
    """The value of the `move` vector before the agent was frozen."""

    obstacles: Group
    """The group of obstacles the agent can collide with."""

    sites: Group
    """The group of sites on which the agent can appear."""

    __proximity: ProximityEngine
    """The Proximity Engine used for all proximity-related methods.
    
    The proximity engine is private (double underscore prefix) as one could retrieve all agents with it.
    Therefore, the Agent class provides the (public) `in_proximity`, `in_close_proximity` and `in_radius` wrapper methods instead.
    """

    config: BaseConfig
    """The config of the simulation that's shared with all agents.
    
    The config can be overriden when inheriting the Agent class.
    However, the config must always:

    1. Inherit `BaseConfig`
    2. Be decorated by `@serde`
    """

    shared: Shared
    """Attributes that are shared between the simulation and all agents."""

    __metrics: Metrics
    """Data collection of the snapshots."""

    def __init__(
        self,
        id: int,  # unique identifier used in e.g. proximity calculation and stats engine
        containers: list[Group],  # sprite groups for rendering
        movement_speed: float,
        images: list[Surface],
        area: Rect,
        obstacles: Group,
        sites: Group,
        proximity: ProximityEngine,
        config: BaseConfig,
        shared: Shared,
        metrics: Metrics,
    ):
        Sprite.__init__(self, *containers)

        self.id = id
        self.config = config
        self.shared = shared
        self.__metrics = metrics

        self.__proximity = proximity

        # Default to first image in case no image is given
        self._image_index = 0
        self._images = images

        self.obstacles = obstacles
        self.sites = sites

        self.area = area
        self.move = random_angle(movement_speed, prng=shared.prng_move)

        # On spawn acts like the __init__ for non-pygame facing state.
        # It could be used to override the initial image if necessary.
        self.on_spawn()

        # Keep changing the position until the position no longer collides with any obstacle.
        while True:
            self.pos = random_pos(self.area, prng=shared.prng_move)
            self.rect.center = round_pos(self.pos)

            obstacle_hit = pg.sprite.spritecollideany(self, self.obstacles, pg.sprite.collide_mask)  # type: ignore
            if not bool(obstacle_hit) and self.area.contains(self.rect):
                break

    def _get_image(self) -> Surface:
        image = self._images[self._image_index]

        if self.config.image_rotation:
            angle = self.move.angle_to(Vector2((0, -1)))

            return pg.transform.rotate(image, angle)
        else:
            return image

    @property
    def image(self) -> Surface:
        """The image that's used for PyGame's rendering."""

        if self._image_cache is not None:
            frame, image = self._image_cache
            if frame == self.shared.counter:
                return image

        new_image = self._get_image()
        self._image_cache = (self.shared.counter, new_image)

        return new_image

    @property
    def rect(self) -> Rect:
        """The bounding-box that's used for PyGame's rendering."""

        rect = self.image.get_rect()
        rect.center = round_pos(self.pos)
        return rect

    @property
    def mask(self) -> Mask:
        """A bit-mask of the image used for collision detection with obstacles and sites."""

        return pg.mask.from_surface(self.image)

    def every_frame(self):
        """Run your own agent logic at every tick of the simulation.
        Every frame of the simulation, this method is called automatically for every agent of the simulation.

        To add your own logic, inherit the `Agent` class and override this method with your own.
        """

        ...

    def update(self):
        self._collect_replay_data()
        self.every_frame()

    def on_spawn(self):
        """Run any code when the agent is spawned into the simulation.

        This method is a replacement for `__init__`, which you should not overwrite directly.
        Instead, you can make alterations to your Agent within this function instead.

        You should override this method when inheriting Agent to add your own logic.

        Some examples include:
        - Changing the image or state of your Agent depending on its assigned identifier.
        """

        ...

    def there_is_no_escape(self) -> bool:
        """Pac-Man-style teleport the agent to the other side of the screen when it is outside of the playable area."""

        changed = False

        if self.pos.x < self.area.left:
            changed = True
            self.pos.x = self.area.right

        if self.pos.x > self.area.right:
            changed = True
            self.pos.x = self.area.left

        if self.pos.y < self.area.top:
            changed = True
            self.pos.y = self.area.bottom

        if self.pos.y > self.area.bottom:
            changed = True
            self.pos.y = self.area.top

        return changed

    def change_position(self):
        """Change the position of the agent.

        The agent's new position is calculated as follows:
        1. The agent checks whether it's outside of the visible screen area.
        If this is the case, then the agent will be teleported to the other edge of the screen.
        2. If the agent collides with any obstacles, then the agent will turn around 180 degrees.
        3. If the agent has not collided with any obstacles, it will have the opportunity to slightly change its angle.
        """
        changed = self.there_is_no_escape()

        prng = self.shared.prng_move

        # Always calculate the random angle so a seed could be used.
        deg = prng.uniform(-30, 30)

        # Only update angle if the agent was teleported to a different area of the simulation.
        if changed:
            self.move.rotate_ip(deg)

        # Obstacle Avoidance
        obstacle_hit = pg.sprite.spritecollideany(self, self.obstacles, pg.sprite.collide_mask)  # type: ignore
        collision = bool(obstacle_hit)

        # Reverse direction when colliding with an obstacle.
        if collision:
            self.move.rotate_ip(180)

        # Random opportunity to slightly change angle.
        # Probabilities are pre-computed so a seed could be used.
        should_change_angle = prng.random()
        deg = prng.uniform(-10, 10)

        # Only allow the angle opportunity to take place when no collisions have occured.
        # This is done so an agent always turns 180 degrees. Any small change in the number of degrees
        # allows the agent to possibly escape the obstacle.
        if not collision and 0.25 > should_change_angle:
            self.move.rotate_ip(deg)

        # Actually update the position at last.
        self.pos += self.move

    # TODO: rename method to better convey that only agents in the same chunk are returned.
    def in_proximity(self: T) -> set[T]:
        """Retrieve other agents that are in the same chunk as the current agent.

        Tweaking the effective proximity radius can be done by modifying the `chunk-size` option in the config.

        This proximity method is quite inaccurate and should not be used.
        Instead, the use of `in_close_proximity` is strongly preferred as it has the same performance characteristics,
        but significantly improves the accuracy.

        `in_proximity` is one of three methods to retrieve neighbouring agents:

        1. `in_proximity`: agents in the same chunk are returned.
        2. `in_close_proximity`: agents in the same chunk, as well as neighbouring chunks, are returned.
        3. `in_radius`: agents within a radius are returned (most accurate but also very slow).
        """
        return self.__proximity.in_same_chunk(self)

    def in_close_proximity(self: T) -> set[T]:
        """Retrieve other agents that are in proximity of the current agent.

        Agent proximity is determined by retrieving the chunk the agent is currently in,
        as well as 8 neighbouring chunks, to retrieve a total of 9 chunks.
        All agents, other than the current agent, that appear in these chunks are considered to be in proximity.

        This proximity method is strongly preferred over `in_proximity` as it better accounts for cases where two agents
        are perhaps one pixel apart, but both are in a different chunk.
        By also retrieving the neighbouring pixels, the accuracy is improved considerably.

        Tweaking the effective proximity radius can be done by modifying the `chunk-size` option in the config.
        Note that this proximity method retrieves 3x the chunk-size, so adjust the chunk size accordingly.

        `in_close_proximity` is one of three methods to retrieve neighbouring agents:

        1. `in_proximity`: agents in the same chunk are returned.
        2. `in_close_proximity`: agents in the same chunk, as well as neighbouring chunks, are returned.
        3. `in_radius`: agents within a radius are returned (most accurate but also very slow).
        """
        return self.__proximity.in_surrounding_chunks(self)

    def in_radius(self: T) -> set[T]:
        """Retrieve other agents that are in a radius of the current agent.

        The exact radius can be configured by adjusting the `chunk-size` option in the config.

        This proximity method is 100% accurate as it calculates the exact distance between
        the current agent and other agents that are in close proximity.
        However, this distance calculation comes with quite the performance cost.
        So if you do not need an exact radius, strongly consider using `in_close_proximity` instead.

        `in_radius` is one of three methods to retrieve neighbouring agents:

        1. `in_proximity`: agents in the same chunk are returned.
        2. `in_close_proximity`: agents in the same chunk, as well as neighbouring chunks, are returned.
        3. `in_radius`: agents within a radius are returned (most accurate but also very slow).
        """
        return set(
            agent
            for agent in self.in_close_proximity()
            if agent.pos.distance_to(self.pos) <= self.__proximity.chunk_size
        )

    def on_site(self) -> bool:
        """Check whether the agent is currently on a site."""

        return bool(
            pg.sprite.spritecollideany(self, self.sites, pg.sprite.collide_mask)  # type: ignore
        )

    def freeze_movement(self):
        """Freeze the movement of the agent. The movement can be continued by calling `continue_movement`."""

        self.__previous_move = self.move
        self.move = Vector2(0, 0)

    def continue_movement(self):
        """Continue the movement of the agent by using the angle and speed of the agent before its movement was frozen."""

        if self.__previous_move is not None:
            self.move = self.__previous_move
            self.__previous_move = None

    def change_image(self, index: int):
        """Change the image of the agent."""

        self._image_index = index

    def save_data(self, column: str, value: Any):
        """Add extra data to the simulation's metrics.

        The following data is collected automatically:
        - agent identifier
        - current frame
        - x and y coordinates

        Examples
        --------

        Saving the number of agents in radius:

        >>> from vi import Agent
        >>> class MyAgent(Agent):
        ...     def every_frame(self):
        ...         in_radius = len(self.in_radius())
        ...         self.save_data("in_radius", in_radius)
        """

        self.__metrics._temporary_snapshots[column].append(value)

    def _collect_replay_data(self):
        """Add the minimum data needed for the replay simulation to the dataframe."""

        x, y = round_pos(self.pos)
        snapshots = self.__metrics._temporary_snapshots

        snapshots["frame"].append(self.shared.counter)
        snapshots["id"].append(self.id)

        snapshots["x"].append(x)
        snapshots["y"].append(y)

        snapshots["image_index"].append(self._image_index)

        if self.config.image_rotation:
            angle = self.move.angle_to(Vector2((0, -1)))
            snapshots["angle"].append(round(angle))
