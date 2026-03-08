import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio

from decision.buy_sel import main_loop 

if __name__ == "__main__":
    asyncio.run(main_loop())

