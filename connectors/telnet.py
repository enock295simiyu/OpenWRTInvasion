import logging
import socket
import time

from netmiko import ConnectHandler, TelnetFallback

from .base import BaseConnector

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("netmiko")

class SshTelnetConnector(BaseConnector):
    def __init__(self,params,addresses, **kwargs):
        super().__init__(params=params,addresses=addresses,**kwargs)
        self.port=params.get('port',23)
        self.device_type = 'linux'

    def _connect(self, address):
        params=self.params.copy()
        logger.info(address)
        print('Connecting to {}'.format(address))
        self.connection=TelnetFallback(
                    host=address,
                    conn_timeout=self.timeout,
                    device_type=self.device_type,
                    timeout= self.timeout,
                    global_delay_factor= 1.0,
                    **params

                )
        prompt = self.connection.find_prompt()
        logger.info(f"Connected to device. Prompt: {prompt}")
        time.sleep(1)

        if "login" in prompt.lower() or "username" in prompt.lower():
            self.exec_command(self.params.get('username'))
            time.sleep(1)

        prompt = self.connection.find_prompt()
        logger.info(f"Connected to device. Prompt: {prompt}")
        if "password" in prompt.lower():
            self.exec_command(self.params.get('username'))
            time.sleep(1)
        prompt = self.connection.find_prompt()
        logger.info(f"Connected to device. Prompt: {prompt}")

    @property
    def is_connected(self):
        if self.connection is None:
            return False
        return self.connection.is_alive()

    def _disconnect(self):
        if self.is_connected:
            self.connection.disconnect()
        self.connection = None

    def exec_command(
            self,
            command,
            timeout=None,
            exit_codes=None,
            raise_unexpected_exit=True,
    ):
        """
       Executes a command and performs the following operations
       - logs executed command
       - logs standard output
       - logs standard error
       - aborts on exceptions
       - raises socket.timeout exceptions
       """
        if exit_codes is None:
            exit_codes = [0]
        if timeout is None:
            timeout = self.timeout
        if not self.is_connected:
            self.connect()
        logger.debug(f'the connection is working"{self.is_connected}')
        logger.info(f"Executing command: {command}")

        try:
            response = self.connection.send_command(command, read_timeout=timeout, expect_string=r"#|\$")
        except socket.timeout:
            raise socket.timeout()

        # any other exception will abort the operation
        except Exception as e:
            logger.exception(e)
            raise e
        error = None
        logger.debug(response)
        if isinstance(response, str) and 'bad command' in response:
            exit_status = 1
            error = response
        else:
            exit_status = 0
        if response:
            logger.debug(response)

        # abort the operation if any of the command
        # returned with a non-zero exit status
        if exit_status not in exit_codes and raise_unexpected_exit:
            log_message = 'Unexpected exit code: {0}'.format(exit_status)
            logger.info(log_message)
            message = error if error else response
            # if message is empty, use log_message
            raise Exception(message or log_message)
        return response, exit_status

