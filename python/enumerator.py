from typing import Dict, List, Set, Optional, Tuple
import numpy as np
from model import World, VisibilityMatrix
from pal import PALSimulation


class MatrixEnumerator:
    # enumerates visibility matrices and checks solvability
    
    def __init__(self, n: int, max_days: int = 15, allow_self_visibility: bool = False):
        # initialize enumerator for n agents with solvability checking
        self.n = n
        self.max_days = max_days
        self.allow_self_visibility = allow_self_visibility
        
        if allow_self_visibility:
            self.total_matrices = 2 ** (n * n)
        else:
            self.total_matrices = 2 ** (n * (n - 1))
        
        self.solvable_matrices: List[VisibilityMatrix] = []
        self.unsolvable_matrices: List[VisibilityMatrix] = []
        self.solvable_count = 0
        self.unsolvable_count = 0
        
        self.example_solvable: Optional[VisibilityMatrix] = None
        self.example_unsolvable: Optional[VisibilityMatrix] = None
    
    def _matrix_from_index(self, index: int) -> VisibilityMatrix:
        # convert an index to a visibility matrix
        matrix = np.zeros((self.n, self.n), dtype=int)
        
        if self.allow_self_visibility:
            # all n*n bits
            for i in range(self.n):
                for j in range(self.n):
                    bit_pos = i * self.n + j
                    matrix[i, j] = (index >> bit_pos) & 1
        else:
            # only n*(n-1) bits excluding diagonal
            bit_pos = 0
            for i in range(self.n):
                for j in range(self.n):
                    if i != j:
                        matrix[i, j] = (index >> bit_pos) & 1
                        bit_pos += 1
        
        return VisibilityMatrix(self.n, matrix, self.allow_self_visibility)
    
    def _check_uniform_solvability(self, visibility: VisibilityMatrix) -> bool:
        # check definition A uniform solvability for all non-empty blue sets
        for blue_mask in range(1, 1 << self.n):
            # test each possible blue set
            blue_set = {i for i in range(self.n) if (blue_mask >> i) & 1}
            actual_world = World(blue_mask, self.n)
            
            sim = PALSimulation(self.n, visibility, actual_world, self.max_days)
            result = sim.run()
            
            if not result['solved']:
                # found unsolvable case
                return False
        
        return True
    
    def _check_instance_solvability(self, visibility: VisibilityMatrix, 
                                   blue_set: Set[int]) -> bool:
        # check definition B instance solvability for a specific blue set
        blue_mask = sum(1 << i for i in blue_set)
        actual_world = World(blue_mask, self.n)
        
        sim = PALSimulation(self.n, visibility, actual_world, self.max_days)
        result = sim.run()
        
        return result['solved']
    
    def enumerate_uniform(self, progress_callback=None) -> Dict:
        # enumerate all matrices and check uniform solvability
        self.solvable_matrices = []
        self.unsolvable_matrices = []
        self.solvable_count = 0
        self.unsolvable_count = 0
        
        for index in range(self.total_matrices):
            if progress_callback:
                progress_callback(index, self.total_matrices)
            
            visibility = self._matrix_from_index(index)
            
            if self._check_uniform_solvability(visibility):
                # matrix is solvable
                self.solvable_count += 1
                self.solvable_matrices.append(visibility)
                if self.example_solvable is None:
                    self.example_solvable = visibility
            else:
                # matrix is unsolvable
                self.unsolvable_count += 1
                self.unsolvable_matrices.append(visibility)
                if self.example_unsolvable is None:
                    self.example_unsolvable = visibility
        
        return {
            'total': self.total_matrices,
            'solvable': self.solvable_count,
            'unsolvable': self.unsolvable_count,
            'solvable_percentage': (self.solvable_count / self.total_matrices * 100) if self.total_matrices > 0 else 0,
            'example_solvable': self.example_solvable,
            'example_unsolvable': self.example_unsolvable
        }
    
    def enumerate_instance(self, blue_set: Set[int], progress_callback=None) -> Dict:
        # enumerate all matrices and check instance solvability for a specific blue set
        self.solvable_matrices = []
        self.unsolvable_matrices = []
        self.solvable_count = 0
        self.unsolvable_count = 0
        
        for index in range(self.total_matrices):
            if progress_callback:
                progress_callback(index, self.total_matrices)
            
            visibility = self._matrix_from_index(index)
            
            if self._check_instance_solvability(visibility, blue_set):
                self.solvable_count += 1
                self.solvable_matrices.append(visibility)
                if self.example_solvable is None:
                    self.example_solvable = visibility
            else:
                self.unsolvable_count += 1
                self.unsolvable_matrices.append(visibility)
                if self.example_unsolvable is None:
                    self.example_unsolvable = visibility
        
        return {
            'total': self.total_matrices,
            'solvable': self.solvable_count,
            'unsolvable': self.unsolvable_count,
            'solvable_percentage': (self.solvable_count / self.total_matrices * 100) if self.total_matrices > 0 else 0,
            'blue_set': blue_set,
            'example_solvable': self.example_solvable,
            'example_unsolvable': self.example_unsolvable
        }
    
    def sample_random(self, num_samples: int, blue_set: Set[int], 
                     definition: str = 'instance') -> Dict:
        # sample random matrices instead of full enumeration
        self.solvable_matrices = []
        self.unsolvable_matrices = []
        self.solvable_count = 0
        self.unsolvable_count = 0
        
        for _ in range(num_samples):
            visibility = VisibilityMatrix.random(self.n, p=0.5, 
                                                allow_self_visibility=self.allow_self_visibility)
            
            if definition == 'uniform':
                is_solvable = self._check_uniform_solvability(visibility)
            else:
                is_solvable = self._check_instance_solvability(visibility, blue_set)
            
            if is_solvable:
                self.solvable_count += 1
                self.solvable_matrices.append(visibility)
                if self.example_solvable is None:
                    self.example_solvable = visibility
            else:
                self.unsolvable_count += 1
                self.unsolvable_matrices.append(visibility)
                if self.example_unsolvable is None:
                    self.example_unsolvable = visibility
        
        return {
            'total': num_samples,
            'solvable': self.solvable_count,
            'unsolvable': self.unsolvable_count,
            'solvable_percentage': (self.solvable_count / num_samples * 100) if num_samples > 0 else 0,
            'example_solvable': self.example_solvable,
            'example_unsolvable': self.example_unsolvable
        }
