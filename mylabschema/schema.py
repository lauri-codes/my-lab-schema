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
        super().normalize(archive, logger)

        # Prefill institute, datetime, sample_id
        if not self.institute:
            self.institute = "My Institute"
        if not self.creation_datetime:
            self.creation_datetime = datetime.datetime.now()
        if not self.sample_id:
            self.sample_id = str(uuid.uuid4())

        # Read in the X-ray fluorescence file, extract composition and save in common metainfo
        if self.x_ray_fluorescence_file:
            with archive.m_context.raw_file(self.x_ray_fluorescence_file) as f:
                data = np.loadtxt(f, delimiter=',', dtype=str)
                material = m_add(archive, "results.material")
                material.elements = self.extract_elements(data)

        # Read in the the UV-Vis measurement, extract band gap and save in common metainfo
        if self.uv_vis_spectrum_file:
            with archive.m_context.raw_file(self.uv_vis_spectrum_file) as f:
                data = np.loadtxt(f, delimiter=',')
                band_gap_section = m_add(archive, "results.properties.electronic.band_structure_electronic.band_gap")
                band_gap_section.value = self.extract_band_gap(data)
                archive.results.properties.available_properties = ['electronic.band_structure_electronic.band_gap']

    def extract_band_gap(self, data: np.ndarray) -> ureg.Quantity:
        '''Extracts a band gap value from a UV-vis spectra.'''
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
        return band_gap_energy.to(ureg.eV)

    def extract_elements(self, data: np.ndarray) -> List[str]:
        '''Extracts a list of chemical elements from the X-ray fluorescence file.'''
        return data[:, 0]
    

def m_add(root, path):
    parts = path.split(".")
    for part in parts:
        child = getattr(root, part)
        props = root.m_def.all_properties
        child_section = props[part]
        child_cls = child_section.sub_section.section_cls
        repeats = child_section.repeats

        # See if child exists. Repeating subsection is accepted only if there is
        # one instance.
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

    return root


m_package.__init_metainfo__()
