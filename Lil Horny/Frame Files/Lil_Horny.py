"""Lil' Horny - Fusion 360 mock-up script.

Fractal 65 Lite frame (slimmed) + DJI O4 Lite + TBS Lucid AIO 1-2S + 0802 motors + batteries,
for designing the O4 camera / battery / antenna-horn mount.

All dimensions are millimetres and live in the CONFIG block. Edit them and re-run to regenerate.
Frame +Y = front, +X = right, +Z = up.

The frame is rebuilt from a photo of the real plate and then streamlined. It is made of editable
sketches inside the "Frame" component:
  "Frame bars+pads"   overlapping bar/pad shapes; extruded to the plate (only material regions)
  "Frame holes"       circles; cut through the plate
Real STEP models of the O4 Lite and the Lucid (next to this script) are imported and auto-placed.
Values marked (ASSUMED) are estimates: verify with calipers.
"""
import math
import os
import traceback

import adsk.core
import adsk.fusion

PROJECT = "Lil' Horny"

# ----------------------------- CONFIG (mm) -----------------------------
MOTOR_X = 26.0            # half left-right motor spacing (ASSUMED: ~65 mm diagonal, squished X)
MOTOR_Y = 19.5            # half front-back motor spacing (ASSUMED)
PLATE_T = 1.5             # carbon plate thickness (spec)
BAR_W = 2.0               # bar width: slimmed 1 mm from the stock ~3 mm for airflow
CENTER_CROSS = False      # stock frame has a + cross between the bosses; off for airflow
BOSS_D = 5.0              # screw boss diameter around AIO holes
AIO_PATTERN = 25.5        # AIO/O4 hole pattern side (spec). Real frame has it turned 45 deg (diamond)
AIO_HOLE_D = 2.2          # M2 clearance
STACK_YAW = 45.0          # boards turned 45 deg to match the frame's diamond hole layout

MOTOR_HOLE_D = 3.6        # centre hole in each motor pad
TRI_R, TRI_D = 3.0, 1.5   # tri-mount: 6.0 mm bolt circle, M1.4 clearance (frame also lists 5.5 mm / M1.6)
PAD_D = 8.4               # motor pad: stays inside the motor's 11 mm footprint
SCREW_BUMP_D = 3.2        # extra carbon around each motor screw hole (stays under the motor base arms)

# 0802 motor: 11 mm wide bell, 6 mm tall; 3 mm tall Y-shaped base whose arms only reach the screw holes
MOTOR_D = 11.0            # bell diameter (you measured 11 mm total width)
MOTOR_BELL_H = 6.0        # (you measured)
MOTOR_BASE_H = 3.0        # (you measured)
MOTOR_HUB_D = 5.0         # centre of the Y base (ASSUMED)
MOTOR_ARM_W = 2.2         # Y arm width (ASSUMED)
MOTOR_ARM_END_D = 2.8     # round end of each arm around the screw (ASSUMED)
MOTOR_SHAFT_D = 1.5
MOTOR_SHAFT_H = 1.5
PROP_D = 31.0             # 31 mm props
PROP_T = 0.5
PROP_Z = PLATE_T + MOTOR_BASE_H + MOTOR_BELL_H + 0.2   # just above the bell

# Printed TPU standoffs (two separate components so each set exports/prints on its own)
STANDOFF_OD = 4.0         # outside diameter
STANDOFF_ID = 2.2         # bore: M2 screw clearance
EXPORT_STL = True         # write each set (4 standoffs) as one STL into an "stl" folder next to this script

# Stack order (bottom -> top): frame plate, O4 Lite, Lucid AIO (micro-USB / motor-socket side up).
STACK_H = 8.0             # plate top -> Lucid PCB top (lowered 3 mm from 11; top standoffs 4.7 mm)

O4_STANDOFF = 1.5         # plate top -> O4 PCB bottom (clears O4 bottom parts)
O4_SIZE = 30.0            # transmission module 30 x 30 x 6 (DJI drawing)
O4_HOLE = 2.6             # 4 x 2.6 (DJI drawing; slotted to the corners, slot not modelled)
O4_PCB_T = 1.0            # (ASSUMED)
O4_COMP_SIZE = 18.0       # (ASSUMED) components split so total height = 6 mm
O4_COMP_TOP_H = 4.0
O4_COMP_BOT_H = 1.0

# TBS Lucid AIO 1-2S. Layout taken from TBS's own STEP (ECAD export): 0.8 mm PCB, 28 x 28 with
# ears to 30 x 30. In your build the side with the micro-USB, ESC FETs and the 4 Molex PicoBlade
# motor sockets faces UP; the MCU side (RX u.FL, buttons, inductor) faces down at the O4.
AIO_SIZE = 28.0
AIO_EAR_D = 4.5
AIO_HOLE = 3.0            # PCB hole for the supplied rubber grommets (ASSUMED)
AIO_PCB_T = 0.8           # (TBS STEP)
LUCID_USB_DIR = 90.0      # direction the micro-USB corner points, deg (0 = right, 90 = front,
                          # 270 = rear). Use 0/90/180/270 so the holes line up with the frame.
