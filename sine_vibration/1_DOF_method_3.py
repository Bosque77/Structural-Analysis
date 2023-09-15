import numpy as np
import matplotlib.pyplot as plt

def compute_acceleration_1DOF_in_G(m, k, zeta, Y0_omega, f_range):
    """
    Compute the acceleration of a mass in a 1DOF system over a range of frequencies using the MDOF approach.
    Return the acceleration in G's.
    
    Parameters:
        m (float): Mass in lbf*s^2/in.
        k (float): Stiffness in lbf/in.
        zeta (float): Damping ratio.
        Y0_omega (float): Base acceleration amplitude at frequency omega (constant at 1G for all frequencies).
        f_range (array-like): Array of frequencies (Hz) for which to compute the acceleration.
    
    Returns:
        numpy.ndarray: Array representing the acceleration of the mass over the frequency range in G's.
    """

    disp_value_G = []
    accel_values_G = []
    
    for f in f_range:
        omega = 2 * np.pi * f

        # Calculate the damping coefficient based on damping ratio
        c = 2 * zeta * np.sqrt(m * k)
        
        # Dynamic stiffness
        Z = k - omega**2 * m + 1j * omega * c
        
        # Force due to constant base acceleration (1G at all frequencies)
        F = k
        
        # Displacement in frequency domain
        X_omega = F / Z
        
        # Acceleration in frequency domain in G's
        X_ddot_omega_G = (-omega**2 * X_omega) / 386.089
        
        # Append to list
        disp_value_G.append(np.abs(X_omega))
        accel_values_G.append(np.abs(X_ddot_omega_G))

    return (np.array(disp_value_G),np.array(accel_values_G))


# Example usage for a 1-DOF system with a damping ratio of 0.01:
m = 1.0/386.089  # lbf*s^2/in
k = 100.0  # Stiffness in lbf/in
zeta = 0.03  # Damping ratio
Y0_omega = 1.0  # Base acceleration amplitude at frequency omega in g's

# Define the frequency range (angular frequencies) over which to compute the amplification factor
f_range = np.linspace(0.1, 300, 500)  # Varying the frequency in Hz

# Natural frequency
f_natural = np.sqrt(k/m) / (2 * np.pi)

# Compute the acceleration in G's for the 1DOF system over the specified frequency range with constant 1G acceleration
disp_values_G, accel_values_G = compute_acceleration_1DOF_in_G(m, k, zeta, Y0_omega, f_range)



# Plotting the displacement in G's as a function of frequency
plt.figure(figsize=(10, 6))
plt.plot(f_range, disp_values_G, label='Displacement', color='purple')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Acceleration (G)')
plt.title('Acceleration of a 1DOF System vs. Frequency (Constant 1G Base Acceleration)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


# Plotting the acceleration in G's as a function of frequency
plt.figure(figsize=(10, 6))
plt.plot(f_range, accel_values_G, label='Acceleration', color='purple')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Acceleration (G)')
plt.title('Acceleration of a 1DOF System vs. Frequency (Constant 1G Base Acceleration)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

f_natural
