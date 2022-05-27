import polars as pl

from vi import Agent, BaseConfig, Simulation


class MyAgent(Agent):
    def every_frame(self):
        # As radius calculation is quite performance heavy,
        # we only calculate it once per frame.
        in_radius = len(self.in_radius())

        # We want to keep track of how many other agents were in our agent's radius,
        # so we add data to the `in_radius` column of our dataframe!
        self.save_data("in_radius", in_radius)

        # If at least one agent is within our agent's radius, then we turn red!
        if in_radius > 0:
            self.change_image(index=1)
        else:
            # Otherwise we turn white.
            self.change_image(index=0)


print(
    # We're using a seed to collect the same data every time.
    Simulation(BaseConfig(chunk_size=25, duration=300, seed=1))
    .batch_spawn_agents(
        MyAgent,  # 👈 use our own MyAgent class.
        image_paths=[
            "examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
    .snapshots.groupby("frame")
    # Count the number of agents (per frame) that see at least one other agent (making them red)
    .agg((pl.col("in_radius") > 0).sum().alias("# red agents"))
    .select("# red agents")
    # Create a statistical summary including the min, mean and max number of red agents.
    .describe()
)