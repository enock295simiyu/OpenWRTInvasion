import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("netmiko")



class BaseConnector:

    def __init__(self, params,addresses,timeout=50,**kwargs):
        self._params = params
        self.addresses = addresses
        try:
            self.hostname = addresses[0]
        except IndexError:
            self.hostname = '127.0.0.1'
        self.kwargs = kwargs
        self.connection = None
        self.timeout = timeout
        self.device_type = 'generic'

    @property
    def params(self):
        params = self._params.copy()
        return params

    @property
    def is_connected(self):
        raise NotImplementedError()

    def _connect(self, address):
        raise NotImplementedError()

    def connect(self):
        success = False
        exception = None
        addresses = self.addresses
        logger.info(f"Connecting to {addresses}")
        if not addresses:
            raise ValueError('No valid IP addresses to initiate connections found')
        if self.is_connected:
            # Do not establish a new connection if
            # a connection was already established.
            return
        for address in addresses:
            try:
                self.hostname = address
                self._connect(address)
                success = True
                break
            except Exception as e:
                time.sleep(2)
                exception = e

        if not success:
            self.disconnect()
            raise exception



    def disconnect(self):
        self._disconnect()

    def _disconnect(self):
        raise NotImplementedError()

    def exec_command(
            self,
            command,
            timeout=60,
            exit_codes=None,
            raise_unexpected_exit=True,
    ):
        raise NotImplementedError()




