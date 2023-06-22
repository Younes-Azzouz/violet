from vi import Agent, Simulation, Config, HeadlessSimulation
import random
import polars as pl
import seaborn as sns


class Rabbit(Agent):
    def update(self):
        # Save rabbit data
        self.save_data('Agent Type', 'Rabbit')
        # Random probability of rabbit death
        ### Play with param
        if random.random() < 0.00262:
            self.reproduce()


class Fox(Agent):
    # Init agent with Energybar
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_bar = 60 

    def update(self):
        # Save Fox agent data for plots
        self.save_data('Agent Type', 'Fox')
        # Decrease energybar by a value every frame (Note that 60 frames per second), if decrease is 0.01 every frame -> 0.6 decrease every second 
        self.energy_bar -= .08 # Changed from 0.08
        # If energy is 0 or less kill the agent
        if self.energy_bar <= 0:
            self.kill()
            return

        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()
                self.energy_bar += 35
                if self.energy_bar >= 60:
                    self.energy_bar = 60 # Reset energy value to as initalized, because fox ate rabbit


        # This is commented for testing energy bar values atm, uncomment later
        # Random probability of fox death
        ### Play with param
        if random.random() < 0.0038569:
            self.kill()


        
df = (
    Simulation(Config(
        image_rotation = True,
        radius = 30, # Radius if which agents are in proximity
        #duration = 240 * 60, # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second
        seed = 1,
    ))
    .batch_spawn_agents(35, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(25, Fox, images=['assi2/images/fox.png'])
    .run()
    .snapshots.groupby(['frame','Agent Type']) # Initialize dataframe
    #.groupby(['frame','id', 'Agent Type'])
    #.groupby(['frame','Agent Type'])
    .agg(pl.count('id').alias('agent number'))
    #.agg(pl.count('Agent Type').alias('id'))
    .sort(['frame', 'Agent Type'])
)
#print(df) # Print dataframe
# Plot df
plot = sns.relplot(x=df['frame'], y=df['agent number'], hue=df['Agent Type'], kind='line')
plot.savefig('assi2/Graphs/Stage3(2).png', dpi=600)