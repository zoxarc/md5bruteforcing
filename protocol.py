# the protocol has the following options:
# W - sent from client, new worker, the client requests a work identifier, which is a three digit number
# S - sent form client, solution is found
# C - sent from client, confirms that the ident doesn't have the solution
# F - sent from server, tells client to terminate

IDENT_LEN = 3
SECRET_LEN = 10
ADDR = ('127.0.0.1', 8880)

def send(sock, data: bytes):
  sock.send(str(len(data)).ljust(1024).encode() + data)

def recv(sock):
  length = sock.recv(1024).decode()
  while len(length) < 1024:#pyright:ignore
    length += sock.recv(1024).decode()
  length = int(length.translate({' ': ''}))#pyright:ignore
  if not length:
    return b'\n\n'
  data = sock.recv(length)
  while len(data) < length:
    data += data
  return data
