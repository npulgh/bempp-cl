"""Interfaces to Helmholtz operators."""
import numpy as _np

from bempp.api.operators.boundary import common as _common


def single_layer(
    domain,
    range_,
    dual_to_range,
    wavenumber,
    parameters=None,
    assembler="default_nonlocal",
    device_interface=None,
    precision=None,
):
    """Assemble the Helmholtz single-layer boundary operator."""
    from bempp.api.operators import _add_wavenumber
    from .modified_helmholtz import single_layer as _modified_single_layer

    if _np.real(wavenumber) == 0:
        return _modified_single_layer(
            domain,
            range_,
            dual_to_range,
            _np.imag(wavenumber),
            parameters,
            assembler,
            device_interface,
            precision,
        )

    options = {"KERNEL_FUNCTION": "helmholtz_single_layer", "COMPLEX_KERNEL": None}

    _add_wavenumber(options, wavenumber)

    return _common.create_operator(
        "helmholtz_single_layer_boundary",
        domain,
        range_,
        dual_to_range,
        parameters,
        assembler,
        options,
        "default_scalar",
        device_interface,
        precision,
    )


def double_layer(
    domain,
    range_,
    dual_to_range,
    wavenumber,
    parameters=None,
    assembler="default_nonlocal",
    device_interface=None,
    precision=None,
):
    """Assemble the Helmholtz double-layer boundary operator."""
    from bempp.api.operators import _add_wavenumber
    from .modified_helmholtz import double_layer as _modified_double_layer

    if _np.real(wavenumber) == 0:
        return _modified_double_layer(
            domain,
            range_,
            dual_to_range,
            _np.imag(wavenumber),
            parameters,
            assembler,
            device_interface,
            precision,
        )

    options = {"KERNEL_FUNCTION": "helmholtz_double_layer", "COMPLEX_KERNEL": None}

    _add_wavenumber(options, wavenumber)

    return _common.create_operator(
        "helmholtz_double_layer_boundary",
        domain,
        range_,
        dual_to_range,
        parameters,
        assembler,
        options,
        "default_scalar",
        device_interface,
        precision,
    )


def adjoint_double_layer(
    domain,
    range_,
    dual_to_range,
    wavenumber,
    parameters=None,
    assembler="default_nonlocal",
    device_interface=None,
    precision=None,
):
    """Assemble the Helmholtz adj. double-layer boundary operator."""
    from bempp.api.operators import _add_wavenumber
    from .modified_helmholtz import (
        adjoint_double_layer as _modified_adjoint_double_layer,
    )

    if _np.real(wavenumber) == 0:
        return _modified_adjoint_double_layer(
            domain,
            range_,
            dual_to_range,
            _np.imag(wavenumber),
            parameters,
            assembler,
            device_interface,
            precision,
        )

    options = {
        "KERNEL_FUNCTION": "helmholtz_adjoint_double_layer",
        "COMPLEX_KERNEL": None,
    }

    _add_wavenumber(options, wavenumber)

    return _common.create_operator(
        "helmholtz_adjoint_double_layer_boundary",
        domain,
        range_,
        dual_to_range,
        parameters,
        assembler,
        options,
        "default_scalar",
        device_interface,
        precision,
    )


def hypersingular(
    domain,
    range_,
    dual_to_range,
    wavenumber,
    parameters=None,
    assembler="default_nonlocal",
    device_interface=None,
    precision=None,
):
    """Assemble the Helmholtz hypersingular boundary operator."""
    from bempp.api.operators import _add_wavenumber
    from .modified_helmholtz import hypersingular as _hypersingular

    if _np.real(wavenumber) == 0:
        return _hypersingular(
            domain,
            range_,
            dual_to_range,
            _np.imag(wavenumber),
            parameters,
            assembler,
            device_interface,
            precision,
        )

    options = {"KERNEL_FUNCTION": "helmholtz_single_layer", "COMPLEX_KERNEL": None}

    _add_wavenumber(options, wavenumber)

    return _common.create_operator(
        "helmholtz_hypersingular_boundary",
        domain,
        range_,
        dual_to_range,
        parameters,
        assembler,
        options,
        "helmholtz_hypersingular",
        device_interface,
        precision,
    )