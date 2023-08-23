from src.server import SimpleServer
import sys

if __name__ == "__main__":
    server = SimpleServer()
    server.start()
    sys.exit()