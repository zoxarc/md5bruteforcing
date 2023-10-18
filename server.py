from socket   import create_server
from select   import select
from sys      import argv
from protocol import send, recv, IDENT_LEN, ADDR
# the protocol has the following options:
# W - sent from client, new worker, the client requests a work identifier
# S - sent form client, solution is found
# C - sent from client, confirms that the ident doesn't have the solution
# F - sent from server, tells client to terminate


def terminate_socks(socks):
  for sock in socks:
    send(sock, b"F")
    sock.close()

def main():
  server = create_server(ADDR)
  # this is the queue of identifiers, each one is a unique number with IDENT_LEN digits
  # to make the server be able to spontenously lose clients it only removes the ident once the client finishes
  # while the client works it just pushes it to the end
  idents = [str(x).rjust(IDENT_LEN, '0').encode() for x in range(10**IDENT_LEN)]
  sockets = [server]
  target = bytes.fromhex(argv[1] if len(argv) > 1 else input("enter hash: "))
  while True:
    for sock in select(sockets, [], [])[0]:
      if sock == server:
        s, _ = server.accept()
        sockets.append(s)
        continue

      msg = recv(sock).split(b'\n\n')
      match msg:
        case [b'W']:
          send(sock, target + b'\n\n' + idents[0])
          idents.append(idents.pop(0)) # move the ident to the end of the list

        case [b'C', ident]:
          sockets.remove(sock); sock.close()
          idents.remove(ident)

        case [b'S', sol]:
          sockets.remove(sock); sock.close()
          terminate_socks(sockets[1:])
          server.close()

          print(f"The solution is {sol.decode()}!")
          return sol

if __name__ == "__main__":
  main()
