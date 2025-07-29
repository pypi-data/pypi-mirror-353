"""Generic rules applying to all IDSs"""

@validator("*")
def validate_homogeneous_time(ids):
    """Validation function for the time mode (ids_properties.homogeneous_time).

    Executed validations are:

    * homogeneous_time must be set to a valid value (0, 1 or 2)
    * "Static" IDSs must have homogeneous_time = 2
    * Root time must be non-empty when homogeneous_time = 1
    * All dynamic quantities must be empty when homogeneous_time = 2
    """
    assert 0 <= ids.ids_properties.homogeneous_time <= 2
    if not hasattr(ids, "time"):  # static IDSs don't have a root time attribute
        assert (
            ids.ids_properties.homogeneous_time == 2
        ), "Static IDS must have homogeneous_time == 2."

    if ids.ids_properties.homogeneous_time == 1:
        assert ids.time.has_value, "time must be non-empty when homogeneous_time == 1"

    if ids.ids_properties.homogeneous_time == 2:
        # Loop over all filled quantities and assert they are not dynamic
        for node in Select(ids, ".*", has_value=True):
            # Use IMAS-Python's metadata to check that this quantity is not dynamic
            # https://imas-python.readthedocs.io/en/stable/generated/imas.ids_metadata.IDSType.html#imas.ids_metadata.IDSType
            assert (
                not node.metadata.type.is_dynamic
            ), "Dynamic quantity may not be filled when homogeneous_time == 2"


@validator("*")
def validate_increasing_time(ids):
    """Validate that all non-empty time vectors are strictly increasing."""
    if ids.ids_properties.homogeneous_time == 1:
        assert Increasing(ids.time)
    else:
        aos_dict = {}
        for time_quantity in Select(ids, "(^|/)time$", has_value=True):
            # 1D time array:
            if time_quantity.metadata.ndim == 1:
                assert Increasing(time_quantity)
            # FLT_0D times also occur for timed arrays of structures
            else:
                # Get the corresponding AoS quantity (e.g. profiles_1d for
                # profiles_1d[0].time):d
                aos = Parent(time_quantity, 2)
                aos_name = aos._obj.metadata.name
                if aos_name in aos_dict.keys():
                    aos_dict[aos_name] = aos

        # Validate time "vectors" for timed arrays of structures
        for aos in aos_dict.values():
            last_time = float("-inf")
            for struct in aos:
                assert (
                    last_time < struct.time
                ), f"Non-increasing time found for dynamic Array of Structures: {aos!r}"
                last_time = struct.time


@validator("*")
def validate_min_max(ids):
    """Validate that ``*_min`` values are lower than ``*_max`` values, and the related
    value is within the bounds.

    Notes:

    * ``{value}_min <= {value}_max`` is only checked when both values are filled.
    * ``{value}_min <= {value} <= {value}_max`` (value is within bounds) is only
      validated when all three quantities are filled.
    """
    for quantity_min in Select(ids, "_min$", has_value=True):
        quantity_name = str(quantity_min.metadata.name)[:-4]  # strip off _min
        quantity = getattr(Parent(quantity_min), quantity_name, None)
        quantity_max = getattr(Parent(quantity_min), quantity_name + "_max", None)

        # If _max exists and is filled, check that it is >= _min
        if quantity_max is not None and quantity_max.has_value:
            assert quantity_min <= quantity_max

            # quantity exist, is not a structure and is filled, check that the quantity
            # is within bounds:
            if (
                quantity is not None
                and not quantity.metadata.data_type.value.startswith("struct")
                and quantity.has_value
            ):
                assert quantity_min <= quantity <= quantity_max


@validator("*")
def validate_errorbars(ids):
    """Validate that ``*_error_upper`` and `*_error_lower`` values are positive, and
    that error_upper is also filled whenever ``error_lower`` is non empty
    """
    for error_upper in Select(ids, "_error_upper$", has_value=True):
        assert (
            error_upper >= 0
        ), "Negative value found for errorbar, while their values must be positive."

    for error_lower in Select(ids, "_error_lower$", has_value=True):
        assert (
            error_lower >= 0
        ), "Negative value found for errorbar, while their values must be positive."
        error_lower_name = str(error_lower.metadata.name)
        error_upper_name = error_lower_name.replace("_error_lower", "_error_upper")
        error_upper = getattr(Parent(error_lower), error_upper_name, None)
        assert (
            error_upper is not None and error_upper.has_value
        ), "No value found for error_upper, while the related error_lower is filled."


@validator("*")
def validate_density_positive(ids):
    """Validate that density values are positive"""
    for node in Select(ids, "^((?!_error_).)*$", has_value=True):
        if node.metadata.units == "m^-3" and not (
            "derivative" in str(node.metadata.path)
        ):
            assert node >= 0, "Negative value found for a density"


@validator("*")
def validate_temperature_positive(ids):
    """Validate that temperature and energy values are positive"""
    for node in Select(ids, "^((?!_error_).)*$", has_value=True):
        if node.metadata.units == "eV" and not (
            "derivative" in str(node.metadata.path)
        ):
            assert node >= 0, "Negative value found for a temperature or energy"
