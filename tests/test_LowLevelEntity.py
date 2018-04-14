import pytest


def test__Port__get_set_dict__pass(port, port_data):
    d = port.get_as_dict()
    assert d == port_data


def test__Port__validate__pass(port_with_instance, port_data, sut):
    port = port_with_instance
    port.instance.sut = sut
    port.validate()
