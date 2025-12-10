# Petri Net Analysis Tool 🔬

Công cụ phân tích 1-safe Petri Net với các thuật toán Reachability, Deadlock Detection và Optimization.

## Mô tả

Tool này thực hiện **5 tasks** phân tích Petri Net:
1. **Load Petri Net** từ file PNML
2. **Explicit Reachability** - BFS và DFS (tìm kiếm theo chiều rộng/sâu)
3. **BDD Symbolic Reachability** - Thuật toán symbolic với Binary Decision Diagrams
4. **Deadlock Detection** - Phát hiện trạng thái deadlock
5. **Optimization** - Tìm marking tối ưu với hàm mục tiêu tuyến tính

## Cấu trúc Project

```
btl/
├── runtest.py              # File test chính
├── test1.pnml             # File mô tả Petri net (PNML format)
├── src/
│   ├── PetriNet.py        # Class chính để đọc và xử lý Petri net
│   ├── BFS.py             # Thuật toán tìm kiếm theo chiều rộng
│   ├── DFS.py             # Thuật toán tìm kiếm theo chiều sâu  
│   ├── BDD.py             # Thuật toán symbolic với Binary Decision Diagram
│   ├── Deadlock.py        # Phát hiện deadlock
│   └── Optimization.py    # Tối ưu hóa mục tiêu tuyến tính
└── __pycache__/           # Cache Python
```
 
### Hướng dẫn cài đặt chi tiết

### Bước 1: Tạo môi trường ảo (Virtual Environment)

```bash
# Tạo virtual environment trong thư mục dự án 
python -m venv venv

# Kích hoạt trên Windows
venv\Scripts\Activate.ps1

# Kích hoạt trên macOS/Linux
source venv/bin/activate
```

**Lưu ý**: Sau khi kích hoạt, ta sẽ thấy `(venv)` xuất hiện trước dấu nhắc lệnh.

### Bước 2: Cài đặt dependencies

```bash
# Cài đặt thư viện cần thiết
pip install psutil numpy pyeda
```

### Bước 3: Kiểm tra cài đặt

```bash
# Kiểm tra Python version
python --version

# Kiểm tra numpy
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"

# Kiểm tra pyeda
python -c "import pyeda; print('PyEDA installed successfully')"

# Kiểm tra tất cả modules trong project
python -c "import src.PetriNet; print('All modules imported successfully')"
```

## Chạy chương trình

### Chạy FULL TEST (Tất cả 5 Tasks)

```bash
# Đảm bảo đang ở thư mục gốc và venv đã kích hoạt
venv\Scripts\Activate.ps1

# Chạy chương trình
python runtest.py
```

**Full test bao gồm:**
- **Task 1**: Load và hiển thị Petri Net từ file PNML
- **Task 2**: Explicit Reachability - BFS và DFS (tracking thời gian & memory)
- **Task 3**: BDD Symbolic Reachability (tracking thời gian & memory)
- **Task 4**: Deadlock Detection
- **Task 5**: Optimization (tìm marking tối ưu)
- So sánh hiệu suất: Explicit (BFS) vs Symbolic (BDD)

---

### Chạy từng Task riêng lẻ

#### Task 1: Load Petri Net

```bash
python -c "from src.PetriNet import PetriNet; pn = PetriNet.read_pnml('test1.pnml'); print(pn)"
```

#### Task 2: Explicit Reachability Analysis (BFS & DFS)

**BFS (Breadth-First Search):**
```bash
python -c "from src.PetriNet import PetriNet; from src.BFS import bfs_reachable_traversal; pn = PetriNet.read_pnml('test1.pnml'); states = bfs_reachable_traversal(pn); print(f'BFS tìm thấy {len(states)} trạng thái')"
```

**DFS (Depth-First Search):**
```bash
python -c "from src.PetriNet import PetriNet; from src.DFS import dfs_reachable_traversal; pn = PetriNet.read_pnml('test1.pnml'); states = dfs_reachable_traversal(pn); print(f'DFS tìm thấy {len(states)} trạng thái')"
```

#### Task 3: BDD Symbolic Reachability

```bash
python -c "from src.PetriNet import PetriNet; from src.BDD import bdd_reachable_counting; pn = PetriNet.read_pnml('test1.pnml'); bdd_res, count = bdd_reachable_counting(pn); print(f'BDD tìm thấy {count} trạng thái (symbolic)')"
```

#### Task 4: Deadlock Detection

```bash
python -c "from src.PetriNet import PetriNet; from src.BDD import bdd_reachable_counting; from src.Deadlock import deadlock_reachable_marking_detector; pn = PetriNet.read_pnml('test2.pnml'); bdd_res, _ = bdd_reachable_counting(pn); dl = deadlock_reachable_marking_detector(pn, bdd_res); print(f'Deadlock: {dl if dl else \"Không phát hiện\"}')"
```

#### Task 5: Optimization (Tìm Marking Tối Ưu)

```bash
python -c "import numpy as np; from src.PetriNet import PetriNet; from src.BDD import bdd_reachable_counting; from src.Optimization import max_reachable_marking; pn = PetriNet.read_pnml('test2.pnml'); bdd_res, _ = bdd_reachable_counting(pn); c = np.array([2, 3, 1, 4, 10, 0, 0, 0, 0, 0]); opt_m, opt_val = max_reachable_marking(pn.place_ids, bdd_res, c); print(f'Marking tối ưu: {opt_m}, Giá trị: {opt_val}')"
```

### Debug và Kiểm tra Module

```bash
# Test PetriNet class
python -c "from src.PetriNet import PetriNet; pn = PetriNet.read_pnml('test2.pnml'); print('✓ PetriNet loaded')"

# Test BFS module
python -c "from src.BFS import bfs_reachable_traversal; print('✓ BFS module working')"

# Test DFS module
python -c "from src.DFS import dfs_reachable_traversal; print('✓ DFS module working')"

# Test BDD module
python -c "from src.BDD import bdd_reachable_counting; print('✓ BDD module working')"

# Test Deadlock module
python -c "from src.Deadlock import deadlock_reachable_marking_detector; print('✓ Deadlock module working')"

# Test Optimization module
python -c "from src.Optimization import max_reachable_marking; print('✓ Optimization module working')"

# Test tất cả modules
python -c "from src.PetriNet import PetriNet; from src.BFS import bfs_reachable_traversal; from src.DFS import dfs_reachable_traversal; from src.BDD import bdd_reachable_counting; from src.Deadlock import deadlock_reachable_marking_detector; from src.Optimization import max_reachable_marking; print('✓ All modules imported successfully')"
```




