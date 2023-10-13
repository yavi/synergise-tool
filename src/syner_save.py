import base64
import sys

if __name__ == "__main__":
    argc = len(sys.argv)
    filename = sys.argv[1]

    with open(filename, "rb") as file:
        encoded = file.read()
        decoded = base64.b64decode(encoded)
        decoded_str = decoded.decode('utf-8')
        print(decoded_str)
