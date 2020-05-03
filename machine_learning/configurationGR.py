import os
from configuration import ROOT_DIR

# inputs and outputs required for machine learning
INPUT_LOGS_OUTPUT_LOGS_DICT = {
    'INPUT':
    [
        ('Hole Depth', 'ft'),
        ('Rate Of Penetration', 'ft/hr'),
        ('Rotary RPM', 'rev/min'),
        ('Rotary Torque', 'in/lb'),
        ('Weight on Bit', 'kDaN'),
        ('Differential Pressure', 'kPa'),
        ('Inclination', 'degree')
    ],
    'OUTPUT':
    [
        'Gamma'
    ]
}


# template well for testing
TEST_FILE = os.sep.join((ROOT_DIR, 'input', 'test_file', '25509696.csv'))