# Parts in the Lucid's own frame with the USB corner at +45 deg (USB side up):
# (name, x, y, rot deg, size along rot, size across, height, side) - positions from TBS STEP,
# sizes ASSUMED from the part numbers.
LUCID_PARTS = [
    ("Micro-USB (J5)", 9.72, 9.71, -45.0, 7.5, 5.0, 3.0, "up"),
    ("Motor socket J1", 14.03 - 1.7, -7.30, 90.0, 5.7, 3.3, 5.2, "up"),
    ("Motor socket J2", 7.30, -14.03 + 1.7, 0.0, 5.7, 3.3, 5.2, "up"),
    ("Motor socket J3", -7.30, 14.05 - 1.7, 0.0, 5.7, 3.3, 5.2, "up"),
    ("Motor socket J4", -14.03 + 1.7, 7.30, 90.0, 5.7, 3.3, 5.2, "up"),
    ("ESC FETs Q1A", 8.10, 3.03, 0.0, 3.3, 3.3, 0.9, "up"),
    ("ESC FETs Q1B", 3.00, -8.07, 0.0, 3.3, 3.3, 0.9, "up"),
    ("ESC FETs Q1C", -3.25, 8.43, 0.0, 3.3, 3.3, 0.9, "up"),
    ("ESC FETs Q1D", -8.43, -3.40, 0.0, 3.3, 3.3, 0.9, "up"),
    ("MCU / gyro / RX chips", 0.0, 0.0, 0.0, 16.0, 16.0, 1.0, "down"),
    ("Inductor L1", 9.11, 1.35, 0.0, 3.0, 3.0, 1.4, "down"),
    ("Button SW1", -10.95, 7.80, 0.0, 3.5, 2.9, 1.2, "down"),
    ("Button SW2", -12.80, 3.06, 0.0, 3.5, 2.9, 1.2, "down"),
    ("Crossfire RX u.FL (J6)", -7.80, -10.35, 0.0, 3.0, 3.0, 1.3, "down"),
]

# DJI O4 Lite camera, bare module (no DJI adapter). From DJI's dimension drawing:
CAM_DEPTH = 13.44               # lens tip -> back of rear connector (DJI)
CAM_LENS_D = 8.5                # (DJI)
CAM_LENS_L = 1.5                # lens proud of the body (DJI)
CAM_BODY_WH = 10.8              # square body / lens holder (DJI)
CAM_BODY_D = 5.2                # (DJI)
CAM_BODY_Z_OFF = -0.5           # body centre sits ~0.5 below board centre (scaled from DJI drawing)
CAM_PCB = (12.36, 3.3, 16.5)    # board stack W, thickness, H (W/H DJI; thickness scaled from drawing)
CAM_TOP_TAB = (13.10, 1.5)      # wider tabs along the top edge: width, height (DJI width)
CAM_CONN = (8.0, CAM_DEPTH - CAM_LENS_L - CAM_BODY_D - CAM_PCB[1], 4.5)  # rear connector at the TOP
CAM_CONN_TOP_GAP = 1.1          # connector starts this far below the board top (scaled)
CAM_REAR_PART = (6.0, 1.0, 4.0) # small part low on the back (scaled)
CAM_CABLE = (6.0, 1.0, 4.0)     # flex cable leaving the top: keep-out W, thickness, length up (ASSUMED)
CAM_REAR_Y = 22.0               # Y of the camera's rear face (connector back)
CAM_CENTER_Z = 9.0              # camera PCB centre height above plate bottom (ASSUMED)
CAM_TILT_DEG = 0.0              # lens-up tilt (0 = level), pivots about the camera's rear centre


# Batteries: (name, (width X, length Y, thickness Z), shown). Hidden ones: eye icon in the browser.
BATTERIES = [
    ("2S 300mAh 38x16x8", (16.0, 38.0, 8.0), True),
    ("Battery 47x16x11.5", (15.72, 47.28, 11.53), False),
    ("1S 270mAh Tiny Whoop (SIZE ASSUMED)", (12.0, 52.0, 7.0), False),
]
BATT_X = 0.0                    # battery runs front-back between the motor-socket pairs
BATT_Y_OFFSET = -2.0            # shift battery rearward to balance the camera
BATT_CLEAR = 0.5                # gap above the tallest Lucid part under it

# Real models next to this script ("" to skip). Each board is flipped parts-side-up, centred on the
# holes and set at the dummy's height; the dummy is then hidden.
O4_STEP = "DJI o4 Lite (v1).step"
O4_USB_DIR = 225.0              # direction the O4's USB-C edge faces (45/135/225/315 keep holes aligned)
# Parts of the O4 STEP to hide (name fragments, upper case): the loose 6-pin FC cable and the DJI
# camera adapter housing you're not using. The original antenna stays. Add "DJI O4 LITE CAM" and
# "MIPI PLUG CABLE" to also hide the STEP's camera + flex (the camera from DJI's drawing stays).
O4_STEP_HIDE = ("6P TABBED PLUG", "SHR-06V", "CAM HOUSING")
LUCID_STEP = "TBS_Lucid_AIO_1-2S.step"
HIDE_DUMMY_IF_STEP = True

