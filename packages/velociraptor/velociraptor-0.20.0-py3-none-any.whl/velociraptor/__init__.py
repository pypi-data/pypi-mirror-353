"""
The velociraptor module.

More information is available in the documentation.
"""

# First things first, we need to upgrade msun and mh from a symbol to a
# first-class unit. We also add a dimensionless unit for magnitudes.
import unyt

try:
    unyt.define_unit("msun", 1.0 * unyt.msun, tex_repr=r"M_\odot")
except RuntimeError:
    # We've already done that, oops.
    pass

try:
    unyt.define_unit("mh", 1.0 * unyt.hydrogen_mass, tex_repr=r"m_{\rm H}")
except RuntimeError:
    # We've already done that, oops.
    pass

try:
    unyt.define_unit("mag", 1.0 * unyt.dimensionless, tex_repr=r"mag")
except RuntimeError:
    # We've already done that, oops.
    pass


from velociraptor.catalogue.catalogue import Catalogue, CatalogueTypeError
from velociraptor.catalogue.velociraptor_catalogue import VelociraptorCatalogue
from velociraptor.catalogue.soap_catalogue import SOAPCatalogue
from velociraptor.__version__ import __version__

from typing import Union, List


def load(
    filename: str,
    disregard_units: bool = False,
    registration_file_path: Union[List[str], str, None] = None,
    mask: slice = Ellipsis,
) -> Catalogue:
    """
    Loads a velociraptor catalogue, producing a Catalogue object.

    Parameters
    ----------

    filename: str
        The filename of your VELOCIraptor catalogue file (i.e.
        the path to the .properties file).

    disregard_units: bool, optional
        If ``True``, then disregard any additional units in the
        VELOCIraptor catalogues, and instead base everything on
        the 'base' units of velocity, length, and mass. In this
        case metallicities are left dimensionless. If you are
        using EAGLE data, you should set this to False, as the
        star formation rate units are presented in non-internal
        units.

    registration_file_path: Union[List[str], str], optional
        The filename of the derived quantities script(s) to register
        additional properties with the catalogue. This is an
        advanced feature. See the documentation for more details.

    mask: Union[None, NDArray[bool], int], optional
        If a boolean array is provided, it is used to mask all
        catalogue arrays. If an int is provided, catalogue arrays
        are masked to the single corresponding element.


    Returns
    -------

    Catalogue
        The Catalogue object that describes your .properties file.
    """

    try:
        catalogue = VelociraptorCatalogue(
            filename, disregard_units=disregard_units, mask=mask
        )
    except CatalogueTypeError:
        catalogue = SOAPCatalogue(filename)

    if registration_file_path is not None:
        catalogue.register_derived_quantities(registration_file_path)

    return catalogue
