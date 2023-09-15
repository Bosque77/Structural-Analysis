import numpy as np
import matplotlib.pyplot as plt

def compute_response_2DOF_MDOF(m1, m2, c1, c2, k1, k2, Y0_omega, f_range):
    """
    Compute the displacement and acceleration response of a 2DOF system using the MDOF approach.
    
    Parameters:
        m1, m2 (float): Masses.
        c1, c2 (float): Damping coefficients.
        k1, k2 (float): Stiffnesses.
        Y0_omega (float): Base acceleration in frequency domain.
        f_range (array-like): Frequency range over which to compute the response.
        
    Returns:
        tuple: Displacement and acceleration responses in the frequency domain for both masses.
    """
    u1_omega_mdof = []  # Displacement response of mass 1 in frequency domain
    u2_omega_mdof = []  # Displacement response of mass 2 in frequency domain
    
    a1_omega_mdof = []  # Acceleration response of mass 1 in frequency domain
    a2_omega_mdof = []  # Acceleration response of mass 2 in frequency domain

    for f in f_range:
        omega = 2 * np.pi * f
        # Forming the impedance matrix
        Z = np.array([[(-omega**2)*m1 + 1j*omega*c1 + k1 + k2, -k2],
                      [-k2, (-omega**2)*m2 + 1j*omega*c2 + k2]])
        
        # Force vector
        F = np.array([[-m1 * Y0_omega], [0]])
        
        # Solve for the displacements in frequency domain
        U = np.linalg.solve(Z, F)
        
        # Append to the lists
        u1_omega_mdof.append(U[0][0])
        u2_omega_mdof.append(U[1][0])
        
        # Compute the accelerations
        a1_omega_mdof.append(-omega**2 * U[0][0])
        a2_omega_mdof.append(-omega**2 * U[1][0])

    return u1_omega_mdof, u2_omega_mdof, a1_omega_mdof, a2_omega_mdof

# System parameters for 2DOF system
m1 = 1000/386.089  # lbf*s^2/in
m2 = 1.0/386.089  # lbf*s^2/in
k1 = 1000000.0  # lbf/in
k2 = 100.0  # lbf/in
zeta1 = 0.03
zeta2 = 0.03
c1 = 2 * zeta1 * np.sqrt(m1 * k1)  # Damping coefficient for mass 1
c2 = 2 * zeta2 * np.sqrt(m2 * k2)  # Damping coefficient for mass 2

Y0_omega = 386.089  # Base excitation acceleration (1G in frequency domain)

f_range = np.linspace(0.1, 300, 500)  # Varying the frequency in Hz

# Compute the responses using the MDOF approach
u1_omega_mdof, u2_omega_mdof, a1_omega_mdof, a2_omega_mdof = compute_response_2DOF_MDOF(m1, m2, c1, c2, k1, k2, Y0_omega, f_range)

# Convert accelerations from in/s^2 to G's for plotting
a1_omega_G_mdof = [a/386.089 for a in a1_omega_mdof]
a2_omega_G_mdof = [a/386.089 for a in a2_omega_mdof]

# Plotting
plt.figure(figsize=(15, 12))

# Displacement plot for mass 1
plt.subplot(2, 2, 1)
plt.plot(f_range, np.abs(u1_omega_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Displacement (in)')
plt.title('Displacement Response of Mass 1 vs. Frequency')
plt.grid(True)

# Acceleration plot for mass 1
plt.subplot(2, 2, 2)
plt.plot(f_range, np.abs(a1_omega_G_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Acceleration (G)')
plt.title('Acceleration Response of Mass 1 vs. Frequency')
plt.grid(True)

# Displacement plot for mass 2
plt.subplot(2, 2, 3)
plt.plot(f_range, np.abs(u2_omega_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Displacement (in)')
plt.title('Displacement Response of Mass 2 vs. Frequency')
plt.grid(True)

# Acceleration plot for mass 2
plt.subplot(2, 2, 4)
plt.plot(f_range, np.abs(a2_omega_G_mdof))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Acceleration (G)')
plt.title('Acceleration Response of Mass 2 vs. Frequency')
plt.grid(True)

plt.tight_layout()
plt.show()
