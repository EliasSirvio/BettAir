import numpy as np

def linearly_independent(triangle: np.ndarray) -> bool:
    """
    Function to confirm that a matrix of three 2D vertices indeed makes a triangle.
    That is, that the three vertices are not on the same line, or in the same point.

    Parameters:
        triangle : array-like, shape (3, 2)
            The vertices of the triangle. 

    Returns:
        bool:
            True if the vertices make a triangle, False if not.   
    """
    assert triangle.shape == (3,2), f"Triangle should have shape (3,2), but had shape {triangle.shape}"
    # Find vectors
    v1 = triangle[1]-triangle[0]
    v2 = triangle[2]-triangle[0]

    determinant = np.linalg.det(np.array([v1, v2]))
    return determinant # True if non-zero

def barycentric_coordinates(triangle: np.ndarray, point: tuple[int, int]):
        """
        Calculate the barycentric coordinates of a point with respect to a triangle.
        
        Parameters:
            triangle : array-like, shape (3, 2)
                The vertices of the triangle.
            point : array-like, shape (2,)
                The point for which to calculate the barycentric coordinates.
        
        Returns:
        array, shape (3,)
            The barycentric coordinates of the point.
        """
        assert triangle.shape == (3,2), f"Triangle had wrong shape! It should have shape (3,2) but had shape {triangle.shape}."

        T = np.vstack((triangle.T, np.ones((1, 3))))
        v = np.append(point, 1)
        try:
            return np.linalg.solve(T, v)
        except np.linalg.LinAlgError:
            raise ValueError("Triangle vertices are not linearly independent!")