from nomad.metainfo import Quantity, Package, Section
from nomad.datamodel.metainfo.eln.material_library import Sample
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
    BrowserAnnotation,
    BrowserAdaptors
)

m_package = Package()


class MyLabSchema(Sample):
    m_def = Section(label='My Lab Schema')

    composition_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.FileEditQuantity),
        a_browser=BrowserAnnotation(adaptor=BrowserAdaptors.RawFileAdaptor)
    )
    band_gap_file = Quantity(
        type=str,
        a_eln=ELNAnnotation(component=ELNComponentEnum.FileEditQuantity),
        a_browser=BrowserAnnotation(adaptor=BrowserAdaptors.RawFileAdaptor)
    )

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        # Read in the composition information and record it in the processed data

        # Read in the band gap measurement and record it in the processed data


m_package.__init_metainfo__()
