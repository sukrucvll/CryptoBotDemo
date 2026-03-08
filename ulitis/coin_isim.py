import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo_db import get_db
zaman_dilimi = ['5m']

coin_listesi= [
'SOLUSDT'
]

