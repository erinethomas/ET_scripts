# SCRIPT TO MAKE A PACE- like figure for E3SM simulations
# author : Erin Thomas ethomas@lanl.gov
# last updated: May 19, 2025
#
# TO use: run this python script within the timing directory that contains the 
# 'e3sm_timing.RUN_NAME.*' file as follows:
#  python ~/PATH_TO_SCRIPT_LOCATION/pace_figure.py e3sm_timing_file_name
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
components = ['LND','ICE','ATM','CPL','ROF','OCN', 'WAV']
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


y_start = 0
rootpe_prev = 0
for comp in components:
    x_start, x_end = processor_ranges[comp]
    width = x_end - x_start
    height = runtime[comp]
    if x_start == rootpe_prev:
        rect = Rectangle((x_start, y_start), width, height, color=colors[comp])
        ax.add_patch(rect)
        ax.text(x_start + width/2, y_start+height/2, comp, ha='center', va='center', fontsize=14, fontweight='bold')
        y_start = y_start+height
    else:
        y_start=0
        rect = Rectangle((x_start, y_start), width, height, color=colors[comp])
        ax.add_patch(rect)
        ax.text(x_start + width/2, y_start+height/2, comp, ha='center', va='center', fontsize=14, fontweight='bold')
        
        
    rootpe_prev = x_start
    y_start_prev = y_start

# Plot settings
ax.set_xlim(0, processor_ranges['WAV'][1])
ax.set_ylim(0, runtime['WAV']+200)
ax.set_xlabel("Processor #")
ax.set_ylabel("Simulation Time (s)")
ax.set_xticks(pe_labels)
#ax.set_yticks(height_labels)

ax.set_facecolor('lightgray')
ax.spines[['top', 'right']].set_visible(False)

plt.xticks(rotation=40)
plt.savefig(path+'/'+outfile)
plt.show()
