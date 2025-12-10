import numpy as np
import time
import tracemalloc
import psutil
import os
from src.PetriNet import PetriNet
from src.BFS import bfs_reachable_traversal
from src.DFS import dfs_reachable_traversal
from src.BDD import bdd_reachable_counting
from src.Deadlock import deadlock_reachable_marking_detector
from src.Optimization import max_reachable_marking

def test_main():
    print("=== TEST TOÀN DIỆN CẤU TRÚC 5 PLACES COMPACT (5 TASKS) ===")
    try:
        # Load file PNML
        pn = PetriNet.read_pnml("test1.pnml")
        print(pn)
    except Exception as e:
        print(f"Lỗi file: {e}")
        return

    # ---------------------------------------------------------
    # TASK 2: REACHABILITY ANALYSIS (BFS) - WITH PERFORMANCE TRACKING
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[2] KIỂM TRA BFS REACHABILITY - ĐÁNH GIÁ HIỆU SUẤT")
    
    # Bắt đầu theo dõi memory
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    mem_before_bfs = process.memory_info().rss / 1024 / 1024  # MB
    
    # Đo thời gian BFS
    start_time_bfs = time.perf_counter()
    bfs_states = bfs_reachable_traversal(pn)
    end_time_bfs = time.perf_counter()
    
    # Đo memory usage
    current, peak = tracemalloc.get_traced_memory()
    mem_after_bfs = process.memory_info().rss / 1024 / 1024  # MB
    tracemalloc.stop()
    
    bfs_time = end_time_bfs - start_time_bfs
    bfs_memory = peak / 1024 / 1024  # MB (peak memory từ tracemalloc)
    bfs_rss_memory = mem_after_bfs - mem_before_bfs  # RSS memory difference
    
    print(f"-> Số trạng thái tìm thấy (BFS): {len(bfs_states)}")
    print(f"-> Thời gian thực thi BFS: {bfs_time:.6f} seconds")
    print(f"-> Peak memory usage (BFS): {bfs_memory:.2f} MB")
    print(f"-> RSS memory difference: {bfs_rss_memory:.2f} MB")
    
    # Sắp xếp để in cho đẹp
    sorted_states = sorted(list(bfs_states), key=lambda x: (x[4], x[3], x[2], x[1]))
    
    print(f"{'P1':<3} {'P2':<3} {'P3':<3} {'P4':<3} {'P5':<3} | {'Diễn giải'}")
    print("-" * 55)
    for s in sorted_states:
        msg = ""
        if s == (1,0,0,0,0): msg = "Start (Task 1)"
        elif s == (1,1,1,0,0): msg = "P1 -> P2, P3 (Loop P1)"
        elif s == (1,0,1,1,0): msg = "P1,P2,P3 -> P4 (Loop P1,P3)"
        elif s == (0,0,0,0,1): msg = "P1,P3,P4 -> P5 (Finish)"
        else: msg = "Trung gian"
        print(f"{s[0]:<3} {s[1]:<3} {s[2]:<3} {s[3]:<3} {s[4]:<3} | {msg}")


    # ---------------------------------------------------------
    # TASK 3: REACHABILITY ANALYSIS (DFS)
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[3] KIỂM TRA DFS REACHABILITY")
    
    dfs_states = dfs_reachable_traversal(pn)
    print(f"-> Số trạng thái tìm thấy (DFS): {len(dfs_states)}")
    
    # So sánh kết quả
    if bfs_states == dfs_states:
        print(">> KẾT QUẢ KHỚP: BFS và DFS tìm thấy cùng tập trạng thái.")
    else:
        print(">> CẢNH BÁO: Kết quả BFS và DFS khác nhau!")


    # ---------------------------------------------------------
    # TASK 4: SYMBOLIC REACHABILITY (BDD) - WITH PERFORMANCE TRACKING
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[4] KIỂM TRA BDD REACHABILITY - ĐÁNH GIÁ HIỆU SUẤT")
    print("DEBUG: Code moi da chay")
    # Bắt đầu theo dõi memory cho BDD
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    mem_before_bdd = process.memory_info().rss / 1024 / 1024  # MB
    
    # Đo thời gian BDD
    start_time_bdd = time.perf_counter()
    bdd_res, count = bdd_reachable_counting(pn)
    end_time_bdd = time.perf_counter()
    
    # Đo memory usage
    current, peak = tracemalloc.get_traced_memory()
    mem_after_bdd = process.memory_info().rss / 1024 / 1024  # MB
    tracemalloc.stop()
    
    bdd_time = end_time_bdd - start_time_bdd
    bdd_memory = peak / 1024 / 1024  # MB (peak memory từ tracemalloc)
    bdd_rss_memory = mem_after_bdd - mem_before_bdd  # RSS memory difference
    
    print(f"-> Số trạng thái đếm được từ BDD: {count}")
    print(f"-> Thời gian thực thi BDD: {bdd_time:.6f} seconds")
    print(f"-> Peak memory usage (BDD): {bdd_memory:.2f} MB")
    print(f"-> RSS memory difference: {bdd_rss_memory:.2f} MB")
    
    # --- PHẦN GIẢI MÃ VÀ IN TRẠNG THÁI TỪ BDD ---
    if bdd_res:
        print(f"-> Chi tiết các trạng thái giải mã từ BDD:")
        print(f"{'P1':<3} {'P2':<3} {'P3':<3} {'P4':<3} {'P5':<3}")
        print("-" * 30)

        bdd_states = set()
        place_map = {pid: i for i, pid in enumerate(pn.place_ids)}
        
        # Duyệt qua các satisfying assignments
        for assignment in bdd_res.satisfy_all():
            fixed = {}
            for var, val in assignment.items():
                if str(var) in place_map:
                    fixed[place_map[str(var)]] = 1 if val else 0
            
            missing = [i for i in range(len(pn.place_ids)) if i not in fixed]
            num_missing = len(missing)
            
            for i in range(1 << num_missing): 
                state = [0] * len(pn.place_ids)
                for idx, val in fixed.items():
                    state[idx] = val
                for j in range(num_missing):
                    state[missing[j]] = (i >> j) & 1
                bdd_states.add(tuple(state))
        
        for s in sorted(list(bdd_states), key=lambda x: (x[4], x[3], x[2], x[1])):
            print(f"{s[0]:<3} {s[1]:<3} {s[2]:<3} {s[3]:<3} {s[4]:<3}")

    if count == len(bfs_states):
        print(">> THÀNH CÔNG: BDD khớp với BFS/DFS.")
    else:
        print(f">> CẢNH BÁO: BDD ({count}) khác BFS ({len(bfs_states)}).")
    
    # ---------------------------------------------------------
    # SO SÁNH HIỆU SUẤT GIỮA PHƯƠNG PHÁP EXPLICIT VÀ SYMBOLIC
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[2,4] SO SÁNH HIỆU SUẤT: EXPLICIT (BFS) vs SYMBOLIC (BDD)")
    print(f"{'Metric':<25} {'Explicit (BFS)':<18} {'Symbolic (BDD)':<18}")
    print("-" * 65)
    
    # So sánh thời gian
    print(f"{'Thời gian (giây)':<25} {bfs_time:.6f}{'':>10} {bdd_time:.6f}{'':>10}")
    
    # So sánh peak memory
    print(f"{'Bộ nhớ đỉnh (MB)':<25} {bfs_memory:.2f}{'':>13} {bdd_memory:.2f}{'':>13}")
    
    # So sánh RSS memory
    print(f"{'Bộ nhớ RSS (MB)':<25} {bfs_rss_memory:.2f}{'':>13} {bdd_rss_memory:.2f}{'':>13}")
    
    # Phân tích chi tiết về hiệu suất
    print(f"\nSO SÁNH HIỆU SUẤT GIỮA PHƯƠNG PHÁP EXPLICIT VÀ SYMBOLIC:")
    print(f"   VỀ THỜI GIAN:")
    time_ratio = bdd_time / bfs_time
    if bfs_time < bdd_time:
        speedup_percent = ((bdd_time - bfs_time) / bdd_time) * 100
        print(f"      • Phương pháp explicit nhanh hơn: {time_ratio:.2f} lần")
        print(f"      • Tăng tốc: {speedup_percent:.1f}%")
    else:
        slowdown_percent = ((bfs_time - bdd_time) / bfs_time) * 100
        print(f"      • Phương pháp symbolic nhanh hơn: {bfs_time/bdd_time:.2f} lần")
        print(f"      • Tăng tốc: {slowdown_percent:.1f}%")
    
    print(f"   VỀ BỘ NHỚ:")
    print(f"      • Bộ nhớ đỉnh - Explicit: {bfs_memory:.2f} MB")
    print(f"      • Bộ nhớ đỉnh - Symbolic: {bdd_memory:.2f} MB")
    print(f"      • Bộ nhớ RSS - Explicit: {bfs_rss_memory:.2f} MB") 
    print(f"      • Bộ nhớ RSS - Symbolic: {bdd_rss_memory:.2f} MB")
    
    if bfs_memory <= bdd_memory:
        mem_diff = bdd_memory - bfs_memory
        print(f"      • Explicit tiết kiệm hơn: {mem_diff:.2f} MB bộ nhớ đỉnh")
    else:
        mem_diff = bfs_memory - bdd_memory
        print(f"      • Symbolic tiết kiệm hơn: {mem_diff:.2f} MB bộ nhớ đỉnh")
    
    print(f"   KẾT LUẬN VỀ SO SÁNH HIỆU SUẤT:")
    if count <= 10:
        print(f"      • Với không gian trạng thái nhỏ ({count} trạng thái):")
        print(f"        - Phương pháp explicit (BFS) hiệu quả hơn về thời gian")
        print(f"        - Overhead của symbolic representation không đáng kể")
    elif count <= 1000:
        print(f"      • Với không gian trạng thái trung bình ({count} trạng thái):")
        print(f"        - Cả hai phương pháp đều khả thi")
        print(f"        - Lựa chọn tùy thuộc vào yêu cầu cụ thể")
    else:
        print(f"      • Với không gian trạng thái lớn ({count} trạng thái):")
        print(f"        - Phương pháp symbolic (BDD) sẽ có lợi thế")
        print(f"        - Khả năng nén và tối ưu hóa cao hơn")
    
    print(f"      • Khuyến nghị: Dùng explicit cho < 100 trạng thái, symbolic cho > 1000 trạng thái")


    # ---------------------------------------------------------
    # TASK 5: DEADLOCK DETECTION
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[5] KIỂM TRA DEADLOCK")
    if bdd_res:
        deadlock_m = deadlock_reachable_marking_detector(pn, bdd_res)
        if deadlock_m:
            print(f"-> PHÁT HIỆN DEADLOCK tại marking: {deadlock_m}")
        else:
            print("-> Không phát hiện deadlock (Hệ thống chạy mãi mãi hoặc code chưa tìm ra).")
    else:
        print("-> Không có BDD để kiểm tra deadlock.")


    # ---------------------------------------------------------
    # TASK 6: OPTIMIZATION (TÌM ĐƯỜNG ĐẾN ĐÍCH)
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("[6] TỐI ƯU HÓA (MỤC TIÊU: TASK 5)")
    
    if bdd_res:
        # 1. Định nghĩa Vector trọng số c
        c = np.array([2, 3, 1, 4, 10]) 
        
        # 2. In thông tin Vector c
        print(f"-> Vector trọng số c: {c.tolist()}")
        print("   Giải thích ý nghĩa trọng số:")
        for i, weight in enumerate(c):
            if weight != 0:
                print(f"   - {pn.place_ids[i]} (index {i}): Trọng số = {weight}")
            else:
                # Uncomment dòng dưới nếu muốn in cả các số 0
                # print(f"   - {pn.place_ids[i]} (index {i}): Trọng số = {weight}")
                pass
        
        # 3. Chạy hàm tối ưu
        opt_m, opt_val = max_reachable_marking(pn.place_ids, bdd_res, c)
        
        if opt_m:
            print(f"\n-> Marking tối ưu tìm được: {opt_m}")
            print(f"-> Giá trị mục tiêu (c * M): {opt_val}")
            
            if opt_val > 0:
                print(">> KẾT LUẬN: TASK 5 KHẢ ĐẠT (REACHABLE)!")
            else:
                print(">> KẾT LUẬN: KHÔNG THỂ ĐẾN TASK 5.")
        else:
            print("-> Không tìm thấy giải pháp tối ưu.")

if __name__ == "__main__":
    test_main()