# Fusion up axis: "auto" follows your Fusion preference (Preferences > General > Default modeling
# orientation); force "Y-up" or "Z-up" if it comes out wrong.
UP_AXIS = "auto"
# -----------------------------------------------------------------------

P = adsk.core.Point3D.create
V = adsk.core.ValueInput.createByReal
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
HERE = os.path.dirname(os.path.abspath(__file__))
WARNINGS = []


def cm(v):
    return v / 10.0


# Orientation. Everything is described in DRONE coordinates (x = right, y = nose, z = up, mm) and
# mapped straight into Fusion's world axes while it is built, so nothing is rotated afterwards.
#   Y-up (Fusion default): nose -> +Z (Front view), up -> +Y, right -> -X
#   Z-up:                  nose -> -Y (Front view), up -> +Z, right -> -X
ORIENT = {"Y-up": ([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], "xZConstructionPlane"),
          "Z-up": ([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], "xYConstructionPlane")}
O = ORIENT["Y-up"][0]           # world = O . drone   (set in run())
HPLANE = ORIENT["Y-up"][1]      # Fusion origin plane that is horizontal for the drone


def w(p):
    """Drone mm -> world mm."""
    return tuple(sum(O[i][j] * p[j] for j in range(3)) for i in range(3))


def d_of(wp):
    """World mm -> drone mm (O is orthonormal, so its inverse is its transpose)."""
    return tuple(sum(O[j][i] * wp[j] for j in range(3)) for i in range(3))


def WP(p):
    """Drone mm -> Fusion world Point3D (cm)."""
    q = w(p)
    return P(cm(q[0]), cm(q[1]), cm(q[2]))


def _dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def sketch_normal(sketch):
    x, y = sketch.xDirection, sketch.yDirection
    return (x.y * y.z - x.z * y.y, x.z * y.x - x.x * y.z, x.x * y.y - x.y * y.x)


class Sk:
    """A sketch plus its height (drone z). p() converts a drone-space point into this sketch's own
    coordinates, so geometry lands where intended however Fusion orients the sketch's axes."""

    def __init__(self, sketch, z):
        self.sketch, self.z = sketch, z

    def __getattr__(self, name):
        return getattr(self.sketch, name)

    def p(self, x, y):
        return self.sketch.modelToSketchSpace(WP((x, y, self.z)))


def new_comp(parent, name):
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ


def set_transform(occ, m):
    """Move an occurrence and capture the position. In a parametric design an uncaptured move is
    undone by the next recompute, which is what sent parts back to their STEP origin."""
    try:
        occ.transform2 = m
    except Exception:
        occ.transform = m
    try:
        design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
        if design.snapshots.hasPendingSnapshot:
            design.snapshots.add()
    except Exception:
        pass


def offset_plane(comp, base, along, dist):
    """Construction plane parallel to `base`, `dist` mm along the world direction `along`."""
    n = base.geometry.normal
    sign = 1.0 if _dot((n.x, n.y, n.z), along) > 0 else -1.0
    planes = comp.constructionPlanes
    inp = planes.createInput()
    inp.setByOffset(base, V(cm(dist) * sign))
    return planes.add(inp)


def sketch_at(comp, z, name=None):
    """Horizontal (drone) sketch at height z."""
    base = getattr(comp, HPLANE)
    plane = base if abs(z) < 1e-9 else offset_plane(comp, base, w((0, 0, 1)), z)
    sk = comp.sketches.add(plane)
    if name:
        sk.name = name
    return Sk(sk, z)


def extrude_dir(comp, sketch, profiles, h, op, world_dir):
    """Extrude h mm in the given world direction, whichever way the sketch normal points."""
    col = adsk.core.ObjectCollection.create()
    for p in profiles:
        col.add(p)
    inp = comp.features.extrudeFeatures.createInput(col, op)
    pos = _dot(sketch_normal(sketch), world_dir) > 0
    dirn = adsk.fusion.ExtentDirections.PositiveExtentDirection if pos else         adsk.fusion.ExtentDirections.NegativeExtentDirection
    inp.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(cm(h))), dirn)
    return comp.features.extrudeFeatures.add(inp)


def extrude_profiles(comp, sk, profiles, h, op, down=False):
    """Extrude drone-up (or down) by h mm."""
    return extrude_dir(comp, sk.sketch, profiles, h, op, w((0, 0, -1 if down else 1)))


def extrude_all(comp, sk, h, op, down=False):
    return extrude_profiles(comp, sk, [sk.profiles.item(i) for i in range(sk.profiles.count)], h, op, down)


def rect_pts(cx, cy, sx, sy, rot):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + dx * sx / 2.0 * ca - dy * sy / 2.0 * sa, cy + dx * sx / 2.0 * sa + dy * sy / 2.0 * ca)
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def add_box(comp, name, cx, cy, z0, sx, sy, sz, rot=0.0):
    """Box centred at (cx, cy), optionally turned by rot degrees about its own centre."""
    sk = sketch_at(comp, z0)
    pts = rect_pts(cx, cy, sx, sy, rot)
    for i in range(4):
        sk.sketchCurves.sketchLines.addByTwoPoints(sk.p(*pts[i]), sk.p(*pts[(i + 1) % 4]))
    body = extrude_all(comp, sk, sz, NEW).bodies.item(0)
    body.name = name
    return body


