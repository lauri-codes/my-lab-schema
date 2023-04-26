import uuid
import datetime
from typing import List

import numpy as np
from scipy.signal import find_peaks, savgol_filter

from nomad.units import ureg
from nomad.metainfo import Quantity, Package
from nomad.datamodel.metainfo.eln.material_library import Sample
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum

m_package = Package()


class MySample(Sample):
    x_ray_fluorescence_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            label='X-ray fluorescence file',
            component=ELNComponentEnum.FileEditQuantity
        )
    )
    uv_vis_spectrum_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(
            label='UV-vis spectrum file',
            component=ELNComponentEnum.FileEditQuantity
        )
    )

    def normalize(self, archive, logger):
        # Call the normalize-function of Sample
        super().normalize(archive, logger)

        # Prefill institute, datetime, sample_id
        if not self.institute:
            self.institute = "My Institute"
        if not self.creation_datetime:
            self.creation_datetime = datetime.datetime.now()
        if not self.sample_id:
            self.sample_id = str(uuid.uuid4())

        # Read in the X-ray fluorescence file, extract composition and save in
        # common metainfo
        if self.x_ray_fluorescence_file:
            with archive.m_context.raw_file(self.x_ray_fluorescence_file) as f:
                data = np.loadtxt(f, delimiter=',', dtype=str)
                material = archive.m_setdefault("results.material")
                material.elements = data[:, 0]

        # Read in the the UV-Vis measurement, extract band gap and save in
        # common metainfo
        if self.uv_vis_spectrum_file:
            with archive.m_context.raw_file(self.uv_vis_spectrum_file) as f:
                data = np.loadtxt(f, delimiter=',')
                wavelength = data[:, 0]
                absorbance = data[:, 1]

                # Smoothen data, calculate gradient
                absorbance_smooth = savgol_filter(absorbance, 25, 3)
                absorbance_gradient = -np.gradient(absorbance_smooth)

                # Find peak in gradient
                peaks, _ = find_peaks(absorbance_gradient, height=0.015)
                assert len(peaks) == 1
                peak_wavelength = wavelength[peaks[0]]

                # Calculate band gap energy from peak position using eV = h * c / lambda
                band_gap_energy = (ureg.speed_of_light * ureg.planck_constant) / (peak_wavelength * ureg('nanometer'))

                band_gap = archive.m_setdefault("results.properties.electronic.band_structure_electronic.band_gap")
                band_gap.value = band_gap_energy


m_package.__init_metainfo__()
