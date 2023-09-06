import matplotlib.pyplot as plt
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser(description='Create a plot.')
parser.add_argument('filename', help='JSON dictionary with results.')
parser.add_argument('lmap', metavar='labels', type=str, nargs='*',
        help='Human-readable plot labels provided as a list of old:new maps')
parser.add_argument('-x', '--xaxis', type=str, help='What to take as x-axis, label:name map',
        default='nodes:Number of nodes')
parser.add_argument('-y', '--yaxis', type=str, help='What to take as y-axis, label:name map',
        default='scf_time:Time to solution (sec)')
args = parser.parse_args()

def split_label(s):
    i = s.find(':')
    return s[:i], s[i+1:]

lmap = {}
for e in args.lmap:
    label_id, label = split_label(e)
    lmap[label_id] = label


with open(args.filename) as json_file:
    inp = json.load(json_file)

x_axis, x_axis_label = split_label(args.xaxis)
y_axis, y_axis_label = split_label(args.yaxis)

data_points = {}
for p in lmap:
    xy_unsorted = []
    for d in inp["data"][p]:
        x = d[x_axis]
        y = d[y_axis]
        xy_unsorted.append((x, y))

    xy_sorted = sorted(xy_unsorted)
    res = list(zip(*xy_sorted))
    data_points[p] = {}
    data_points[p]['x'] = res[0]
    data_points[p]['y'] = res[1]

nodes = []
for e in lmap:
    nodes = list(set(nodes) | set(data_points[e]['x']))

nodes = sorted(nodes)

xlabels = [str(e) for e in nodes]

x = np.arange(len(xlabels))

## time in sec.
#qe_native_time = [207, 169, 169]
## energy in kJ
#qe_native_energy = [893.503, 1436.458, 2087.321]
#
#qe_sirius_time = [143, 141, 109]
#qe_sirius_energy = [395.230, 716.140, 898.400]
#
#
#for i in range(len(nodes)):
#    qe_native_time[i] = qe_native_time[i] * nodes[i] / 3600.0
#    qe_sirius_time[i] = qe_sirius_time[i] * nodes[i] / 3600.0
#

fig, ax = plt.subplots()


ax.set_title(inp['title'])

ax.set_ylabel(y_axis_label)
ax.set_xticks(x)
ax.set_xlabel(x_axis_label)
ax.set_xticklabels(xlabels)

for e in lmap:
    ax.plot(x, data_points[e]['y'], 'o-', label=lmap[e])

ax.set_ylim(ymin=0)
ax.grid(True)
ax.legend()

plt.savefig(f"{inp['title']}.pdf", format="pdf", transparent=True)
#plt.savefig("output.png", format="png", dpi=300, transparent=True)