def add_cyl(comp, name, cx, cy, z0, d, h):
    sk = sketch_at(comp, z0)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.p(cx, cy), cm(d / 2.0))
    body = extrude_all(comp, sk, h, NEW).bodies.item(0)
    body.name = name
    return body


def set_opacity(body, o):
    try:
        body.opacity = o
    except Exception:
        pass


def rotz(x, y, deg):
    a = math.radians(deg)
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


MOTORS = [(-MOTOR_X, MOTOR_Y, "FL"), (MOTOR_X, MOTOR_Y, "FR"),
          (-MOTOR_X, -MOTOR_Y, "RL"), (MOTOR_X, -MOTOR_Y, "RR")]
TRI_ANGLES = [90 + 120 * k for k in range(3)]

# AIO screw bosses sit at front/rear/left/right (the 25.5 pattern turned 45 deg)
HR = AIO_PATTERN / math.sqrt(2.0)
HOLE_F, HOLE_B, HOLE_L, HOLE_R = (0, HR), (0, -HR), (-HR, 0), (HR, 0)
FL, FR, RL, RR = (-MOTOR_X, MOTOR_Y), (MOTOR_X, MOTOR_Y), (-MOTOR_X, -MOTOR_Y), (MOTOR_X, -MOTOR_Y)


def tri_holes(mx, my):
    return [(mx + TRI_R * math.cos(math.radians(a)), my + TRI_R * math.sin(math.radians(a)))
            for a in TRI_ANGLES]


def _in_poly(x, y, poly):
    s = None
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        cr = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
        if abs(cr) < 1e-9:
            continue
        if s is None:
            s = cr > 0
        elif (cr > 0) != s:
            return False
    return True


def material_profiles(sk, polys, circles):
    """Profiles whose centroid lies inside one of the material shapes (so windows stay open)."""
    keep = []
    for i in range(sk.profiles.count):
        p = sk.profiles.item(i)
        cen = p.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).centroid
        dc = d_of((cen.x * 10.0, cen.y * 10.0, cen.z * 10.0))
        if abs(dc[2] - sk.z) > 1e-3:                       # came back in sketch space, not model
            m_ = sk.sketch.sketchToModelSpace(cen)
            dc = d_of((m_.x * 10.0, m_.y * 10.0, m_.z * 10.0))
        x, y = dc[0], dc[1]
        if any(_in_poly(x, y, q) for q in polys) or \
                any(math.hypot(x - cx, y - cy) <= r for cx, cy, r in circles):
            keep.append(p)
    return keep


def sketch_bar(sk, polys, p, q, w):
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2.0, dx / L * w / 2.0
    quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
    for i in range(4):
        sk.sketchCurves.sketchLines.addByTwoPoints(sk.p(*quad[i]), sk.p(*quad[(i + 1) % 4]))
    polys.append(quad)


def sketch_disc(sk, circles, p, d):
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.p(*p), cm(d / 2.0))
    circles.append((p[0], p[1], d / 2.0))


# ----------------------------- frame -----------------------------

def build_frame(root):
    occ = new_comp(root, "Frame - Fractal 65 Lite (streamlined)")
    c = occ.component

    sk = sketch_at(c, PLATE_T, "Frame bars+pads")
    polys, circles = [], []
    paths = [[FL, HOLE_F, FR], [RL, HOLE_B, RR], [FL, HOLE_L, RL], [FR, HOLE_R, RR]]
    if CENTER_CROSS:
        paths += [[HOLE_F, HOLE_B], [HOLE_L, HOLE_R]]
    for path in paths:
        for i in range(len(path) - 1):
            sketch_bar(sk, polys, path[i], path[i + 1], BAR_W)
    for mx, my, _ in MOTORS:
        sketch_disc(sk, circles, (mx, my), PAD_D)
        for h in tri_holes(mx, my):
            sketch_disc(sk, circles, h, SCREW_BUMP_D)
    for h in (HOLE_F, HOLE_B, HOLE_L, HOLE_R):
        sketch_disc(sk, circles, h, BOSS_D)
    body = extrude_profiles(c, sk, material_profiles(sk, polys, circles), PLATE_T, NEW, down=True).bodies.item(0)
    body.name = "Carbon plate 1.5mm"

    hs = sketch_at(c, PLATE_T, "Frame holes")
    circ = hs.sketchCurves.sketchCircles
    for h in (HOLE_F, HOLE_B, HOLE_L, HOLE_R):
        circ.addByCenterRadius(hs.p(*h), cm(AIO_HOLE_D / 2.0))
    for mx, my, _ in MOTORS:
        circ.addByCenterRadius(hs.p(mx, my), cm(MOTOR_HOLE_D / 2.0))
        for h in tri_holes(mx, my):
            circ.addByCenterRadius(hs.p(*h), cm(TRI_D / 2.0))
    extrude_all(c, hs, PLATE_T, CUT, down=True)


