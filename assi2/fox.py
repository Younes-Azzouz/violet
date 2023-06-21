from vi import Agent, Simulation

(
    Simulation()
    .batch_spawn_agents(100, Agent, images=['images/cockroach.png'])
    .run()
)