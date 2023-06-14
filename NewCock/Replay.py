from vi import TimeMachine
import polars as pl

df = pl.read_parquet("agents.parquet")

TimeMachine(df,["images/cockroach.png", 
                "images/redroach.png"]).run()
