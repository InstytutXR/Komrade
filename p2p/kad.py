# ###
# # Kademlia patches
# ###

# from kademlia.storage import *
# from kademlia.network import *
# from kademlia.routing import RoutingTable
# from rpcudp.protocol import RPCProtocol
# import os

# handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# log = logging.getLogger('kademlia')
# log.addHandler(handler)
# log.setLevel(logging.DEBUG)


# PROXY_ADDR = ('0.0.0.0',8368)


# """UDP proxy server."""

# import asyncio


# class ProxyDatagramProtocol(asyncio.DatagramProtocol):

#     def __init__(self, remote_address=PROXY_ADDR):
#         self.remote_address = remote_address
#         self.remotes_d = {}
#         super().__init__()

#     def connection_made(self, transport):
#         self.transport = transport

#     def datagram_received(self, data, addr):
#         if addr in self.remotes_d:
#             self.remotes_d[addr].transport.sendto(data)
#             return
#         loop = asyncio.get_event_loop()
#         self.remotes_d[addr] = RemoteDatagramProtocol(self, addr, data)
#         coro = loop.create_datagram_endpoint(
#             lambda: self.remotes_d[addr], remote_addr=self.remote_address)
#         asyncio.ensure_future(coro)


# class RemoteDatagramProtocol(asyncio.DatagramProtocol):

#     def __init__(self, proxy, addr, data):
#         print('RemoteDP got:',proxy,addr,data)
#         self.proxy = proxy
#         self.addr = addr
#         self.data = data
#         super().__init__()

#     def connection_made(self, transport):
#         self.transport = transport
#         self.transport.sendto(self.data)

#     def datagram_received(self, data, _):
#         self.proxy.transport.sendto(data, self.addr)

#     def connection_lost(self, exc):
#         self.proxy.remotes.pop(self.attr)


# async def start_datagram_proxy(protocol_class, bind, port, remote_host, remote_port):
#     loop = asyncio.get_event_loop()
#     protocol = protocol_class((remote_host, remote_port))
#     return await loop.create_datagram_endpoint(
#         lambda: protocol, local_addr=(bind, port))


# def main(bind='0.0.0.0', port=8888,
#         remote_host='0.0.0.0', remote_port=9999):
#     loop = asyncio.get_event_loop()
#     print("Starting datagram proxy...")
#     coro = start_datagram_proxy(bind, port, remote_host, remote_port)
#     transport, _ = loop.run_until_complete(coro)
#     print("Datagram proxy is running...")
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#     print("Closing transport...")
#     transport.close()
#     loop.close()



# log = logging.getLogger('kademlia')  # pylint: disable=invalid-name



# class KadProtocol(KademliaProtocol):
#     # remote_address = PROXY_ADDR
#     # REMOTES_D={}

#     # def __init__(self, source_node, storage, ksize):
#     #     RPCProtocol.__init__(self,wait_timeout=5)
#     #     self.router = RoutingTable(self, ksize, source_node)
#     #     self.storage = storage
#     #     self.source_node = source_node

#     # def datagram_received(self, data, addr):
#     #     #if not hasattr(self,'remotes_d'): self.remotes_d={}
#     #     # print('\n\n!?!?!?',self.REMOTES_D, type(self.REMOTES_D))
#     #     # if addr in self.REMOTES_D:
#     #     #     self.REMOTES_D[addr].transport.sendto(data)
#     #     #     return
#     #     loop = asyncio.get_event_loop()
#     #     # self.REMOTES_D[addr] = RemoteDatagramProtocol(self, addr, data)
#     #     RDP = RemoteDatagramProtocol(self, addr, data)
#     #     coro = loop.create_datagram_endpoint(lambda: RDP, remote_addr=self.remote_address)
#     #     asyncio.ensure_future(coro)

#     def handle_call_response(self, result, node):
#         """
#         If we get a response, add the node to the routing table.  If
#         we get no response, make sure it's removed from the routing table.
#         """
#         if not result[0]:
#             log.warning("no response from %s, ?removing from router", node)
#             self.router.remove_contact(node)
#             return result

#         log.info("got successful response from %s", node)
#         self.welcome_if_new(node)
#         return result



