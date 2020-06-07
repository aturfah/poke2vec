# Logic for loading and preprocessing the data

import config
from config import GenerateTeamsConfig
from config import ModelConfig
from config import TestTeamConfig

from os.path import join
import numpy as npy
import json

def load_data(path_to_file):
    # Reads a txt file and returns a onehot encoding
    output = None
    with open(path_to_file) as file_:
        output = file_.readlines()

    return output

def get_filenames():
    # Read the filenames from the config
    gt_conf = GenerateTeamsConfig()
    m_conf = ModelConfig()
    output = []
    for suff in m_conf.targetFilesSuffix:
        out_filename = "{}_{}".format(gt_conf.outputFilenamePrefix, suff)
        uniq_filename = "{}_{}".format(gt_conf.uniqueFilenamePrefix, suff)
        output.append( (join(config.TEAMS_TXT_DIR,out_filename), join(config.TEAMS_TXT_DIR,uniq_filename)) )

    return output

def gen_onehot_map(uniq_fnames):
    # Get onehot mapping from all unique names across the files
    unique_names = set()
    for fname in uniq_fnames:
        [unique_names.add(x.strip()) for x in load_data(fname)]
    unique_names = list(unique_names)

    return {
        name: unique_names.index(name) for name in unique_names
    } 

def count_file_lines(thefilepath):
    # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s07.html
    count = 0
    thefile = open(thefilepath)
    while 1:
        buffer = thefile.read(8192*1024)
        if not buffer: break
        count += buffer.count('\n')
    thefile.close()
    return count

def onehot_encode_data(file_names):
    # Onehot encode a list of names
    m_conf = ModelConfig()
    data_fnames = []
    uniq_fnames = []
    for name_tuple in file_names:
        data_fnames.append(name_tuple[0])
        uniq_fnames.append(name_tuple[1])

    onehot_mapping = gen_onehot_map(uniq_fnames)
    num_pokes = len(onehot_mapping.keys())

    total_lines = 0
    for fname in data_fnames:
        total_lines += count_file_lines(fname)

    super_mat = npy.zeros( (total_lines * GenerateTeamsConfig().teamLength, num_pokes + 1), dtype=npy.float16)
    weight_mat = npy.zeros( (total_lines * GenerateTeamsConfig().teamLength, 1), dtype=npy.int16)

    idx = 0
    for fname in data_fnames:
        print("Reading {}".format(fname))
        file_i = open(fname)

        while True:
            line = file_i.readline().strip()
            if not line:
                break

            team = line.split(",")
            weight = team[-1]
            team = team[:-1]

            for poke_idx in range(len(team)):
                temp_arr = team[:poke_idx] + team[(poke_idx+1):]

                line_encode = npy.zeros(num_pokes)
                for poke in temp_arr:
                    line_encode[onehot_mapping[poke]] = 1/5

                result_encode = npy.zeros(1)
                result_encode[0] = onehot_mapping[team[poke_idx]]

                weight_encode = npy.zeros(1)
                weight_encode[0] = int(weight)

                super_mat[idx, :] = npy.concatenate([line_encode, result_encode])
                weight_mat[idx, 0] = weight_encode
                idx += 1

    super_duper_mat = npy.hstack((super_mat, weight_mat))
    npy.random.shuffle(super_duper_mat)

    data_mat = super_duper_mat[:, 0:num_pokes]
    label_mat = super_duper_mat[:, num_pokes]
    weight_mat = super_duper_mat[:, num_pokes + 1]

    # Save the files locally
    matrix_datafile = join(config.TEAMS_MAT_DIR, m_conf.matrixDataFile)
    label_datafile = join(config.TEAMS_MAT_DIR, m_conf.matrixLabelFile)
    weights_datafile = join(config.TEAMS_MAT_DIR, m_conf.matrixWeightFile)
    onehot_outfile = join(config.TEAMS_MAT_DIR, "{}.json".format(m_conf.onehotFile))

    print("Saving Data...")
    npy.save(matrix_datafile, data_mat)
    npy.save(label_datafile, label_mat)
    npy.save(weights_datafile, weight_mat)
    with open(onehot_outfile, 'w') as doot:
        json.dump(onehot_mapping, doot)

    return onehot_mapping, data_mat, label_mat, weight_mat

def prepare_data(file_names):
    try:
        # Check if data already exists in the mat dir
        m_conf = ModelConfig()
        mat_file = "{}.npy".format(m_conf.matrixDataFile)
        lab_file = "{}.npy".format(m_conf.matrixLabelFile)
        wei_file = "{}.npy".format(m_conf.matrixWeightFile)
        onehot_file = "{}.json".format(m_conf.onehotFile)

        data_matrix = npy.load(join(config.TEAMS_MAT_DIR, mat_file))
        label_matrix = npy.load(join(config.TEAMS_MAT_DIR, lab_file))
        weight_matrix = npy.load(join(config.TEAMS_MAT_DIR, wei_file))
        with open(join(config.TEAMS_MAT_DIR, onehot_file)) as json_file:
            onehot = json.load(json_file)

        return onehot, data_matrix, label_matrix, weight_matrix
    except:
        # If not then load from the filenames
        return onehot_encode_data(file_names)

def prepare_test_data(onehot_mapping):
    test_teams_file = join(config.TEAMS_TXT_DIR, TestTeamConfig().out_file)
    teams = []
    with open(test_teams_file) as in_file:
        teams.extend([x.strip() for x in in_file.readlines()])

    num_pokes = len(onehot_mapping.keys())

    super_mat = npy.zeros( (len(teams) * GenerateTeamsConfig().teamLength, num_pokes + 1), dtype=npy.float16)
    idx = 0
    for team_str in teams:
        team = team_str.split(",")
        team = team[:-1]

        for poke_idx in range(len(team)):
            temp_arr = team[:poke_idx] + team[(poke_idx+1):]

            line_encode = npy.zeros(num_pokes)
            for poke in temp_arr:
                line_encode[onehot_mapping[poke]] = 1/5

            result_encode = npy.zeros(1)
            result_encode[0] = onehot_mapping[team[poke_idx]]

            super_mat[idx, :] = npy.concatenate([line_encode, result_encode])
            idx += 1

    data_mat = super_mat[:, 0:num_pokes]
    label_mat = super_mat[:, num_pokes]

    print(data_mat.shape)
    print(label_mat.shape)

    raise RuntimeError("PEW")