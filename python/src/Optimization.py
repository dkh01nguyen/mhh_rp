import collections
from typing import Tuple, List, Optional
from pyeda.inter import *
from collections import deque
import numpy as np

def max_reachable_marking(
    place_ids: List[str], 
    bdd: BinaryDecisionDiagram, 
    c: np.ndarray
) -> Tuple[Optional[List[int]], Optional[int]]:
    """
    Optimize linear objective function c^T * M over reachable markings represented by BDD.
    
    Args:
        place_ids: List of place identifiers
        bdd: BDD representing reachable markings 
        c: Coefficient vector for linear objective function
    
    Returns:
        Tuple of (optimal_marking, optimal_value) or (None, None) if no solution
    """
    # Check if BDD is satisfiable (có marking nào khả đạt không)
    if bdd.is_zero():
        return None, None
    
    # Nếu BDD là tautology (luôn true), chọn marking tối ưu
    if bdd.is_one():
        # Chọn marking tối ưu khi tất cả combination đều valid
        optimal_marking = []
        for i in range(len(c)):
            # Chọn 1 nếu coefficient dương, 0 nếu âm
            optimal_marking.append(1 if c[i] >= 0 else 0)
        optimal_value = int(np.dot(c, optimal_marking))
        return optimal_marking, optimal_value
    
    max_value = float('-inf')
    optimal_marking = None
    
    # Get all variables from BDD and create mapping by name
    var_name_to_idx = {}
    for i, place_id in enumerate(place_ids):
        var_name_to_idx[place_id] = i
    
    # Iterate through all satisfying assignments from BDD
    for assignment in bdd.satisfy_all():
        # For each assignment, determine which variables are constrained
        constrained_vars = {}  # index -> value mapping
        free_var_indices = []  # Indices of variables not in assignment
        
        # Process all variables in assignment (constrained by BDD)
        for var, value in assignment.items():
            var_name = var.name
            if var_name in var_name_to_idx:
                idx = var_name_to_idx[var_name]
                constrained_vars[idx] = 1 if value else 0
        
        # Find free variables (not in assignment)
        for i in range(len(place_ids)):
            if i not in constrained_vars:
                free_var_indices.append(i)
        
        # Generate all combinations của don't care variables
        num_free = len(free_var_indices)
        for combo in range(2 ** num_free):  # 2^n combinations
            marking = [0] * len(place_ids)
            
            # Set constrained variables
            for i, val in constrained_vars.items():
                marking[i] = val
            
            # Set free variables according to current combination
            for j, var_idx in enumerate(free_var_indices):
                bit_val = (combo >> j) & 1
                marking[var_idx] = bit_val
            
            # Calculate objective value
            current_value = int(np.dot(c, marking))
            
            if current_value > max_value:
                max_value = current_value
                optimal_marking = marking
    
    if optimal_marking is None:
        return None, None
    
    return optimal_marking, max_value
  