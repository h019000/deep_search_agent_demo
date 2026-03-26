import os
from hello_agents import HelloAgentsLLM
from config import Configuration
from agent import DeepResearchAgent

import logging
logging.basicConfig(level=logging.INFO)

os.environ["LLM_MODEL_ID"] = "gpt-3.5-turbo"

config = Configuration.from_env()
agent = DeepResearchAgent(config=config)
for event in agent.run_stream("What are the latest advances in Reinforcement Learning on ArXiv?"):
    print(event.get('type'), event.get('message', event.get('task_id')))

