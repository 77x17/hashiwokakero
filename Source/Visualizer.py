import matplotlib.pyplot as plt
import os
import re

# --- CẤU HÌNH ---
OUTPUT_DIR = "Outputs"
BENCHMARK_DIR = "Benchmark"  # Thư mục chứa ảnh kết quả
TIMEOUT_MS = 30000           # Giới hạn 30 giây

# Tạo thư mục Benchmark nếu chưa có
os.makedirs(BENCHMARK_DIR, exist_ok=True)

ALGORITHMS = ["BruteForce", "AStar", "Backtracking", "PySAT"]

# Style: PySAT màu xanh lá, BruteForce màu đỏ
STYLES = {
    "BruteForce":   {"color": "red",    "marker": "x", "linestyle": "--"},
    "AStar":        {"color": "orange", "marker": "s", "linestyle": "-."},
    "Backtracking": {"color": "blue",   "marker": "^", "linestyle": "-"},
    "PySAT":        {"color": "green",  "marker": "o", "linestyle": "-"}
}

def get_time_from_file(filepath):
    """Đọc file lấy time. Trả về TIMEOUT_MS nếu file lỗi hoặc TLE"""
    if not os.path.exists(filepath):
        return TIMEOUT_MS
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        if "STATUS: TIMEOUT" in content or "STATUS: FAILED" in content:
            return TIMEOUT_MS
        
        match = re.search(r"Time \(ms\)\s*:\s*([\d\.]+)", content)
        if match:
            t = float(match.group(1))
            # Nếu thời gian > 30000 thì gán bằng 30000 để vẽ đường thẳng
            return min(t, TIMEOUT_MS)
            
    return TIMEOUT_MS

def draw_chart(input_indices, title, filename):
    """Hàm vẽ biểu đồ"""
    plt.figure(figsize=(10, 6))
    
    # Duyệt từng thuật toán
    for algo in ALGORITHMS:
        times = []
        for i in input_indices:
            file_name = f"output-{i:02d}.txt"
            file_path = os.path.join(OUTPUT_DIR, algo, file_name)
            times.append(get_time_from_file(file_path))
        
        # Vẽ đường
        style = STYLES[algo]
        plt.plot(input_indices, times, 
                 label=algo, 
                 color=style["color"], 
                 marker=style["marker"], 
                 linestyle=style["linestyle"],
                 linewidth=2, markersize=8)

    # --- CẤU HÌNH TRỤC ---
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Input Test Case", fontsize=12)
    plt.ylabel("Execution Time (ms)", fontsize=12)
    
    # Set trục Y từ 0 đến 32000 (để dư ra 1 chút trên đầu cho thoáng)
    plt.ylim(-500, 32000) 
    
    # Vẽ đường Timeout màu đỏ đậm ngang mức 30000
    plt.axhline(y=TIMEOUT_MS, color='darkred', linestyle='-', linewidth=1.5, label="Timeout Limit (30s)")
    
    # Cấu hình trục X chỉ hiện các số nguyên có trong input_indices
    plt.xticks(input_indices)
    
    # Lưới (Grid)
    plt.grid(True, which="both", ls="--", alpha=0.5)
    
    # Chú thích (Legend)
    plt.legend(loc="upper left")
    
    plt.tight_layout()
    
    # Lưu file vào thư mục Benchmark
    save_path = os.path.join(BENCHMARK_DIR, filename)
    plt.savefig(save_path, dpi=300)
    print(f"✅ Đã lưu biểu đồ tại: {save_path}")
    plt.close()

if __name__ == "__main__":
    print(f"--- Đang vẽ biểu đồ vào thư mục '{BENCHMARK_DIR}' ---")
    
    # 1. Biểu đồ 7x7 (Input 1, 2, 3)
    draw_chart([1, 2, 3], "Benchmark: Small Puzzles (7x7)", "chart_01_small_7x7.png")
    
    # 2. Biểu đồ 10x10 (Input 4, 5, 6)
    draw_chart([4, 5, 6], "Benchmark: Medium Puzzles (10x10)", "chart_02_medium_10x10.png")
    
    # 3. Biểu đồ 15x15 (Input 7, 8, 9, 10)
    draw_chart([7, 8, 9, 10], "Benchmark: Large Puzzles (15x15)", "chart_03_large_15x15.png")
    
    # 4. Biểu đồ TỔNG HỢP (Input 1 -> 10)
    draw_chart(range(1, 11), "Benchmark: Overall Performance (All Inputs)", "chart_04_overall.png")