# class KadServer(Server):
#     protocol_class = KademliaProtocol # KadProtocol #KademliaProtocol

#     # def __init__(self, *x, **y):
#     #     self.storage = y['storage']
#     #     # raise Exception(str(self.storage))
#     #     super().__init__(*x,**y)
#     #     log.info(f'Storage has {len(self.storage.data)} keys')

#     def __repr__(self):
#         repr = f"""
#         KadServer()
#             ksize = {self.ksize}
#             alpha = {self.alpha}
#             storage = {len(self.storage.data)} keys
#             node = {self.node}
#             transport = {self.transport}
#             protocol = {self.protocol}
#             refresh_loop = {self.refresh_loop}
#             save_state_loop = {self.save_state_loop}
#             bootstrappable_neighbors = {self.bootstrappable_neighbors()}
#         """
#         return repr



#     # async def get(self, key):
#     #     """
#     #     Get a key if the network has it.

#     #     Returns:
#     #         :class:`None` if not found, the value otherwise.
#     #     """
#     #     log.info("Looking up key %s", key)
#     #     dkey = digest(key)
#     #     # if this node has it, return it
#     #     if self.storage.get(dkey) is not None:
#     #         log.info('I already have this')
#     #         return self.storage.get(dkey)
#     #     node = Node(dkey)
#     #     nearest = self.protocol.router.find_neighbors(node)
#     #     log.info(f'My nearest nodes are: {nearest}')
#     #     if not nearest:
#     #         log.warning("There are no known neighbors to get key %s", key)
#     #         return None
#     #     spider = ValueSpiderCrawl(self.protocol, node, nearest,
#     #                               self.ksize, self.alpha)
#     #     found = await spider.find()

#     #     log.info(f'spider done crawling: {spider}')
#     #     log.info(f'spider found value: {found}')

#     #     self.storage[dkey]=found
#     #     return found

#     # async def set(self, key, value):
#     #     """
#     #     Set the given string key to the given value in the network.
#     #     """
#     #     if not check_dht_value_type(value):
#     #         raise TypeError(
#     #             "Value must be of type int, float, bool, str, or bytes"
#     #         )
#     #     log.info("setting '%s' = '%s' on network", key, value)
#     #     dkey = digest(key)

#     #     print('STORE??',type(self.storage),self.storage)
#     #     self.storage.set(dkey,value)
#     #     return await self.set_digest(dkey, value)

#     # async def set_digest(self, dkey, value):
#     #     """
#     #     Set the given SHA1 digest key (bytes) to the given value in the
#     #     network.
#     #     """
#     #     node = Node(dkey)

#     #     nearest = self.protocol.router.find_neighbors(node)
#     #     if not nearest:
#     #         log.warning("There are no known neighbors to set key %s",
#     #                     dkey.hex())
#     #         #return False

#     #     spider = NodeSpiderCrawl(self.protocol, node, nearest,
#     #                              self.ksize, self.alpha)
#     #     nodes = await spider.find()
#     #     log.info("setting '%s' on %s", dkey.hex(), list(map(str, nodes)))

#     #     # if this node is close too, then store here as well
#     #     neighbs=[n.distance_to(node) for n in nodes]
#     #     log.info('setting on %s neighbors', neighbs)
#     #     biggest = max(neighbs) if neighbs else 0
#     #     log.info('my distance to node is %s, biggest distance is %s',
#     #              self.node.distance_to(node),biggest)
#     #     if self.node.distance_to(node) < biggest:
#     #         self.storage.set(dkey,value)
        
#     #     log.info('here are the nodes %s' % nodes)
#     #     results = [self.protocol.call_store(n, dkey, value) for n in nodes]
#     #     log.info('here are the results')

#     #     # return true only if at least one store call succeeded
#     #     return any(await asyncio.gather(*results))



# #### NEVERMIND
# # KadServer = Server

# import time
# if __name__=='__main__':
#     # test
#     hfs = HalfForgetfulStorage(fn='test.db')

#     #hfs['a']=1
#     # time.sleep(2)
#     hfs['a']=1000

#     print(hfs['a'])


#     print(hfs['a'])