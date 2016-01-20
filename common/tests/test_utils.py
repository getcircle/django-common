from protobufs.services.common import containers_pb2 as common_containers
from unittest import TestCase

from ..utils import (
    should_inflate_field,
    should_populate_field,
)


class Test(TestCase):

    def test_should_inflate_field_disabled(self):
        inflations = common_containers.InflationsV1()
        self.assertTrue(should_inflate_field('random_field', inflations))

        inflations = common_containers.InflationsV1(disabled=True)
        self.assertFalse(should_inflate_field('random_field', inflations))

    def test_should_inflate_field_accepts_dict(self):
        self.assertTrue(should_inflate_field('random_field', {'disabled': False}))
        self.assertFalse(should_inflate_field('random_field', {'disabled': True}))

    def test_should_inflate_field_only(self):
        self.assertFalse(should_inflate_field('random', {'only': ['other']}))
        self.assertTrue(should_inflate_field('random', {'only': ['random']}))

    def test_should_inflate_field_exclude_and_include_collision(self):
        inflations = {'only': ['random'], 'exclude': ['random']}
        self.assertFalse(should_inflate_field('random', inflations))
        self.assertFalse(should_inflate_field('other', inflations))

    def test_should_inflate_field_exclude(self):
        inflations = {'exclude': ['random']}
        self.assertTrue(should_inflate_field('other', inflations))
        self.assertFalse(should_inflate_field('random', inflations))

    def test_should_populate_field_only(self):
        fields = {'only': ['random']}
        self.assertTrue(should_populate_field('random', fields))
        self.assertFalse(should_populate_field('other', fields))

    def test_should_populate_field_exclude(self):
        fields = {'exclude': ['random']}
        self.assertFalse(should_populate_field('random', fields))
        self.assertTrue(should_populate_field('other', fields))

    def test_should_populate_field_exclude_and_only_collision(self):
        fields = {'only': ['random'], 'exclude': ['random']}
        self.assertFalse(should_populate_field('random', fields))
        self.assertFalse(should_populate_field('other', fields))

    def test_should_populate_field_converts_dict(self):
        fields = {'only': ['random']}
        self.assertTrue(should_populate_field('random', fields))
        fields = common_containers.FieldsV1(only=['random'])
        self.assertTrue(should_populate_field('random', fields))

    def test_should_populate_field_false_if_no_fields(self):
        self.assertTrue(should_populate_field('random', None))
