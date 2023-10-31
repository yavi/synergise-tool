import sys
from rich.prompt import Confirm

import pandas as pd

if __name__ == "__main__":
    argc = len(sys.argv)
    filename = sys.argv[1]

    with open(filename, "r") as file:
        while line := file.read(49000):
            print(f"\n\n{line}\n\n")
            df=pd.DataFrame([line])
            df.to_clipboard(index=False,header=False)
            if len(line) < 49000:
                break
            Confirm.ask("Next part?")
