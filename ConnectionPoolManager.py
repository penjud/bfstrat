import queue
import threading
import logging

class ConnectionPoolManager:
    def __init__(self, max_connections):
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.active_connections = 0 # Counter for active connections
        self.logger = logging.getLogger(__name__) # Logger instance

    def get_connection(self):
        with self.lock:
            if not self.pool.empty():
                self.active_connections += 1 # Increment counter
                self.logger.info(f"Active connections: {self.active_connections}")
                return self.pool.get()
            else:
                # Create a new connection if the pool is empty
                new_connection = self.create_new_connection()
                self.active_connections += 1 # Increment counter
                self.logger.info(f"Active connections: {self.active_connections}")
                return new_connection

    def return_connection(self, connection):
        with self.lock:
            if not self.pool.full():
                self.pool.put(connection)
                self.active_connections -= 1 # Decrement counter
                self.logger.info(f"Active connections: {self.active_connections}")

def create_new_connection(self):
        # Implement your logic to create a new connection to Betfair API
        pass

def close_all_connections(self):
        with self.lock:
            while not self.pool.empty():
                connection = self.pool.get()
                # Implement your logic to close the connection
                self.close_connection(connection)

def close_connection(self, connection):
        # Implement your logic to close a single connection
        pass