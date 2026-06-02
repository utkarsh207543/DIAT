import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt

# --- User Configuration ---
# Replace with the actual VISA resource string for your instrument
VISA_ADDRESS = "TCPIP0::192.168.0.43::inst0::INSTR"

# --- Sweep Configuration ---
START_VOLTAGE = -10.0  # Volts
STOP_VOLTAGE = 10.0  # Volts
STEP_VOLTAGE = 1  # Volts

# --- Systematic Variation Parameters ---
# 10 different delays to vary the ramp rate (dV/dt), which influences the measured current.
# Shorter delay = faster ramp = higher current.
RAMP_DELAYS = np.logspace(-2, 0, 2)  # 10 steps from 0.01s to 1.0s

# 10 different integration (aperture) times for the current measurement.
# Longer aperture = more accurate/less noisy reading.
APERTURE_TIMES = np.logspace(-3, -1, 2)  # 10 steps from 1ms to 100ms

# --- Safety Limit ---
CURRENT_COMPLIANCE = .5 # in Amps, the maximum current allowed


def plot_results(results_data):
    """
    Generates C-V plots from the collected measurement data.
    Creates one plot per unique aperture time.
    """
    if not results_data:
        print("No data collected, skipping plot generation.")
        return

    print("\n--- Generating Plots ---")

    # Get a sorted list of the unique aperture times used in the measurements
    unique_apertures = sorted(list(set(res['aperture'] for res in results_data)))

    for aperture in unique_apertures:
        # Create a new figure for each aperture time
        plt.figure(figsize=(10, 7))

        # Find and plot all sweeps that match the current aperture time
        for sweep in results_data:
            if sweep['aperture'] == aperture:
                # Plot Voltage vs. Capacitance
                plt.plot(sweep['voltages'], sweep['capacitances'], marker='o', markersize=2,
                         label=f"Ramp Delay = {sweep['delay']:.3f} s")

        plt.title(f"Capacitance vs. Voltage (Aperture Time: {aperture:.4f} s)")
        plt.xlabel("Voltage (V)")
        plt.ylabel("Capacitance (F)")
        plt.grid(True)
        plt.legend()
        plt.yscale('log')  # Use a logarithmic scale for capacitance for better visualization

    print("All plots generated. Displaying now...")
    plt.show()


def measure_cv_sweep():
    """
    Connects to a Keysight B2911A, performs a voltage sweep, calculates
    capacitance at each step, and finally plots the results.
    """
    instrument = None
    all_sweep_results = []
    try:
        # --- Establish Connection ---
        print("--- Establishing Connection ---")
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource(VISA_ADDRESS)
        instrument.timeout = 25000
        instrument.read_termination = '\n'
        instrument.write_termination = '\n'
        print("Connection established successfully.")
        print(f"Instrument ID: {instrument.query('*IDN?')}")

        # --- Generate Voltage Points ---
        voltage_points = np.arange(START_VOLTAGE, STOP_VOLTAGE + STEP_VOLTAGE, STEP_VOLTAGE)
        total_measurements = len(RAMP_DELAYS) * len(APERTURE_TIMES) * (len(voltage_points) - 1)
        print(
            f"\nConfiguration: {len(voltage_points)} voltage points, {len(RAMP_DELAYS)} ramp delays, {len(APERTURE_TIMES)} aperture times.")
        print(f"Total measurements to be performed: {total_measurements}")
        print("This may take a long time. Plots will be displayed upon completion.")

        # --- Main Measurement Loop ---
        for delay in RAMP_DELAYS:
            for aperture in APERTURE_TIMES:
                print("\n" + "=" * 50)
                print(f"STARTING NEW SWEEP")
                print(f"Ramp Delay (dt): {delay:.4f} s | Aperture Time: {aperture:.4f} s")
                print("=" * 50)

                # --- Instrument Setup for this Sweep ---
                print("--- Configuring Instrument for Sweep ---")
                instrument.write("*RST")
                instrument.write(":SOUR:FUNC:MODE VOLT")
                instrument.write(":SENS:FUNC 'CURR'")
                instrument.write(f":SENS:CURR:PROT {CURRENT_COMPLIANCE}")
                instrument.write(f":SENS:CURR:APER {aperture}")
                instrument.write(":SENS:CURR:RANG:AUTO ON")
                instrument.write(":OUTP:STAT OFF")
                print("Instrument configured.")

                # Temporary lists to store data for the current sweep
                current_voltages = []
                current_capacitances = []

                try:
                    # --- Perform the Voltage Sweep ---
                    print(f"Moving to start voltage: {START_VOLTAGE} V")
                    instrument.write(f":SOUR:VOLT {START_VOLTAGE}")
                    instrument.write(":OUTP:STAT ON")
                    time.sleep(0.5)

                    print("Starting sweep...")
                    for i in range(1, len(voltage_points)):
                        v_start = voltage_points[i - 1]
                        v_end = voltage_points[i]

                        instrument.write(f":SOUR:VOLT {v_end}")
                        time.sleep(delay)  # This delay sets the ramp time (dt)

                        measured_current = float(instrument.query(":MEAS:CURR?"))

                        # --- Calculation ---
                        dV = v_end - v_start
                        dt = delay
                        dV_dt = dV / dt

                        capacitance = 0  # Default value
                        if dV_dt != 0:
                            capacitance = abs(measured_current / dV_dt)
                            print(f"  V: {v_end:+.2f}V, I: {measured_current:.4e}A -> C: {capacitance:.4e}F")

                        # Store results for this data point
                        current_voltages.append(v_end)
                        current_capacitances.append(capacitance)

                    print("Sweep finished.")
                    instrument.write(":OUTP:STAT OFF")

                    # Add the completed sweep's data to the main results list
                    all_sweep_results.append({
                        'delay': delay,
                        'aperture': aperture,
                        'voltages': current_voltages,
                        'capacitances': current_capacitances
                    })

                except pyvisa.errors.VisaIOError as e:
                    print(f"  A VISA error occurred during the sweep: {e}")
                    instrument.write(":OUTP:STAT OFF")
                    continue

    except pyvisa.errors.VisaIOError as e:
        print(f"\n--- VISA Error ---")
        print(f"An error occurred while communicating with the instrument: {e}")
        print("Please check the VISA address and connection.")

    except Exception as e:
        print(f"\n--- An Unexpected Error Occurred ---")
        print(e)

    finally:
        # --- Close Connection and Plot ---
        if instrument:
            print("\n--- Measurement Complete ---")
            instrument.write(":OUTP:STAT OFF")
            instrument.close()
            print("Connection Closed.")

        # Generate the plots with all collected data
        plot_results(all_sweep_results)


if __name__ == "__main__":
    measure_cv_sweep()