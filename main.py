import argparse
import trackers
import fundamentals

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fundamentals",action="store_true")
args = parser.parse_args()

if args.fundamentals:
    fundamentals.run()
else:
    trackers.run()