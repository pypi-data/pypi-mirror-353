"""Pre-processing options to be performed on a gxsm file.

This file contains methods that can be performed on gxsm data
in order to help convert it to more 'understandable' data
(primarily, converting to physical units data).

We call it pre-processing because it will be bundled in a pre-
processing callable if called using xarray.open_mfdataset().

If using on it's own, you can simply feed an xarray.Dataset
to be corrected.

Note: these methods assume the provided dataset has been validated
as corresponding to a gxsm file!
"""

import xarray
from . import filename as fn
from . import utils
from . import channel_config  as cc

# Lists the expected gxsm data variables and coords that are *not* metadata and
# should be kept.
GXSM_DATA_VAR = 'FloatField'
GXSM_DATA_DIFFERENTIAL = 'dz'

GXSM_KEPT_COORDS = ['dimx', 'dimy']
GXSM_KEPT_DATA_VARS = [GXSM_DATA_VAR, GXSM_DATA_DIFFERENTIAL]

# For it to be a proper gxsm file, we expect this attr key and val
GXSM_FORMAT_CHECK = ('Creator', 'gxsm')


def preprocess(ds: xarray.Dataset,
               use_physical_units: bool,
               allow_convert_from_metadata: bool,
               simplify_metadata: bool,
               channels_config_dict: dict | None
               ) -> xarray.Dataset:
    """Convert floatfield and (optionally) simplify metadata.

    This is the top-level handler for preprocessing the gxsm dataset into our
    desired format.

    Args:
        ds: the Dataset instance we are to convert, assumed to be from a gxsm
            data file.
        use_physical_units: whether or not to record the data in physical
            units. If true, we require 'conversion_factor'  and 'units'
            to exist (see optional exception below). Else, 'units' will be
            'raw' and 'conversion_factor' '1.0'.
        allow_convert_from_metadata: for some channels, there are hardcoded
            gxsm metadata attributes that contain the V-to-units conversion.
            If this attribute is true, we will use the metadata conversion
            as a fallback (i.e. if the config does not contain it).
        simplify_metadata: whether or not to convert all metadata variables
            to attributes.
        channels_config_dict: a dict containing gxsm channel configuration data
            (including the V-to-x unit conversion for each channel).
    """
    if not is_gxsm_file(ds):
        raise TypeError('The provided file does not appear to be a gxsm file!')

    # Note: Could also use ds['basename'].data.tobytes() [gxsm-specific]
    # (but this is the filepath on the device it was first recorded).
    filename = ds.encoding['source']
    gxsm_file_attribs = fn.parse_gxsm_filename(filename)
    channel_config = cc.CreateGxsmChannelConfig(channels_config_dict, ds,
                                                gxsm_file_attribs,
                                                use_physical_units,
                                                allow_convert_from_metadata)
    ds = clean_floatfield(ds)
    ds = clean_kept_coords(ds)
    ds = convert_floatfield(ds, channel_config)
    if simplify_metadata:
        ds = clean_up_metadata(ds, [channel_config.name])
    return ds


def clean_floatfield(ds: xarray.Dataset) -> xarray.Dataset:
    """Remove spurious dimensions from FloatField array.

    The main data array, 'FloatField', has 2 spurious dimensions: 'time' and
    'value'. This makes the array of the form [1,1,dimy,dimy,...]. This is
    unnecessary and makes it hard to remove unnecessary meatadata/coords
    later.

    Thus, this helper just explicitly removes those first 2 dimensions!

    Args:
        ds: input xarray.Dataset, presumably with original 'FloatField' da.

    Returns:
        output xarray.Dataset, with the first two dimensions of the data
        removed.
    """
    da = xarray.DataArray(
        data=ds[GXSM_DATA_VAR].data[0, 0, ...],
        dims=['dimy', 'dimx'],
        coords={'dimy': ds.dimy, 'dimx': ds.dimx})

    ds[GXSM_DATA_VAR] = da
    return ds


