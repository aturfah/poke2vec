import requests
from bs4 import BeautifulSoup
import json
import datetime
from pathlib import Path

import config

CONFIG = config.TestTeamConfig()

def parse_battle_urls(page_url):
    output = []

    r = requests.get(page_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    all_list_elts = soup.find_all("li")

    for l_elt in all_list_elts:
        link = l_elt.a
        if "data-target" in link.attrs and link.attrs["data-target"] != "push":
            continue

        output.append(link.attrs["href"])

    # print("{url}: {num}".format(url=page_url, num=len(output)))
    return output


def parse_teams(battle_json_url):
    r = requests.get(battle_json_url)
    battle_json = json.loads(r.text)

    battle_time = datetime.datetime.fromtimestamp(battle_json["uploadtime"])
    # Only consider teams from or after the desired date
    if battle_time <  datetime.datetime(CONFIG.year, CONFIG.month, 1):
        raise RuntimeError("Date too early: {}".format(battle_json_url))

    battle_log = str(battle_json["log"]).splitlines()

    p1_team = []
    p2_team = []
    for line in battle_log:
        components = line.split("|")[1:]
        if not components:
            continue

        if components[0] != "poke":
            continue

        poke = components[2]
        if "," in poke:
            poke = poke.split(",")[0]

        if components[1] == "p1":
            p1_team.append(poke)
        elif components[1] == "p2":
            p2_team.append(poke)

        if len(p1_team) >= 6 and len(p2_team) >= 6:
            break

    if len(p1_team) != 6 or len(p2_team) != 6:
        raise RuntimeError("Invalid Team Length: {}".format(battle_json_url))

    return [p1_team, p2_team]


def main():
    base_url = "https://replay.pokemonshowdown.com/search/?format={}&rating&output=html&page={}"
    page_num = 0
    battle_urls = []
    while True:
        new_url = base_url.format(CONFIG.tier, page_num)

        try:
            battle_urls.extend(parse_battle_urls(new_url))
        except Exception as exc:
            break

        page_num += 1

    print("# Battles to check: {}".format(len(battle_urls)))

    base_url = "https://replay.pokemonshowdown.com{}.json"
    teams = []
    counter = 0
    for battle_id in battle_urls:
        counter += 1
        battle_log_url = base_url.format(battle_id)
        try:
            teams.extend(parse_teams(battle_log_url))
        except Exception as exc:
            pass

        print("Battle URL # {} | # Teams: {}".format(counter, len(teams)), end="\r")

    print("Battle URL # {} | # Teams: {}".format(counter, len(teams)))

    # Write teams to file
    out_full_path = Path(config.TEAMS_TXT_DIR).joinpath(CONFIG.out_file)
    with open(out_full_path, "w") as out_file:
        teams_joined = [",".join(x + ["1"]) for x in teams]
        out_file.writelines(["{}\n".format(x) for x in teams_joined])

    print("FINISHED!!!")

if __name__ == "__main__":
    main()
