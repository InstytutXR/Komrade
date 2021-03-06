"""
Package for interacting on the network at a high level.
"""
STORE_ANYWHERE=True


import random
import pickle
import asyncio
import logging

class CannotReachNetworkError(Exception): pass

from kademlia.protocol import KademliaProtocol
from kademlia.utils import digest
from kademlia.storage import HalfForgetfulStorage
from kademlia.node import Node
from kademlia.crawling import ValueSpiderCrawl
from kademlia.crawling import NodeSpiderCrawl

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


# pylint: disable=too-many-instance-attributes
class Server:
    """
    High level view of a node instance.  This is the object that should be
    created to start listening as an active node on the network.
    """

    protocol_class = KademliaProtocol

    @property
    def logger(self):
        if not hasattr(self,'_logger'):
            import logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger = logger = logging.getLogger(self.title)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        return self._logger

    def __init__(self, ksize=20, alpha=3, node_id=None, storage=None,log=None):
        """
        Create a server instance.  This will start listening on the given port.

        Args:
            ksize (int): The k parameter from the paper
            alpha (int): The alpha parameter from the paper
            node_id: The id for this node on the network.
            storage: An instance that implements the interface
                     :class:`~kademlia.storage.IStorage`
        """
        self.ksize = ksize
        self.alpha = alpha
        self.log = log if log is not None else self.logger.debug

        self.storage = HalfForgetfulStorage() #storage or ForgetfulStorage()
        print('[Server] storage loaded with %s keys' % len(self.storage.data))
        self.node = Node(node_id or digest(random.getrandbits(255)))
        self.transport = None
        self.protocol = None
        self.refresh_loop = None
        self.save_state_loop = None

        ## echo
        #self.re_echo()

    #def re_echo(self):
    #    return [asyncio.create_task(self.set_digest(k,v)) for k,v in self.storage.items()]

    def __repr__(self):
        neighbs=self.bootstrappable_neighbors()
        neighbors=' '.join(':'.join(str(x) for x in ip_port) for ip_port in neighbs)
        repr = f"""storing {len(self.storage.data)} keys and has {len(neighbs)} neighbors""" #:\n\t{neighbors}"""
        return repr



    def stop(self):
        if self.transport is not None:
            self.transport.close()

        if self.refresh_loop:
            self.refresh_loop.cancel()

        if self.save_state_loop:
            self.save_state_loop.cancel()

    def _create_protocol(self):
        return self.protocol_class(self.node, self.storage, self.ksize, self.log)

    async def listen(self, port, interface='0.0.0.0'):
        """
        Start listening on the given port.

        Provide interface="::" to accept ipv6 address
        """
        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(self._create_protocol,
                                               local_addr=(interface, port))
        self.log("Node %i listening on %s:%i" % (self.node.long_id, interface, port))
        self.transport, self.protocol = await listen
        # finally, schedule refreshing table
        self.refresh_table()

    def refresh_table(self):
        self.log("Refreshing routing table")
        asyncio.ensure_future(self._refresh_table())
        loop = asyncio.get_event_loop()
        self.refresh_loop = loop.call_later(3600, self.refresh_table)

    async def _refresh_table(self):
        """
        Refresh buckets that haven't had any lookups in the last hour
        (per section 2.3 of the paper).
        """
        results = []
        for node_id in self.protocol.get_refresh_ids():
            node = Node(node_id)
            nearest = self.protocol.router.find_neighbors(node, self.alpha)
            spider = NodeSpiderCrawl(self.protocol, node, nearest,
                                     self.ksize, self.alpha)
            spider.log=self.log
            results.append(spider.find())

        # do our crawling
        await asyncio.gather(*results)

        # now republish keys older than one hour
        # repub_every=3600
        repub_every=3600
        for dkey, value in self.storage.iter_older_than(repub_every):
            await self.set_digest(dkey, value)

    def bootstrappable_neighbors(self):
        """
        Get a :class:`list` of (ip, port) :class:`tuple` pairs suitable for
        use as an argument to the bootstrap method.

        The server should have been bootstrapped
        already - this is just a utility for getting some neighbors and then
        storing them if this server is going down for a while.  When it comes
        back up, the list of nodes can be used to bootstrap.
        """
        neighbors = self.protocol.router.find_neighbors(self.node)
        return [tuple(n)[-2:] for n in neighbors]

    async def bootstrap(self, addrs):
        """
        Bootstrap the server by connecting to other known nodes in the network.

        Args:
            addrs: A `list` of (ip, port) `tuple` pairs.  Note that only IP
                   addresses are acceptable - hostnames will cause an error.
        """
        self.log("Attempting to bootstrap node with %i initial contacts",
                  len(addrs))
        cos = list(map(self.bootstrap_node, addrs))
        gathered = await asyncio.gather(*cos)
        nodes = [node for node in gathered if node is not None]
        spider = NodeSpiderCrawl(self.protocol, self.node, nodes,
                                 self.ksize, self.alpha)
        spider.log=self.log
        return await spider.find()

    async def bootstrap_node(self, addr):
        result = await self.protocol.ping(addr, self.node.id)
        return Node(result[1], addr[0], addr[1]) if result[0] else None

    async def get(self, key, store_anywhere=STORE_ANYWHERE):
        """
        Get a key if the network has it.

        Returns:
            :class:`None` if not found, the value otherwise.
        """
        dkey = digest(key)
        self.log("Looking up key %s %s" % (key,dkey))
        
        # if this node has it, return it
        if self.storage.get(dkey) is not None:
            self.log(f'already have {key} ({dkey}) in storage, returning...')
            return self.storage.get(dkey)
        node = Node(dkey)
        self.log(f'creating node {node}')
        nearest = self.protocol.router.find_neighbors(node)
        self.log(f'nearest = {nearest}')
        if not nearest:
            raise CannotReachNetworkError("There are no known neighbors to get key %s" % key)


        found = None
        #while found is None:
        spider = ValueSpiderCrawl(self.protocol, node, nearest, self.ksize, self.alpha, log=self.log)
        self.log(f'spider crawling... {spider}')
        found = await spider.find()
        self.log('spider found <-',found,'for key',key,'(',dkey,')')
        #await asyncio.sleep(5)

        self.log(f"Eventually found for key {key} value {found}")
        # if not found:
            # return None
            #raise Exception('nothing found!')

        # # set it locally? @EDIT
        # if store_anywhere and found:
            # self.log(f'storing anywhere: {dkey} -> {found}')
        #     self.storage[dkey]=found
        
        return found

    async def set(self, key, value):
        """
        Set the given string key to the given value in the network.
        """
        if not check_dht_value_type(value):
            raise TypeError(
                "Value must be of type int, float, bool, str, or bytes"
            )
        self.log(f"setting '{key}' = '{value}' ({type(value)}) on network")

        dkey = digest(key)
        return await self.set_digest(dkey, value)

    async def set_digest(self, dkey, value, store_anywhere=STORE_ANYWHERE):
        """
        Set the given SHA1 digest key (bytes) to the given value in the
        network.
        """

        node = Node(dkey)
        self.log('set_digest()',node)

        nearest = self.protocol.router.find_neighbors(node)
        self.log('set_digest() nearest -->',nearest)
        if not nearest:
            self.log("There are no known neighbors to set key %s" % dkey.hex())
            return False

        spider = NodeSpiderCrawl(self.protocol, node, nearest,
                                 self.ksize, self.alpha, log=self.log)

        nodes = await spider.find()
        self.log(f"setting '%s' on %s" % (dkey.hex(), list(map(str, nodes))))

        # if this node is close too, then store here as well
        biggest = max([n.distance_to(node) for n in nodes])
        if self.node.distance_to(node) < biggest:
            self.log(f'< bigges -> {dkey} --> {value}')
            self.storage[dkey] = value


        results = [self.protocol.call_store(n, dkey, value) for n in nodes]
        results = await asyncio.gather(*results)
        self.log(f'--> set() results --> {results}')
        
        if store_anywhere:
            self.log(f'store_anywhere -> {dkey} --> {value}')
            self.storage[dkey]=value
        
        # return true only if at least one store call succeeded
        return any(results)

    def save_state(self, fname):
        """
        Save the state of this node (the alpha/ksize/id/immediate neighbors)
        to a cache file with the given fname.
        """
        self.log("Saving state to %s" % fname)
        data = {
            'ksize': self.ksize,
            'alpha': self.alpha,
            'id': self.node.id,
            'neighbors': self.bootstrappable_neighbors()
        }
        if not data['neighbors']:
            self.log("No known neighbors, so not writing to cache.")
            return
        with open(fname, 'wb') as file:
            pickle.dump(data, file)

    @classmethod
    async def load_state(cls, fname, port, interface='0.0.0.0'):
        """
        Load the state of this node (the alpha/ksize/id/immediate neighbors)
        from a cache file with the given fname and then bootstrap the node
        (using the given port/interface to start listening/bootstrapping).
        """
        self.log("Loading state from %s" % fname)
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        svr = Server(data['ksize'], data['alpha'], data['id'])
        await svr.listen(port, interface)
        if data['neighbors']:
            await svr.bootstrap(data['neighbors'])
        return svr

    def save_state_regularly(self, fname, frequency=600):
        """
        Save the state of node with a given regularity to the given
        filename.

        Args:
            fname: File name to save retularly to
            frequency: Frequency in seconds that the state should be saved.
                        By default, 10 minutes.
        """
        self.save_state(fname)
        loop = asyncio.get_event_loop()
        self.save_state_loop = loop.call_later(frequency,
                                               self.save_state_regularly,
                                               fname,
                                               frequency)


def check_dht_value_type(value):
    """
    Checks to see if the type of the value is a valid type for
    placing in the dht.
    """
    typeset = [
        int,
        float,
        bool,
        str,
        bytes
    ]
    return type(value) in typeset  # pylint: disable=unidiomatic-typecheck
