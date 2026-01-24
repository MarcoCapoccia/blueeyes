from typing import Set, List, Tuple, Optional, Dict
from model import World, VisibilityMatrix
from epistemic import compute_leavers_mask


class PALSimulation:
    # simulates the blue-eyed islanders puzzle using public announcement logic
    
    def __init__(self, n: int, visibility: VisibilityMatrix, actual_world: World, max_days: int = 15):
        # initialize simulation with visibility matrix and actual world
        self.n = n
        self.visibility = visibility
        self.actual_world = actual_world
        self.max_days = max_days
        
        self.world_set = self._initial_announcement()
        self.history: List[Dict] = []
        self.current_day = 0
        self.solved = False
        self.stuck = False
    
    def _initial_announcement(self) -> Set[World]:
        # day 0 initial public announcement filters to worlds with at least one blue-eyed agent
        world_set = set()
        # check all possible worlds
        for mask in range(1 << self.n):
            world = World(mask, self.n)
            if world.blue_count() >= 1:
                # keep worlds with at least one blue
                world_set.add(world)
        return world_set
    
    def step(self) -> Optional[Dict]:
        # perform one day of the simulation
        if self.solved or self.stuck or self.current_day >= self.max_days:
            return None
        
        day_info = {
            'day': self.current_day,
            'world_set_size': len(self.world_set),
            'leavers': [],
            'epistemic_states': {},
            'leavers_mask': 0
        }
        
        # compute who would leave in actual world
        leavers_mask = compute_leavers_mask(
            self.actual_world, self.visibility, self.world_set
        )
        day_info['leavers_mask'] = leavers_mask
        
        # convert  to list
        leavers = []
        for agent in range(self.n):
            if (leavers_mask >> agent) & 1:
                leavers.append(agent)
        day_info['leavers'] = leavers
        
        from epistemic import get_all_epistemic_states
        day_info['epistemic_states'] = get_all_epistemic_states(
            self.actual_world, self.visibility, self.world_set
        )
        
        # filter worlds consistent with observed leavers
        new_world_set = set()
        for world in self.world_set:
            world_leavers = compute_leavers_mask(world, self.visibility, self.world_set)
            if world_leavers == leavers_mask:
                new_world_set.add(world)
        
        # check termination conditions
        actual_blue_mask = self.actual_world.mask
        
        if leavers_mask == actual_blue_mask and actual_blue_mask != 0:
            # all blue agents know theyre blue
            self.solved = True
            day_info['status'] = 'solved'
        elif new_world_set == self.world_set or len(new_world_set) == 0:
            # no progress or empty set
            self.stuck = True
            day_info['status'] = 'stuck'
        else:
            day_info['status'] = 'continuing'
        
        self.world_set = new_world_set
        self.history.append(day_info)
        self.current_day += 1
        
        return day_info
    
    def run(self) -> Dict:
        # run the simulation until termination or max_days
        while not self.solved and not self.stuck and self.current_day < self.max_days:
            step_result = self.step()
            if step_result is None:
                # already terminated
                break
        
        return {
            'solved': self.solved,
            'stuck': self.stuck,
            'days': self.current_day,
            'history': self.history,
            'final_world_set_size': len(self.world_set)
        }
    
    def reset(self):
        # reset the simulation to initial state
        self.world_set = self._initial_announcement()
        self.history = []
        self.current_day = 0
        self.solved = False
        self.stuck = False
