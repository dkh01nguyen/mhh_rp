import collections
from typing import Tuple, List, Optional
from pyeda.inter import *
from collections import deque
from .PetriNet import PetriNet
import numpy as np

def can_fire_1safe(M: np.ndarray, I_t: np.ndarray, O_t: np.ndarray) -> bool:
    # Enable: M >= I_t
    if np.any(M < I_t):
        return False
    # 1-safe sau khi bắn: M - I_t + O_t <= 1
    M_next = M - I_t + O_t
    if np.any(M_next > 1):
        return False
    return True

def fire(M: np.ndarray, I_t: np.ndarray, O_t: np.ndarray) -> np.ndarray:
    return M - I_t + O_t

def build_var_map(pn):
    # Use BDD variables for restrict dict keys
    return {pid: bddvar(pid) for pid in pn.place_ids}

def marking_to_dict(pn, M: np.ndarray, var_map: dict) -> dict:
    return {var_map[pid]: bool(M[i]) for i, pid in enumerate(pn.place_ids)}

def deadlock_reachable_marking_detector(pn, bdd) -> Optional[list]:
    """
    Kích hoạt tuần tự:
    - Ở mỗi bước, thử lần lượt các transition theo thứ tự ưu tiên; fire transition đầu tiên khả thi.
    - Nếu không transition nào khả thi ở bước hiện tại: kiểm tra BDD. Nếu marking thuộc BDD -> trả về marking, ngược lại -> None.
    - Phát hiện vòng lặp (seen set) để kết luận không deadlock nếu hệ lặp vô hạn mà không có bước thất bại.
    """
    M = pn.M0.copy()
    var_map = build_var_map(pn)

    seen = set()
    def key(mark: np.ndarray) -> tuple:
        return tuple(int(x) for x in mark.tolist())

    while True:
        k = key(M)
        if k in seen:
            # Lặp vô hạn không có thất bại thì, không deadlock theo định nghĩa
            return None
        seen.add(k)

        # Thử lần lượt các transition theo thứ tự
        fired = False
        for t in range(len(pn.trans_ids)):
            I_t = pn.I[t]
            O_t = pn.O[t]
            if can_fire_1safe(M, I_t, O_t):
                M = fire(M, I_t, O_t)
                fired = True
                break  # chỉ fire 1 transition mỗi bước

        if not fired:
            # Không có transition nào khả thi, thì kiểm tra deadlock
            mdict = marking_to_dict(pn, M, var_map)
            if bdd.restrict(mdict).is_one():
                return M.tolist()
            return None