def convert_floatfield(ds: xarray.Dataset, channel_config: cc.GxsmChannelConfig
                       ) -> xarray.Dataset:
    """Convert gxsm file 'FloatField' variable to 'raw' or 'physical' data.

    gxsm stores its recorded data in a 'FloatField' attribute, containing
    raw DAC counter data. In order to convert it to raw units, we must
    perform the following:
        data['raw'] = data['FloatField'] * data['dz']

    To convert it to physical units:
        data['physical'] = data['FloatField'] * data['dz'] * V_to_x_conversion

    where:
    - data['dz'] is the differential in 'z', correlating a DAC counter to
        a physical unit *within gxsm's understanding of the world*. Since the
        DAC data is received from one of the hardware device input channels
        (ADC#), this 'dz' is used to convert from the DC received voltage V
        to a unit x *without knowledge of the actual V-to-x conversion*. Thus,
        with the exception of the case of the topography channel, this is a
        'pseudo-unit'.
    - V_to_x_conversion is a conversion factor from this 'pseudo-unit' to
        physical units. Another way to think of this is that the 'pseudo-unit'
        considers V_to_x_conversion to be 1-to-1, and this is a correction of
        that (for the cases where the conversion is *not* 1-to-1).

    Args:
        ds: the Dataset instance we are to convert, assumed to be from a gxsm
            data file.
        channel_config: a GxsmChannelConfig instance, holding the necessary
            info to convert and name our new data variable.

    Returns:
        A modified Dataset, where the 'FloatField' variable has been replaced
        by a variabled named after its channel, with physical units stored.

        Note: the channel name will either be taken directly from the gxsm file
        save format (e.g. topography files are saved with "Topo"), *or* with
        the desired channel name indicated in the config.

    Raises:
        None.
    """
    converted_data = (ds[GXSM_DATA_VAR] * ds[GXSM_DATA_DIFFERENTIAL]
                      * channel_config.conversion_factor)

    converted_data.attrs['units'] = channel_config.units
    ds[channel_config.name] = converted_data

    # Delete the original data variables
    ds = ds.drop_vars(GXSM_KEPT_DATA_VARS)
    return ds


def clean_kept_coords(ds: xarray.Dataset) -> xarray.Dataset:
    """Update kept coords to be in nm and have 'units' attr.

    Helper to ensure our spatial coordinate dimensions (GXSM_KEPT_DATA_COORDS)
    are properly labeled and using SI units.

    Args:
        ds: xarray Dataset instance.

    Returns:
        xarray.Dataset instance, with GXSM_KEPT_DATA_COORDS converted to nm
        and with a 'units' attr indicating as such.
    """
    for coord in GXSM_KEPT_COORDS:
        # Convert kept coords to 'nm' and add metadata units
        updated_coord = ds[coord] * cc.GXSM_TOPO_CONVERSION_FACTOR
        updated_coord.attrs['units'] = cc.GXSM_TOPO_UNITS
        ds[coord] = updated_coord
    return ds


def clean_up_metadata(ds: xarray.Dataset, saved_vars_list: list = []
                      ) -> xarray.Dataset:
    """Convert 'metadata' variables to attributes.

    gxsm does not store *all* metadata as attributes in its NetCDF file.
    Instead, many of them are stored as variables. This is to better qualify
    them: a description (long_name) and units (var_unit) attributes are
    provided.

    However, we find this introduces confusion between metadata and actual data
    (note that there are >100 metadata variables!). To better divide data and
    metadata, we provide this method; it moves all metadata variables to
    attributes, and places them appropriately within the xarray.Dataset.

    This means that the units are removed! Since this appears standard in
    other microscopy files, we believe it to be ok. A user curious about the
    units is encouraged to open the file using xarray directly, or study any
    appropriate documentation.

    Note that that we do not check vars in provided saved_vars_list for
    'units' attrs. We assume this will be (or has been) done separately.

    Args:
        ds: the Dataset instance we are to convert, assumed to be from a gxsm
            data file.
        saved_vars_list: a list of dataset variables to keep (i.e. not turn
            into attributes). This could contain any variables the user knows
            are not metadata.
        config: a dict containing gxsm channel configuration data (including
            the V-to-x unit conversion for each channel).

    Returns:
        A modified Dataset, where all metadata is stored as attributes.

    Raises:
        None.
    """
    # Create whitelist of hard-coded gxsm data vars to skip, as well as
    # desired channel names (in case we run this before or after
    # sanitizing the actual data).
    data_vars_whitelist = GXSM_KEPT_DATA_VARS + saved_vars_list

    # We are creating a new ds from grabbed data (rather than manually
    # removing vars/coords), since the latter threw strange exceptions.
    kept_data_vars = {}
    kept_coords = {}
    new_attrs = {}

    for coord in ds.coords:
        if coord not in GXSM_KEPT_COORDS:
            new_attrs[coord] = utils.extract_numpy_data(ds[coord].values)
        else:
            kept_coords[coord] = ds[coord]

    for var in ds.data_vars:
        if var not in data_vars_whitelist:
            new_attrs[var] = utils.extract_numpy_data(ds[var].values)
        else:
            kept_data_vars[var] = ds[var]

    full_attrs = {**ds.attrs, **new_attrs}
    new_ds = xarray.Dataset(data_vars=kept_data_vars, coords=kept_coords,
                            attrs=full_attrs)
    return new_ds


def is_gxsm_file(ds: xarray.Dataset) -> bool:
    """Check if the provided file is a supported gxsm file."""
    try:
        return GXSM_FORMAT_CHECK[1] in ds.attrs[GXSM_FORMAT_CHECK[0]].lower()
    except KeyError:
        return False
