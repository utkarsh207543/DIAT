import numpy as np
import matplotlib.pyplot as plt

def potential_energy(x):
    # Define the potential energy function for the quantum well
    if 0 < x < 1:
        return 0
    else:
        return np.inf

def plot_quantum_well(num_states):
    # Plot the quantum well potential
    x_values = np.linspace(0, 1, 1000)
    potential_values = [potential_energy(x) for x in x_values]

    # Calculate and plot wavefunctions for the specified number of states
    num_rows = (num_states + 1) // 2  # Ensure at least one row
    num_cols = min(num_states, 2)  # Maximum of 2 columns

    # Create subplots
    fig, axs = plt.subplots(num_rows, 2, figsize=(8 * num_cols, 4 * num_rows))

    # Flatten the array if there's only one row
    axs = axs.flatten() if num_rows > 1 else np.expand_dims(axs, axis=0)

    # Plot quantum well potential in the first subplot
    axs[0].plot(x_values, potential_values, label='Quantum Well Potential', color='black')
    axs[0].set_title('Quantum Well Potential')
    axs[0].set_xlabel('Position (x)')
    axs[0].set_ylabel('Potential Energy')
    axs[0].legend()

    # Calculate eigenvectors and eigenvalues (replace this with your actual calculation)
    # For demonstration purposes, let's use random values
    np.random.seed(42)
    eigenvectors = np.random.rand(len(x_values), num_states)
    eigenvalues = np.sort(np.random.rand(num_states))

    # Plot energy states using eigenvectors and eigenvalues
    for i, ax in enumerate(axs[1:]):
        eigenstate = eigenvectors[:, i]
        eigenstate /= np.max(np.abs(eigenstate))  # Normalize for better visualization
        ax.plot(x_values, eigenstate + eigenvalues[i], label=f'n={i+1} state')
        ax.set_title(f'n={i+1} State')
        ax.set_xlabel('Position (x)')
        ax.set_ylabel('Energy')
        ax.legend()

    plt.suptitle(f'1D Quantum Well and Energy States for {num_states} States')
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to prevent subplot overlap
    plt.show()

if __name__ == "__main__":
    num_states = 4  # Specify the number of states to calculate
    plot_quantum_well(num_states)
