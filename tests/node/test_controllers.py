import unittest

import hug

from typing import List
from unittest import mock

from bson.objectid import ObjectId

from shipyard.node import controllers
from shipyard.node.model import Node


test_nodes = Node.Schema().load([
    {
        '_id': str(ObjectId()),
        'name': 'Test1',
        'ip': '1.1.1.1',
        'ssh_user': 'Test1',
        'ssh_pass': 'Test1'
    },
    {
        '_id': str(ObjectId()),
        'name': 'Test2',
        'ip': '2.2.2.2',
        'ssh_user': 'Test2',
        'ssh_pass': 'Test2'
    }
], many=True)


class MockService():

    @staticmethod
    def get_all() -> List[Node]:
        return test_nodes

    @staticmethod
    def get_by_id(node_id: str) -> Node:
        for i in range(len(test_nodes)):
            if ObjectId(node_id) == test_nodes[i]._id:
                return test_nodes[i]

        return None

    @staticmethod
    def get_by_name(node_name: str) -> Node:
        for i in range(len(test_nodes)):
            if node_name == test_nodes[i].name:
                return test_nodes[i]

        return None

    @staticmethod
    def create(new_node: Node) -> str:
        for i in range(len(test_nodes)):
            if new_node.name == test_nodes[i].name:
                raise ValueError

        return str(ObjectId())

    @staticmethod
    def delete(node_id: str) -> Node:
        for i in range(len(test_nodes)):
            if ObjectId(node_id) == test_nodes[i]._id:
                return test_nodes[i]

        return None


@mock.patch('shipyard.node.controllers.NodeService', MockService)
class TestControllers(unittest.TestCase):

    def test_get_node_list(self):
        response = hug.test.call('GET', controllers, '')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)
        self.assertEqual(len(response.data), 2)

        response = hug.test.call('GET', controllers, '', params={
            'name': test_nodes[0].name
        })
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('GET', controllers, '', params={
            'name': 'Error'
        })
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)

    def test_post_node(self):
        response = hug.test.call('POST', controllers, '', body={
            'name': 'Test3',
            'ip': '3.3.3.3',
            'ssh_user': 'Test3',
            'ssh_pass': 'Test3'
        })
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['_id'], str)

        response = hug.test.call('POST', controllers, '', body={
            'name': 'Test3',
            'ssh_user': 'Test3',
            'ssh_pass': 'Test3'
        })
        self.assertEqual(response.status, hug.HTTP_BAD_REQUEST)
        self.assertIsNotNone(response.data)

        response = hug.test.call('POST', controllers, '', body=Node.Schema(
            exclude=['_id']).dump(test_nodes[0]))
        self.assertEqual(response.status, hug.HTTP_CONFLICT)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

    def test_get_node(self):
        response = hug.test.call(
            'GET', controllers, f'{str(test_nodes[0]._id)}')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('GET', controllers, f'{ObjectId()}')
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

        response = hug.test.call('GET', controllers, 'error')
        self.assertEqual(response.status, hug.HTTP_BAD_REQUEST)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

    def test_delete_node(self):
        response = hug.test.call(
            'DELETE', controllers, f'{str(test_nodes[0]._id)}')
        self.assertEqual(response.status, hug.HTTP_OK)
        self.assertIsNotNone(response.data)

        response = hug.test.call('DELETE', controllers, f'{ObjectId()}')
        self.assertEqual(response.status, hug.HTTP_NOT_FOUND)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)

        response = hug.test.call('DELETE', controllers, 'error')
        self.assertEqual(response.status, hug.HTTP_BAD_REQUEST)
        self.assertIsNotNone(response.data)
        self.assertIsInstance(response.data['error'], str)