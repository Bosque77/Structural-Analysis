import numpy as np
import matplotlib.pyplot as plt

def compute_response_1DOF_MDOF(m, c, k, Y0_omega, f_range):
    """
    Compute the displacement and acceleration response of a 1DOF system using the MDOF approach.
    
    Parameters:
        m (float): Mass.
        c (float): Damping coefficient.
        k (float): Stiffness.
        Y0_omega (float): Base acceleration in frequency domain.
        f_range (array-like): Frequency range over which to compute the response.
        
    Returns:
        (array-like, array-like): Displacement and acceleration responses in the frequency domain.
    """
    u_omega_mdof = []  # Displacement response in frequency domain
    a_omega_mdof = []  # Acceleration response in frequency domain

    for f in f_range:
        omega = 2 * np.pi * f
        # Compute the impedance for 1DOF system
        Z = k - m * omega**2 + 1j * omega * c
        # Compute the displacement response
        u = (-m * Y0_omega) / Z
        u_omega_mdof.append(u)
        # Compute the acceleration response
        a = -omega**2 * u
        a_omega_mdof.append(a)

    return u_omega_mdof, a_omega_mdof

# System parameters
m = 1.0/386.089  # lbf*s^2/in
k = 100.0  # lbf/in
zeta = 0.03  # Damping ratio
c = 2 * zeta * np.sqrt(m * k)  # Damping coefficient based on damping ratio
Y0_omega = 386.089  # Base excitation acceleration (1G in frequency domain)


f_range = np.linspace(0.1, 300, 500)  # Varying the frequency in Hz

# Compute the response using the MDOF approach
u_omega_mdof, a_omega_mdof = compute_response_1DOF_MDOF(m, c, k, Y0_omega, f_range)

# Convert acceleration from in/s^2 to G's for plotting
a_omega_G_mdof = [a/386.089 for a in a_omega_mdof]

# Plotting
plt.figure(figsize=(15, 6))

# Displacement plot
plt.subplot(1, 2, 1)
plt.plot(f_range, np.abs(u_omega_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Displacement (in)')
plt.title('Displacement Response vs. Frequency (MDOF Approach)')
plt.grid(True)

# Acceleration plot
plt.subplot(1, 2, 2)
plt.plot(f_range, np.abs(a_omega_G_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Acceleration (G)')
plt.title('Acceleration Response vs. Frequency (MDOF Approach)')
plt.grid(True)

plt.tight_layout()
plt.show()
