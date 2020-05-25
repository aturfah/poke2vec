"""
Generate Teams from Chaos files
"""

import argparse
import json
from os.path import join
from itertools import combinations
from operator import mul
from functools import reduce
from math import ceil, factorial
from time import time

from numpy.random import binomial

import config
from config import GenerateTeamsConfig

def parse_args(gt_conf):
    parser = argparse.ArgumentParser(
        description="Generate Teams from Chaos files")
    parser.add_argument("--files", metavar="N", type=str, nargs="+",
                        default=gt_conf.dataFiles)
    parser.add_argument("--thresholds", metavar="N", type=float, nargs="+",
                        default=gt_conf.thresholdLimit)
    args = parser.parse_args()
    return args


def generate_probabilities(chaos_conf, threshold):
    info = chaos_conf["info"]
    data = chaos_conf["data"]

    names = data.keys()

    # Figure out what count is
    ability_counts = {}
    for name in names:
        abilities = data[name]["Abilities"]
        ability_counts[name] = sum([abilities[x] for x in abilities.keys()])

    # Build Out Marginal Probability Mapping
    marginal_probs = {}
    for name in names:
        pct = data[name]["usage"]
        raw = ability_counts[name]

        if threshold > 1:
            if raw < threshold:
                continue
        elif threshold < 0:
            raise RuntimeError("Invalid Threshold")
        else:
            if pct < threshold:
                continue

        marginal_probs[name] = {
            "pct": pct,
            "raw": raw
        }

    info["ability_total"] = sum([ability_counts[x] for x in marginal_probs.keys()])


    # Build Out Conditional Probability Mapping
    # Matrix is of the form D[i][j] P(i | j)
    conditional_probs = {}
    for base_name in marginal_probs.keys():
        temp_map = {}
        for cond_name in marginal_probs.keys():
            if cond_name == base_name:
                continue
            # https://www.smogon.com/forums/threads/official-smogon-university-usage-statistics-discussion-thread-mk-2.3508502/
            teammate_score = data[base_name]["Teammates"].get(cond_name, None)
            teammate_infl_pct = 0
            teammate_cond_prob = marginal_probs[base_name]["pct"]
            if teammate_score is not None:
                teammate_infl_pct = teammate_score / marginal_probs[base_name]["raw"]
                teammate_cond_prob = teammate_cond_prob + teammate_infl_pct

            temp_map[cond_name] = {
                "score": teammate_score,
                "inflation": teammate_infl_pct,
                "prob": max(teammate_cond_prob, 0)
            }

        conditional_probs[base_name] = temp_map

    # Now make them valid distributions
    tot_marginal = sum([marginal_probs[name]["pct"] for name in marginal_probs.keys()])

    for name in marginal_probs.keys():
        marginal_probs[name]["pct"] = marginal_probs[name]["pct"] / tot_marginal

    # Construct joint distribution
    joint_dist = {}
    total_joint = 0
    for base_name in conditional_probs.keys():
        temp_map = {}
        for cond_name in conditional_probs[base_name].keys():
            temp_map[cond_name] = conditional_probs[base_name][cond_name]["prob"] * marginal_probs[cond_name]["pct"]
            total_joint += temp_map[cond_name]

        joint_dist[base_name] = temp_map

    # Use 'Normalized' joint to reconstruct conditional
    for base_name in conditional_probs.keys():
        temp_map = {}
        for cond_name in conditional_probs[base_name].keys():
            temp_map[cond_name] = conditional_probs[base_name][cond_name]
            temp_map[cond_name]["prob"] = joint_dist[base_name][cond_name] / (total_joint * marginal_probs[cond_name]["pct"])

        conditional_probs[base_name] = temp_map

    # Scale Conditional so that when summed it is equivalent to the marginal
    for base_name in conditional_probs.keys():
        total_cond = 0
        for cond_name in conditional_probs[base_name]:
            total_cond += conditional_probs[base_name][cond_name]["prob"] * marginal_probs[cond_name]["pct"]

        for cond_name in conditional_probs[base_name]:
            conditional_probs[base_name][cond_name]["prob"] *= marginal_probs[base_name]["pct"] / total_cond

    print("Number of Pokemon: {num_pokes} | Total Pct Accounted For: {tot_pct}".format(
        num_pokes=len(marginal_probs.keys()),
        tot_pct=tot_marginal / 6
    ))

    return info, marginal_probs, conditional_probs


