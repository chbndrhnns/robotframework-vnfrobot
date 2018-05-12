import pytest


def test__Port__get_set_dict__pass(port_with_instance, port_data):
    d = port_with_instance.get_as_dict()
    assert d == port_data


def test__Port__validate__pass(port_with_instance, sut):
    port = port_with_instance
    port.instance.sut = sut
    port.validate()


def test__Address__get_set_dict__pass(address_with_instance, address_data):
    d = address_with_instance.get_as_dict()
    assert d == address_data


def test__Address__validate__pass(address_with_instance, sut):
    port = address_with_instance
    port.instance.sut = sut
    port.validate()