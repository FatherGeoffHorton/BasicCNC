import sys
import tomllib 
import svgpathtools
from math import sqrt


jobfile = sys.argv[1]
try:
    with open("Jobfile.cfg", "rb") as f:
        data = tomllib.load(f)
except Exception as e:
    sys.exit(f"Failed loading job file {jobfile} with error {e}")

INFILE = data["INFILE"]
OUTFILE = data["OUTFILE"]
MACHINEFILE = data["MACHINE_FILE"]
STOCKFILE = data["STOCK_FILE"]
BITFILE = data["BIT_FILE"]

try:
    with open(MACHINEFILE, "rb") as f:
        machine = tomllib.load(f)
except Exception as e:
    sys.exit(f"Failed loading machine file {jobfile} with error {e}")

try:
    with open(STOCKFILE, "rb") as f:
        stock = tomllib.load(f)
except Exception as e:
    sys.exit(f"Failed loading stock file {stockfile} with error {e}")

try:
    with open(BITFILE, "rb") as f:
        bitdata = tomllib.load(f)
except Exception as e:
    sys.exit(f"Failed loading bit file {bitfile} with error {e}")

PREAMBLE = """G21
M5
M0
M3 S10000
"""
FINALE = """S0
M5
M30
"""



all_paths = []
paths, attributes = svgpathtools.svg2paths(INFILE)
i = 0
for path in paths:
    paths = path.continuous_subpaths()
    for pathhe in paths:
        all_paths.append(pathhe)

upper_x = data["jobparms"]["UPPER_X"]
upper_y = data["jobparms"]["UPPER_Y"]

MIN_GAP = data["jobparms"]["MIN_GAP"]
Z_SAFE = data["jobparms"]["Z_SAFE"]

# These are used to find the boundaries of the input shapes
# They start out intentionally extreme so that they always get replaced
min_x = 1000000
max_x = -1000000
min_y = 1000000
max_y = -1000000

# pathpoints is a vector of vectors; each subvector is a tuplet of (x, y) points
pathpoints = []

for path in all_paths:
    length = 0
    for seg in path:
        length += seg.length()
    pts = length / MIN_GAP
    coords = []
    for p in range(int(pts)):
        pt = path.point(p / length)
        x = pt.real
        y = pt.imag
        vals = (x, y)
        if min_x > x:
            min_x = x
        if max_x < x:
            max_x = x
        if min_y > y:
            min_y = y
        if max_y < y:
            max_y = y
        coords.append(vals)
    pathpoints.append(coords)

# scale paths to desired job size
x_off = min_x
y_off = min_y
x_scale = upper_x / (max_x - min_x)
y_scale = upper_y / (max_y - min_y)
if x_scale < 1 and y_scale < 1:
    if x_scale < y_scale:
        y_scale = x_scale
    else:
        x_scale = y_scale

# First pass: Scale (if needed) and create (x, y) pairs for the toolpaths
toolpaths = []

for path in pathpoints:
    toolpath = []
    for pt in path:
        # scaling and offsetting
        x = (pt[0] - x_off) * x_scale
        y = (pt[1] - y_off) * y_scale
        move = (x, y)
        toolpath.append(move)
    toolpaths.append(toolpath)


def enkode(path, cut_depth, total_depth):
    point = path[0]
    start_string = path_string = f"G00 X{point[0]:.2f} Y{point[1]:.2f} Z{Z_SAFE}\n"
    z = cut_depth
    while z <= total_depth:
        path_string += f"(Pass for depth {z:.2f})\n"
        for point in path:
            path_string += f"G01 X{point[0]:.2f} Y{point[1]:.2f} Z{-z:.2f}\n"
        # return safely to start
        path_string += start_string
        z += cut_depth
    return path_string
    

gcodefile = open(OUTFILE, "w")
gcodefile.write(PREAMBLE)

#for path in svgpath.paths_to_points(paths, resolution=1):
#    for trace in path:
#        i = i + 1
#        if showonly is None or i in showonly:
#            style = styles[i % 5]
#            ax.plot(trace[:, 0], trace[:, 1], style, label = f"{i}")
#plt.legend(loc = "best")
#plt.show()

CUT_LIST = eval(data["cuts"]["CUT_LIST"])
default_type = data["cuts"]["default_type"]
default_depth = data["cuts"]["default_depth"]
print(default_type)
i = 0
print(CUT_LIST)
for path in toolpaths:
    i = i + 1
    cut_info = CUT_LIST.get(i, None)
    if cut_info is None:
        print(f"No data for path {i}; using defaults")
        cut_info = (default_type, default_depth)
    else:
        cut_type = cut_info[0]
    if cut_type == "x":
        print(f"Skipping path {i}")
        continue
    else:
        full_depth = cut_info[1]
    print(f"For path {i}, cut_type = {cut_type}, full_depth = {full_depth}")
    path_string = ""
    if cut_type.lower() == "c":
        print(f"Cutting path {i}")
        cut_depth = bitdata["CUT_DEPTH"]
        stryng = enkode(path, cut_depth, full_depth)
    gcodefile.write(f"(Path #{i})\n")
    gcodefile.write(stryng)

gcodefile.write(FINALE)
gcodefile.close()
