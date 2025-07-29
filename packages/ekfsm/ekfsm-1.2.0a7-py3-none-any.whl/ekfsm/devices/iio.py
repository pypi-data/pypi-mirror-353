from .generic import SysFSDevice


def iio_get_in_value(dev: SysFSDevice, attrset: str) -> float:
    """
    Calculate a value from an IIO in_* attribute set, using the _raw, _scale and _offset attributes (if present).
    Typical name of attrset are "in_temp" or "in_voltage0".

    Formula according to https://wiki.st.com/stm32mpu/wiki/How_to_use_the_IIO_user_space_interface

    Parameters
    ----------
    dev
        sysfs device object pointing to the iio directory
    attrset
        name of the attribute set to read from (e.g. "in_temp")

    Returns
    -------
    float
        calculated value from the attribute set (no unit conversion)

    Raises
    ------
    FileNotFoundError
        if the neiter _input nor _raw attribute is found

    """
    # check if _input exists
    try:
        content = dev.read_attr_utf8(f"{attrset}_input")
        return float(content)
    except StopIteration:
        pass

    # check if _raw exists
    try:
        content = dev.read_attr_utf8(f"{attrset}_raw")
    except StopIteration:
        raise FileNotFoundError(f"{attrset}_raw not found")

    raw = float(content)

    # use offset if present
    try:
        content = dev.read_attr_utf8(f"{attrset}_offset")
        raw += float(content)
    except StopIteration:
        pass

    # use scale if present
    try:
        content = dev.read_attr_utf8(f"{attrset}_scale")
        raw *= float(content)
    except StopIteration:
        pass

    return raw
