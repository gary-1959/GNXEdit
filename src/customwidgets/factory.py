# factory.py
#
# GNXEdit factory custom widget items for Digitech GNX1
#
# Copyright 2024 gary-1959
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PySide6.QtCore import Qt

factory_patch_names = { 0:'HYBRID', 1:'CLNCHO', 2:'2CHUNK', 3:'WARPME', 4:'BLKBAS', 5:'MEATX2', 6:'ERIC J', 7:'CARLOS', 
                        8:'KOBB  ', 9:'BASSMN', 10:'MATCHD', 11:'VOXTOP', 12:'BLUDLY', 13:'BLUBAL', 14:'TEXBLU', 15:'PICKEN',
                        16:'PSTEEL', 17:'A MIXO', 18:'MO WAH', 19:'FAZOUT', 20:'THICKR', 21:'ACOUST', 22:'CMPCLN', 23:'WRMCLN',
                        24:'RECTFY', 24:'SOLO  ', 26:'WHAMMY', 27:'STACKD', 28:'VOLSWL', 29:'BIGDUK', 30:'JAZZY ', 31:'5THS  ',
                        32:'FUSOLO', 33:'SURFIN', 34:'FUZZO ', 35:'TREMBO', 36:'CLNWAH', 37:'FNKPHS', 38:'ENVLOP', 39:'BLKFUZ',
                        40:'TUNCAB', 41:'TRGPHS', 42:'PSYNTH', 43:'ROTARY', 44:'YAYA  ', 45:'STUTTR', 46:'TRIPLT', 47:'DIVBOM' }

#factory_amp_names = {0:"DIRECT", 1:"BLKFAC", 2:"BOUTIQ", 3:"RECTIF", 4:"HOTROD", 5:"TWEED", 6:"BRTCMB", 7:"CLNTUB",
#                    8:"BRTSTK", 9:"CRUNCH", 10:"HIGAIN", 11:"BLUES", 12:"MODGAN", 13:"FUZZ", 14:"BASSMN", 15:"HIWATG", 16:"ACOUST",
#                    17:"USER 1", 18:"USER 2", 19:"USER 3", 20:"USER 4", 21:"USER 5", 22:"USER 6", 23:"USER 7", 24:"USER 8", 25:"USER 9", 63:"CUSTOM"}

#factory_cab_names = {0:"DIRECT", 1:"AMERICAN 2x12", 2:"BRITISH 4x12", 3:"VINTAGE 30 4x12", 4:"BRITISH 2x12", 5:"AMERICAN 1x12",
#                        6:"BLONDE 2x12", 7:"FANE 4x12", 8:"GREENBACK 4x12",
#                        9:"USER 1", 10:"USER 2", 11:"USER 3", 12:"USER 4", 13:"USER 5", 
#                        14:"USER 6", 15:"USER 7", 16:"USER 8", 17:"USER 9", 63:"CUSTOM"}

factory_waveforms = {0:"TRIANGLE", 1:"SINE", 2:"SQUARE"}
factory_onoff = {0:"OFF", 1: "ON"}
factory_wah_types = {0:"CRY", 1:"BOUTIQUE", 2:"FULL"}
factory_compressor_attack = {0: "FAST", 1: "MEDIUM", 2: "SLOW"}
factory_compressor_ratio = {0: "1.2:1", 1: "1.5:1", 2: "1.8:1", 3: "2.0:1", 4: "2.5:1", 5: "3.0:1", 6: "4.0:1", 7: "5.0:1", 8: "8.0:1",
                            9: "10:1", 10: "20:1", 11: "INF"}

factory_pickup_names = {0:"OFF", 1:"SINGLE COIL -> HUMBUCKER", 2:"HUMBUCKER -> SINGLE COIL"}

factory_whammy_shift = {0: "1 Octave Up", 1: "2 Octaves Up", 2: "2nd Down", 3: "2nd Dn Rev", 4: "4th Down", 5: "1 Octave Dn",
                        6: "2 Octaves Dn", 7: "Dive Bomb", 8: "Min3>Maj3 Up", 9: "2nd>Maj3 Up", 10: "3rd>4th Up",
                        11: "4th>5th Up", 12: "5th>Oct Up", 13: "Harm Oct Up", 14: "Harm Oct Dn", 15: "Oct Up>Down"}

factory_ips_shift = {0: "Octave Down", 1: "7th Down", 2: "6th Down", 3: "5th Down", 4: "4th Down", 5: "3rd Down", 6: "2nd Down", 7: "2nd Up",
                        8: "3rd Up", 9: "4th Up", 10: "5th Up", 11: "6th Up", 12: "7th Up", 13: "Octave Up"}

factory_ips_scale = {0: "Major", 1: "Minor", 2: "Dorian", 3: "Mixolydian", 4: "Lydian", 5: "Harm Minor"}

factory_ips_key = {0: "E", 1: "F", 2: "Gb", 3: "G", 4: "Ab", 5: "A", 6: "Bb", 7: "B", 8: "C", 9: "Db", 10: "D", 11: "Eb"}

