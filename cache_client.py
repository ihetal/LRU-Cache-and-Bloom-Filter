import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from bloom_filter import BloomFilter
from lru_cache import lru_cache

BUFFER_SIZE = 1024

bloomfilter = BloomFilter(50, 0.05)
cachedb = dict()


@lru_cache(5)
def get(key):
    if bloomfilter.is_member(key):
        return cachedb.get(key)
    else:
        return None


def put(key, value):
    bloomfilter.add(key)
    cachedb[key] = value


def delete(key):
    if bloomfilter.is_member(key):

        del cachedb[key]
        print("Inside delete", cachedb)
        get.cache_clear(key)


class UDPClient():

    def send(self, request, server):
        print('Connecting to server at {}:{}'.format(
            server['host'], server['port']))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (server['host'], server['port']))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()


def process(udp_clients):
    client_ring = NodeRing(NODES)
    hash_codes = set()
    # PUT all users.
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        put(key, u)
        server = client_ring.get_node(key)
        response = udp_clients.send(data_bytes, server)
        print(response)
        hash_codes.add(str(response.decode()))

    print(
        f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")

    # GET all users.
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        response = get(key)
        if not(response):
            server = client_ring.get_node(key)
            response = udp_clients.send(data_bytes, server)
        print(response)


if __name__ == "__main__":
    clients = UDPClient()
    process(clients)
