import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import savgol_filter
from nomad.units import ureg

def logistic(x, mu, sig):
    return 1 / (np.exp((x-mu)/sig) + 1) + 0.02*np.random.random(x.size)

composition = np.loadtxt('tests/data/x_ray_fluorescence.csv', delimiter=',', dtype=str)
print(composition)

n_points = 500
x = np.linspace(450, 550, n_points)
y = logistic(x, 500, 1)
gradient = np.gradient(y)

data = np.zeros((n_points, 2))
data[:, 0] = x
data[:, 1] = y


def extract_band_gap(data: np.ndarray) -> ureg.Quantity:
    '''Extracts a band gap value from a UV-vis spectra.'''
    # Extract wavelength and absorbance data
    wavelength = data[:, 0]
    absorbance = data[:, 1]

    # Smoothen data, calculate gradient
    absorbance_smooth = savgol_filter(absorbance, 25, 3)
    absorbance_gradient = -np.gradient(absorbance_smooth)

    # Plot
    fig, ax = plt.subplots(figsize=(9, 6), layout='constrained')
    ax.plot(wavelength, absorbance)
    ax.plot(wavelength, absorbance_smooth)
    ax.plot(wavelength, absorbance_gradient)
    ax.set_xlabel("Wavelength (nm)", fontsize=16)
    ax.set_ylabel("Absorbance (AU)", fontsize=16)
    plt.show()

    # Find peak
    peaks, _ = find_peaks(absorbance_gradient, height=0.015)
    assert len(peaks) == 1
    peak_wavelength = wavelength[peaks[0]]

    # Calculate band gap energy from peak position using eV = hc/lambda
    band_gap_energy = (ureg.speed_of_light * ureg.planck_constant) / (peak_wavelength * ureg('nanometer'))
    return band_gap_energy.to(ureg.eV)

print(extract_band_gap(data))


# np.savetxt("uv_vis_spectra.csv", data, delimiter=",")

