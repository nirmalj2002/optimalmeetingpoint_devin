"""
Benchmark plotting for optimal meeting point algorithms.
"""

import time
import random
from typing import List, Dict, Any
import statistics

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Plotting will be skipped.")

from .benchmarks_run import generate_test_grid, benchmark_algorithm


def run_plotting_benchmarks() -> List[Dict[str, Any]]:
    """
    Run benchmarks specifically designed for plotting.
    
    Returns:
        List of benchmark results
    """
    print("=== Running Plotting Benchmarks ===\n")
    
    plot_configs = [
        {"name": "Tiny", "rows": 10, "cols": 10, "house_density": 0.15},
        {"name": "Small", "rows": 25, "cols": 25, "house_density": 0.1},
        {"name": "Medium", "rows": 50, "cols": 50, "house_density": 0.08},
        {"name": "Large", "rows": 75, "cols": 75, "house_density": 0.06},
        {"name": "XLarge", "rows": 100, "cols": 100, "house_density": 0.04},
        {"name": "XXLarge", "rows": 120, "cols": 120, "house_density": 0.03},
    ]
    
    results = []
    
    for config in plot_configs:
        print(f"Benchmarking: {config['name']} ({config['rows']}x{config['cols']})")
        
        grid_no_obstacles = generate_test_grid(
            config['rows'], config['cols'], 
            config['house_density'], 0.0, seed=42
        )
        
        grid_with_obstacles = generate_test_grid(
            config['rows'], config['cols'], 
            config['house_density'], 0.05, seed=42
        )
        
        main_time, main_std, main_result = benchmark_algorithm(
            grid_no_obstacles, "main", num_runs=10
        )
        
        fast_time, fast_std, fast_result = benchmark_algorithm(
            grid_no_obstacles, "fast", num_runs=10
        )
        
        bfs_time, bfs_std, bfs_result = benchmark_algorithm(
            grid_no_obstacles, "bfs", num_runs=10
        )
        
        main_obstacles_time, main_obstacles_std, main_obstacles_result = benchmark_algorithm(
            grid_with_obstacles, "main", num_runs=10
        )
        
        result_entry = {
            "name": config['name'],
            "size": config['rows'] * config['cols'],
            "rows": config['rows'],
            "cols": config['cols'],
            "main_time": main_time,
            "main_std": main_std,
            "fast_time": fast_time,
            "fast_std": fast_std,
            "bfs_time": bfs_time,
            "bfs_std": bfs_std,
            "main_obstacles_time": main_obstacles_time,
            "main_obstacles_std": main_obstacles_std,
            "main_result": main_result,
            "fast_result": fast_result,
            "bfs_result": bfs_result,
            "main_obstacles_result": main_obstacles_result
        }
        
        results.append(result_entry)
        
        print(f"  Main (no obstacles): {main_time:.4f}s ± {main_std:.4f}s")
        print(f"  Fast path: {fast_time:.4f}s ± {fast_std:.4f}s")
        print(f"  BFS path: {bfs_time:.4f}s ± {bfs_std:.4f}s")
        print(f"  Main (with obstacles): {main_obstacles_time:.4f}s ± {main_obstacles_std:.4f}s")
        
        if fast_result == bfs_result == main_result:
            print("  ✓ All algorithms agree on result")
        else:
            print("  ✗ Algorithm results differ!")
    
    return results


