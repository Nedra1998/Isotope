#!/usr/bin/env python3
import json
import numpy as np
from argparse import ArgumentParser

from terminaltables import SingleTable
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

DELTAE = "\u0394E*"
SIGMA = "\u03c3"
MU = "\u03BC"


def preview(hex, end='\n'):
    black = convert_color(sRGBColor(0, 0, 0), LabColor)
    white = convert_color(sRGBColor(1, 1, 1), LabColor)
    color = convert_color(hex, sRGBColor)
    lcolor = convert_color(color, LabColor)
    if delta_e_cie2000(lcolor, white) > delta_e_cie2000(lcolor, black):
        print("\033[48;2;{};{};{};38;2;255;255;255m{}\033[0m".format(
            int(255 * color.rgb_r), int(255 * color.rgb_g),
            int(255 * color.rgb_b), color.get_rgb_hex()),
              end=end)
    else:
        print("\033[48;2;{};{};{};38;2;0;0;0m{}\033[0m".format(
            int(255 * color.rgb_r), int(255 * color.rgb_g),
            int(255 * color.rgb_b), color.get_rgb_hex()),
              end=end)


def loadScheme(filePath):
    schemeRaw = {}
    with open(filePath) as file:
        schemeRaw = json.load(file)
    scheme = {}
    for key, val in schemeRaw.items():
        scheme[key] = [sRGBColor.new_from_rgb_hex(x) for x in val]
    return scheme


def schemeColors(scheme):
    colors = []
    for key, val in scheme.items():
        if key in ['black', 'white', 'fg', 'bg', 'fg/bg']:
            continue
        else:
            colors += val
    return colors


def schemeMonochrome(scheme):
    colors = []
    for key, val in scheme.items():
        if not key in ['black', 'white', 'fg', 'bg', 'fg/bg']:
            continue
        else:
            colors += val
    return colors


def schemeLight(scheme):
    if 'white' in scheme:
        return scheme['white']
    return []


def schemeDark(scheme):
    if 'black' in scheme:
        return scheme['black']
    return []


def averageLab(colors):
    lcolors = [convert_color(v, LabColor) for v in colors]
    return (np.mean([v.lab_l
                     for v in lcolors]), np.mean([v.lab_a for v in lcolors]),
            np.mean([v.lab_b for v in lcolors]))


def stdLab(colors):
    lcolors = [convert_color(v, LabColor) for v in colors]
    return (np.std([v.lab_l
                    for v in lcolors]), np.std([v.lab_a for v in lcolors]),
            np.std([v.lab_b for v in lcolors]))


def averagedes(colors):
    if len(colors) == 1:
        return np.nan
    lcolors = [convert_color(v, LabColor) for v in colors]
    des = []
    for i, a in enumerate(lcolors):
        for j, b in enumerate(lcolors):
            if j <= i:
                continue
            des.append(delta_e_cie2000(a, b))
    return np.mean(des)


def stddes(colors):
    if len(colors) == 1:
        return np.nan
    lcolors = [convert_color(v, LabColor) for v in colors]
    des = []
    for i, a in enumerate(lcolors):
        for j, b in enumerate(lcolors):
            if j <= i:
                continue
            des.append(delta_e_cie2000(a, b))
    return np.std(des)


def contrast(a, b):
    a = convert_color(a, sRGBColor)
    b = convert_color(b, sRGBColor)
    la = 0.2126 * a.rgb_r + 0.7152 * a.rgb_g + 0.0722 * a.rgb_b
    lb = 0.2126 * b.rgb_r + 0.7152 * b.rgb_g + 0.0722 * b.rgb_b
    return (la + 0.05) / (lb + 0.05)


def averageContrast(a, b):
    crs = []
    for ca in a:
        for cb in b:
            crs.append(contrast(ca, cb))
    return np.mean(crs)


def stdContrast(a, b):
    crs = []
    for ca in a:
        for cb in b:
            crs.append(contrast(ca, cb))
    return np.std(crs)


