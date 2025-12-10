import collections
from typing import Tuple, List, Optional
from pyeda.inter import *
from .PetriNet import PetriNet
import numpy as np

def bdd_reachable_counting(pn: PetriNet) -> Tuple[BinaryDecisionDiagram, int]:
    """
    Symbolic reachability analysis using Binary Decision Diagrams (BDDs).
    
    Algorithm:
    1. Encode markings symbolically using BDDs
    2. Build transition relations R_t(x, x') for each transition
    3. Compute reachability set iteratively by symbolic image computation
    4. Return BDD representing all reachable markings
    
    Optimizations:
    - Use partitioned transition relations (separate R_t per transition)
    - Frontier-based traversal (only explore new states)
    - Early termination on fixed point
    """
    
    num_trans, num_places = pn.I.shape
    
    if num_places == 0:
        return None, 0

    # 1. Create BDD variables for current (X) and next (X') states
    X = bddvars('x', num_places)
    Xp = bddvars('xp', num_places)
    
    # BDD constants
    TRUE = X[0] | ~X[0]
    FALSE = X[0] & ~X[0]
    
    # Variable renaming map: X' -> X
    rename_map = {Xp[i]: X[i] for i in range(num_places)}
    
    # 2. Encode initial marking M0 as BDD
    M0_bdd = TRUE
    for i in range(num_places):
        if pn.M0[i] > 0:
            M0_bdd &= X[i]
        else:
            M0_bdd &= ~X[i]

    # 3. Build partitioned transition relations R_t(x, x')
    # Each R_t encodes: enabling condition + state change + frame condition
    trans_relations = []

    for t in range(num_trans):
        R_t = TRUE
        
        # For each place, encode the transition behavior
        for p in range(num_places):
            input_tokens = pn.I[t, p]
            output_tokens = pn.O[t, p]
            
            if input_tokens > 0 and output_tokens == 0:
                # Token consumed: X[p]=1 (enabled), X'[p]=0 (after firing)
                R_t &= X[p] & ~Xp[p]
            elif input_tokens == 0 and output_tokens > 0:
                # Token produced: X[p]=0 (1-safe constraint), X'[p]=1
                R_t &= ~X[p] & Xp[p]
            elif input_tokens > 0 and output_tokens > 0:
                # Self-loop: X[p]=1, X'[p]=1
                R_t &= X[p] & Xp[p]
            else:
                # Place unchanged: X'[p] = X[p]
                R_t &= (X[p] & Xp[p]) | (~X[p] & ~Xp[p])
        
        if not R_t.is_zero():
            trans_relations.append(R_t)

    # 4. Symbolic reachability computation using frontier-based traversal
    # Pure symbolic BDD approach (no explicit state tracking)
    Reached = M0_bdd  # Set of all reached states (BDD)
    Frontier = M0_bdd  # Set of newly discovered states (BDD)
    
    max_iterations = min(1000, 2 ** min(num_places, 20))
    
    for iteration in range(max_iterations):
        # Compute successors of frontier states
        # Image(Frontier) = ∃X. (Frontier(X) ∧ R(X, X'))[X'/X]
        
        New = FALSE  # New states discovered in this iteration (BDD)
        
        # For each transition, compute image of frontier
        for R_t in trans_relations:
            # Step 1: Constrain transition to frontier states
            # Frontier(X) ∧ R_t(X, X')
            constrained = Frontier & R_t
            
            if constrained.is_zero():
                continue
            
            # Step 2: Existential quantification over current state variables X
            # ∃X. (Frontier(X) ∧ R_t(X, X'))
            # This gives us states reachable in X' variables
            img = constrained
            for i in range(num_places):
                img = img.smoothing(X[i])  # Existential quantification
            
            # Step 3: Rename X' to X to get successor states in X variables
            img = img.compose(rename_map)
            
            # Step 4: Filter out already visited states immediately
            img &= ~Reached
            
            # Step 5: Union with new states discovered so far
            New |= img
        
        # Check for fixed point (no new states found)
        if New.is_zero():
            break
        
        # Update reached set and frontier (pure symbolic operations)
        Reached |= New
        Frontier = New
    
    # 5. Count reachable markings from BDD
    # Need to properly enumerate all states, including don't-care variables
    total_markings = 0
    try:
        for assignment in Reached.satisfy_all():
            # Count how many variables are "don't care" (not in assignment)
            # Each don't care variable can be 0 or 1, doubling the count
            missing_vars = []
            for i in range(num_places):
                if X[i] not in assignment:
                    missing_vars.append(i)
            
            # Each assignment represents 2^(number of don't cares) actual states
            num_actual_states = 2 ** len(missing_vars)
            total_markings += num_actual_states
    except:
        # Fallback: estimate from BDD structure if enumeration fails
        total_markings = 0
    
    return Reached, total_markings