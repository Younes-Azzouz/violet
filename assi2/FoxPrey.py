from vi import Agent, Simulation, Config
import random
import polars as pl
import seaborn as sns

class Rabbit(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population = 0
    
    def update(self):
        # Save rabbit agent data for plots
        self.save_data('Agent Type', 'Rabbit')
        self.save_data('Population', self.population)
        
        # Update rabbit population based on Lotka-Volterra dynamics
        rabbit_growth_rate = 0.02
        rabbit_death_rate = 0.005
        self.population += self.population * (rabbit_growth_rate - rabbit_death_rate * self.population)
        
        # Random probability of rabbit death
        if random.random() < 0.00262:
            self.population -= 1
            self.reproduce()

class Fox(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population = 0
    
    def update(self):
        # Save Fox agent data for plots
        self.save_data('Agent Type', 'Fox')
        self.save_data('Population', self.population)
        
        # Update fox population based on Lotka-Volterra dynamics
        fox_growth_rate = 0.01
        fox_death_rate = 0.01
        self.population += self.population * (fox_growth_rate * self.population - fox_death_rate)
        
        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()
        
        # Random probability of fox death
        if random.random() < 0.0038569:
            self.population -= 1
            self.kill()
                

df = (
    Simulation(Config(
        image_rotation=True,
        radius=30,  # Radius at which agents are in proximity
        seed=1,
    ))
    .batch_spawn_agents(35, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(25, Fox, images=['assi2/images/fox.png'])
    .run()
    .snapshots.groupby(['frame', 'Agent Type'])
    .agg(pl.sum('Population').alias('agent number'))
    .sort(['frame', 'Agent Type'])
)

# Plot df
plot = sns.relplot(x=df['frame'], y=df['agent number'], hue=df['Agent Type'], kind='line')
plot.savefig('assi2/Graphs/Stage1(6).png', dpi=600)
