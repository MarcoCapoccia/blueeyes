from typing import Dict, Optional, Set
from model import World, VisibilityMatrix
from pal import PALSimulation


class SingleMatrixSimulator:
    # simulator for a single visibility matrix configuration
    
    def __init__(self, n: int, visibility: VisibilityMatrix, actual_blue_set: Set[int], max_days: int = 15):
        # initialize simulator with visibility matrix and blue agent set
        self.n = n
        self.visibility = visibility
        self.actual_blue_set = actual_blue_set
        self.max_days = max_days
        
        actual_mask = sum(1 << i for i in actual_blue_set)
        self.actual_world = World(actual_mask, n)
        
        self.simulation: Optional[PALSimulation] = None
        self.reset()
    
    def reset(self):
        # reset the simulation
        self.simulation = PALSimulation(
            self.n, self.visibility, self.actual_world, self.max_days
        )
    
    def step(self) -> Optional[Dict]:
        # perform one step of the simulation
        if self.simulation is None:
            self.reset()
        return self.simulation.step()
    
    def run(self) -> Dict:
        # run the full simulation
        if self.simulation is None:
            self.reset()
        return self.simulation.run()
    
    def get_current_state(self) -> Dict:
        # get current state without stepping
        if self.simulation is None:
            self.reset()
        
        return {
            'day': self.simulation.current_day,
            'world_set_size': len(self.simulation.world_set),
            'solved': self.simulation.solved,
            'stuck': self.simulation.stuck,
            'history': self.simulation.history
        }
    
    def update_visibility(self, visibility: VisibilityMatrix):
        # update the visibility matrix and reset
        self.visibility = visibility
        self.reset()
    
    def update_actual_blue_set(self, blue_set: Set[int]):
        # update the actual blue set and reset
        self.actual_blue_set = blue_set
        actual_mask = sum(1 << i for i in blue_set)
        self.actual_world = World(actual_mask, self.n)
        self.reset()
    
    def get_epistemic_states(self) -> Dict[int, str]:
        # get current epistemic states for all agents
        if self.simulation is None:
            self.reset()
        
        from epistemic import get_all_epistemic_states
        return get_all_epistemic_states(
            self.actual_world, self.visibility, self.simulation.world_set
        )
