import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0545718e-34  # Reduced Planck's constant (Joule*seconds)
m_e = 9.10938356e-31  # Mass of electron (kg)
m_hh = 0.5 * m_e      # Effective mass of heavy hole (kg)
m_hl = 0.25 * m_e     # Effective mass of light hole (kg)
eV = 1.60218e-19      # Electron volt (Joules)
L = 1e-9  # Width of the quantum well (meters)

# User-defined number of states range
num_states_start = int(input("Enter the starting number of states: "))
num_states_stop = int(input("Enter the maximum number of states: "))
num_states_step = int(input("Enter the step size: "))

# Function to compute matrix element <HH|x|HL>
def position_matrix_element_hh_hl(n_hh, n_hl, L):
    if (n_hh + n_hl) % 2 == 0:
        return 0
    else:
        return (-2 * L / (np.pi**2) * (1 / (n_hh**2 - n_hl**2)))

# Function to compute emission probabilities
def emission_probabilities(n_hh, n_hl, L):
    matrix_element = position_matrix_element_hh_hl(n_hh, n_hl, L)
    sigma_plus = matrix_element**2 / 2
    sigma_minus = matrix_element**2 / 2
    return sigma_plus, sigma_minus

# Varying num_states and storing TM:TE ratio
num_states_range = np.arange(num_states_start, num_states_stop + 1, num_states_step)
tm_te_ratios = []

for num_states in num_states_range:
    sigma_plus_probs = np.zeros((num_states, num_states))
    sigma_minus_probs = np.zeros((num_states, num_states))

    for n_hh in range(1, num_states + 1):
        for n_hl in range(1, num_states + 1):
            sigma_plus, sigma_minus = emission_probabilities(n_hh, n_hl, L)
            sigma_plus_probs[n_hh-1, n_hl-1] = sigma_plus
            sigma_minus_probs[n_hh-1, n_hl-1] = sigma_minus

    overall_dominant_emission = sigma_plus_probs + sigma_minus_probs

    # Determine dominant emission type for each (HH, HL) pair
    dominant_emission = np.argmax(overall_dominant_emission, axis=1)
    dominant_emission_type = ['σ+' if x == 0 else 'σ-' for x in dominant_emission]

    # Count occurrences of each emission type
    count_sigma_minus = dominant_emission_type.count('σ-')
    count_sigma_plus = dominant_emission_type.count('σ+')

    # Compute TM:TE ratio
    if count_sigma_minus > 0:  # Avoid division by zero
        tm_te_ratio = count_sigma_plus / count_sigma_minus
    else:
        tm_te_ratio = 0  # If no σ-, assume TM:TE = 0

    tm_te_ratios.append(tm_te_ratio)

# Plot TM:TE Ratio vs. Number of States
plt.figure(figsize=(8, 6))
plt.plot(num_states_range, tm_te_ratios, 'bo-', label="TM:TE Ratio")
plt.xlabel("Number of States")
plt.ylabel("TM:TE Ratio")
plt.title("TM:TE Ratio vs. Number of States")
plt.grid(True)
plt.legend()
plt.show()
