# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from .secure_element.secure_element import SecureElement

# Set of TAx device names for quick lookup
_TAX_DEVICES = {"TA100", "TA101", "TA075"}


def get_secure_element_data(
    device: str = "ATECC608",
    interface: str = "I2C",
    address: str = "0x6C",
    is_lite_manifest: bool = False,
):
    """
    Returns the JSON manifest for the specified secure element device.
    For TAx devices, attempts to import and use the TAx NDA package.
    For other devices, uses the standard SecureElement class.
    """
    if device in _TAX_DEVICES:
        try:
            from .TA_element import TAElement
        except ImportError as exc:
            raise ImportError(
                "TAx NDA package is not available. Please contact MCHP for the tpds-device-manifest NDA package."
            ) from exc
        return TAElement(device, interface, address, is_lite_manifest).build_json()
    return SecureElement(device, interface, address, is_lite_manifest).build_json()
