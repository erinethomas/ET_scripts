# SCRIPT TO MAKE A PACE- like figure for E3SM simulations
# author : Erin Thomas ethomas@lanl.gov
# last updated: May 19, 2025
#
# TO use: run this python script within the E3SM 'timing' directory that contains the 
# 'e3sm_timing.RUN_NAME.*' file
#  for example:
#  python ~/PATH_TO_THIS_SCRIPT_/pace_figure.py e3sm_timing.RUN_NAME.file
#

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import re
import os
import argparse

parser = argparse.ArgumentParser(description="My script with two arguments")
parser.add_argument("arg1", help="File name")
args = parser.parse_args()
infile = args.arg1

outfile = 'PACE_figure.png'

# Load the timing log
path = os.getcwd()

with open(path+'/'+infile, "r") as f:
    content = f.read()
    
# Extract runtimes for each component
components = ['CPL', 'ATM', 'ICE', 'LND', 'OCN', 'WAV','ROF']
runtime = {}
for comp in components:
    match = re.search(rf"{comp} Run Time\s*:\s*([\d.]+)\s*seconds", content)
    if match:
        runtime[comp] = float(match.group(1))
    else:
        runtime[comp] = 0.0

# Extract Processor ranges for each component
with open(path+'/'+infile, "r") as f:
   lines = f.readlines()
# Extract lines 18 to 27 (Python is 0-indexed, so lines[17] to lines[26])
comp_pes_lines = lines[17:27] # this will / should always be the same for all timing files

# Dictionary to store component name and its comp_pes value
rootpe= {}
ntasks = {}
for line in comp_pes_lines:
    parts = line.split()
    if len(parts) >= 3:
        component = parts[0]
        component = component.upper()
        ntasks[component] = int(parts[5])
        rootpe[component] = int(parts[4])
        
processor_ranges = {}        
for comp in components:
    processor_ranges[comp] = (rootpe[comp],rootpe[comp]+ntasks[comp])
    
a = [v[0] for v in processor_ranges.values()]
b = [v[1] for v in processor_ranges.values()] 
pe_labels = list(dict.fromkeys(a+b))


# Colors for each component
colors = {
    'ICE': 'cyan',
    'LND': 'limegreen',
    'ROF': 'red',
    'OCN': 'slateblue',
    'WAV': 'darkblue',
    'ATM': 'deepskyblue',
    'CPL': 'darkorange',
}

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

# Track vertical stacking (start from 0)
stack_bottom = 0
ice_height = runtime['ICE']
atm_height = runtime['ATM']
cpl_height = runtime['CPL']
lnd_height = runtime['LND']
rof_height = runtime['ROF']
wav_height = runtime['WAV']
ocn_height = runtime['OCN']

# First, draw base layer components
base_components = ['ICE', 'LND', 'OCN', 'WAV']
for comp in base_components:
    x_start, x_end = processor_ranges[comp]
    width = x_end - x_start
    height = runtime[comp]
    rect = Rectangle((x_start, 0), width, height, color=colors[comp])
    ax.add_patch(rect)
    ax.text(x_start + width/2, height/2, comp, ha='center', va='center', fontsize=14, fontweight='bold')

# Draw ROF layer above LND
base_rof = lnd_height
rof_rect = Rectangle((processor_ranges['ROF'][0], base_rof),
                     processor_ranges['ROF'][1] - processor_ranges['ROF'][0],
                     rof_height, color=colors['ROF'])
ax.add_patch(rof_rect)
ax.text((processor_ranges['ROF'][1] + processor_ranges['ROF'][0]) / 2,
        lnd_height + rof_height/2, 'ROF', ha='center', va='center', fontsize=14, fontweight='bold')


# Draw ATM layer above ICE
base_atm = max(lnd_height+rof_height, ice_height)
atm_rect = Rectangle((processor_ranges['ATM'][0], base_atm),
                     processor_ranges['ATM'][1] - processor_ranges['ATM'][0],
                     atm_height, color=colors['ATM'])
ax.add_patch(atm_rect)
ax.text((processor_ranges['ATM'][1] + processor_ranges['ATM'][0]) / 2,
        base_atm + atm_height/2, 'ATM', ha='center', va='center', fontsize=14, fontweight='bold')

# Draw CPL layer above ATM
base_cpl = base_atm + atm_height
cpl_rect = Rectangle((processor_ranges['CPL'][0], base_cpl),
                     processor_ranges['CPL'][1] - processor_ranges['CPL'][0],
                     cpl_height, color=colors['CPL'])
ax.add_patch(cpl_rect)
ax.text((processor_ranges['CPL'][1] + processor_ranges['CPL'][0]) / 2,
        base_cpl + cpl_height/2, 'CPL', ha='center', va='center', fontsize=14, fontweight='bold')

height_labels= [0,base_atm,base_cpl,ocn_height,wav_height,base_cpl+cpl_height] 
height_labels = sorted(height_labels)

# Plot settings
ax.set_xlim(0, processor_ranges['WAV'][1])
ax.set_ylim(0, wav_height+200)
ax.set_xlabel("Processor #")
ax.set_ylabel("Simulation Time (s)")
ax.set_xticks(pe_labels)
ax.set_yticks(height_labels)

ax.set_facecolor('lightgray')
ax.spines[['top', 'right']].set_visible(False)

plt.xticks(rotation=45)
plt.savefig(path+'/'+outfile)
plt.show()
