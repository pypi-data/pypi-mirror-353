from socket import socket as Socket, AddressFamily, SocketKind
from contextlib import contextmanager
from typing import Generator
from j2pipeline.tcp.client import Client

@contextmanager
def client(host: str = 'localhost',
           port: int = 50027) -> Generator[Client, None, None]:
    socket: Socket = Socket(family=AddressFamily.AF_INET,
                            type=SocketKind.SOCK_STREAM)
    socket.connect((host, port))
    client: Client = Client(socket=socket)
    try:
        yield client
    finally:
        client.close()