def sample_team(n, team_prob, total_prob):
    # probability based on stick breaking approach
    prob = min(team_prob / (1 - total_prob), 1)
    return binomial(n, prob)


def team_validity_check(team):
    # Species Clause Heuristics
    invalid_team = False

    # TODO: Garchomp + Garchomp-Mega Can't Occur
    # TODO: See if can mix this with regional forms

    team_members = set()
    mega_present = False
    rotom_present = False
    greninja_present = False
    gourgeist_present = False
    therian_incarnate = set()
    for x in team:
        if x in team_members:
            invalid_team = True
            break
        team_members.add(x)

        if "-mega" in x.lower() and mega_present is False:
            mega_present = True
        elif "-mega" in x.lower() and mega_present is True:
            invalid_team = True
            break

        if "greninja" in x.lower() and greninja_present is False:
            greninja_present = True
        elif "greninja" in x.lower() and greninja_present is True:
            invalid_team = True
            break

        if x.lower() in ["thundurus", "thundurus-therian", "landorus", "landorus-therian", "tornadus", "tornadus-therian"]:
            if x in therian_incarnate:
                invalid_team = True
                break
            elif "-" in x:
                therian_incarnate.add(x)
                therian_incarnate.add(x.split("-")[0])
            else:
                therian_incarnate.add(x)
                therian_incarnate.add("{}-Therian".format(x))

        if "rotom" in x.lower() and rotom_present is False:
            rotom_present = True
        elif "rotom" in x.lower() and rotom_present is True:
            invalid_team = True
            break

        if "gourgeist" in x.lower() and gourgeist_present is False:
            gourgeist_present = True
        elif "gourgeist" in x.lower() and gourgeist_present is True:
            invalid_team = True
            break

    return not invalid_team


def calculate_team_prob(team, m_prob, c_prob):
    team_probs = []
    for i in range(len(team)):
        ref_poke = team[i]
        rest_of_team = team[:i] + team[(i+1):]
        ref_marginal = m_prob[ref_poke]["pct"]
        rest_cond_prob = [c_prob[teammate][ref_poke]["prob"] for teammate in rest_of_team]
        team_probs.append(ref_marginal * reduce(mul, rest_cond_prob, 1))

    return sum(team_probs) * factorial(len(team) - 1)


def generate_teams(info, m_prob, c_prob, out_filename):
    total_teams = round(info["ability_total"])
    names = m_prob.keys()
    main_outfile = open(out_filename, "w")

    num_to_search = 0
    team_combinations = None
    total_prob = None
    if GenerateTeamsConfig().method == "comb":
        team_combinations = combinations(names, GenerateTeamsConfig().teamLength)
        num_to_search = factorial(len(names)) / ( factorial(GenerateTeamsConfig().teamLength) * factorial(len(names) - GenerateTeamsConfig().teamLength) )
        total_prob = 1
    elif GenerateTeamsConfig().method == "beam":
        team_combinations, total_prob = generate_teams_beam(info, m_prob, c_prob)
        num_to_search = len(team_combinations)
    else:
        raise RuntimeError("Invalid Method (either 'comb' or 'beam' expected: {}".format(GenerateTeamsConfig().method))

    print("Number of Teams to Search: {num} | Total Teams: {tot} | Total Prob: {prob}".format(
        num=num_to_search,
        tot=total_teams,
        prob=total_prob))

    counter = 0
    buffer = []
    pct_chosen = 0
    num_chosen = 0
    for team in team_combinations:
        counter += 1
        team = list(team)

        if team_validity_check(team) is False:
            continue

        team_prob = calculate_team_prob(team, m_prob, c_prob) / total_prob

        # team_appearances = sample_team(total_teams - num_chosen, team_prob, pct_chosen)
        team_appearances = round(total_teams * team_prob)

        if team_appearances > 0:
            num_chosen += team_appearances
            pct_chosen += team_prob
            buffer.append(team + ["{}\n".format(str(team_appearances))] )

        if counter % GenerateTeamsConfig().checkpointIteration == 0:
            print("Iteration: {}".format(counter),
                    "| Total Probability Captured: {}".format(pct_chosen),
                    "| Num Teams Generated: {}".format(num_chosen))


        if len(buffer) % GenerateTeamsConfig().bufferSize == 0:
            main_outfile.writelines([",".join(x) for x in buffer])
            buffer = []


    if buffer:
        main_outfile.writelines([",".join(x) for x in buffer])

    if counter % GenerateTeamsConfig().checkpointIteration != 0:
        print("Iteration: {}".format(counter),
                "| Total Probability Captured: {}".format(pct_chosen),
                "| Num Teams Generated: {}".format(num_chosen))

    main_outfile.close()


