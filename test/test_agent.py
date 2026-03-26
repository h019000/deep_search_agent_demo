import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_SRC = ROOT_DIR / "backend" / "src"
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

load_dotenv(BACKEND_ENV)

from config import Configuration
from agent import DeepResearchAgent

import logging
logging.basicConfig(level=logging.INFO)


config = Configuration.from_env()
agent = DeepResearchAgent(config=config)
for event in agent.run_stream("What are the latest advances in Reinforcement Learning on ArXiv?"):
    print(event.get("type"), event.get("message", event.get("task_id")))
