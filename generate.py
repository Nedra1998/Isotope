#!/usr/bin/env python3
import json
import numpy as np
from argparse import ArgumentParser

from terminaltables import SingleTable
from colormath.color_objects import sRGBColor, LabColor, HSVColor, HSLColor, XYZColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

XTERM = []
with open('xterm.json') as file:
    schemeRaw = json.load(file)
for entry in schemeRaw:
    XTERM.append({
        'id':
        entry['colorId'],
        'color':
        convert_color(sRGBColor.new_from_rgb_hex(entry['hexString']),
                      LabColor),
        'name':
        entry['name']
    })


def fmtHex(str):
    black = convert_color(sRGBColor(0, 0, 0), LabColor)
    white = convert_color(sRGBColor(1, 1, 1), LabColor)
    color = sRGBColor.new_from_rgb_hex(str)
    lcolor = convert_color(color, LabColor)
    if delta_e_cie2000(lcolor, white) > delta_e_cie2000(lcolor, black):
        return "\033[48;2;{};{};{};38;2;255;255;255m{}\033[0m".format(
            int(255 * color.rgb_r), int(255 * color.rgb_g),
            int(255 * color.rgb_b), color.get_rgb_hex())
    else:
        return "\033[48;2;{};{};{};38;2;0;0;0m{}\033[0m".format(
            int(255 * color.rgb_r), int(255 * color.rgb_g),
            int(255 * color.rgb_b), color.get_rgb_hex())


def closestXTerm(color):
    color = convert_color(color, LabColor)
    des = [delta_e_cie2000(color, x['color']) for x in XTERM]
    return XTERM[np.argmin(des)]


def colorCodes(color):
    rgb = convert_color(color, sRGBColor)
    hsl = convert_color(color, HSLColor)
    lab = convert_color(color, LabColor)
    xcolor = closestXTerm(color)
    return {
        'hex': rgb.get_rgb_hex(),
        'lab': lab,
        'rgb': rgb,
        'hsl': hsl,
        'xhex': convert_color(xcolor['color'], sRGBColor).get_rgb_hex(),
        'xid': xcolor['id'],
        'xname': xcolor['name']
    }


def detailTable(colors):
    print("\033[1m{:7}  {:20} {:3} {:7}   {:22}   {:20} {:21}\033[0m".format(
        "HEX", "NAME", "ID", "XHEX", "L*A*B", "RGB", "HSL"))
    for color in colors:
        codes = colorCodes(color)
        print(
            "{:7}  {:20} {:3} {:7}  {: 6.3f} {: 7.3f} {: 7.3f}  {:6.3f} {:6.3f} {:6.3f}  {:7.3f} {:6.3f} {:6.3f}"
            .format(fmtHex(codes['hex']), codes['xname'], codes['xid'],
                    fmtHex(codes['xhex']), codes['lab'].lab_l,
                    codes['lab'].lab_a, codes['lab'].lab_b, codes['rgb'].rgb_r,
                    codes['rgb'].rgb_g, codes['rgb'].rgb_b, codes['hsl'].hsl_h,
                    codes['hsl'].hsl_s, codes['hsl'].hsl_l))

BASEA = convert_color(sRGBColor.new_from_rgb_hex("#263238"), LabColor)
BASEB = convert_color(sRGBColor.new_from_rgb_hex("#eceff1"), LabColor)
L_STEPS = 8
monochrome = [
    LabColor(np.interp(x, [0, 1], [BASEA.lab_l, BASEB.lab_l]),
             np.interp(x, [0, 1], [BASEA.lab_a, BASEB.lab_a]),
             np.interp(x, [0, 1], [BASEA.lab_b, BASEB.lab_b]))
    for x in np.linspace(0, 1, L_STEPS)
]
detailTable(monochrome)
avgMonL = np.mean([x.lab_l for x in monochrome])

HUE_BASE = 0
HUE_STEPS = [19, 28, 14, 76, 37, 61, 35]

