"""
Optimal Meeting Point Problem Solution

Given an MxN grid where:
- 0 = empty land (candidate meeting point)
- 1 = house
- any other value (e.g., 2) = obstacle (cannot be used or traversed)

Compute the minimum total Manhattan distance from all houses to a single empty cell
that is reachable from every house. Return -1 if no valid meeting cell exists.
"""

from typing import List, Tuple, Set
from collections import deque


def min_total_distance(grid: List[List[int]]) -> int:
    """
    Find the minimum total Manhattan distance from all houses to an optimal meeting point.
    
    Args:
        grid: MxN grid where 0=empty, 1=house, other=obstacle
        
    Returns:
        Minimum total Manhattan distance, or -1 if no valid meeting point exists
    """
    if not grid or not grid[0]:
        return -1
    
    m, n = len(grid), len(grid[0])
    
    houses = []
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                houses.append((i, j))
    
    if not houses:
        return -1
    
    has_obstacles = any(grid[i][j] not in (0, 1) for i in range(m) for j in range(n))
    
    if not has_obstacles:
        return _fast_total_distance(grid, houses)
    else:
        return _bfs_total_distance(grid, houses)


def _fast_total_distance(grid: List[List[int]], houses: List[Tuple[int, int]]) -> int:
    """
    Fast O(M*N) algorithm for grids with only 0s and 1s (no obstacles).
    Uses separable Manhattan distance computation.
    
    Args:
        grid: MxN grid with only 0s and 1s
        houses: List of house positions
        
    Returns:
        Minimum total Manhattan distance
    """
    m, n = len(grid), len(grid[0])
    
    min_distance = float('inf')
    
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 0:  # Empty cell
                total_dist = sum(abs(house_row - i) + abs(house_col - j) 
                               for house_row, house_col in houses)
                min_distance = min(min_distance, total_dist)
    
    return min_distance if min_distance != float('inf') else -1


def _bfs_total_distance(grid: List[List[int]], houses: List[Tuple[int, int]]) -> int:
    """
    BFS-based algorithm for grids with obstacles.
    Uses visit-id technique to avoid re-allocating visited arrays.
    
    Args:
        grid: MxN grid that may contain obstacles
        houses: List of house positions
        
    Returns:
        Minimum total Manhattan distance, or -1 if no valid meeting point exists
    """
    m, n = len(grid), len(grid[0])
    num_houses = len(houses)
    
    total_distances = [[0] * n for _ in range(m)]
    reach_count = [[0] * n for _ in range(m)]
    
    visit_id = [[0] * n for _ in range(m)]
    current_visit_id = 1
    
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    for house_idx, (start_row, start_col) in enumerate(houses):
        queue = deque([(start_row, start_col, 0)])
        visit_id[start_row][start_col] = current_visit_id
        
        while queue:
            row, col, dist = queue.popleft()
            
            if grid[row][col] == 0:
                total_distances[row][col] += dist
                reach_count[row][col] += 1
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                if (0 <= new_row < m and 0 <= new_col < n and
                    grid[new_row][new_col] in (0, 1) and  # Empty or house, not obstacle
                    visit_id[new_row][new_col] != current_visit_id):
                    
                    visit_id[new_row][new_col] = current_visit_id
                    queue.append((new_row, new_col, dist + 1))
        
        current_visit_id += 1
    
    min_distance = float('inf')
    
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 0 and reach_count[i][j] == num_houses:
                min_distance = min(min_distance, total_distances[i][j])
    
    return min_distance if min_distance != float('inf') else -1
