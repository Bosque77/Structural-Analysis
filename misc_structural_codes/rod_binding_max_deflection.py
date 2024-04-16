


import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

def find_theta(D_large, D_small, h_hole, x_target=0):
    """
    Calculate the angle theta in degrees for the given parameters such that:
        x = D_large - h_hole * tan(theta) - D_small / cos(theta)
    matches the x_target (default is 0).

    Parameters:
    - D_large: The larger diameter.
    - D_small: The smaller diameter.
    - h_hole: The height of the hole.
    - x_target: The target x value, default is 0.

    Returns:
    - The angle theta in degrees that satisfies the equation.
    """

    # Define the equation whose root we are looking for
    def equation(theta):
        return D_large - h_hole * np.tan(theta) - D_small / np.cos(theta) - x_target

    # Initial guess for theta
    theta_initial = np.pi / 4  # Midpoint of 0 and pi/2, good starting point

    # Use fsolve to find the root, handling cases where the solution might fail
    try:
        theta_solution = fsolve(equation, theta_initial)
        # Convert to degrees and return
        theta_degrees = np.rad2deg(theta_solution)
        return theta_degrees[0]  # Return the first solution if multiple are found
    except Exception as e:
        print("An error occurred:", e)
        return None




if __name__ == "__main__":
    D_large = 0.6
    D_small = 0.46
    h_hole = 0.25
    theta = find_theta(D_large, D_small, h_hole)
    print(f"Theta: {theta} degrees")

    deflection_height = 0.5

    # Calculate the deflection
    deflection_at_height = deflection_height * np.tan(np.deg2rad(theta))
    print(f"Deflection at height {deflection_height} is {deflection_at_height}")




