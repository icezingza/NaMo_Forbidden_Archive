import logging

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

logger = logging.getLogger(__name__)


class PersonaAgent(Agent):
    def __init__(self, unique_id, model, name, knowledge_base):
        super().__init__(unique_id, model)
        self.name = name
        self.knowledge = knowledge_base

    def step(self):
        # จำลองการโต้ตอบแบบกลุ่ม (Multi-Agent Interaction)
        logger.info(f"[Apurva Sim]: {self.name} is assessing situational equilibrium.")


class ApurvaSimulation(Model):
    """
    Mesa World Simulation: Simulation of erotic/taboo scenarios
    """

    def __init__(self, width, height):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # เพิ่ม Agent
        names = ["Seraphina", "Mōriko", "Alisa", "Lalita"]
        for i, name in enumerate(names):
            agent = PersonaAgent(i, self, name, "Taboo Context")
            self.schedule.add(agent)
            self.grid.place_agent(agent, (i, i))

    def step(self):
        self.schedule.step()
