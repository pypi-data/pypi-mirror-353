from socket import socket as Socket
from dataclasses import dataclass

@dataclass(slots=True)
class Client:
    socket: Socket

    def send(self, message: str) -> str:
        data: bytes = message.encode(encoding='UTF-8')
        size: bytes = f'{len(data):16}'.encode(encoding='UTF-8')
        self.socket.send(size)
        self.socket.send(data)
        while True:
            recv_size: int = int(self.socket.recv(16).decode(encoding='UTF-8').strip())
            recv_message: str = self.socket.recv(recv_size).decode(encoding='UTF-8')
            return recv_message

    def close(self) -> None:
        self.socket.close()