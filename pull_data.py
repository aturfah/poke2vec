"""
Pull Data from smogon server for given month
"""

import requests
import argparse

from os.path import join, isfile
import json
import config
from config import PullDataConfig

def parse_args(pd_conf):
    parser = argparse.ArgumentParser(
        description="Pull down data from smogon.com/stats")
    parser.add_argument("--tiers", metavar="N", type=str, nargs="+",
                        default=pd_conf.defaultTier)
    parser.add_argument("--levels", metavar="N", type=str, nargs="+",
                        default=pd_conf.defaultLevel)
    parser.add_argument("--months", metavar="N", type=str, nargs="+",
                        default=pd_conf.defaultMonth)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    pd_conf = PullDataConfig()
    args = parse_args(pd_conf)

    chosen_tiers = args.tiers
    chosen_levels = args.levels
    chosen_month = args.months

    base_url = "https://www.smogon.com/stats/{month}/chaos/{tier}-{level}.json"
    base_fname = "{month}_{tier}_{level}.json"

    for month in chosen_month:
        for tier in chosen_tiers:
            for level in chosen_levels:
                mod_url = base_url.format(month=month, tier=tier, level=level)
                mod_fname = join(config.DATA_DIR, base_fname.format(month=month, tier=tier, level=level))

                if isfile(mod_fname):
                    print("File already exists: {}".format(mod_fname))
                    continue

                print("Sending request to: {}".format(mod_url))

                req = requests.get(mod_url)
                if req.status_code != 200:
                    print("\tSkipping invalid URL: {}".format(mod_url))
                    continue

                print("\tWriting File: {}".format(mod_fname))
                with open(mod_fname, 'w') as out_file:
                    out_file.write( json.dumps(req.json()) )

    print("Completed!")
