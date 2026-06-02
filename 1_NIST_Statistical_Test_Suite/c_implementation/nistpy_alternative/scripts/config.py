"""
Configuration and Constants

Converted from C header files to Python
"""

# Test identifiers
TEST_FREQUENCY = 1
TEST_BLOCK_FREQUENCY = 2
TEST_CUSUM = 3
TEST_RUNS = 4
TEST_LONGEST_RUN = 5
TEST_RANK = 6
TEST_FFT = 7
TEST_NONPERIODIC = 8
TEST_OVERLAPPING = 9
TEST_UNIVERSAL = 10
TEST_APEN = 11
TEST_RND_EXCURSION = 12
TEST_RND_EXCURSION_VAR = 13
TEST_SERIAL = 14
TEST_LINEARCOMPLEXITY = 15

NUMOFTESTS = 15

# Constants
ALPHA = 0.01
MAX = lambda a, b: a if a > b else b
MIN = lambda a, b: a if a < b else b
MAXNUMOFTEMPLATES = 148
MAXFILESPERMITTEDFORPARTITION = 148

# Generator options
NUMOFGENERATORS = 9

# Generator names
generator_dir = [
    "Input",
    "Linear-Congruential",
    "Quadratic-Congruential-1",
    "Quadratic-Congruential-2",
    "Cubic-Congruential",
    "XOR",
    "Modular-Exponentiation",
    "Blum-Blum-Shub",
    "Micali-Schnorr",
    "G-using-SHA-1"
]

# Test names
test_names = [
    "",  # 0 index unused
    "Frequency",
    "BlockFrequency",
    "CumulativeSums",
    "Runs",
    "LongestRun",
    "Rank",
    "FFT",
    "NonOverlappingTemplate",
    "OverlappingTemplate",
    "Universal",
    "ApproximateEntropy",
    "RandomExcursions",
    "RandomExcursionsVariant",
    "Serial",
    "LinearComplexity"
]


class TestParameters:
    """Test parameters container"""
    def __init__(self):
        self.n = 0
        self.blockFrequencyBlockLength = 0
        self.nonOverlappingTemplateBlockLength = 0
        self.overlappingTemplateBlockLength = 0
        self.approximateEntropyBlockLength = 0
        self.serialBlockLength = 0
        self.linearComplexitySequenceLength = 0
        self.numOfBitStreams = 0


# Global variables
tp = TestParameters()
epsilon = None
test_vector = [0] * (NUMOFTESTS + 1)
stats = [None] * (NUMOFTESTS + 1)
results = [None] * (NUMOFTESTS + 1)
freqfp = None
summary = None
