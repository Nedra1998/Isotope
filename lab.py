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
    hsv = convert_color(color, HSVColor)
    lab = convert_color(color, LabColor)
    xcolor = closestXTerm(color)
    return {
        'hex': sRGBColor(rgb.clamped_rgb_r, rgb.clamped_rgb_g, rgb.clamped_rgb_b).get_rgb_hex(),
        'lab': lab,
        'rgb': rgb,
        'hsv': hsv,
        'xhex': convert_color(xcolor['color'], sRGBColor).get_rgb_hex(),
        'xid': xcolor['id'],
        'xname': xcolor['name']
    }


def detailTable(colors):
    print("\033[1m{:7}  {:20} {:3} {:7}   {:25}   {:20} {:21}\033[0m".format(
        "HEX", "NAME", "ID", "XHEX", "L*A*B", "RGB", "HSV"))
    for color in colors:
        codes = colorCodes(color)
        print(
            "{:7}  {:20} {:3} {:7}  {:8.3f} {: 8.3f} {: 8.3f}  {:6.3f} {:6.3f} {:6.3f}  {:7.3f} {:7.3f} {:7.3f}"
            .format(fmtHex(codes['hex']), codes['xname'], codes['xid'],
                    fmtHex(codes['xhex']), codes['lab'].lab_l,
                    codes['lab'].lab_a, codes['lab'].lab_b, codes['rgb'].rgb_r,
                    codes['rgb'].rgb_g, codes['rgb'].rgb_b, codes['hsv'].hsv_h,
                    codes['hsv'].hsv_s, codes['hsv'].hsv_v))

colors = []
for l in np.linspace(0, 100, 3):
    for a in np.linspace(-127, 127, 3):
        for b in np.linspace(-127, 127, 3):
            colors.append(LabColor(l, a, b))
detailTable(colors)
colors = []
for r in np.linspace(0, 1, 3):
    for g in np.linspace(0, 1, 3):
        for b in np.linspace(0, 1, 3):
            colors.append(sRGBColor(r, g, b))
detailTable(colors)
colors = []
for h in np.linspace(0, 360, 9):
    colors.append(HSVColor(h, 1, 1))
detailTable(colors)
