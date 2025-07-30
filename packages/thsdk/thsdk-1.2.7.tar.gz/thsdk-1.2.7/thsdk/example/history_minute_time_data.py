from thsdk import THS, Interval, Adjust
import pandas as pd
import time
from datetime import datetime
from zoneinfo import ZoneInfo

with THS() as ths:
    response = ths.historical_daily_minute_data("USHA600519", "20250605")
    print("历史当日分钟数据:")
    if response.errInfo != "":
        print(f"错误信息: {response.errInfo}")
    print(pd.DataFrame(response.payload.result))
    time.sleep(1)

