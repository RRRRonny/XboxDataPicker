import unittest
import sys
from core.data_provider import NetworkRequester


class TestNetworRequester(unittest.TestCase):
    def test_replace(self):
        requester = NetworkRequester("apikey")
        values = {'gametag':'newtag'}
        origin_str = '{gametag}'
        self.assertEquals(requester.replace(values,origin_str),'newtag')




if __name__ == "__main__":
    unittest.main()