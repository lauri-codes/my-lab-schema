import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter


def logistic(x, mu, sig):
    return 1 / (np.exp((x-mu)/sig) + 1) + 0.02*np.random.random(x.size)

n_points = 500
x = np.linspace(470, 530, n_points)
y = logistic(x, 500, 1)
gradient = np.gradient(y)

data = np.zeros((n_points, 2))
data[:, 0] = x
data[:, 1] = y

# Extract wavelength and absorbance data
wavelength = data[:, 0]
absorbance = data[:, 1]

# Smoothen data, calculate gradient
absorbance_smooth = savgol_filter(absorbance, 25, 3)
absorbance_gradient = -np.gradient(absorbance_smooth)

# Plot
fig, ax = plt.subplots(figsize=(8, 6), layout='constrained')
ax.plot(wavelength, absorbance, color="orange", linestyle="-", linewidth=2, label="raw data")
ax.plot(wavelength, absorbance_smooth, color="k", linestyle="--", linewidth=1, label="smoothed data")
ax.plot(wavelength, absorbance_gradient, color="blue", linestyle="-", linewidth=2, label="gradient")
ax.set_xlabel("Wavelength (nm)", fontsize=16)
ax.set_ylabel("Absorbance (AU)", fontsize=16)
plt.legend(loc="upper right")
plt.show()

# # np.savetxt("uv_vis_spectra.csv", data, delimiter=",")
