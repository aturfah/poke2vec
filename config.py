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

TIER = "gen7ou"
MONTH = "2019-06"
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
        self.dataFiles = ["{month}_{tier}_{level}.json".format(month=MONTH, tier=TIER, level=LEVEL)]
        self.thresholdLimit = [0.005]
        self.outputFilenamePrefix = "teams"
        self.uniqueFilenamePrefix = "unique"
        self.mprobFilenamePrefix = "mprob"
        self.cprobFilenamePrefix = "cprob"
        """
            Threshold; Metagame Size vs Time
            50,000; 64  => 69s
            50,000; 70  => 80s
            50,000; 92  => 117
            50,000; 102 => 127s
            70,000; 92  => 162s
            100,000; 64 => 117s
            100,000; 88 => 217s
            150,000; 88 => 332s
            150,000; 125 => 544s
            200,000; 60 => 184s
            200,000; 66 => 230s
            200,000; 88 => 395s
            200,000; 125 => 706s
            200,000; 200 => 1676s
            250,000; 89 => 470s
            250,000; 116 => 840s
            250,000; 125 => 923s
        """
        self.beamSearchThreshold = 250000
        self.teamLength = 6
        self.method = "beam"
        self.checkpointIteration = 15000
        self.bufferSize = 2000

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
        self.numEpochs = 15
        self.hiddenLayerSize = 50
        self.batchSize = 512

class TestTeamConfig():
    def __init__(self):
        self.year, self.month = [int(x) for x in MONTH.split("-")]
        self.tier = TIER
        self.out_file = "test_teams_{month}_{tier}.txt".format(month=MONTH, tier=TIER)