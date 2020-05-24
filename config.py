"""
Configuration things for this project
"""

from pathlib import Path

DATA_DIR = "data/chaos"
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
TEAMS_TXT_DIR = "data/txt"
Path(TEAMS_TXT_DIR).mkdir(parents=True, exist_ok=True)
TEAMS_MAT_DIR = "data/mat"
Path(TEAMS_MAT_DIR).mkdir(parents=True, exist_ok=True)

TIER = "gen8ou"
MONTH = "2020-03"
LEVEL = "1695"

# Pull_data Config
class PullDataConfig():
    # See https://www.smogon.com/stats/ for details
    def __init__(self):
        self.defaultTier = [TIER]
        self.defaultLevel = [LEVEL]
        self.defaultMonth = [MONTH]

# Generate Teams Config
class GenerateTeamsConfig():
    # Thresholds < 1 => pct of total from corresponding file
    def __init__(self):
        self.dataFiles = ["{month}_{tier}_{level}.json".format(month=MONTH, tier=TIER, level=LEVEL)] # "2020-01_gen8ou_1825.json"]
        self.thresholdLimit = [0.01]
        self.outputFilenamePrefix = "teams"
        self.uniqueFilenamePrefix = "unique"
        self.mprobFilenamePrefix = "mprob"
        self.cprobFilenamePrefix = "cprob"
        """
            Threshold; Metagame Size vs Time
            50,000; 64  => 69s
            50,000; 70  => 80s
            50,000; 102 => 127s
            100,000; 64 => 117s
            100,000; 88 => 217s
            200,000; 66 => 230s
            200,000; 88 => 395s
        """
        self.beamSearchThreshold = 200000
        self.teamLength = 6
        self.method = "beam"
        self.checkpointIteration = 10000
        self.bufferSize = 1000

# Model Config
class ModelConfig():
    def __init__(self):
        # Preprocessing Stuff
        self.targetFilesSuffix = ["{month}_{tier}_{level}.txt".format(month=MONTH, tier=TIER, level=LEVEL)]
        self.matrixDataFile = "{month}_{tier}_data".format(month=MONTH, tier=TIER)
        self.matrixLabelFile = "{month}_{tier}_label".format(month=MONTH, tier=TIER)
        self.matrixWeightFile = "{month}_{tier}_weight".format(month=MONTH, tier=TIER)
        self.onehotFile = "{month}_{tier}_onehot".format(month=MONTH, tier=TIER)

        # Actual Model Stuff
        self.hiddenLayerSize = 10
        self.batchSize = 512
