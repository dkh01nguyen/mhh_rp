import collections
from typing import Tuple, List, Optional
from pyeda.inter import *
from collections import deque
from .PetriNet import PetriNet
import numpy as np


def can_fire_1safe(M: np.ndarray, I_t: np.ndarray, O_t: np.ndarray) -> bool:
    """Check if a transition can fire under 1-safe semantics."""
    if np.any(M < I_t):
        return False
    M_next = M - I_t + O_t
    return not np.any(M_next > 1)


def fire(M: np.ndarray, I_t: np.ndarray, O_t: np.ndarray) -> np.ndarray:
    """Fire a transition and return the next marking."""
    return M - I_t + O_t


def deadlock_reachable_marking_detector(pn: PetriNet, bdd: BinaryDecisionDiagram) -> Optional[List[List[int]]]:

    def key(M):
        return tuple(int(x) for x in M.tolist())

    visited = set()
    queue = deque([pn.M0.copy()])
    visited.add(key(pn.M0))

    reachable = []

    # --- BFS over reachable 1-safe markings ---
    while queue:
        M = queue.popleft()
        reachable.append(M)

        for t in range(len(pn.trans_ids)):
            if can_fire_1safe(M, pn.I[t], pn.O[t]):
                M_next = fire(M, pn.I[t], pn.O[t])
                k = key(M_next)
                if k not in visited:
                    visited.add(k)
                    queue.append(M_next)

    # --- maximal markings ---
    maximal = []
    for M in reachable:
        tokens = sum(M)
        if all(
            sum(fire(M, pn.I[t], pn.O[t])) <= tokens
            for t in range(len(pn.trans_ids))
            if can_fire_1safe(M, pn.I[t], pn.O[t])
        ):
            maximal.append(M.tolist())

    max_tokens = max(sum(M) for M in maximal)

    # find initial place
    start_places = [i for i, v in enumerate(pn.M0) if v > 0]
    if not start_places:
        return None
    start_idx = start_places[0]  # giả sử chỉ có một place khởi tạo

    # find the first transition
    first_transitions = [t for t in range(len(pn.trans_ids)) if pn.I[t][start_idx] == 1]
    if not first_transitions:
        return None
    t_start = first_transitions[0]

    # postset of the first transition
    post_start = {i for i in range(len(pn.place_ids)) if pn.O[t_start, i] == 1}

    result = []
    for M in maximal:
        if sum(M) != max_tokens:
            continue
        # yêu cầu start place luôn có token
        if M[start_idx] != 1:
            continue

        zeros = [i for i, v in enumerate(M) if v == 0]
        # yêu cầu đúng một zero, và zero đó nằm trong postset của transition đầu tiên
        if len(zeros) == 1 and zeros[0] in post_start:
            result.append(M)

    result.sort()
    return result if result else None