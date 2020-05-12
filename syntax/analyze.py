#!/usr/bin/env python3

from pprint import pprint
import json
from argparse import ArgumentParser
import numpy as np

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

XCOLOR = {}
BASE = [
    "#263238", "#37474f", "#455a64", "#546e7a", "#607d8b", "#f44336",
    "#e91e63", "#9c27b0", "#673ab7", "#3f51b5", "#2196f3", "#03a9f4",
    "#00bcd4", "#009688", "#4caf50", "#8bc34a", "#cddc39", "#ffeb3b",
    "#ffc107", "#ff9800", "#ff5722", "#78909c", "#90a4ae", "#b0bec5",
    "#cfd8dc", "#eceff1"
]
ESCAPE=True


def load_xcolor():
    global XCOLOR
    with open('colors.json') as file:
        raw = json.load(file)
    for entry in raw:
        XCOLOR[str(entry['colorId'])] = entry['hexString']
        XCOLOR[entry['name']] = entry['hexString']


ATTRS = {
    'fg': None,
    'bg': None,
    'sp': None,
    'bold': None,
    'underline': None,
    'undercurl': None,
    'reverse': None,
    'italic': None,
    'standout': None,
    'strikethrough': None
}

# Follow all "links to" then read attributes


def fmtHex(str):
    black = convert_color(sRGBColor(0, 0, 0), LabColor)
    white = convert_color(sRGBColor(1, 1, 1), LabColor)
    color = sRGBColor.new_from_rgb_hex(str)
    if ESCAPE:
        lcolor = convert_color(color, LabColor)
        if delta_e_cie2000(lcolor, white) > delta_e_cie2000(lcolor, black):
            return "\033[48;2;{};{};{};38;2;255;255;255m{}\033[0m".format(
                int(255 * color.rgb_r), int(255 * color.rgb_g),
                int(255 * color.rgb_b), color.get_rgb_hex())
        else:
            return "\033[48;2;{};{};{};38;2;0;0;0m{}\033[0m".format(
                int(255 * color.rgb_r), int(255 * color.rgb_g),
                int(255 * color.rgb_b), color.get_rgb_hex())
    else:
        return color.get_rgb_hex()


def preprocess(lines):
    groups = {}
    lastGroup = None
    for line in lines:
        if line.strip() == '':
            continue
        if 'xxx' in line:
            lastGroup = line.split('xxx')[0].strip()
            base = line.split('xxx')[-1].strip()
            source = base.split('links to')[0].strip()
            links = base.split('links to')[-1].strip()
            groups[lastGroup] = {
                'source': source,
                'links': links if 'links to' in base else None
            }
        else:
            groups[lastGroup]['source'] += ' ' + line.split(
                'links to')[0].strip()
            groups[lastGroup]['links'] = line.split(
                'links to')[-1].strip() if 'links to' in line else None
    return groups


def evalGroup(key, groups):
    attrs = ATTRS.copy()
    if groups[key]['links']:
        attrs = evalGroup(groups[key]['links'], groups)
    src = {
        x.split('=')[0].strip(): x.split('=')[-1].strip()
        for x in groups[key]['source'].split()
    }
    xreplace = lambda x: XCOLOR[x] if x in XCOLOR else x
    if 'guifg' in src and src['guifg'].startswith('#'):
        attrs['fg'] = xreplace(src['guifg'])
    elif 'ctermfg' in src and not src['ctermfg'] in ['fg', 'bg']:
        attrs['fg'] = xreplace(src['ctermfg'])
    if 'guibg' in src and src['guibg'].startswith('#'):
        attrs['bg'] = xreplace(src['guibg'])
    elif 'ctermbg' in src and not src['ctermbg'] in ['fg', 'bg']:
        attrs['bg'] = xreplace(src['ctermbg'])
    if 'guisp' in src and src['guisp'].startswith('#'):
        attrs['sp'] = xreplace(src['guisp'])
    elif 'ctermsp' in src and not src['ctermsp'] in ['fg', 'bg']:
        attrs['sp'] = xreplace(src['ctermsp'])
    if 'gui' in src:
        if 'bold' in src['gui']:
            attrs['bold'] = True
        if 'underline' in src['gui']:
            attrs['underline'] = True
        if 'undercurl' in src['gui']:
            attrs['undercurl'] = True
        if 'reverse' in src['gui']:
            attrs['reverse'] = True
        if 'italic' in src['gui']:
            attrs['italic'] = True
        if 'standout' in src['gui']:
            attrs['standout'] = True
        if 'strikethrough' in src['gui']:
            attrs['strikethrough'] = True
        if 'NONE' in src['gui']:
            attrs['bold'] = False
            attrs['underline'] = False
            attrs['undercurl'] = False
            attrs['reverse'] = False
            attrs['italic'] = False
            attrs['standout'] = False
            attrs['strikethrough'] = False
    elif 'cterm' in src:
        if 'bold' in src['cterm']:
            attrs['bold'] = True
        if 'underline' in src['cterm']:
            attrs['underline'] = True
        if 'undercurl' in src['cterm']:
            attrs['undercurl'] = True
        if 'reverse' in src['cterm']:
            attrs['reverse'] = True
        if 'italic' in src['cterm']:
            attrs['italic'] = True
        if 'standout' in src['cterm']:
            attrs['standout'] = True
        if 'strikethrough' in src['cterm']:
            attrs['strikethrough'] = True
        if 'NONE' in src['cterm']:
            attrs['bold'] = False
            attrs['underline'] = False
            attrs['undercurl'] = False
            attrs['reverse'] = False
            attrs['italic'] = False
            attrs['standout'] = False
            attrs['strikethrough'] = False
    return attrs


