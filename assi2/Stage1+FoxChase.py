from vi import Agent, Simulation, Config
import random
import polars as pl
import seaborn as sns

#######
# We need to play around with the paramets of random death for rabbits and foxes, so that in the long run they average out
#######
class Rabbit(Agent):
    def update(self): 
        # Save rabbit agent data for plots      
        self.save_data('Agent Type', 'Rabbit')
        # Random probability of Rabbit spawning
        if random.random() < 0.00262:
            self.reproduce()
    

class Fox(Agent):
    def update(self):
        # Save Fox agent data for plots
        self.save_data('Agent Type', 'Fox')
        # Init chasing fox
        self.hunting_fox()
        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()

        # Random probability of fox death
        ### Play with param
        if random.random() < 0.0038569:
            self.kill()

    def hunting_fox(self):
        #if self.died_time == 0:
            in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
            closest = 500
            for agent, dist in in_proximity:
                if dist < closest:
                    self.move = (agent.pos - self.pos).normalize() * 1.05
                    closest = dist
                if agent.alive() and dist < 10:
                    #self.energy_bar = 50 # no inheriting the rabbit energy
                    agent.kill()
                    self.reproduce()
        

                
df = (
    Simulation(Config(
        image_rotation = True,
        radius = 30, # Radius if which agents are in proximity
        #duration = 60 * 60, # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second
        seed = 3,
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
plot.savefig('assi2/Graphs/Stage1+FoxChase-Seed3.png', dpi=600)
