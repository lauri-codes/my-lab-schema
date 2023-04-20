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
                material = m_get_section(archive, "results.material")
                material.elements = data[:, 0]

        # Read in the the UV-Vis measurement, extract band gap and save in common metainfo
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

                band_gap_section = m_get_section(archive, "results.properties.electronic.band_structure_electronic.band_gap")
                band_gap_section.value = band_gap_energy
    

def m_get_section(root, path):
    '''Given a root section and a path, looks if a unique section can be found
    under that path and returns it. Will create the sections along the path if
    no instances are found.
    '''
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
