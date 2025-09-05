"""
Benchmark runner for optimal meeting point algorithms.
"""

import time
import random
from typing import List, Tuple
import statistics
from optimal_meeting_point import min_total_distance, _fast_total_distance, _bfs_total_distance


def generate_test_grid(rows: int, cols: int, house_density: float = 0.1, 
                      obstacle_density: float = 0.0, seed: int = 42) -> List[List[int]]:
    """
    Generate a test grid with specified dimensions and densities.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        house_density: Fraction of cells that should be houses (0-1)
        obstacle_density: Fraction of cells that should be obstacles (0-1)
        seed: Random seed for reproducibility
        
    Returns:
        Generated grid
    """
    random.seed(seed)
    
    grid = [[0] * cols for _ in range(rows)]
    total_cells = rows * cols
    
    num_houses = int(total_cells * house_density)
    house_positions = random.sample([(i, j) for i in range(rows) for j in range(cols)], 
                                   num_houses)
    
    for i, j in house_positions:
        grid[i][j] = 1
    
    if obstacle_density > 0:
        available_positions = [(i, j) for i in range(rows) for j in range(cols) 
                              if grid[i][j] == 0]
        num_obstacles = int(len(available_positions) * obstacle_density)
        
        if num_obstacles > 0:
            obstacle_positions = random.sample(available_positions, 
                                             min(num_obstacles, len(available_positions)))
            for i, j in obstacle_positions:
                grid[i][j] = 2
    
    return grid


def benchmark_algorithm(grid: List[List[int]], algorithm_name: str, 
                       num_runs: int = 5) -> Tuple[float, float, int]:
    """
    Benchmark a specific algorithm on a grid.
    
    Args:
        grid: Test grid
        algorithm_name: Name of algorithm to test
        num_runs: Number of runs for averaging
        
    Returns:
        Tuple of (mean_time, std_time, result)
    """
    times = []
    result = None
    
    for _ in range(num_runs):
        start_time = time.perf_counter()
        
        if algorithm_name == "main":
            result = min_total_distance(grid)
        elif algorithm_name == "fast":
            houses = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) 
                     if grid[i][j] == 1]
            if houses:
                result = _fast_total_distance(grid, houses)
            else:
                result = -1
        elif algorithm_name == "bfs":
            houses = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) 
                     if grid[i][j] == 1]
            if houses:
                result = _bfs_total_distance(grid, houses)
            else:
                result = -1
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    mean_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0.0
    
    return mean_time, std_time, result


def run_benchmarks():
    """Run comprehensive benchmarks and print results."""
    print("=== Optimal Meeting Point Benchmarks ===\n")
    
    test_configs = [
        {"name": "Small Dense", "rows": 20, "cols": 20, "house_density": 0.2, "obstacle_density": 0.0},
        {"name": "Small Sparse", "rows": 20, "cols": 20, "house_density": 0.05, "obstacle_density": 0.0},
        {"name": "Medium Dense", "rows": 50, "cols": 50, "house_density": 0.1, "obstacle_density": 0.0},
        {"name": "Medium with Obstacles", "rows": 50, "cols": 50, "house_density": 0.1, "obstacle_density": 0.1},
        {"name": "Large Sparse", "rows": 100, "cols": 100, "house_density": 0.02, "obstacle_density": 0.0},
        {"name": "Large with Obstacles", "rows": 100, "cols": 100, "house_density": 0.05, "obstacle_density": 0.05},
    ]
    
    results = []
    
    for config in test_configs:
        print(f"Testing: {config['name']} ({config['rows']}x{config['cols']})")
        print(f"House density: {config['house_density']:.1%}, Obstacle density: {config['obstacle_density']:.1%}")
        
        grid = generate_test_grid(
            config['rows'], config['cols'], 
            config['house_density'], config['obstacle_density']
        )
        
        houses = sum(1 for row in grid for cell in row if cell == 1)
        obstacles = sum(1 for row in grid for cell in row if cell == 2)
        empty = sum(1 for row in grid for cell in row if cell == 0)
        
        print(f"Grid composition: {houses} houses, {obstacles} obstacles, {empty} empty")
        
        mean_time, std_time, result = benchmark_algorithm(grid, "main", num_runs=5)
        
        config_result = {
            "name": config['name'],
            "size": f"{config['rows']}x{config['cols']}",
            "houses": houses,
            "obstacles": obstacles,
            "main_time": mean_time,
            "main_std": std_time,
            "result": result
        }
        
        print(f"Main algorithm: {mean_time:.4f}s ± {std_time:.4f}s (result: {result})")
        
        if obstacles == 0 and houses > 0:
            fast_mean, fast_std, fast_result = benchmark_algorithm(grid, "fast", num_runs=5)
            bfs_mean, bfs_std, bfs_result = benchmark_algorithm(grid, "bfs", num_runs=5)
            
            config_result.update({
                "fast_time": fast_mean,
                "fast_std": fast_std,
                "bfs_time": bfs_mean,
                "bfs_std": bfs_std,
                "fast_result": fast_result,
                "bfs_result": bfs_result
            })
            
            print(f"Fast algorithm: {fast_mean:.4f}s ± {fast_std:.4f}s (result: {fast_result})")
            print(f"BFS algorithm:  {bfs_mean:.4f}s ± {bfs_std:.4f}s (result: {bfs_result})")
            
            if fast_result == bfs_result:
                print("✓ Fast and BFS results match")
            else:
                print("✗ Fast and BFS results differ!")
            
            if fast_mean > 0:
                speedup = bfs_mean / fast_mean
                print(f"Fast algorithm speedup: {speedup:.2f}x")
        
        results.append(config_result)
        print("-" * 60)
    
    print("\n=== Summary ===")
    print(f"{'Test Case':<20} {'Size':<10} {'Houses':<8} {'Time (s)':<12} {'Result':<8}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['name']:<20} {result['size']:<10} {result['houses']:<8} "
              f"{result['main_time']:.4f}±{result['main_std']:.3f} {result['result']:<8}")
    
    return results


if __name__ == "__main__":
    run_benchmarks()