def process(filePath):
    lines = []
    with open(filePath) as file:
        lines = file.readlines()
    groups = preprocess(lines)
    evaledGroups = {x: evalGroup(x, groups) for x in groups}
    return evaledGroups


def de(a, b):
    return delta_e_cie2000(
        convert_color(sRGBColor.new_from_rgb_hex(a), LabColor),
        convert_color(sRGBColor.new_from_rgb_hex(b), LabColor))


def main():
    parser = ArgumentParser()
    parser.add_argument('-E', '--no-escape', action='store_false', help='Disables escape codes for no colors')
    parser.add_argument('schemes', nargs='+', help='Schemes to analyze')
    args = parser.parse_args()
    global ESCAPE
    ESCAPE = args.no_escape
    load_xcolor()
    schemes = [process(x) for x in args.schemes]
    cumsum = {}
    for scheme in schemes:
        for group, attrs in scheme.items():
            if not group in cumsum:
                cumsum[group] = {
                    'fg': {x: []
                           for x in BASE},
                    'bg': {x: []
                           for x in BASE},
                    'sp': {x: []
                           for x in BASE},
                    'bold': 0,
                    'underline': 0,
                    'undercurl': 0,
                    'reverse': 0,
                    'italic': 0,
                    'standout': 0,
                    'strikethrough': 0,
                    'count': 0
                }
            if attrs['fg']:
                cumsum[group]['fg'][BASE[np.argmin(
                    [de(x, attrs['fg']) for x in BASE])]].append(attrs['fg'])
            if attrs['bg']:
                cumsum[group]['bg'][BASE[np.argmin(
                    [de(x, attrs['bg']) for x in BASE])]].append(attrs['bg'])
            cumsum[group]['bold'] += 1 if attrs['bold'] else 0
            cumsum[group]['underline'] += 1 if attrs['underline'] else 0
            cumsum[group]['undercurl'] += 1 if attrs['undercurl'] else 0
            cumsum[group]['reverse'] += 1 if attrs['reverse'] else 0
            cumsum[group]['italic'] += 1 if attrs['italic'] else 0
            cumsum[group]['standout'] += 1 if attrs['standout'] else 0
            cumsum[group][
                'strikethrough'] += 1 if attrs['strikethrough'] else 0
            cumsum[group]['count'] += 1

    for group, attrs in cumsum.items():
        if ESCAPE:
            print("\033[1m{}:\033[0m".format(group))
        else:
            print("{}:".format(group))
        if np.any([len(x) != 0 for x in attrs['fg'].values()]):
            print("  fg:")
            for color, matches in attrs['fg'].items():
                if len(matches) == 0:
                    continue
                print("    {}:".format(fmtHex(color)),
                      *[fmtHex(x) for x in matches])
        if np.any([len(x) != 0 for x in attrs['bg'].values()]):
            print("  bg:")
            for color, matches in attrs['bg'].items():
                if len(matches) == 0:
                    continue
                print("    {}:".format(fmtHex(color)),
                      *[fmtHex(x) for x in matches])
        if np.any([len(x) != 0 for x in attrs['sp'].values()]):
            print("  sp:")
            for color, matches in attrs['sp'].items():
                if len(matches) == 0:
                    continue
                print("    {}:".format(fmtHex(color)),
                      *[fmtHex(x) for x in matches])
        for key, count in attrs.items():
            if key in ['fg', 'bg', 'sp'] or count == 0:
                continue
            print("    {}: {}".format(key, count))


if __name__ == '__main__':
    main()
