from typing import List, Set, Dict, Tuple
import numpy as np


class World:
    # represents a world as a bitmask where bit i = 1 means agent i has blue eyes
    
    def __init__(self, mask: int, n: int):
        # initialize a world with given bitmask and number of agents
        self.mask = mask
        self.n = n
        assert 0 <= mask < (1 << n), f"Mask {mask} out of range for n={n}"
    
    def has_blue_eyes(self, agent: int) -> bool:
        # check if agent has blue eyes in this world
        return bool((self.mask >> agent) & 1)
    
    def blue_count(self) -> int:
        # return the number of agents with blue eyes
        return bin(self.mask).count('1')
    
    def blue_agents(self) -> Set[int]:
        # return set of agents with blue eyes
        return {i for i in range(self.n) if self.has_blue_eyes(i)}
    
    def __eq__(self, other):
        # check equality between two worlds
        return isinstance(other, World) and self.mask == other.mask and self.n == other.n
    
    def __hash__(self):
        # compute hash for set and dict usage
        return hash((self.mask, self.n))
    
    def __repr__(self):
        # return string representation of world with binary mask
        return f"World(mask={self.mask:0{self.n}b}, n={self.n})"


class VisibilityMatrix:
    # binary visibility matrix V[i][j] = 1 means agent j sees agent i's eye color
    
    def __init__(self, n: int, matrix: np.ndarray = None, allow_self_visibility: bool = False):
        # initialize visibility matrix with optional custom matrix
        self.n = n
        if matrix is None:
            self.matrix = np.zeros((n, n), dtype=int)
        else:
            assert matrix.shape == (n, n), f"Matrix shape {matrix.shape} != ({n}, {n})"
            self.matrix = matrix.astype(int).copy()
        
        if not allow_self_visibility:
            np.fill_diagonal(self.matrix, 0)
        
        self.allow_self_visibility = allow_self_visibility
    
    def sees(self, observer: int, observed: int) -> bool:
        # check if observer sees observed agent's eye color
        return bool(self.matrix[observed, observer])
    
    def get_observation_signature(self, world: World, agent: int) -> Tuple[int, ...]:
        # get the observation signature for an agent in a world
        signature = []
        for i in range(self.n):
            if self.sees(agent, i):
                # add bit for each visible agent
                signature.append(1 if world.has_blue_eyes(i) else 0)
        return tuple(signature)
    
    def get_visible_agents(self, agent: int) -> List[int]:
        # return list of agents that the given agent can see
        return [i for i in range(self.n) if self.sees(agent, i)]
    
    def set_visibility(self, observer: int, observed: int, value: bool):
        # set visibility V[observed][observer] = value
        if not self.allow_self_visibility and observer == observed:
            return
        self.matrix[observed, observer] = 1 if value else 0
    
    def toggle_visibility(self, observer: int, observed: int):
        # toggle visibility between observer and observed
        if not self.allow_self_visibility and observer == observed:
            return
        self.matrix[observed, observer] = 1 - self.matrix[observed, observer]
    
    def copy(self):
        # create a copy of this visibility matrix
        return VisibilityMatrix(self.n, self.matrix.copy(), self.allow_self_visibility)
    
    @classmethod
    def complete_graph(cls, n: int) -> 'VisibilityMatrix':
        # create a complete graph visibility matrix
        matrix = np.ones((n, n), dtype=int)
        np.fill_diagonal(matrix, 0)
        return cls(n, matrix)
    
    @classmethod
    def ring(cls, n: int) -> 'VisibilityMatrix':
        # create a ring topology visibility matrix
        matrix = np.zeros((n, n), dtype=int)
        for i in range(n):
            # each agent sees previous and next
            matrix[(i - 1) % n, i] = 1
            matrix[(i + 1) % n, i] = 1
        return cls(n, matrix)
    
    @classmethod
    def star(cls, n: int, center: int = 0) -> 'VisibilityMatrix':
        # create a star topology visibility matrix
        matrix = np.zeros((n, n), dtype=int)
        for i in range(n):
            if i != center:
                # others see center and center sees others
                matrix[center, i] = 1
                matrix[i, center] = 1
        return cls(n, matrix)
    
    @classmethod
    def disconnected(cls, n: int) -> 'VisibilityMatrix':
        # create a disconnected graph visibility matrix
        return cls(n, np.zeros((n, n), dtype=int))
    
    @classmethod
    def random(cls, n: int, p: float = 0.5, allow_self_visibility: bool = False) -> 'VisibilityMatrix':
        # create a random visibility matrix with edge probability p
        matrix = np.random.binomial(1, p, (n, n)).astype(int)
        return cls(n, matrix, allow_self_visibility)
    
    def __repr__(self):
        # return string representation of visibility matrix
        return f"VisibilityMatrix(n={self.n}, matrix=\n{self.matrix})"
