# Driver code to fit and export the model

import numpy as npy
import json

from model import preprocess
from model import model

from config import ModelConfig

def output_results(model, onehot_mapping):
    names = list(onehot_mapping.keys())

    u_mat = model.layer_weights("U-layer")[0]
    v_mat = model.layer_weights("V-layer")[0]

    output = {}
    for name in names:
        temp = {}
        name_idx = onehot_mapping[name]

        temp["vvec"] = [float(x) for x in v_mat[name_idx, :]]
        temp["uvec"] = [float(x) for x in u_mat[:, name_idx]]
        temp["avg"] = [float(x) for x in npy.add(v_mat[name_idx, :], u_mat[:, name_idx]) * 0.5]

        output[name] = temp

    with open("test.json", "w") as outfile:
        json.dump(output, outfile)

if __name__ == "__main__":
    fnames = preprocess.get_filenames()
    onehot_mapping, data_mat, label_mat, weight_mat = preprocess.prepare_data(fnames)

    model = model.Model(data_mat, label_mat, weight_mat)
    model.train(ModelConfig().numEpochs)

    output_results(model, onehot_mapping)