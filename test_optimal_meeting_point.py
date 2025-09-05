"""
Unit tests for optimal meeting point problem solution.
"""

import pytest
from optimal_meeting_point import min_total_distance, _fast_total_distance, _bfs_total_distance


class TestOptimalMeetingPoint:
    
    def test_example_case(self):
        """Test the provided example case."""
        grid = [
            [1, 0, 2, 0, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0]
        ]
        result = min_total_distance(grid)
        assert result == 7  # The original expected value was incorrect (previously 6), but the correct value is 7.
                           # This is verified by manually summing the Manhattan distances from all houses (cells with 1)
                           # to the optimal empty cell (row 1, col 2): (0,0)->(1,2)=3, (0,4)->(1,2)=3, (2,2)->(1,2)=1; total=7.
    
    def test_empty_grid(self):
        """Test empty grid returns -1."""
        assert min_total_distance([]) == -1
        assert min_total_distance([[]]) == -1
    
    def test_no_houses(self):
        """Test grid with no houses returns -1."""
        grid = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        assert min_total_distance(grid) == -1
    
    def test_no_empty_land(self):
        """Test grid with houses but no empty land returns -1."""
        grid = [
            [1, 2, 1],
            [2, 2, 2],
            [1, 2, 1]
        ]
        assert min_total_distance(grid) == -1
    
    def test_single_house(self):
        """Test grid with single house."""
        grid = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ]
        result = min_total_distance(grid)
        assert result == 1  # Minimum distance to adjacent empty cell
    
    def test_unreachable_houses(self):
        """Test case where some houses are unreachable from empty land."""
        grid = [
            [1, 2, 0],
            [2, 2, 0],
            [1, 2, 0]
        ]
        assert min_total_distance(grid) == -1
    
    def test_fast_path_simple(self):
        """Test fast path with simple 0/1 grid."""
        grid = [
            [1, 0, 1],
            [0, 0, 0],
            [1, 0, 1]
        ]
        result = min_total_distance(grid)
        assert result >= 0  # Should find a valid solution
    
    def test_large_grid_performance(self):
        """Test with larger grid to verify performance."""
        grid = [[0] * 20 for _ in range(20)]
        grid[0][0] = 1
        grid[0][19] = 1
        grid[19][0] = 1
        grid[19][19] = 1
        
        result = min_total_distance(grid)
        assert result >= 0
    
    def test_consistency_fast_vs_bfs(self):
        """Test that fast path and BFS give same results for 0/1 grids."""
        grid = [
            [1, 0, 0, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [1, 0, 0, 1]
        ]
        
        houses = [(0, 0), (0, 3), (3, 0), (3, 3)]
        
        fast_result = _fast_total_distance(grid, houses)
        bfs_result = _bfs_total_distance(grid, houses)
        
        assert fast_result == bfs_result
    
    def test_obstacles_block_path(self):
        """Test that obstacles properly block paths in BFS."""
        grid = [
            [1, 0, 2, 0, 1],
            [0, 2, 2, 2, 0],
            [0, 0, 0, 0, 0]
        ]
        
        result = min_total_distance(grid)
        assert result >= 0
    
    def test_multiple_optimal_solutions(self):
        """Test case with multiple equally optimal solutions."""
        grid = [
            [1, 0, 0, 1],
            [0, 0, 0, 0]
        ]
        
        result = min_total_distance(grid)
        assert result >= 0
    
    def test_edge_case_single_empty_cell(self):
        """Test with only one empty cell available."""
        grid = [
            [1, 2, 1],
            [2, 0, 2],
            [1, 2, 1]
        ]
        
        result = min_total_distance(grid)
        assert result == -1
    
    def test_linear_arrangement(self):
        """Test houses arranged in a line."""
        grid = [
            [1, 0, 1, 0, 1]
        ]
        
        result = min_total_distance(grid)
        assert result == 5
    
    def test_internal_helper_functions(self):
        """Test internal helper functions directly."""
        grid = [
            [1, 0, 1],
            [0, 0, 0],
            [1, 0, 1]
        ]
        houses = [(0, 0), (0, 2), (2, 0), (2, 2)]
        
        fast_result = _fast_total_distance(grid, houses)
        assert fast_result >= 0
        
        bfs_result = _bfs_total_distance(grid, houses)
        assert bfs_result >= 0
        
        assert fast_result == bfs_result


if __name__ == "__main__":
    pytest.main([__file__])
