import matplotlib.pyplot as plt
from PIL import Image


def calculate_dimensions(frequency, gain):
    # Constants for horn antenna design
    wavelength = 300 / frequency  # Wavelength in cm
    aperture_efficiency = 0.6  # Efficiency factor for aperture antenna

    # Calculating aperture size based on gain
    aperture_size = (gain * wavelength) / (4 * aperture_efficiency)

    # Calculating horn dimensions (assuming rectangular horn)
    horn_length = wavelength / 2
    horn_width = aperture_size / horn_length

    return horn_length, horn_width


def generate_blueprint(horn_length, horn_width):
    # Create a plot
    fig, ax = plt.subplots()

    # Plot the horn antenna
    ax.plot([0, horn_length], [0, horn_width], color='black')
    ax.plot([0, horn_length], [0, -horn_width], color='black')
    ax.plot([horn_length, horn_length], [-horn_width, horn_width], color='black')

    # Set plot limits
    ax.set_xlim(0, horn_length)
    ax.set_ylim(-horn_width, horn_width)

    # Set aspect ratio to be equal
    ax.set_aspect('equal', 'box')

    # Save the plot as an image
    plt.savefig('horn_blueprint.png')
    plt.close()


def main():
    # Get user input for frequency and gain
    frequency = float(input("Enter the frequency in GHz: "))
    gain = float(input("Enter the gain in dB: "))

    # Calculate horn dimensions
    horn_length, horn_width = calculate_dimensions(frequency, gain)

    # Generate blueprint image
    generate_blueprint(horn_length, horn_width)

    print("Blueprint generated as horn_blueprint.png")


if __name__ == "__main__":
    main()
