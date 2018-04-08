from unittest import TestCase

from exc import ArgumentMissingException
from integrations.GossObjects import GossFile


class TestGossObjects(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__file__get_yaml__missing_required_attrs__exception(self):
        # prepare
        o = GossFile()
        dst = '/bin/bash'
        o.set_destination(dst=dst)

        # run
        with self.assertRaisesRegexp(ArgumentMissingException, 'required'):
            o.get_yaml()

        # check

    def test__file__get_yaml__sut__pass(self):
        # prepare
        o = GossFile()
        dst = '/bin/bash'

        # run
        o.set_destination(dst=dst)

        # check


    def test__file__set_required_attributes__pass(self):
        # prepare
        o = GossFile()
        attrs = [{'file': '/usr/bin/bash'}]

        # run
        o.set_required_attributes(attrs=attrs)

        # check
        self.assertEqual(o.required_attributes['file'], 1)
