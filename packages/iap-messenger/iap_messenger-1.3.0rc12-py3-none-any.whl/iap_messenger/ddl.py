import gc
import zmq
import threading
import logging

LOGGER = logging.getLogger(__name__)

class DDL:
    """
    DDL (Data Distribution Layer) class using PyZMQ for client-server communication
    to store and retrieve byte data based on UIDs.
    """
    def __init__(self, host: str = "*", port: int = 5555):
        """
        Initializes the DDL service with ZMQ context and server socket.

        Args:
            host (str): The host address to bind the server socket. Default is "*", which binds to all interfaces.
            port (int): The port number for communication. Default is 5555.
        """
        self.context = zmq.Context()
        self.datastore: dict[str, bytes] = {}

        self.server_address = f"tcp://*:{port}"
        self.address = f"{host}:{port}"
        self.server_socket = self.context.socket(zmq.REP)
        self.server_socket.bind(self.server_address)
        LOGGER.info(f"DDL Server socket bound to {self.server_address}")
        self._stop_event = threading.Event()
        self.server_thread: threading.Thread | None = None

    def store_data_in_datastore(self, uid: str, data: bytes) -> None:
        """
        Stores byte data in the DDL's in-memory datastore.
        This is typically called on the instance that will run the server
        or an instance that shares the datastore dict.

        Args:
            uid (str): The unique identifier for the data.
            data (bytes): The byte data to store.
        """
        self.datastore[uid] = data
        LOGGER.debug(f"Data stored in local datastore for UID: {uid} (size: {len(data)} bytes)")

    def _server_loop(self) -> None:
        """
        The main loop for the server. Listens for requests and responds.
        This method is intended to be run in a separate thread.
        """
        LOGGER.info(f"DDL Server listening on {self.server_address}...")
        poller = zmq.Poller()
        poller.register(self.server_socket, zmq.POLLIN)

        while not self._stop_event.is_set():
            try:
                # Poll for incoming messages with a timeout to allow checking _stop_event
                socks = dict(poller.poll(timeout=10000))  # 10 second timeout
                if self.server_socket in socks and socks[self.server_socket] == zmq.POLLIN:
                    uid_request = self.server_socket.recv_string()
                    LOGGER.debug(f"Server received request for UID: '{uid_request}'")

                    if uid_request in self.datastore:
                        data_to_send = self.datastore[uid_request]
                        self.server_socket.send(data_to_send)
                        LOGGER.debug(f"Server sent data for UID: '{uid_request}' (size: {len(data_to_send)} bytes)")
                        del self.datastore[uid_request]  # remove after sending
                        gc.collect()  # Suggest garbage collection
                    else:
                        error_message = f"ERROR: UID '{uid_request}' not found in datastore."
                        self.server_socket.send_string(error_message)
                        LOGGER.warning(f"Server: UID '{uid_request}' not found.")
                else:
                    if self._stop_event.is_set():
                        LOGGER.info("Server loop: Stop event set, exiting loop.")
                        break
            except zmq.error.ContextTerminated:
                LOGGER.info("Server loop: ZMQ Context terminated, stopping.")
                break
            except zmq.error.ZMQError as e:
                if e.errno == zmq.ETERM:
                    LOGGER.info("Server loop: ZMQ Context terminated, stopping.")
                    break
                else:
                    LOGGER.error(f"ZMQ error in server loop: {e}", exc_info=True)
                    try:
                        self.server_socket.send_string("ERROR: Server encountered a ZMQ issue.")
                    except zmq.error.ZMQError as zmq_e:
                        LOGGER.error(f"Server error: Could not send error reply: {zmq_e}")

            except Exception as e:
                LOGGER.error(f"Server error: {e}", exc_info=True)
                try:
                    if not self.server_socket.closed:
                         self.server_socket.send_string("ERROR: Server encountered an internal issue.")
                except zmq.error.ZMQError as zmq_e:
                    LOGGER.error(f"Server error: Could not send error reply: {zmq_e}")
                break # Exit loop on unexpected errors

        LOGGER.info("DDL Server loop has stopped.")

    def start_server(self) -> None:
        """
        Starts the DDL server in a new daemon thread.
        If the server is already running, this method does nothing.
        """
        LOGGER.info("Starting DDL Server thread...")
        if self.server_thread is None or not self.server_thread.is_alive():
            self._stop_event.clear()
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            LOGGER.info("DDL Server thread started.")
        else:
            LOGGER.info("DDL Server is already running.")

    def stop_server(self) -> None:
        """
        Signals the server thread to stop and waits for it to join.
        """
        if self.server_thread and self.server_thread.is_alive():
            LOGGER.info("Stopping DDL Server thread...")
            self._stop_event.set()
            self.server_thread.join(timeout=5)
            if self.server_thread.is_alive():
                LOGGER.warning("DDL Server thread did not stop in time.")
            else:
                LOGGER.info("DDL Server thread stopped successfully.")
        else:
            LOGGER.info("DDL Server is not running or thread already stopped.")

    def get_data_from_server(self, uid: str, client: str, timeout_ms: int = 5000) -> tuple[bytes, str | None]:
        """
        Client method to request data from the DDL server.
        A new client socket is created, connected, used, and closed for each call.

        Args:
            uid (str): The UID of the data to retrieve.
            address (str)   : The address (e.g., "tcp://localhost:5555" or "localhost:5555")
                                  for the client socket to connect to.
            timeout_ms (int): Timeout in milliseconds for the request.

        Returns:
            tuple[bytes | None, str | None]: A tuple (data, error_message).
            - If data is found: (data_bytes, None)
            - If error (UID not found, timeout, etc.): (None, error_string)
        """
        client_address = f"tcp://{client}" if not client.startswith("tcp://") else client
        if not uid:
            error_msg = "Client UID cannot be empty."
            LOGGER.error(error_msg)
            return b"", error_msg
        if not client_address:
            error_msg = "Client address cannot be empty."
            LOGGER.error(error_msg)
            return b"", error_msg
        LOGGER.debug(f"Client attempting to connect to {client_address} for UID: '{uid}'")

        client_socket = None  # Ensure client_socket is defined for the finally block
        try:
            client_socket = self.context.socket(zmq.REQ)
            # Set LINGER to 0 to close immediately and not block on pending messages
            client_socket.setsockopt(zmq.LINGER, 0)
            client_socket.connect(client_address)
            LOGGER.debug(f"Client socket connected to {client_address}")

            poller = zmq.Poller()
            poller.register(client_socket, zmq.POLLIN)

            client_socket.send_string(uid, flags=zmq.NOBLOCK)

            socks = dict(poller.poll(timeout=timeout_ms))
            if client_socket in socks and socks[client_socket] == zmq.POLLIN:
                response = client_socket.recv()
                try:
                    decoded_response = response.decode('utf-8')
                    if decoded_response.startswith("ERROR:"):
                        LOGGER.warning(f"Client received error from server: {decoded_response}")
                        return b"", decoded_response
                except UnicodeDecodeError:
                    # Not a UTF-8 string, assume it's binary data
                    pass

                LOGGER.debug(f"Client received data for UID: '{uid}' (size: {len(response)} bytes)")
                return response, None
            else:  # Timeout
                error_msg = f"Client timeout: No response for UID '{uid}' from {client_address} within {timeout_ms}ms."
                LOGGER.warning(error_msg)
                return b"", error_msg

        except zmq.error.ZMQError as e:
            error_msg = f"Client ZMQError while requesting UID '{uid}' from {client_address}: {e}"
            LOGGER.error(error_msg, exc_info=True)
            return b"", error_msg
        except Exception as e:  # Catch any other unexpected errors
            error_msg = f"Client general exception while requesting UID '{uid}' from {client_address}: {e}"
            LOGGER.error(error_msg, exc_info=True)
            return b"", error_msg
        finally:
            if client_socket and not client_socket.closed:
                client_socket.close()
                LOGGER.debug(f"Client socket to {client_address} closed.")

    def close(self) -> None:
        """
        Stops the server and cleans up ZMQ resources (server socket and context).
        """
        LOGGER.info("Closing DDL resources...")
        self.stop_server()

        # Client sockets are now managed per-call in get_data_from_server
        if hasattr(self, 'server_socket') and self.server_socket and not self.server_socket.closed:
            self.server_socket.close(linger=0)  # linger=0 to close immediately
            LOGGER.info("DDL server_socket closed.")

        if not self.context.closed:
            self.context.term()
            LOGGER.info("ZMQ context terminated.")
        else:
            LOGGER.info("ZMQ context already terminated or closed.")