def summary(scheme):
    table = [
        ["Val", "Colors", "Mono"] + [*scheme.keys()],
        ["{}L".format(SIGMA)],
        ["{}a".format(SIGMA)],
        ["{}b".format(SIGMA)],
        ["{}L".format(MU)],
        ["{}a".format(MU)],
        ["{}b".format(MU)],
        ["{}{}".format(SIGMA, DELTAE)],
        ["{}{}".format(MU, DELTAE)],
        ["{}CRL".format(SIGMA)],
        ["{}CRL".format(MU)],
        ["{}CRD".format(SIGMA)],
        ["{}CRD".format(MU)],
    ]
    colors = schemeColors(scheme)
    light = schemeLight(scheme)
    dark = schemeDark(scheme)
    slab = stdLab(colors)
    alab = averageLab(colors)
    table[1].append("{:5.2f}".format(slab[0]))
    table[2].append("{:5.2f}".format(slab[1]))
    table[3].append("{:5.2f}".format(slab[2]))
    table[4].append("{:5.2f}".format(alab[0]))
    table[5].append("{:5.2f}".format(alab[1]))
    table[6].append("{:5.2f}".format(alab[2]))
    table[7].append("{:5.2f}".format(stddes(colors)))
    table[8].append("{:5.2f}".format(averagedes(colors)))
    table[9].append("{:5.2f}".format(stdContrast(colors, light)))
    table[10].append("{:5.2f}".format(averageContrast(colors, light)))
    table[11].append("{:5.2f}".format(stdContrast(colors, dark)))
    table[12].append("{:5.2f}".format(averageContrast(colors, dark)))

    colors = schemeMonochrome(scheme)
    slab = stdLab(colors)
    alab = averageLab(colors)
    table[1].append("{:5.2f}".format(slab[0]))
    table[2].append("{:5.2f}".format(slab[1]))
    table[3].append("{:5.2f}".format(slab[2]))
    table[4].append("{:5.2f}".format(alab[0]))
    table[5].append("{:5.2f}".format(alab[1]))
    table[6].append("{:5.2f}".format(alab[2]))
    table[7].append("{:5.2f}".format(stddes(colors)))
    table[8].append("{:5.2f}".format(averagedes(colors)))
    table[9].append("{:5.2f}".format(stdContrast(colors, light)))
    table[10].append("{:5.2f}".format(averageContrast(colors, light)))
    table[11].append("{:5.2f}".format(stdContrast(colors, dark)))
    table[12].append("{:5.2f}".format(averageContrast(colors, dark)))

    for key, colors in scheme.items():
        slab = stdLab(colors)
        alab = averageLab(colors)
        table[1].append("{:5.2f}".format(slab[0]))
        table[2].append("{:5.2f}".format(slab[1]))
        table[3].append("{:5.2f}".format(slab[2]))
        table[4].append("{:5.2f}".format(alab[0]))
        table[5].append("{:5.2f}".format(alab[1]))
        table[6].append("{:5.2f}".format(alab[2]))
        table[7].append("{:5.2f}".format(stddes(colors)))
        table[8].append("{:5.2f}".format(averagedes(colors)))
        table[9].append("{:5.2f}".format(stdContrast(colors, light)))
        table[10].append("{:5.2f}".format(averageContrast(colors, light)))
        table[11].append("{:5.2f}".format(stdContrast(colors, dark)))
        table[12].append("{:5.2f}".format(averageContrast(colors, dark)))

    print(SingleTable(table).table)


def main():
    parser = ArgumentParser('quality')
    parser.add_argument('scheme', help="name of color scheme")
    parser.add_argument('-s',
                        '--summary',
                        action='store_true',
                        help='displays summary table')
    parser.add_argument('-d',
                        '--detail',
                        action='store_true',
                        help='display detailed report for each color')
    args = parser.parse_args()
    print(args)
    schemeName = args.scheme
    scheme = loadScheme('{}.json'.format(schemeName))
    print("  \033[1m{}:\033[0m".format(schemeName))
    for key, val in scheme.items():
        print("{:>8}:".format(key), end=' ')
        for v in val:
            preview(v, end=' ')
        print()
    if args.summary:
        summary(scheme)


if __name__ == "__main__":
    main()
