import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.signal import savgol_filter
from nomad.units import ureg
from nomad.datamodel import EntryArchive
from nomad.datamodel.results import Results



def m_add(root, path, value):
    parts = path.split(".")
    for part in parts[:-1]:
        child = getattr(root, part)
        props = root.m_def.all_properties
        child_section = props[part]
        child_cls = child_section.sub_section.section_cls
        repeats = child_section.repeats

        # See if child exists. Non-repeating sections are accepted as they are,
        # repeating sections are accepted if there is only one instance
        if child:
            root = child
            if repeats:
                if len(child) != 1:
                    raise ValueError('Cannot add value as path contains a repeating section with multiple entries.')
                root = child[0]
        # Otherwise create child
        else:
            child_instance = child_cls()
            if repeats:
                root.m_add_sub_section(child_section, child_instance)
            else:
                setattr(root, part, child_instance)
            root = child_instance

    setattr(root, parts[-1], value)


a = EntryArchive()
m_add(a, "results.properties.available_properties", ["test"])
print(a.results.properties.available_properties)

# def logistic(x, mu, sig):
#     return 1 / (np.exp((x-mu)/sig) + 1) + 0.02*np.random.random(x.size)

# composition = np.loadtxt('tests/data/x_ray_fluorescence.csv', delimiter=',', dtype=str)
# print(composition)

# n_points = 500
# x = np.linspace(470, 530, n_points)
# y = logistic(x, 500, 1)
# gradient = np.gradient(y)

# data = np.zeros((n_points, 2))
# data[:, 0] = x
# data[:, 1] = y


# def extract_band_gap(data: np.ndarray) -> ureg.Quantity:
#     '''Extracts a band gap value from a UV-vis spectra.'''
#     # Extract wavelength and absorbance data
#     wavelength = data[:, 0]
#     absorbance = data[:, 1]

#     # Smoothen data, calculate gradient
#     absorbance_smooth = savgol_filter(absorbance, 25, 3)
#     absorbance_gradient = -np.gradient(absorbance_smooth)

#     # Plot
#     fig, ax = plt.subplots(figsize=(6, 6), layout='constrained')
#     ax.plot(wavelength, absorbance, color="orange", linestyle="-", linewidth=2, label="raw data")
#     ax.plot(wavelength, absorbance_smooth, color="k", linestyle="--", linewidth=1, label="smoothed data")
#     ax.plot(wavelength, absorbance_gradient, color="blue", linestyle="-", linewidth=2, label="gradient")
#     ax.set_xlabel("Wavelength (nm)", fontsize=16)
#     ax.set_ylabel("Absorbance (AU)", fontsize=16)
#     plt.legend(loc="upper right")
#     plt.show()

#     # Find peak
#     peaks, _ = find_peaks(absorbance_gradient, height=0.015)
#     assert len(peaks) == 1
#     peak_wavelength = wavelength[peaks[0]]

#     # Calculate band gap energy from peak position using eV = hc/lambda
#     band_gap_energy = (ureg.speed_of_light * ureg.planck_constant) / (peak_wavelength * ureg('nanometer'))
#     return band_gap_energy.to(ureg.eV)

# print(extract_band_gap(data))


# # np.savetxt("uv_vis_spectra.csv", data, delimiter=",")
