import pytest

from inpost.static.statuses import (
    CompartmentActualStatus,
    CompartmentExpectedStatus,
    DeliveryType,
    ParcelAdditionalInsurance,
    ParcelCarrierSize,
    ParcelDeliveryType,
    ParcelLockerSize,
    ParcelOwnership,
    ParcelPointOperations,
    ParcelServiceName,
    ParcelShipmentType,
    ParcelStatus,
    ParcelType,
    PaymentStatus,
    PaymentType,
    PointType,
    ReturnsStatus,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("OTHER", ParcelCarrierSize.OTHER),
        ("A", ParcelCarrierSize.A),
        ("B", ParcelCarrierSize.B),
        ("C", ParcelCarrierSize.C),
        ("D", ParcelCarrierSize.D),
        ("PENIS", ParcelCarrierSize.UNKNOWN),
        ("KURWA", ParcelCarrierSize.UNKNOWN),
    ],
)
def test_parcel_carrier_size_bracket(test_input, expected):
    size = ParcelCarrierSize[test_input]
    assert size == expected, f"size: {size} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("8x38x64", "A"),
        ("19x38x64", "B"),
        ("41x38x64", "C"),
        ("50x50x80", "D"),
    ],
)
def test_parcel_carrier_size_normal(test_input, expected):
    size_new = ParcelCarrierSize(test_input)
    size_get = ParcelCarrierSize[expected]
    assert size_new == size_get, f"size_new: {size_new} != size_get: {size_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("A", ParcelLockerSize.A),
        ("B", ParcelLockerSize.B),
        ("C", ParcelLockerSize.C),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_locker_size_bracket(test_input, expected):
    size = ParcelLockerSize[test_input]
    assert size == expected, f"size: {size} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("8x38x64", "A"),
        ("19x38x64", "B"),
        ("41x38x64", "C"),
    ],
)
def test_parcel_locker_size_normal(test_input, expected):
    size_new = ParcelLockerSize(test_input)
    size_get = ParcelLockerSize[expected]
    assert size_new == size_get, f"size_new: {size_new} != size_get: {size_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("parcel_locker", ParcelDeliveryType.parcel_locker),
        ("courier", ParcelDeliveryType.courier),
        ("parcel_point", ParcelDeliveryType.parcel_point),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_delivery_type_bracket(test_input, expected):
    type = ParcelDeliveryType[test_input]
    assert type == expected, f"type: {type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Paczkomat", "parcel_locker"),
        ("Kurier", "courier"),
        ("PaczkoPunkt", "parcel_point"),
    ],
)
def test_parcel_delivery_type_normal(test_input, expected):
    type_new = ParcelDeliveryType(test_input)
    type_get = ParcelDeliveryType[expected]
    assert type_new == type_get, f"type_new: {type_new} != type_get: {type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("parcel", ParcelShipmentType.parcel),
        ("courier", ParcelShipmentType.courier),
        ("parcel_point", ParcelShipmentType.parcel_point),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_shipment_type_bracket(test_input, expected):
    type = ParcelShipmentType[test_input]
    assert type == expected, f"type: {type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Paczkomat", "parcel"),
        ("Kurier", "courier"),
        ("PaczkoPunkt", "parcel_point"),
    ],
)
def test_parcel_shipment_type_normal(test_input, expected):
    type_new = ParcelShipmentType(test_input)
    type_get = ParcelShipmentType[expected]
    assert type_new == type_get, f"type_new: {type_new} != type_get: {type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("UNINSURANCED", ParcelAdditionalInsurance.UNINSURANCED),
        ("ONE", ParcelAdditionalInsurance.ONE),
        ("TWO", ParcelAdditionalInsurance.TWO),
        ("THREE", ParcelAdditionalInsurance.THREE),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_additional_insurance_bracket(test_input, expected):
    insurance = ParcelAdditionalInsurance[test_input]
    assert insurance == expected, f"insurance: {insurance} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, "UNINSURANCED"),
        (2, "ONE"),
        (3, "TWO"),
        (4, "THREE"),
    ],
)
def test_parcel_additional_insurance_normal(test_input, expected):
    insurace_new = ParcelAdditionalInsurance(test_input)
    insurance_get = ParcelAdditionalInsurance[expected]
    assert insurace_new == insurance_get, f"insurace_new: {insurace_new} != insurance_get: {insurance_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("TRACKED", ParcelType.TRACKED),
        ("SENT", ParcelType.SENT),
        ("RETURNS", ParcelType.RETURNS),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_type_bracket(test_input, expected):
    parcel_type = ParcelType[test_input]
    assert parcel_type == expected, f"parcel_type: {parcel_type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Przychodzące", "TRACKED"),
        ("Wysłane", "SENT"),
        ("Zwroty", "RETURNS"),
    ],
)
def test_parcel_type_normal(test_input, expected):
    parcel_type_new = ParcelType(test_input)
    parcel_type_get = ParcelType[expected]
    assert (
        parcel_type_new == parcel_type_get
    ), f"parcel_type_new: {parcel_type_new} != parcel_type_get: {parcel_type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("PL", PointType.PL),
        ("parcel_locker_superpop", PointType.parcel_locker_superpop),
        ("POK", PointType.POK),
        ("POP", PointType.POP),
        ("PENIS", PointType.UNKNOWN),
    ],
)
def test_point_type_bracket(test_input, expected):
    point_type = PointType[test_input]
    assert point_type == expected, f"point_type: {point_type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Paczkomat", "PL"),
        ("some paczkomat or pok stuff", "parcel_locker_superpop"),
        ("Mobilny punkt obsługi klienta", "POK"),
        ("Punkt odbioru paczki", "POP"),
    ],
)
def test_point_type_normal(test_input, expected):
    point_type_new = PointType(test_input)
    point_type_get = PointType[expected]
    assert point_type_new == point_type_get, f"point_type_new: {point_type_new} != point_type_get: {point_type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("CREATE", ParcelPointOperations.CREATE),
        ("SEND", ParcelPointOperations.SEND),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_point_operations_bracket(test_input, expected):
    parcel_point_operation = ParcelPointOperations[test_input]
    assert (
        parcel_point_operation == expected
    ), f"parcel_point_operation: {parcel_point_operation} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("c2x-target", "CREATE"),
        ("remote-send", "SEND"),
    ],
)
def test_parcel_point_operations_normal(test_input, expected):
    parcel_point_operation_new = ParcelPointOperations(test_input)
    parcel_point_operation_get = ParcelPointOperations[expected]
    assert (
        parcel_point_operation_new == parcel_point_operation_get
    ), f"parcel_point_operation_new: {parcel_point_operation_new} != parcel_point_operation_get: {parcel_point_operation_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("CREATED", ParcelStatus.CREATED),
        ("OFFERS_PREPARED", ParcelStatus.OFFERS_PREPARED),
        ("OFFER_SELECTED", ParcelStatus.OFFER_SELECTED),
        ("CONFIRMED", ParcelStatus.CONFIRMED),
        ("READY_TO_PICKUP_FROM_POK", ParcelStatus.READY_TO_PICKUP_FROM_POK),
        ("OVERSIZED", ParcelStatus.OVERSIZED),
        ("DISPATCHED_BY_SENDER_TO_POK", ParcelStatus.DISPATCHED_BY_SENDER_TO_POK),
        ("DISPATCHED_BY_SENDER", ParcelStatus.DISPATCHED_BY_SENDER),
        ("COLLECTED_FROM_SENDER", ParcelStatus.COLLECTED_FROM_SENDER),
        ("TAKEN_BY_COURIER", ParcelStatus.TAKEN_BY_COURIER),
        ("ADOPTED_AT_SOURCE_BRANCH", ParcelStatus.ADOPTED_AT_SOURCE_BRANCH),
        ("SENT_FROM_SOURCE_BRANCH", ParcelStatus.SENT_FROM_SOURCE_BRANCH),
        ("READDRESSED", ParcelStatus.READDRESSED),
        ("OUT_FOR_DELIVERY", ParcelStatus.OUT_FOR_DELIVERY),
        ("READY_TO_PICKUP", ParcelStatus.READY_TO_PICKUP),
        ("PICKUP_REMINDER_SENT", ParcelStatus.PICKUP_REMINDER_SENT),
        ("PICKUP_TIME_EXPIRED", ParcelStatus.PICKUP_TIME_EXPIRED),
        ("AVIZO", ParcelStatus.AVIZO),
        ("TAKEN_BY_COURIER_FROM_POK", ParcelStatus.TAKEN_BY_COURIER_FROM_POK),
        ("REJECTED_BY_RECEIVER", ParcelStatus.REJECTED_BY_RECEIVER),
        ("UNDELIVERED", ParcelStatus.UNDELIVERED),
        ("DELAY_IN_DELIVERY", ParcelStatus.DELAY_IN_DELIVERY),
        ("RETURNED_TO_SENDER", ParcelStatus.RETURNED_TO_SENDER),
        ("READY_TO_PICKUP_FROM_BRANCH", ParcelStatus.READY_TO_PICKUP_FROM_BRANCH),
        ("DELIVERED", ParcelStatus.DELIVERED),
        ("CANCELED", ParcelStatus.CANCELED),
        ("CLAIMED", ParcelStatus.CLAIMED),
        ("STACK_IN_CUSTOMER_SERVICE_POINT", ParcelStatus.STACK_IN_CUSTOMER_SERVICE_POINT),
        ("STACK_PARCEL_PICKUP_TIME_EXPIRED", ParcelStatus.STACK_PARCEL_PICKUP_TIME_EXPIRED),
        ("UNSTACK_FROM_CUSTOMER_SERVICE_POINT", ParcelStatus.UNSTACK_FROM_CUSTOMER_SERVICE_POINT),
        ("COURIER_AVIZO_IN_CUSTOMER_SERVICE_POINT", ParcelStatus.COURIER_AVIZO_IN_CUSTOMER_SERVICE_POINT),
        ("TAKEN_BY_COURIER_FROM_CUSTOMER_SERVICE_POINT", ParcelStatus.TAKEN_BY_COURIER_FROM_CUSTOMER_SERVICE_POINT),
        ("STACK_IN_BOX_MACHINE", ParcelStatus.STACK_IN_BOX_MACHINE),
        (
            "STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED",
            ParcelStatus.STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED,
        ),
        ("UNSTACK_FROM_BOX_MACHINE", ParcelStatus.UNSTACK_FROM_BOX_MACHINE),
        ("ADOPTED_AT_SORTING_CENTER", ParcelStatus.ADOPTED_AT_SORTING_CENTER),
        ("OUT_FOR_DELIVERY_TO_ADDRESS", ParcelStatus.OUT_FOR_DELIVERY_TO_ADDRESS),
        ("PICKUP_REMINDER_SENT_ADDRESS", ParcelStatus.PICKUP_REMINDER_SENT_ADDRESS),
        ("UNDELIVERED_WRONG_ADDRESS", ParcelStatus.UNDELIVERED_WRONG_ADDRESS),
        ("UNDELIVERED_COD_CASH_RECEIVER", ParcelStatus.UNDELIVERED_COD_CASH_RECEIVER),
        ("REDIRECT_TO_BOX", ParcelStatus.REDIRECT_TO_BOX),
        ("CANCELED_REDIRECT_TO_BOX", ParcelStatus.CANCELED_REDIRECT_TO_BOX),
        ("PENIS", ParcelLockerSize.UNKNOWN),
    ],
)
def test_parcel_status_normal(test_input, expected):
    parcel_status = ParcelStatus[test_input]
    assert parcel_status == expected, f"parcel_status: {parcel_status} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("W trakcie przygotowania", "CREATED"),
        ("Oferty przygotowane", "OFFERS_PREPARED"),
        ("Oferta wybrana", "OFFER_SELECTED"),
        ("Potwierdzona", "CONFIRMED"),
        ("Gotowa do odbioru w PaczkoPunkcie", "READY_TO_PICKUP_FROM_POK"),
        ("Gabaryt", "OVERSIZED"),
        ("Nadana w PaczkoPunkcie", "DISPATCHED_BY_SENDER_TO_POK"),
        ("Nadana w paczkomacie", "DISPATCHED_BY_SENDER"),
        ("Odebrana od nadawcy", "COLLECTED_FROM_SENDER"),
        ("Odebrana przez Kuriera", "TAKEN_BY_COURIER"),
        ("Przyjęta w oddziale", "ADOPTED_AT_SOURCE_BRANCH"),
        ("Wysłana z oddziału", "SENT_FROM_SOURCE_BRANCH"),
        ("Zmiana punktu dostawy", "READDRESSED"),
        ("Wydana do doręczenia", "OUT_FOR_DELIVERY"),
        ("Gotowa do odbioru", "READY_TO_PICKUP"),
        ("Wysłano przypomnienie o odbiorze", "PICKUP_REMINDER_SENT"),
        ("Upłynął czas odbioru", "PICKUP_TIME_EXPIRED"),
        ("Powrót do oddziału", "AVIZO"),
        ("Odebrana z PaczkoPunktu nadawczego", "TAKEN_BY_COURIER_FROM_POK"),
        ("Odrzucona przez odbiorcę", "REJECTED_BY_RECEIVER"),
        ("Nie dostarczona", "UNDELIVERED"),
        ("Opóźnienie w dostarczeniu", "DELAY_IN_DELIVERY"),
        ("Zwrócona do nadawcy", "RETURNED_TO_SENDER"),
        ("Gotowa do odbioru z oddziału", "READY_TO_PICKUP_FROM_BRANCH"),
        ("Doręczona", "DELIVERED"),
        ("Anulowana", "CANCELED"),
        ("Zareklamowana", "CLAIMED"),
        ("Przesyłka magazynowana w punkcie obsługi klienta", "STACK_IN_CUSTOMER_SERVICE_POINT"),
        ("Upłynął czas odbioru", "STACK_PARCEL_PICKUP_TIME_EXPIRED"),
        ("?", "UNSTACK_FROM_CUSTOMER_SERVICE_POINT"),
        ("Przekazana do punktu obsługi klienta", "COURIER_AVIZO_IN_CUSTOMER_SERVICE_POINT"),
        ("Odebrana przez kuriera z punktu obsługi klienta", "TAKEN_BY_COURIER_FROM_CUSTOMER_SERVICE_POINT"),
        ("Przesyłka magazynowana w paczkomacie tymczasowym", "STACK_IN_BOX_MACHINE"),
        ("Upłynął czas odbioru z paczkomatu", "STACK_PARCEL_IN_BOX_MACHINE_PICKUP_TIME_EXPIRED"),
        ("Odebrana z paczkomatu", "UNSTACK_FROM_BOX_MACHINE"),
        ("Przyjęta w sortowni", "ADOPTED_AT_SORTING_CENTER"),
        ("Gotowa do doręczenia", "OUT_FOR_DELIVERY_TO_ADDRESS"),
        ("Wysłano przypomnienie o odbiorze", "PICKUP_REMINDER_SENT_ADDRESS"),
        ("Nie dostarczono z powodu złego adresu", "UNDELIVERED_WRONG_ADDRESS"),
        ("Nie dostarczono z powodu nieopłacenia", "UNDELIVERED_COD_CASH_RECEIVER"),
        ("Przekierowana do paczkomatu", "REDIRECT_TO_BOX"),
        ("Anulowano przekierowanie do paczkomatu", "CANCELED_REDIRECT_TO_BOX"),
    ],
)
def test_parcel_status_bracket(test_input, expected):
    parcel_status_new = ParcelStatus(test_input)
    parcel_status_get = ParcelStatus[expected]
    assert (
        parcel_status_new == parcel_status_get
    ), f"parcel_status_new: {parcel_status_new} != parcel_status_get: {parcel_status_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("BOX_MACHINE", DeliveryType.BOX_MACHINE),
        ("PENIS", DeliveryType.UNKNOWN),
    ],
)
def test_delivery_type_normal(test_input, expected):
    delivery_type = DeliveryType[test_input]
    assert delivery_type == expected, f"delivery_type: {delivery_type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Paczkomat", "BOX_MACHINE"),
    ],
)
def test_delivery_type_bracket(test_input, expected):
    delivery_type_new = DeliveryType(test_input)
    delivery_type_get = DeliveryType[expected]
    assert (
        delivery_type_new == delivery_type_get
    ), f"delivery_type_new: {delivery_type_new} != delivery_type_get: {delivery_type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("ACCEPTED", ReturnsStatus.ACCEPTED),
        ("USED", ReturnsStatus.USED),
        ("DELIVERED", ReturnsStatus.DELIVERED),
        ("PENIS", ReturnsStatus.UNKNOWN),
    ],
)
def test_returns_status_normal(test_input, expected):
    returns_status = ReturnsStatus[test_input]
    assert returns_status == expected, f"returns_status: {returns_status} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Zaakceptowano", "ACCEPTED"),
        ("Nadano", "USED"),
        ("Dostarczono", "DELIVERED"),
    ],
)
def test_returns_status_bracket(test_input, expected):
    returns_status_new = ReturnsStatus(test_input)
    returns_status_get = ReturnsStatus[expected]
    assert (
        returns_status_new == returns_status_get
    ), f"returns_status_new: {returns_status_new} != returns_status_get: {returns_status_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("FRIEND", ParcelOwnership.FRIEND),
        ("OWN", ParcelOwnership.OWN),
        ("PENIS", ParcelOwnership.UNKNOWN),
    ],
)
def test_parcel_ownership_normal(test_input, expected):
    parcel_ownership = ParcelOwnership[test_input]
    assert parcel_ownership == expected, f"parcel_ownership: {parcel_ownership} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Zaprzyjaźniona", "FRIEND"),
        ("Własna", "OWN"),
    ],
)
def test_parcel_ownership_bracket(test_input, expected):
    parcel_ownership_new = ParcelOwnership(test_input)
    parcel_ownership_get = ParcelOwnership[expected]
    assert (
        parcel_ownership_new == parcel_ownership_get
    ), f"parcel_ownership_new: {parcel_ownership_new} != parcel_ownership_get: {parcel_ownership_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("OPENED", CompartmentExpectedStatus.OPENED),
        ("CLOSED", CompartmentExpectedStatus.CLOSED),
        ("PENIS", CompartmentExpectedStatus.UNKNOWN),
    ],
)
def test_compartment_expected_status_normal(test_input, expected):
    compartment_expected = CompartmentExpectedStatus[test_input]
    assert compartment_expected == expected, f"compartment_expected: {compartment_expected} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Otwarta", "OPENED"),
        ("Zamknięta", "CLOSED"),
    ],
)
def test_compartment_expected_status_bracket(test_input, expected):
    compartment_expected_new = CompartmentExpectedStatus(test_input)
    compartment_expected_get = CompartmentExpectedStatus[expected]
    assert (
        compartment_expected_new == compartment_expected_get
    ), f"compartment_expected_new: {compartment_expected_new} != compartment_expected_get: {compartment_expected_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("OPENED", CompartmentActualStatus.OPENED),
        ("CLOSED", CompartmentActualStatus.CLOSED),
        ("PENIS", CompartmentActualStatus.UNKNOWN),
    ],
)
def test_compartment_actual_status_normal(test_input, expected):
    compartment_actual = CompartmentActualStatus[test_input]
    assert compartment_actual == expected, f"compartment_actual: {compartment_actual} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Otwarta", "OPENED"),
        ("Zamknięta", "CLOSED"),
    ],
)
def test_compartment_actual_status_bracket(test_input, expected):
    compartment_actual_new = CompartmentActualStatus(test_input)
    compartment_actual_get = CompartmentActualStatus[expected]
    assert (
        compartment_actual_new == compartment_actual_get
    ), f"compartment_actual_new: {compartment_actual_new} != compartment_actual_get: {compartment_actual_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("NOTSUPPORTED", PaymentType.NOTSUPPORTED),
        ("BY_CARD_IN_MACHINE", PaymentType.BY_CARD_IN_MACHINE),
        ("PENIS", PaymentType.UNKNOWN),
    ],
)
def test_payment_type_normal(test_input, expected):
    payment_type = PaymentType[test_input]
    assert payment_type == expected, f"payment_type: {payment_type} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Payments are not supported", "NOTSUPPORTED"),
        ("Payment by card in the machine", "BY_CARD_IN_MACHINE"),
    ],
)
def test_payment_type_bracket(test_input, expected):
    payment_type_new = PaymentType(test_input)
    payment_type_get = PaymentType[expected]
    assert (
        payment_type_new == payment_type_get
    ), f"payment_type_new: {payment_type_new} != payment_type_get: {payment_type_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (None, None),
        ("C2X_COMPLETED", PaymentStatus.C2X_COMPLETED),
        ("PENIS", PaymentStatus.UNKNOWN),
    ],
)
def test_payment_status_normal(test_input, expected):
    payment_status = PaymentStatus[test_input]
    assert payment_status == expected, f"payment_status: {payment_status} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("Completed", "C2X_COMPLETED"),
    ],
)
def test_payment_status_bracket(test_input, expected):
    payment_status_new = PaymentStatus(test_input)
    payment_status_get = PaymentStatus[expected]
    assert (
        payment_status_new == payment_status_get
    ), f"payment_status_new: {payment_status_new} != payment_status_get: {payment_status_get}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("ALLEGRO_PARCEL", ParcelServiceName.ALLEGRO_PARCEL),
        ("ALLEGRO_PARCEL_SMART", ParcelServiceName.ALLEGRO_PARCEL_SMART),
        ("ALLEGRO_LETTER", ParcelServiceName.ALLEGRO_LETTER),
        ("ALLEGRO_COURIER", ParcelServiceName.ALLEGRO_COURIER),
        ("STANDARD", ParcelServiceName.STANDARD),
        ("STANDARD_PARCEL_SMART", ParcelServiceName.STANDARD_PARCEL_SMART),
        ("PASS_THRU", ParcelServiceName.PASS_THRU),
        ("CUSTOMER_SERVICE_POINT", ParcelServiceName.CUSTOMER_SERVICE_POINT),
        ("REVERSE", ParcelServiceName.REVERSE),
        ("STANDARD_COURIER", ParcelServiceName.STANDARD_COURIER),
        ("REVERSE_RETURN", ParcelServiceName.REVERSE_RETURN),
    ],
)
def test_parcel_service_name_normal(test_input, expected):
    parcel_servicename = ParcelServiceName[test_input]
    assert parcel_servicename == expected, f"parcel_servicename: {parcel_servicename} != expected: {expected}"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (1, "ALLEGRO_PARCEL"),
        (2, "ALLEGRO_PARCEL_SMART"),
        (3, "ALLEGRO_LETTER"),
        (4, "ALLEGRO_COURIER"),
        (5, "STANDARD"),
        (6, "STANDARD_PARCEL_SMART"),
        (7, "PASS_THRU"),
        (8, "CUSTOMER_SERVICE_POINT"),
        (9, "REVERSE"),
        (10, "STANDARD_COURIER"),
        (11, "REVERSE_RETURN"),
    ],
)
def test_parcel_service_name_bracket(test_input, expected):
    parcel_servicename_new = ParcelServiceName(test_input)
    parcel_servicename_get = ParcelServiceName[expected]
    assert (
        parcel_servicename_new == parcel_servicename_get
    ), f"parcel_servicename_new: {parcel_servicename_new} != parcel_servicename_get: {parcel_servicename_get}"
