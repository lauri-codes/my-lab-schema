import datetime
import uuid
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter
from nomad.units import ureg
from nomad.metainfo import Quantity, Package, Section
from nomad.datamodel.results import (
    Results,
    Material,
    Properties,
    ElectronicProperties,
    BandStructureElectronic,
    BandGap
)
from nomad.datamodel.metainfo.eln.material_library import Sample
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    BrowserAnnotation,
    BrowserAdaptors
)

m_package = Package()


class MySample(Sample):
    m_def = Section(
        label='MySample',
        properties={
            'editable': {
                'exclude': ['institute']
            }
        }
    )
    composition_file = Quantity(
        type=str,
        label='Composition file',
        a_eln=ELNAnnotation(component=ELNComponentEnum.FileEditQuantity),
        a_browser=BrowserAnnotation(adaptor=BrowserAdaptors.RawFileAdaptor)
    )
    uv_vis_spectrum_file = Quantity(
        type=str,
        label='UV-vis spectrum file',
        a_eln=ELNAnnotation(component=ELNComponentEnum.FileEditQuantity),
        a_browser=BrowserAnnotation(adaptor=BrowserAdaptors.RawFileAdaptor)
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

        # Read in the composition information and record it in the processed data
        if self.composition_file:
            with archive.m_context.raw_file(self.composition_file) as f:
                data = np.loadtxt(f, delimiter=',', dtype=str)
                elements = data[:, 0]
                if not archive.results:
                    archive.results = Results()
                if not archive.results.material:
                    archive.results.material = Material()
                archive.results.material.elements = elements

        # Read in the band gap measurement and record it in the processed data
        if self.uv_vis_spectrum_file:
            with archive.m_context.raw_file(self.uv_vis_spectrum_file) as f:
                data = np.loadtxt(f, delimiter=',')
                band_gap = self.extract_band_gap(data)
                if not archive.results:
                    archive.results = Results()
                if not archive.results.properties:
                    archive.results.properties = Properties()
                if not archive.results.properties.electronic:
                    archive.results.properties.electronic = ElectronicProperties()
                if not archive.results.properties.electronic.band_structure_electronic:
                    archive.results.properties.electronic.m_add_sub_section(ElectronicProperties.band_structure_electronic, BandStructureElectronic())
                if not archive.results.properties.electronic.band_structure_electronic[0].band_gap:
                    archive.results.properties.electronic.band_structure_electronic[0].m_add_sub_section(BandStructureElectronic.band_gap, BandGap())
                archive.results.properties.electronic.band_structure_electronic[0].band_gap[0].value = band_gap


    def extract_band_gap(self, data: np.ndarray) -> ureg.Quantity:
        '''Extracts a band gap value from a UV-vis spectra.'''
        # Extract wavelength and absorbance data
        wavelength = data[:, 0]
        absorbance = data[:, 1]

        # Smoothen data, calculate gradient
        absorbance_smooth = savgol_filter(absorbance, 25, 3)
        absorbance_gradient = -np.gradient(absorbance_smooth)

        # Find peak
        peaks, _ = find_peaks(absorbance_gradient, height=0.015)
        assert len(peaks) == 1
        peak_wavelength = wavelength[peaks[0]]

        # Calculate band gap energy from peak position using eV = hc/lambda
        band_gap_energy = (ureg.speed_of_light * ureg.planck_constant) / (peak_wavelength * ureg('nanometer'))
        return band_gap_energy.to(ureg.eV)


m_package.__init_metainfo__()