# ----------------------------- motors / props -----------------------------

def build_motors(root):
    occ = new_comp(root, "Motors - 0802 x4")
    c = occ.component
    for mx, my, n in MOTORS:
        sk = sketch_at(c, PLATE_T, "Y base " + n)
        polys, circles = [], []
        sketch_disc(sk, circles, (mx, my), MOTOR_HUB_D)
        for h in tri_holes(mx, my):
            sketch_bar(sk, polys, (mx, my), h, MOTOR_ARM_W)
            sketch_disc(sk, circles, h, MOTOR_ARM_END_D)
        base = extrude_profiles(c, sk, material_profiles(sk, polys, circles), MOTOR_BASE_H, NEW).bodies.item(0)
        base.name = "Y base " + n
        z_bell = PLATE_T + MOTOR_BASE_H
        add_cyl(c, "Bell " + n, mx, my, z_bell, MOTOR_D, MOTOR_BELL_H)
        add_cyl(c, "Shaft " + n, mx, my, z_bell + MOTOR_BELL_H, MOTOR_SHAFT_D, MOTOR_SHAFT_H)


def build_props(root):
    occ = new_comp(root, "Prop discs 31mm (keep-out)")
    c = occ.component
    for mx, my, n in MOTORS:
        set_opacity(add_cyl(c, "Prop " + n, mx, my, PROP_Z, PROP_D, PROP_T), 0.35)


# ----------------------------- boards -----------------------------

