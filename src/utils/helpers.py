
import logging

def configure_agent_logger():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("agent")
