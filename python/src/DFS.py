from collections import deque
import numpy as np
from .PetriNet import PetriNet
from typing import Set, Tuple

def dfs_reachable_traversal(pn: PetriNet) -> Set[Tuple[int, ...]]:
    # Chuyển marking ban đầu M0 (numpy array) thành tuple để có thể hash và lưu trong set
    m0 = tuple(map(int, pn.M0))
    
    # visited chứa tất cả các marking đã thăm (để tránh lặp vô hạn)
    visited = {m0}

    # stack dùng cho DFS (LIFO), bắt đầu từ M0
    stack = [m0] 
    
    # Số lượng transition = số hàng của ma trận I (T x P)
    num_transitions = pn.I.shape[0]

    # DFS
    while stack:
        # Lấy 1 marking từ cuối stack (LIFO)
        curr_m_tuple = stack.pop()

        # Chuyển tuple về numpy array để tính toán vector
        curr_m = np.array(curr_m_tuple)

        # Thử fire từng transition t
        for t in range(num_transitions):

            # Input arc vector của transition t (I_t,p)
            input_req = pn.I[t]

            # Output arc vector của transition t (O_t,p)
            output_prod = pn.O[t]

            # Kiểm tra transition có enabled không: M >= I
            if np.all(curr_m >= input_req):

                # Bắn transition: M' = M - I + O
                new_m = curr_m - input_req + output_prod
                
                # Kiểm tra 1-safe (mỗi place không vượt quá 1 token)
                if np.all(new_m <= 1):

                    # Chuyển về tuple để hash và lưu trong set
                    new_m_tuple = tuple(map(int, new_m))

                    # Nếu marking mới chưa thăm → thêm vào
                    if new_m_tuple not in visited:
                        visited.add(new_m_tuple)
                        stack.append(new_m_tuple)
            
    return visited