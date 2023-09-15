import numpy as np
import matplotlib.pyplot as plt

def amplification_factor_damped(mass, k, f, zeta):
    f0 = np.sqrt(k / mass) / (2 * np.pi)  # Natural frequency in Hz
    r = f / f0  # Frequency ratio
    X = 1 / np.sqrt((1 - r**2)**2 + (2 * zeta * r)**2)
    return X, r

def transmissibility_damped(mass, k, f, zeta):
    f0 = np.sqrt(k / mass) / (2 * np.pi)  # Natural frequency in Hz
    r = f / f0  # Frequency ratio
    T = np.sqrt((1 + (2 * zeta * r)**2) / ((1 - r**2)**2 + (2 * zeta * r)**2))
    return T, r


def plot_amplification(weight, k, f_range, damping_ratios):
    mass = weight / 386.089  # Convert lbf to effective mass for lbf/in
    
    plt.figure(figsize=(10,6))
    
    for zeta in damping_ratios:
        r_values = []
        amplification_values = []
        for f in f_range:
            amplification, r = amplification_factor_damped(mass, k, f, zeta)
            r_values.append(r)
            amplification_values.append(amplification)
        plt.plot(r_values, amplification_values, label=f'Damping Ratio = {zeta*100}%')
    
    plt.xlabel('Frequency Ratio (r)')
    plt.ylabel('Amplification Factor')
    plt.title('Frequency Response of a 1-DOF system with Different Damping Ratios')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    return plt


def plot_transmissibility(weight, k, f_range, damping_ratios):
    mass = weight / 386.089  # Convert lbf to effective mass for lbf/in
    
    # Transmissibility plot
    plt.figure(figsize=(10,6))
    for zeta in damping_ratios:
        r_values = []
        transmissibility_values = []
        for f in f_range:
            transmissibility, r = transmissibility_damped(mass, k, f, zeta)
            r_values.append(r)
            transmissibility_values.append(transmissibility)
        plt.plot(r_values, transmissibility_values, label=f'Damping Ratio = {zeta*100}%')
    plt.xlabel('Frequency Ratio (r)')
    plt.ylabel('Transmissibility')
    plt.title('Transmissibility of a 1-DOF system with Different Damping Ratios')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()




# Example usage:
weight = 1.0  # lbf
k = 100.0  # lbf/in



w_o = np.sqrt(k / (weight/386.089)) / (2 * np.pi)  # Natural frequency in Hz

print(w_o)

f_range = np.linspace(0.1, 300, 500)  # Varying the frequency in Hz

# Damping ratios
damping_ratios = [0.03]

# Re-plotting with the corrected mass definition
# plt = plot_amplification_damped(weight, k, f_range, damping_ratios)
plt = plot_transmissibility(weight, k, f_range, damping_ratios)

plt.figure
plt.show()