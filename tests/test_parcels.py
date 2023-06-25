import logging

import pytest

from inpost.static import CompartmentActualStatus
from inpost.static.parcels import CompartmentLocation, CompartmentProperties, Parcel
from tests.test_data import (
    courier_parcel,
    open_data_result,
    parcel_locker,
    parcel_locker_multi,
    parcel_locker_multi_main,
    parcel_properties,
    qr_result,
    qr_result_multi,
    qr_result_multi_main,
)


def build_dict(object, test_data, keys: list):
    test_input_dict = {}
    expected_dict = {}
    for key in keys:
        test_input_dict[key] = eval("object." + key)
        expected_dict[key] = eval("test_data." + key)
    return test_input_dict, expected_dict


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, "465649"),
        (courier_parcel, None),
    ],
)
def test_open_code(test_input, expected):
    parcel_code = Parcel(test_input, logging.getLogger(__name__)).open_code
    assert parcel_code == expected, f"parcel_code: {parcel_code} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, qr_result),
        (parcel_locker_multi, qr_result_multi),
        (parcel_locker_multi_main, qr_result_multi_main),
    ],
)
def test_generate_qr_image(test_input, expected):
    qr_image = Parcel(test_input, logging.getLogger(__name__)).generate_qr_image
    assert qr_image.read() == expected, f"qr_image: {qr_image} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, None),
        (courier_parcel, None),
    ],
)
def test_compartment_properties(test_input, expected):
    compartment_properties = Parcel(test_input, logging.getLogger(__name__)).compartment_properties
    assert (
        compartment_properties == expected
    ), f"compartment_properties: {compartment_properties} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, parcel_properties),
    ],
)
def test_compartment_properties_setter(test_input, expected):
    parcel = Parcel(test_input, logging.getLogger(__name__))
    parcel.compartment_properties = expected
    test_data = CompartmentProperties(expected, logging.getLogger(__name__))
    test_input_dict, expected_dict = build_dict(
        parcel.compartment_properties, test_data, ["_status", "_session_uuid", "_session_expiration_time", "_location"]
    )
    assert (
        test_input_dict == expected_dict
    ), f"compartment_properties_setter: {test_input_dict} != expected: {expected_dict}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, None),
        (courier_parcel, None),
    ],
)
def test_compartment_location(test_input, expected):
    compartment_location = Parcel(test_input, logging.getLogger(__name__)).compartment_location
    assert compartment_location == expected, f"compartment_location: {compartment_location} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, parcel_properties),
    ],
)
def test_compartment_location_setter(test_input, expected):
    parcel = Parcel(test_input, logging.getLogger(__name__))
    parcel.compartment_properties = expected
    parcel.compartment_location = expected
    test_data = CompartmentLocation(expected, logging.getLogger(__name__))
    test_input_dict, expected_dict = build_dict(
        parcel.compartment_location,
        test_data,
        ["name", "side", "column", "row", "open_compartment_waiting_time", "action_time", "confirm_action_time"],
    )
    assert (
        test_input_dict == expected_dict
    ), f"compartment_location_setter: {test_input_dict} != expected: {expected_dict}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, None),
        (courier_parcel, None),
    ],
)
def test_compartment_status(test_input, expected):
    parcel_status = Parcel(test_input, logging.getLogger(__name__)).compartment_status
    assert parcel_status == expected, f"parcel_status: {parcel_status} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("CLOSED", CompartmentActualStatus.CLOSED),
        ("OPENED", CompartmentActualStatus.OPENED),
        ("PENIS", CompartmentActualStatus.UNKNOWN),
        (CompartmentActualStatus.CLOSED, CompartmentActualStatus.CLOSED),
        (CompartmentActualStatus.OPENED, CompartmentActualStatus.OPENED),
    ],
)
def test_compartment_status_setter(test_input, expected):
    parcel = Parcel(parcel_locker, logging.getLogger(__name__))
    parcel.compartment_properties = parcel_properties
    parcel.compartment_status = test_input
    assert (
        parcel.compartment_status == expected
    ), f"compartment_status: {parcel.compartment_status} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, open_data_result),
        (courier_parcel, None),
    ],
)
def test_compartment_open_data(test_input, expected):
    parcel_open_data = Parcel(test_input, logging.getLogger(__name__)).compartment_open_data
    assert parcel_open_data == expected, f"parcel_open_data: {parcel_open_data} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, parcel_locker),
        (parcel_locker, parcel_locker),
        (parcel_locker, parcel_locker),
        (parcel_locker, parcel_locker),
        (parcel_locker, parcel_locker),
        (parcel_locker_multi, parcel_locker_multi),
        (parcel_locker_multi, parcel_locker_multi),
        (parcel_locker_multi, parcel_locker_multi),
        (parcel_locker_multi, parcel_locker_multi),
        (parcel_locker_multi, parcel_locker_multi),
        (parcel_locker_multi_main, parcel_locker_multi_main),
        (parcel_locker_multi_main, parcel_locker_multi_main),
        (parcel_locker_multi_main, parcel_locker_multi_main),
        (parcel_locker_multi_main, parcel_locker_multi_main),
        (parcel_locker_multi_main, parcel_locker_multi_main),
        (courier_parcel, None),
    ],
)
def test_mocked_location(test_input, expected):
    mocked_location = Parcel(test_input, logging.getLogger(__name__)).mocked_location
    expected = expected["pickUpPoint"]["location"]
    is_in_range = (
        abs(mocked_location["latitude"] - expected["latitude"]) <= 0.00005
        and abs(mocked_location["longitude"] - expected["longitude"]) <= 0.00005
    )
    assert is_in_range, (
        f"mocked_location invalid threshold. Should be less or equal to 0.00005 but on of values is not meeting it"
        f"mocked_latitude: {mocked_location['latitude']}, expected: {expected['latitude']},"
        f" diff: {abs(mocked_location['latitude'] - expected['latitude'])}"
        f"mocked_latitude: {mocked_location['longitude']}, expected: {expected['longitude']},"
        f" diff: {abs(mocked_location['latitude'] - expected['longitude'])}"
    )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, False),
        (parcel_locker_multi, True),
        (parcel_locker_multi_main, True),
        (courier_parcel, False),
    ],
)
def test_is_multicompartment(test_input, expected):
    is_multicompartment = Parcel(test_input, logging.getLogger(__name__)).is_multicompartment
    assert is_multicompartment is expected, f"is_multicompartment: {is_multicompartment} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, None),
        (parcel_locker_multi, False),
        (parcel_locker_multi_main, True),
        (courier_parcel, None),
    ],
)
def test_is_main_multicompartment(test_input, expected):
    is_main_multicompartment = Parcel(test_input, logging.getLogger(__name__)).is_main_multicompartment
    assert (
        is_main_multicompartment is expected
    ), f"is_main_multicompartment: {is_main_multicompartment} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (parcel_locker, True),
        (parcel_locker_multi, False),
        (parcel_locker_multi_main, True),
        (courier_parcel, None),
    ],
)
def test_has_airsensor(test_input, expected):
    has_airsensor = Parcel(test_input, logging.getLogger(__name__)).has_airsensor
    assert has_airsensor is expected, f"has_airsensor: {has_airsensor} != expected: {expected}"


# TODO: Add rest tests!
