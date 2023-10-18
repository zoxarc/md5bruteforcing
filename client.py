from multiprocessing import Process, cpu_count
from socket          import create_connection
from select          import select
from hashlib         import md5
from protocol        import send, recv, SECRET_LEN, IDENT_LEN, ADDR

# the protocol has the following options:
# W - sent from client, new worker, the client requests a work identifier
# S - sent form client, solution is found
# C - sent from client, confirms that the ident doesn't have the solution
# F - sent from server, tells client to terminate

def task():
  try: 
    sock = create_connection(ADDR)
    send(sock, b"W")
    target, work_iden = recv(sock).split(b'\n\n')
  except (ConnectionRefusedError, ConnectionResetError, ValueError): return True

  work = (str(x).encode() + work_iden for x in range(10**(SECRET_LEN - IDENT_LEN))) 
  for x in work:
    if select([sock], [], [], 0)[0] == [sock]: # this means that someone found a solution
      _ = recv(sock)
      return True

    if md5(x).digest() == target:
      send(sock, b"S\n\n" + x)
      return True

  send(sock, b"C\n\n" + work_iden)
  sock.close()
  return False


UNLIMITED = -2
def run_task(iterations = UNLIMITED):
  iterations += 1
  while (iterations == -1) or ((iterations := iterations - 1) > 0):
    if task(): return


def main():
  p_list = []
  for _ in range(cpu_count()):
    p = Process(target=run_task)
    p.start()
    p_list.append(p)
  for p in p_list:
    p.join()

if __name__ == "__main__":
  main()

