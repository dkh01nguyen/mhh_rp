from collections import deque
import numpy as np
from .PetriNet import PetriNet
from typing import Set, Tuple

def bfs_reachable_traversal(pn: PetriNet) -> Set[Tuple[int, ...]]:
    m0 = tuple(map(int, pn.M0))
    
    # visited chứa tất cả marking đã được duyệt
    visited = {m0}

    # queue cho BFS (FIFO), bắt đầu từ M0
    queue = deque([m0])
    
    # Số lượng transition trong Petri net
    num_transitions = pn.I.shape[0]

    # BFS
    while queue:
        # Lấy phần tử đầu tiên trong queue (FIFO)
        curr_m_tuple = queue.popleft()

        # Chuyển tuple -> numpy array để thực hiện tính toán
        curr_m = np.array(curr_m_tuple)

        # Thử fire từng transition
        for t in range(num_transitions):

            # Vector nhu cầu input (I)
            input_req = pn.I[t]

            # Vector output (O)
            output_prod = pn.O[t]

            # Kiểm tra transition có enabled không (M >= I)
            if np.all(curr_m >= input_req):

                # Fire: M' = M - I + O
                new_m = curr_m - input_req + output_prod
                
                # Kiểm tra 1-safe (không cho phép token > 1)
                if np.all(new_m <= 1):

                    # Chuyển về tuple để hash
                    new_m_tuple = tuple(map(int, new_m))
                    
                    # Nếu marking mới chưa được thăm → thêm vào queue
                    if new_m_tuple not in visited:
                        visited.add(new_m_tuple)
                        queue.append(new_m_tuple)
            
    return visited