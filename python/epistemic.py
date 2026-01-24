from typing import Set, Dict, List
from model import World, VisibilityMatrix


def indistinguishable_worlds(world: World, agent: int, visibility: VisibilityMatrix, 
                            world_set: Set[World]) -> Set[World]:
    # find all worlds in world_set that are indistinguishable from world for agent
    sig = visibility.get_observation_signature(world, agent)
    indistinguishable = set()
    
    # check all worlds for matching signature
    for w in world_set:
        if visibility.get_observation_signature(w, agent) == sig:
            indistinguishable.add(w)
    
    return indistinguishable


def knows_blue(world: World, agent: int, visibility: VisibilityMatrix, 
               world_set: Set[World]) -> bool:
    # check if agent knows they have blue eyes in the given world
    if not world.has_blue_eyes(agent):
        return False
    
    # must be blue in all indistinguishable worlds
    indisting = indistinguishable_worlds(world, agent, visibility, world_set)
    return all(w.has_blue_eyes(agent) for w in indisting)


def knows_red(world: World, agent: int, visibility: VisibilityMatrix, 
              world_set: Set[World]) -> bool:
    # check if agent knows they have red eyes in the given world
    if world.has_blue_eyes(agent):
        return False
    
    indisting = indistinguishable_worlds(world, agent, visibility, world_set)
    return all(not w.has_blue_eyes(agent) for w in indisting)


def get_epistemic_state(world: World, agent: int, visibility: VisibilityMatrix,
                       world_set: Set[World]) -> str:
    # get the epistemic state of an agent in a world
    if knows_blue(world, agent, visibility, world_set):
        return "knows_blue"
    elif knows_red(world, agent, visibility, world_set):
        return "knows_red"
    else:
        return "uncertain"


def compute_leavers_mask(world: World, visibility: VisibilityMatrix, 
                        world_set: Set[World]) -> int:
    # compute the bitmask of agents who know they are blue in the given world
    leavers = 0
    for agent in range(world.n):
        if knows_blue(world, agent, visibility, world_set):
            # set bit for this agent
            leavers |= (1 << agent)
    return leavers


def get_all_epistemic_states(world: World, visibility: VisibilityMatrix,
                             world_set: Set[World]) -> Dict[int, str]:
    # get epistemic states for all agents in a world
    states = {}
    for agent in range(world.n):
        states[agent] = get_epistemic_state(world, agent, visibility, world_set)
    return states
