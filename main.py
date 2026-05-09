import os
import time
import news
import argparse
import trackers
import fundamentals

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fundamentals",action="store_true")
parser.add_argument("-r","--refresh",action="store_true")
parser.add_argument("-n","--news",action="store_true")
args = parser.parse_args()

if args.fundamentals:
    fundamentals.run()
elif args.refresh:
    while True:
        os.system("clear")
        trackers.run()
        time.sleep(300)
elif args.news:
    news.run()
else:
    trackers.run()