def board_holes():
    """25.5 mm pattern turned by STACK_YAW: lands on the frame's diamond bosses."""
    h = AIO_PATTERN / 2.0
    return [rotz(dx * h, dy * h, STACK_YAW) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def add_pcb(comp, name, z0, size, t, ear_d, hole_d):
    """Square PCB (turned by STACK_YAW) with optional round ears and the 25.5 mm mounting holes."""
    sk = sketch_at(comp, z0, name + " outline")
    corners = rect_pts(0, 0, size, size, STACK_YAW)
    for i in range(4):
        sk.sketchCurves.sketchLines.addByTwoPoints(sk.p(*corners[i]), sk.p(*corners[(i + 1) % 4]))
    if ear_d > 0:
        for hx, hy in board_holes():
            sk.sketchCurves.sketchCircles.addByCenterRadius(sk.p(hx, hy), cm(ear_d / 2.0))
    body = extrude_all(comp, sk, t, NEW).bodies.item(0)
    body.name = name
    hs = sketch_at(comp, z0, name + " holes")
    for hx, hy in board_holes():
        hs.sketchCurves.sketchCircles.addByCenterRadius(hs.p(hx, hy), cm(hole_d / 2.0))
    extrude_all(comp, hs, t, CUT)
    return body


def lucid_parts_world():
    """LUCID_PARTS turned so the USB corner points at LUCID_USB_DIR: (name, x, y, rot, sx, sy, h, side)."""
    yaw = LUCID_USB_DIR - 45.0
    out = []
    for name, x, y, rot, sx, sy, h, side in LUCID_PARTS:
        wx, wy = rotz(x, y, yaw)
        out.append((name, wx, wy, rot + yaw, sx, sy, h, side))
    return out


def build_stack(root):
    """Plate -> O4 Lite -> Lucid AIO. Returns (Lucid PCB top z, O4 dummy occ, Lucid dummy occ)."""
    z_o4 = PLATE_T + O4_STANDOFF
    z_o4_top = z_o4 + O4_PCB_T
    o4_occ = new_comp(root, "DJI O4 Lite air unit (dummy)")
    c = o4_occ.component
    add_pcb(c, "PCB", z_o4, O4_SIZE, O4_PCB_T, 0, O4_HOLE)
    add_box(c, "Top components", 0, 0, z_o4_top, O4_COMP_SIZE, O4_COMP_SIZE, O4_COMP_TOP_H, STACK_YAW)
    add_box(c, "Bottom components", 0, 0, z_o4 - O4_COMP_BOT_H, O4_COMP_SIZE, O4_COMP_SIZE,
            O4_COMP_BOT_H, STACK_YAW)

    z_aio_top = PLATE_T + STACK_H
    z_aio = z_aio_top - AIO_PCB_T
    lucid_occ = new_comp(root, "TBS Lucid AIO 1-2S (dummy)")
    c = lucid_occ.component
    add_pcb(c, "PCB", z_aio, AIO_SIZE, AIO_PCB_T, AIO_EAR_D, AIO_HOLE)
    lowest = z_aio
    for name, x, y, rot, sx, sy, h, side in lucid_parts_world():
        z0 = z_aio_top if side == "up" else z_aio - h
        lowest = min(lowest, z0)
        add_box(c, name, x, y, z0, sx, sy, h, rot)

    o4_top = z_o4_top + O4_COMP_TOP_H
    if lowest < o4_top:
        WARNINGS.append("Check clearance: the Lucid's underside parts sit %.1f mm below the top of the "
                        "simplified O4 block. Use Inspect > Interference on the real STEP models."
                        % (o4_top - lowest))
    build_standoffs(root, z_o4_top, z_aio)
    return z_aio_top, o4_occ, lucid_occ


def add_tube(comp, name, cx, cy, z0, od, id_, h):
    sk = sketch_at(comp, z0)
    circ = sk.sketchCurves.sketchCircles
    circ.addByCenterRadius(sk.p(cx, cy), cm(od / 2.0))
    circ.addByCenterRadius(sk.p(cx, cy), cm(id_ / 2.0))
    ring = [sk.profiles.item(i) for i in range(sk.profiles.count)
            if sk.profiles.item(i).profileLoops.count == 2]
    body = extrude_profiles(comp, sk, ring, h, NEW).bodies.item(0)
    body.name = name
    return body


def build_standoffs(root, z_o4_top, z_aio):
    """Printable TPU standoffs, as two components: bottom (plate -> O4) and top (O4 -> Lucid), 4 each."""
    h_bot = O4_STANDOFF
    h_top = z_aio - z_o4_top
    sets = []
    for label, z0, h in (("Standoffs BOTTOM plate-O4 %.1fmm x4 (TPU)" % h_bot, PLATE_T, h_bot),
                         ("Standoffs TOP O4-Lucid %.1fmm x4 (TPU)" % h_top, z_o4_top, h_top)):
        occ = new_comp(root, label)
        for i, (hx, hy) in enumerate(board_holes()):
            add_tube(occ.component, "Standoff %d" % (i + 1), hx, hy, z0, STANDOFF_OD, STANDOFF_ID, h)
        sets.append((occ, h))
    if not EXPORT_STL:
        return
    out = os.path.join(HERE, "stl")
    os.makedirs(out, exist_ok=True)
    em = adsk.core.Application.get().activeProduct.exportManager
    for (occ, h), fname in zip(sets, ("standoffs_BOTTOM_plate-to-O4_%.1fmm_x4.stl" % h_bot,
                                      "standoffs_TOP_O4-to-Lucid_%.1fmm_x4.stl" % h_top)):
        opts = em.createSTLExportOptions(occ, os.path.join(out, fname))
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        em.execute(opts)


# ----------------------------- camera -----------------------------

def add_cyl_y(comp, name, cx, cz, y0, d, length):
    """Cylinder along the drone's nose axis (+y) from y0, centred at drone (cx, cz)."""
    f = w((0, 1, 0))
    base = max((comp.xYConstructionPlane, comp.xZConstructionPlane, comp.yZConstructionPlane),
               key=lambda pl: abs(_dot((pl.geometry.normal.x, pl.geometry.normal.y, pl.geometry.normal.z), f)))
    plane = offset_plane(comp, base, f, y0) if abs(y0) > 1e-9 else base
    sk = comp.sketches.add(plane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(WP((cx, y0, cz))), cm(d / 2.0))
    body = extrude_dir(comp, sk, [sk.profiles.item(0)], length, NEW, f).bodies.item(0)
    body.name = name
    return body


def build_camera(root):
    """Bare O4 Lite camera, lens facing +Y: connector + cable at the top, board, body, lens."""
    occ = new_comp(root, "DJI O4 Lite camera (from DJI drawing)")
    c = occ.component
    zc = CAM_CENTER_Z
    py = CAM_REAR_Y
    pcb_z0 = zc - CAM_PCB[2] / 2.0
    pcb_z1 = zc + CAM_PCB[2] / 2.0
    add_box(c, "Cable connector", 0, py + CAM_CONN[1] / 2.0,
            pcb_z1 - CAM_CONN_TOP_GAP - CAM_CONN[2], *CAM_CONN)
    add_box(c, "Rear part (low)", 0, py + CAM_CONN[1] - CAM_REAR_PART[1] / 2.0, pcb_z0 + 0.5, *CAM_REAR_PART)
    add_box(c, "Cable exit (keep-out)", 0, py + CAM_CONN[1] - CAM_CABLE[1] / 2.0, pcb_z1, *CAM_CABLE)
    y = py + CAM_CONN[1]
    add_box(c, "Board stack", 0, y + CAM_PCB[1] / 2.0, pcb_z0, *CAM_PCB)
    add_box(c, "Top tabs", 0, y + CAM_PCB[1] / 2.0, pcb_z1 - CAM_TOP_TAB[1],
            CAM_TOP_TAB[0], CAM_PCB[1], CAM_TOP_TAB[1])
    y += CAM_PCB[1]
    zb = zc + CAM_BODY_Z_OFF
    add_box(c, "Body", 0, y + CAM_BODY_D / 2.0, zb - CAM_BODY_WH / 2.0, CAM_BODY_WH, CAM_BODY_D, CAM_BODY_WH)
    y += CAM_BODY_D
    add_cyl_y(c, "Lens", 0, zb, y, CAM_LENS_D, CAM_LENS_L)
    if CAM_TILT_DEG:
        m = adsk.core.Matrix3D.create()
        m.setToRotation(math.radians(CAM_TILT_DEG), adsk.core.Vector3D.create(*w((1, 0, 0))),
                        WP((0, py, zc)))
        set_transform(occ, m)


# ----------------------------- STEP import -----------------------------

def _bbox_mm(ent):
    b = ent.boundingBox
    lo, hi = b.minPoint, b.maxPoint
    return (lo.x * 10, lo.y * 10, lo.z * 10), (hi.x * 10, hi.y * 10, hi.z * 10)


def _centre(ent):
    lo, hi = _bbox_mm(ent)
    return tuple((lo[i] + hi[i]) / 2.0 for i in range(3))


def _matvec(R, v):
    return tuple(sum(R[i][j] * v[j] for j in range(3)) for i in range(3))


def _matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _rot_to_z(u):
    """Rotation matrix taking unit vector u onto +Z."""
    ux, uy, uz = u
    if uz > 0.999:
        return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if uz < -0.999:
        return [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
    n = math.hypot(uy, ux)
    ax, ay = uy / n, -ux / n               # axis = u x Z
    c, s = uz, math.sqrt(1 - uz * uz)
    a = (ax, ay, 0.0)
    K = [[0, 0, ay], [0, 0, -ax], [-ay, ax, 0]]
    return [[c * (i == j) + (1 - c) * a[i] * a[j] + s * K[i][j] for j in range(3)] for i in range(3)]


def _rot_z(deg):
    t = math.radians(deg)
    return [[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]]


def import_board_step(root, fname, label, z_bottom, usb_dir, snaps, probe=None, hide=(), known=None):
    """Import a board STEP and place it: USB side up, PCB centred on the origin, PCB bottom at z_bottom,
    and the USB turned to usb_dir. `snaps` = the board-frame angles the USB can sit at (edge or corner).
    `probe`: name fragment of a part whose top-centre (world mm) is returned. `hide`: name fragments
    of parts to hide. Returns (occurrence or None, message, probe point or None)."""
    path = os.path.join(HERE, fname) if fname else ""
    if not fname or not os.path.isfile(path):
        return None, ("%s not found" % fname) if fname else "", None
    occ = new_comp(root, label)
    comp = occ.component
    im = adsk.core.Application.get().importManager
    im.importToTarget(im.createSTEPImportOptions(path), comp)

    bodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    occs = [comp.allOccurrences.item(i) for i in range(comp.allOccurrences.count)]
    for o in occs:
        bodies += [o.bRepBodies.item(i) for i in range(o.bRepBodies.count)]
    # PCB = the thin ~30 x 30 body with the biggest footprint (ECAD exports may be surface bodies,
    # so don't rely on volume)
    pcb, best = None, 0.0
    for b in bodies:
        lo, hi = _bbox_mm(b)
        d = sorted(hi[i] - lo[i] for i in range(3))
        if d[0] < 2.0 and 27.0 < d[1] and d[2] < 31.5 and d[1] * d[2] > best:
            pcb, best = b, d[1] * d[2]
    usb = next((o for o in occs if "USB" in o.component.name.upper()), None)
    for o in occs:
        if any(h in o.component.name.upper() for h in hide):
            o.isLightBulbOn = False
    probe_box = None
    if probe:
        po = next((o for o in occs if probe in o.component.name.upper()), None)
        if po is not None:
            probe_box = _bbox_mm(po)

    if known is not None:
        R, t = known
        how = "placed from its known STEP layout"
    elif pcb is not None and usb is not None:
        lo, hi = _bbox_mm(pcb)
        pc = tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
        dims = [hi[i] - lo[i] for i in range(3)]
        thin = dims.index(min(dims))
        uc = _centre(usb)
        up = [0.0, 0.0, 0.0]
        up[thin] = 1.0 if uc[thin] > pc[thin] else -1.0      # USB side goes up
        R1 = _rot_to_z(up)
        d = _matvec(R1, tuple(uc[i] - pc[i] for i in range(3)))
        ang = math.degrees(math.atan2(d[1], d[0])) % 360.0
        phi = min(snaps, key=lambda s: abs((ang - s + 180.0) % 360.0 - 180.0))
        R = _matmul(_rot_z(usb_dir - phi), R1)
        c2 = _matvec(R, pc)
        t = (-c2[0], -c2[1], z_bottom - (c2[2] - min(dims) / 2.0))
        how = "auto-placed"
    else:
        return occ, "%s imported but not auto-placed (PCB or USB not found): align it by hand." % fname, None
    Rw, tw = _matmul(O, R), w(t)                         # drone placement -> world placement
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(cm(tw[0]), cm(tw[1]), cm(tw[2])),
                              adsk.core.Vector3D.create(Rw[0][0], Rw[1][0], Rw[2][0]),
                              adsk.core.Vector3D.create(Rw[0][1], Rw[1][1], Rw[2][1]),
                              adsk.core.Vector3D.create(Rw[0][2], Rw[1][2], Rw[2][2]))
    set_transform(occ, m)

    probe_pt = None
    if probe_box:
        lo, hi = probe_box
        corners = [_matvec(R, (x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        corners = [tuple(p[i] + t[i] for i in range(3)) for p in corners]
        probe_pt = (sum(p[0] for p in corners) / 8.0, sum(p[1] for p in corners) / 8.0,
                    max(p[2] for p in corners))
    return occ, "%s %s on the stack (USB facing %g deg)." % (fname, how, usb_dir), probe_pt


# ----------------------------- batteries / mount -----------------------------

def battery_z0(z_aio_top):
    """Battery bottom: above the tallest USB-side Lucid part under the widest battery footprint."""
    w = max(s[0] for _, s, _ in BATTERIES) / 2.0
    l = max(s[1] for _, s, _ in BATTERIES) / 2.0
    tallest = 0.0
    for name, x, y, rot, sx, sy, h, side in lucid_parts_world():
        r = max(sx, sy) / 2.0
        if side == "up" and abs(x - BATT_X) < w + r and abs(y - BATT_Y_OFFSET) < l + r:
            tallest = max(tallest, h)
    return z_aio_top + tallest + BATT_CLEAR


def build_batteries(root, z_aio_top):
    z0 = battery_z0(z_aio_top)
    for name, size, shown in BATTERIES:
        occ = new_comp(root, "Battery " + name)
        set_opacity(add_box(occ.component, "Battery", BATT_X, BATT_Y_OFFSET, z0, *size), 0.6)
        occ.isLightBulbOn = shown


def build_mount_ref(root, z_aio_top):
    """Empty mount component with a reference sketch: front/back M2 bolt holes on top of the Lucid."""
    occ = new_comp(root, "O4 Cam + Battery + Antenna Mount (design here)")
    c = occ.component
    sk = sketch_at(c, z_aio_top, "Mount ref - F/B bolt holes on Lucid")
    for h in (HOLE_F, HOLE_B):
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.p(*h), cm(AIO_HOLE_D / 2.0))
    for _, size, _ in BATTERIES:
        r = rect_pts(BATT_X, BATT_Y_OFFSET, size[0], size[1], 0.0)
        for i in range(4):
            sk.sketchCurves.sketchLines.addByTwoPoints(sk.p(*r[i]), sk.p(*r[(i + 1) % 4]))


# ----------------------------- orientation -----------------------------

def up_axis():
    """'Y-up' or 'Z-up': UP_AXIS, or Fusion's default modelling orientation when set to 'auto'."""
    if UP_AXIS in ("Y-up", "Z-up"):
        return UP_AXIS
    try:
        o = adsk.core.Application.get().preferences.generalPreferences.defaultModelingOrientation
        return "Z-up" if o == adsk.core.DefaultModelingOrientations.ZUpModelingOrientation else "Y-up"
    except Exception:
        return "Y-up"


def set_orientation():
    """Pick the drone -> world mapping for this Fusion's up axis. Returns 'Y-up' or 'Z-up'."""
    global O, HPLANE
    mode = up_axis()
    O, HPLANE = ORIENT[mode]
    return mode


# ----------------------------- main -----------------------------

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        del WARNINGS[:]
        # Built directly in Fusion's orientation: nose faces the Front view, top faces the Top view.
        mode = set_orientation()
        top = new_comp(design.rootComponent, PROJECT)
        root = top.component

        build_frame(root)
        build_motors(root)
        build_props(root)
        z_top, o4_dummy, lucid_dummy = build_stack(root)
        build_camera(root)
        build_batteries(root, z_top)
        build_mount_ref(root, z_top)

        msgs = []
        # O4: keeps its original antenna (moves with the board); hides the loose parts
        o4_step, m, _ = import_board_step(root, O4_STEP, "DJI O4 Lite (STEP)", PLATE_T + O4_STANDOFF,
                                          O4_USB_DIR, [0.0, 90.0, 180.0, 270.0], hide=O4_STEP_HIDE)
        msgs.append(m)
        if o4_step is not None and "placed" in m and HIDE_DUMMY_IF_STEP:
            o4_dummy.isLightBulbOn = False
        # Lucid: TBS's STEP has the board centred on its origin, PCB top at z=0, USB side at -Z.
        # Flip it USB-side up, then turn the USB corner (at +45 deg after the flip) to LUCID_USB_DIR.
        flip = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
        lucid_known = (_matmul(_rot_z(LUCID_USB_DIR - 45.0), flip), (0.0, 0.0, PLATE_T + STACK_H - AIO_PCB_T))
        lucid_step, m, _ = import_board_step(root, LUCID_STEP, "TBS Lucid AIO 1-2S (STEP)",
                                             PLATE_T + STACK_H - AIO_PCB_T, LUCID_USB_DIR,
                                             [45.0, 135.0, 225.0, 315.0], known=lucid_known)
        msgs.append(m)
        if lucid_step is not None and "placed" in m and HIDE_DUMMY_IF_STEP:
            lucid_dummy.isLightBulbOn = False

        msgs += WARNINGS
        msgs.append("Built for a %s design: nose faces the Front view, top faces the Top view." % mode)

        app.activeViewport.fit()
        ui.messageBox("%s mock-up built.\n\n%s\n\nDimensions marked ASSUMED in the script are estimates."
                      % (PROJECT, "\n".join(x for x in msgs if x)), PROJECT)
    except Exception:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()), PROJECT)