if __name__ == '__main__':
    # Basic logging setup for the example
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s')

    LOGGER.info("Starting DDL example...")

    server_host_for_client = "localhost"
    server_port = 5556

    ddl_service = DDL(port=server_port)
    ddl_service.start_server()

    threading.Event().wait(0.5) # Give server time to start

    client_connect_address = f"tcp://{server_host_for_client}:{server_port}"

    ddl_service.store_data_in_datastore("uid123", b"Hello ZMQ World!")
    ddl_service.store_data_in_datastore("uid456", b"Another piece of data.")

    data, error = ddl_service.get_data_from_server("uid123", client_connect_address)
    if error:
        LOGGER.error(f"Failed to get uid123: {error}")
    else:
        LOGGER.info(f"Got data for uid123: {data.decode() if data else 'None'}")

    data, error = ddl_service.get_data_from_server("uid456", client_connect_address)
    if error:
        LOGGER.error(f"Failed to get uid456: {error}")
    else:
        LOGGER.info(f"Got data for uid456: {data.decode() if data else 'None'}")

    data, error = ddl_service.get_data_from_server("uid789_nonexistent", client_connect_address)
    if error:
        LOGGER.warning(f"Correctly failed to get uid789_nonexistent: {error}")
    else:
        LOGGER.error(f"Incorrectly got data for uid789_nonexistent: {data.decode() if data else 'None'}")

    LOGGER.info("Testing client timeout (this will take ~2 seconds)...")
    data, error = ddl_service.get_data_from_server("uid_timeout_test", client_connect_address, timeout_ms=2000)
    if error and "timeout" in error.lower():
        LOGGER.info(f"Correctly timed out for uid_timeout_test: {error}")
    elif error:
        LOGGER.error(f"Timeout test failed with an unexpected error: {error}")
    else:
        LOGGER.error(f"Timeout test failed. Expected timeout, but got data: {data.decode() if data else 'None'}")

    LOGGER.info("Shutting down DDL service...")
    ddl_service.close()
    LOGGER.info("DDL example finished.")