exp_pot_off = {"minval": 0, "maxval": 1, "minunit": 0, "maxunit": 1, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                    "x": 0, "y": 0, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                    "unitscale": ["--", "--"], "tooltipformat": "s" }

exp_pot_vol = {"minval": 0, "maxval": 99, "minunit": 0, "maxunit": 99, "prefix": "", "suffix":"", "dialmin": 1, "dialmax": 12, "dialstep": 1, "img": "direct",
                "x": 0, "y": 0, "w": 60, "h": 60, "start": 45, "end": 315, "rotate": 180, "ds": 2, "color": Qt.black,  "ticks": True,  "marks": range(1,11,1),
                "unitscale": None, "tooltipformat": "0.1f" }

factory_expression_assignments = {
    0:  { "section": 0xFF, "parameter": 0xFF, "name": "OFF",                        "pot": exp_pot_off},
    1:  { "section": 0x03, "parameter": 0x02, "name": "Compressor 1",               "pot": None},
    2:  { "section": 0x03, "parameter": 0x03, "name": "Compressor 2",               "pot": None},
    3:  { "section": 0x03, "parameter": 0x04, "name": "Compressor 3",               "pot": None},
    4:  { "section": 0x03, "parameter": 0x05, "name": "Compressor 4",               "pot": None},

    5:  { "section": 0x04, "parameter": 0x02, "name": "Whammy 1",                   "pot": None},
    6:  { "section": 0x04, "parameter": 0x03, "name": "Whammy 2",                   "pot": None},
    7:  { "section": 0x04, "parameter": 0x04, "name": "Whammy 3",                   "pot": None},
    8:  { "section": 0x04, "parameter": 0x05, "name": "Whammy 4",                   "pot": None},

    9:  { "section": 0x05, "parameter": 0x01, "name": "Warp 1",                     "pot": None},
    10: { "section": 0x05, "parameter": 0x02, "name": "Warp 2",                     "pot": None},
    11: { "section": 0x05, "parameter": 0x03, "name": "Warp 3",                     "pot": None},
    12: { "section": 0x05, "parameter": 0x04, "name": "Warp 4",                     "pot": None},

    13: { "section": 0x06, "parameter": 0x01, "name": "Green Amp 1",                "pot": None},
    14: { "section": 0x06, "parameter": 0x08, "name": "Green Amp 2",                "pot": None},

    15: { "section": 0x08, "parameter": 0x01, "name": "Red Amp 1",                  "pot": None},
    16: { "section": 0x08, "parameter": 0x08, "name": "Red Amp 2",                  "pot": None},

    17: { "section": 0x0A, "parameter": 0x02, "name": "Gate 1",                     "pot": None},
    18: { "section": 0x0A, "parameter": 0x03, "name": "Gate 2",                     "pot": None},
    19: { "section": 0x0A, "parameter": 0x04, "name": "Gate 3",                     "pot": None},

    20: { "section": 0x0B, "parameter": 0x02, "name": "Modulation 1",               "pot": None},
    21: { "section": 0x0B, "parameter": 0x03, "name": "Modulation 2",               "pot": None},
    22: { "section": 0x0B, "parameter": 0x04, "name": "Modulation 3",               "pot": None},
    23: { "section": 0x0B, "parameter": 0x05, "name": "Modulation 4",               "pot": None},
    24: { "section": 0x0B, "parameter": 0x06, "name": "Modulation 5",               "pot": None},
    25: { "section": 0x0B, "parameter": 0x07, "name": "Modulation 6",               "pot": None},

    26: { "section": 0x0C, "parameter": 0x02, "name": "Delay 1",                    "pot": None},
    27: { "section": 0x0C, "parameter": 0x03, "name": "Delay 2",                    "pot": None},
    28: { "section": 0x0C, "parameter": 0x04, "name": "Delay 3",                    "pot": None},
    29: { "section": 0x0C, "parameter": 0x05, "name": "Delay 4",                    "pot": None},
    30: { "section": 0x0C, "parameter": 0x06, "name": "Delay 5",                    "pot": None},
    31: { "section": 0x0C, "parameter": 0x07, "name": "Delay 6",                    "pot": None},

    32: { "section": 0x0D, "parameter": 0x02, "name": "Reverb 1",                   "pot": None},
    33: { "section": 0x0D, "parameter": 0x03, "name": "Reverb 2",                   "pot": None},
    34: { "section": 0x0D, "parameter": 0x04, "name": "Reverb 3",                   "pot": None},
    35: { "section": 0x0D, "parameter": 0x05, "name": "Reverb 4",                   "pot": None},
    36: { "section": 0x0D, "parameter": 0x06, "name": "Reverb 5",                   "pot": None},

    37: { "section": 0x0E, "parameter": 0x01, "name": "Volume Pre",                 "pot": exp_pot_vol},
    38: { "section": 0x0E, "parameter": 0x02, "name": "Volume Post",                "pot": exp_pot_vol},
    39: { "section": 0x0E, "parameter": 0x04, "name": "LFO1",                       "pot": None},
    40: { "section": 0x0E, "parameter": 0x05, "name": "LFO2",                       "pot": None}
}

