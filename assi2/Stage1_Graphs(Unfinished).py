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
        self.save_data('Agent Type', 0)
        # Random probability of rabbit death
        ### Play with param
        if random.random() < 0.003:
            self.reproduce()
    

class Fox(Agent):
    def update(self):
        # Save Fox agent data for plots
        self.save_data('Agent Type', 1)
        # Asexual reproduction, if Fox collide with rabbit -> Kill rabbit + extra fox
        in_proximity = self.in_proximity_accuracy().filter_kind(Rabbit)
        for agent, _ in in_proximity:
            if agent.alive():
                agent.kill()
                self.reproduce()

        # Random probability of fox death
        ### Play with param
        if random.random() < 0.002:
            self.kill()
        

                
print(
    Simulation(Config(
        image_rotation = True,
        radius = 20, # Radius if which agents are in proximity
        duration = 60 * 60 # Run simulation + present graphs over a 60 seconds time frame, 60 frames per second
    ))
    .batch_spawn_agents(10, Rabbit, images=['assi2/images/rabbit.png'])
    .batch_spawn_agents(10, Fox, images=['assi2/images/fox.png'])
    .run()
    .snapshots # Initialize dataframe
    .groupby(['frame','id', 'Agent Type'])
    #.groupby(['frame','Agent Type'])
    #.sort(['frame','Agent Type'])
)
#print(df) # Print dataframe
# Plot df
#plot = sns.relplot(x=df['frame'], y=df['Agent'], hue=df['Agent'])
#plot.savefig('assi2/Graphs/Stage1.png', dpi=600)
