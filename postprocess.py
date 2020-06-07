import json

import numpy as npy

if __name__ == "__main__":
    data = None
    with open("test.json") as json_file:
        data = json.loads(json_file.read())

    names_file = open("names.txt", "w")

    # Reconstruct the matrices
    v_mat = []
    u_mat = []
    avg_mat = []

    names = list(data.keys())

    for name in names:
        if name == "confusion_matrix":
            continue

        names_file.write("{}\n".format(name.replace(" ", "-")))
        v_mat.append(data[name]["vvec"])
        u_mat.append(data[name]["uvec"])
        avg_mat.append(data[name]["avg"])

    v_mat = npy.array(v_mat)
    u_mat = npy.array(u_mat)
    avg_mat = npy.array(avg_mat)

    npy.savetxt("vmat.txt", v_mat)
    npy.savetxt("umat.txt", u_mat)
    npy.savetxt("avg_mat.txt", avg_mat)
    npy.savetxt("confusion.txt", npy.array(data["confusion_matrix"]), fmt='%d')
