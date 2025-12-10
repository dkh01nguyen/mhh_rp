import numpy as np
import xml.etree.ElementTree as ET
from typing import List, Optional

class PetriNet:
    def __init__(
        self,
        place_ids: List[str],
        trans_ids: List[str],
        place_names: List[Optional[str]],
        trans_names: List[Optional[str]],
        I: np.ndarray,   
        O: np.ndarray, 
        M0: np.ndarray
    ):
        self.place_ids = place_ids
        self.trans_ids = trans_ids
        self.place_names = place_names
        self.trans_names = trans_names
        self.I = I
        self.O = O
        self.M0 = M0

    @classmethod
    def read_pnml(cls, filename: str) -> "PetriNet":
        tree = ET.parse(filename)
        root = tree.getroot()

        places = []
        transitions = []
        arcs = []

        # Helper để lấy tag name bỏ qua namespace
        def get_tag(element):
            return element.tag.split('}')[-1] if '}' in element.tag else element.tag

        # Duyệt XML để lấy dữ liệu
        for elem in root.iter():
            tag = get_tag(elem)
            
            if tag == 'place':
                p_id = elem.get('id')
                p_name = None
                initial_marking = 0
                for child in elem:
                    child_tag = get_tag(child)
                    if child_tag == 'name':
                        for sub in child:
                            if get_tag(sub) == 'text':
                                p_name = sub.text
                    elif child_tag == 'initialMarking':
                        for sub in child:
                            if get_tag(sub) == 'text':
                                try:
                                    initial_marking = int(sub.text)
                                except ValueError:
                                    initial_marking = 0
                places.append({'id': p_id, 'name': p_name, 'm0': initial_marking})

            elif tag == 'transition':
                t_id = elem.get('id')
                t_name = None
                for child in elem:
                    child_tag = get_tag(child)
                    if child_tag == 'name':
                        for sub in child:
                            if get_tag(sub) == 'text':
                                t_name = sub.text
                transitions.append({'id': t_id, 'name': t_name})

            elif tag == 'arc':
                source = elem.get('source')
                target = elem.get('target')
                arcs.append({'source': source, 'target': target})

        # Xây dựng danh sách ID
        place_ids = [p['id'] for p in places]
        place_names = [p['name'] for p in places]
        
        trans_ids = [t['id'] for t in transitions]
        trans_names = [t['name'] for t in transitions]

        # Map ID sang index
        p_idx_map = {pid: i for i, pid in enumerate(place_ids)}
        t_idx_map = {tid: i for i, tid in enumerate(trans_ids)}

        n_places = len(place_ids)
        n_trans = len(trans_ids)
        
        # --- SỬA ĐỔI QUAN TRỌNG: MA TRẬN KÍCH THƯỚC (Trans x Place) ---
        # Theo expected.txt, ma trận là T x P chứ không phải P x T
        I = np.zeros((n_trans, n_places), dtype=int)
        O = np.zeros((n_trans, n_places), dtype=int)
        M0 = np.array([p['m0'] for p in places], dtype=int)

        # Điền ma trận
        for arc in arcs:
            src = arc['source']
            tgt = arc['target']

            # Place -> Transition (Input Matrix I)
            if src in p_idx_map and tgt in t_idx_map:
                p_idx = p_idx_map[src]
                t_idx = t_idx_map[tgt]
                # I[t, p] = 1 (Thay vì I[p, t])
                I[t_idx, p_idx] += 1 

            # Transition -> Place (Output Matrix O)
            elif src in t_idx_map and tgt in p_idx_map:
                t_idx = t_idx_map[src]
                p_idx = p_idx_map[tgt]
                # O[t, p] = 1 (Thay vì O[p, t])
                O[t_idx, p_idx] += 1

        return cls(place_ids, trans_ids, place_names, trans_names, I, O, M0)

    def __str__(self) -> str:
        s = []
        s.append("Places: " + str(self.place_ids))
        s.append("Place names: " + str(self.place_names))
        s.append("\nTransitions: " + str(self.trans_ids))
        s.append("Transition names: " + str(self.trans_names))
        s.append("\nI (input) matrix:")
        s.append(str(self.I))
        s.append("\nO (output) matrix:")
        s.append(str(self.O))
        s.append("\nInitial marking M0:")
        s.append(str(self.M0))
        return "\n".join(s)


