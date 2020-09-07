import socket
import sys
import tty
import termios
import threading


class Server(object):
    def __init__(self, port):
        self.socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socks.bind(('0.0.0.0', port))
        self.socks.listen(5)

        print('Listening port {} ...'.format(port))

    def run(self):
        talk, addr = self.socks.accept()
        print('connection from', addr)
        print('Please start your show with the system commands')

        t1 = threading.Thread(target=self.send_input, args=(talk,))
        t1.start()

        t2 = threading.Thread(target=self.display, args=(talk,))
        t2.start()

        t1.join()
        t2.join()

    def read_char(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def display(self, talk):
        while True:
            new_content = talk.recv(4096).strip()
            if new_content:
                print(new_content.decode().replace('\n', '\r\n'), flush=True)
                print('\r')
                # print('\r\n> ', end='', flush=True)

    def send_input(self, talk):
        while True:
            char = self.read_char()

            # if it's ENTER
            if char == '\r':
                char = '\n'

            print('{char}', end='', flush=True)
            talk.send(char.encode())

    def __del__(self):
        self.socks.close()


def main():
    s = Server(2333)
    s.run()


if __name__ == "__main__":
    main()