def beam_step(base_teams, names):
    new_teams_set = set()

    for team in base_teams:
        for name in names:
            cand_new_team = team + [name]

            # Filter out invalid team combinations
            if team_validity_check(cand_new_team) is False:
                continue

            # Sort alphabetically to avoid duplications
            cand_new_team.sort()
            new_teams_set.add("|".join(cand_new_team))

    new_teams = [x.split("|") for x in new_teams_set]
    new_teams_prob = [{
        "team": x,
        "prob": calculate_team_prob(x, m_prob, c_prob)} for x in new_teams]
    new_teams_prob.sort(key=lambda k: k["prob"], reverse=True)

    actual_teams = new_teams_prob[0:GenerateTeamsConfig().beamSearchThreshold]

    return [x["team"] for x in actual_teams], sum([x["prob"] for x in actual_teams])


def generate_teams_beam(info, m_prob, c_prob):
    names = m_prob.keys()
    base_teams = [[x] for x in m_prob.keys()]

    start_time = time()
    counter = 1
    while counter < GenerateTeamsConfig().teamLength:
        step_time = time()
        base_teams, team_probs = beam_step(base_teams, names)
        print("Beam Step: {} ({}) | Time Elapsed {:.02f}s ({:.02f}s)".format(
            counter,
            len(base_teams),
            time() - step_time,
            time() - start_time))
        counter += 1

    print("Time Spent Generating Teams: {:.02f}s".format(time() - start_time))
    return base_teams, team_probs


def generate_filename(prefix, gt_conf):
    fname = "{prefix}_{fname}".format(prefix=prefix,
                                      fname=filename.replace(".json", ".txt"))
    fname = join(config.TEAMS_TXT_DIR, fname)
    return fname

def write_mprob(m_prob, fname):
    mprob_file = open(fname, 'w')
    mprob_file.write("pokemon,true.prob\n")
    for name in m_prob.keys():
        mprob_file.write("{},{}\n".format(name, m_prob[name]["pct"]))

    mprob_file.close()

def write_cprob(c_prob, fname):
    cprob_file = open(fname, 'w')
    cprob_file.write("base.pokemon,cond.pokemon,true.prob\n")
    for base_name in c_prob.keys():
        for cond_name in c_prob[base_name].keys():
            cprob_file.write("{},{},{}\n".format(base_name,
                cond_name,
                c_prob[base_name][cond_name]["prob"]))

if __name__ == "__main__":
    gt_conf = GenerateTeamsConfig()

    args = parse_args(gt_conf)
    files = args.files
    thresholds = args.thresholds

    if len(files) != len(thresholds):
        if len(thresholds) == 1:
            thresholds = thresholds * len(files)
        else:
            raise RuntimeError("Invalid File and Thresholds lengths")

    idxs = range(len(files))
    teams = []
    for idx in idxs:
        filename = files[idx]
        thresh = thresholds[idx]
        out_filename = generate_filename(gt_conf.outputFilenamePrefix, gt_conf)
        uniq_filename = generate_filename(gt_conf.uniqueFilenamePrefix, gt_conf)
        mprob_filename = generate_filename(gt_conf.mprobFilenamePrefix, gt_conf)
        cprob_filename = generate_filename(gt_conf.cprobFilenamePrefix, gt_conf)

        print(filename, thresh)
        json_in = None
        with open(join(config.DATA_DIR, filename)) as in_file:
            json_in = json.loads(in_file.read())

        info, m_prob, c_prob = generate_probabilities(json_in, thresh)

        write_mprob(m_prob, mprob_filename)
        write_cprob(c_prob, cprob_filename)

        unique_outfile = open(uniq_filename, "w")
        [unique_outfile.write("{}\n".format(x)) for x in list(m_prob.keys())]
        unique_outfile.close()

        test_pokes = list(c_prob.keys())[0:9]
        for test_poke in test_pokes:
            total = 0
            for x in c_prob[test_poke]:
                total += c_prob[test_poke][x]["prob"] * m_prob[x]["pct"]
            print("\t{} | Marginal: {} | Sum Conditional: {}".format(test_poke, m_prob[test_poke]["pct"], total))

        generate_teams(info, m_prob, c_prob, out_filename)