def create_performance_plots(results: List[Dict[str, Any]]):
    """
    Create performance comparison plots.
    
    Args:
        results: Benchmark results from run_plotting_benchmarks
    """
    if not HAS_MATPLOTLIB:
        print("Skipping plots - matplotlib not available")
        return
    
    names = [r['name'] for r in results]
    sizes = [r['size'] for r in results]
    main_times = [r['main_time'] for r in results]
    fast_times = [r['fast_time'] for r in results]
    bfs_times = [r['bfs_time'] for r in results]
    main_obstacles_times = [r['main_obstacles_time'] for r in results]
    
    main_stds = [r['main_std'] for r in results]
    fast_stds = [r['fast_std'] for r in results]
    bfs_stds = [r['bfs_std'] for r in results]
    main_obstacles_stds = [r['main_obstacles_std'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    x_pos = range(len(names))
    width = 0.2
    
    ax1.bar([x - 1.5*width for x in x_pos], main_times, width, 
            yerr=main_stds, label='Main (Auto)', alpha=0.8, capsize=3)
    ax1.bar([x - 0.5*width for x in x_pos], fast_times, width, 
            yerr=fast_stds, label='Fast Path', alpha=0.8, capsize=3)
    ax1.bar([x + 0.5*width for x in x_pos], bfs_times, width, 
            yerr=bfs_stds, label='BFS Path', alpha=0.8, capsize=3)
    ax1.bar([x + 1.5*width for x in x_pos], main_obstacles_times, width, 
            yerr=main_obstacles_stds, label='Main (Obstacles)', alpha=0.8, capsize=3)
    
    ax1.set_xlabel('Grid Size')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Algorithm Performance Comparison')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(names, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    speedup_ratios = [bfs_times[i] / fast_times[i] if fast_times[i] > 0 else 1 
                     for i in range(len(results))]
    
    ax2.bar(x_pos, speedup_ratios, alpha=0.7, color='green')
    ax2.set_xlabel('Grid Size')
    ax2.set_ylabel('Speedup Ratio (BFS/Fast)')
    ax2.set_title('Fast Path Speedup over BFS')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(names, rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='No speedup')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('benchmarks/performance_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved performance comparison chart: benchmarks/performance_comparison.png")
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    ax.plot(sizes, main_times, 'o-', label='Main (Auto)', linewidth=2, markersize=6)
    ax.plot(sizes, fast_times, 's-', label='Fast Path', linewidth=2, markersize=6)
    ax.plot(sizes, bfs_times, '^-', label='BFS Path', linewidth=2, markersize=6)
    ax.plot(sizes, main_obstacles_times, 'd-', label='Main (Obstacles)', linewidth=2, markersize=6)
    
    ax.set_xlabel('Grid Size (cells)')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Algorithm Scaling with Grid Size')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('benchmarks/scaling_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved scaling analysis chart: benchmarks/scaling_analysis.png")
    
    plt.close('all')


def print_numerical_summary(results: List[Dict[str, Any]]):
    """
    Print numerical summary of benchmark results.
    
    Args:
        results: Benchmark results
    """
    print("\n=== Numerical Summary ===")
    print(f"{'Grid':<10} {'Size':<8} {'Main':<12} {'Fast':<12} {'BFS':<12} {'Speedup':<8}")
    print("-" * 80)
    
    total_speedup = 0
    valid_speedups = 0
    
    for result in results:
        speedup = result['bfs_time'] / result['fast_time'] if result['fast_time'] > 0 else 1.0
        if speedup > 1:
            total_speedup += speedup
            valid_speedups += 1
        
        print(f"{result['name']:<10} {result['size']:<8} "
              f"{result['main_time']:.4f}s     {result['fast_time']:.4f}s     "
              f"{result['bfs_time']:.4f}s     {speedup:.2f}x")
    
    if valid_speedups > 0:
        avg_speedup = total_speedup / valid_speedups
        print(f"\nAverage Fast Path Speedup: {avg_speedup:.2f}x")
    
    largest = max(results, key=lambda x: x['size'])
    print(f"Largest grid tested: {largest['rows']}x{largest['cols']} "
          f"({largest['size']} cells) in {largest['main_time']:.4f}s")


def main():
    """Main function to run plotting benchmarks."""
    print("Starting benchmark plotting suite...")
    
    results = run_plotting_benchmarks()
    
    if HAS_MATPLOTLIB:
        create_performance_plots(results)
    
    print_numerical_summary(results)
    
    print("\n=== Benchmark Complete ===")
    if HAS_MATPLOTLIB:
        print("Charts saved to:")
        print("  - benchmarks/performance_comparison.png")
        print("  - benchmarks/scaling_analysis.png")
    else:
        print("Install matplotlib to generate charts: pip install matplotlib")


if __name__ == "__main__":
    main()
