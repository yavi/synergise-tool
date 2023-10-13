import sys

if __name__ == "__main__":
    argc = len(sys.argv)
    filename = sys.argv[1]

    with open(filename, "r") as file:
        while line := file.read(49000):
            print(f"\n\n{line}\n\n")
