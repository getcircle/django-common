from protobufs.services.common import containers_pb2 as common_containers
from unittest import TestCase

from ..utils import (
    fields_for_item,
    fields_for_repeated_item,
    inflations_for_repeated_item,
    inflations_for_item,
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

    def test_fields_for_repeated_item(self):
        fields = {
            'only': [
                '[]collections.[]items.post.title',
                'description',
                '[]collections.[]items.post.by_profile_id',
            ],
            'exclude': ['[]collections.[]items.post.content'],
        }
        per_collection_fields = fields_for_repeated_item('collections', fields)
        self.assertEqual(
            per_collection_fields.only,
            ['[]items.post.title', '[]items.post.by_profile_id'],
        )
        self.assertEqual(
            per_collection_fields.exclude,
            ['[]items.post.content'],
        )

        per_item_fields = fields_for_repeated_item('items', per_collection_fields)
        self.assertEqual(per_item_fields.only, ['post.title', 'post.by_profile_id'])
        self.assertEqual(per_item_fields.exclude, ['post.content'])

    def test_fields_for_item(self):
        fields = {
            'only': ['post.title', 'post.by_profile_id', 'description'],
            'exclude': ['post.content'],
        }
        per_item_fields = fields_for_item('post', fields)
        self.assertEqual(per_item_fields.only, ['title', 'by_profile_id'])
        self.assertEqual(per_item_fields.exclude, ['content'])

    def test_inflations_for_repeated_item(self):
        inflations = {
            'only': [
                '[]collections.[]items.post.title',
                'description',
                '[]collections.[]items.post.by_profile_id',
            ],
            'exclude': ['[]collections.[]items.post.content'],
        }
        per_collection_inflations = inflations_for_repeated_item('collections', inflations)
        self.assertFalse(per_collection_inflations.disabled)
        self.assertEqual(
            per_collection_inflations.only,
            ['[]items.post.title', '[]items.post.by_profile_id'],
        )
        self.assertEqual(
            per_collection_inflations.exclude,
            ['[]items.post.content'],
        )

        per_item_inflations = inflations_for_repeated_item('items', per_collection_inflations)
        self.assertEqual(per_item_inflations.only, ['post.title', 'post.by_profile_id'])
        self.assertEqual(per_item_inflations.exclude, ['post.content'])

        inflations['disabled'] = True
        per_collection_inflations = inflations_for_repeated_item('collections', inflations)
        self.assertTrue(per_collection_inflations.disabled)

        per_item_inflations = inflations_for_repeated_item('items', per_collection_inflations)
        self.assertTrue(per_item_inflations.disabled)

    def test_inflations_for_item(self):
        inflations = {
            'only': ['post.title', 'post.by_profile_id', 'description'],
            'exclude': ['post.content'],
        }
        per_item_inflations = inflations_for_item('post', inflations)
        self.assertEqual(per_item_inflations.only, ['title', 'by_profile_id'])
        self.assertEqual(per_item_inflations.exclude, ['content'])

        inflations['disabled'] = True
        per_item_inflations = inflations_for_item('post', inflations)
        self.assertTrue(per_item_inflations.disabled)
