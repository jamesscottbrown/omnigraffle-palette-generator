import json
import re
import plistlib
import argparse
from os import listdir, makedirs
from os.path import isfile, join, exists
from shutil import copyfile
import sys


def get_size(file_name):
    with open(file_name) as f:
        for line in f:
            if "MediaBox" in line:
                m = re.search('\[\s*\S+?\s+.+?\s+(.+?)\s+(.+?)\s*\]', line)
                return m.groups([1, 2])

    return 0, 0


def convert_directory_to_stencil(dir_name, palette_name):

    if palette_name[-1] == "/":
        palette_name = palette_name[:-1]

    if palette_name[-9:] != ".gstencil":
        palette_name = palette_name + ".gstencil"

    if exists(palette_name):
        sys.exit("Output file %s already exists" % palette_name)
    else:
        makedirs(palette_name)

    if dir_name[-1] == "/":
        dir_name = dir_name[:-1]

    data = json.loads(
        '{"Layers": [{"Print": "YES", "Lock": "NO", "Name": "Layer 1", "View": "YES"}], "MagnetsVisible": "NO", "ModificationDate": "2011-10-01 20:53:35 -0700", "SmartDistanceGuidesActive": "NO", "ColumnSpacing": 36.0, "SheetTitle": "Canvas 1", "PrintOnePage": false, "NotesVisible": "NO", "AutoAdjust": false, "Modifier": "Todd Zazelenchuk", "RowSpacing": 36.0, "SmartAlignmentGuidesActive": "YES", "GraphicsList": [], "saveQuickLookFiles": "YES", "HPages": 2, "DisplayScale": "1 pt = 1 px", "GuidesLocked": "NO", "ActiveLayerIndex": 0, "GuidesVisible": "YES", "RowAlign": 2, "ApplicationVersion": ["com.omnigroup.OmniGrafflePro", "138.28.0.154505"], "UseEntirePage": false, "PrintInfo": {"NSLeftMargin": ["float", "36"], "NSTopMargin": ["float", "36"], "NSRightMargin": ["float", "36"], "NSBottomMargin": ["float", "36"], "NSPaperSize": ["coded", "BAtzdHJlYW10eXBlZIHoA4QBQISEhAdOU1ZhbHVlAISECE5TT2JqZWN0AIWEASqEhAx7X05TU2l6ZT1mZn2WgWQCgRgDhg=="], "NSPrintReverseOrientation": ["none"]}, "CanvasOrigin": "{0, 0}", "BackgroundGraphic": {"Style": {"shadow": {"Draws": "NO"}, "stroke": {"Draws": "NO"}}, "ID": 2, "Bounds": "{{0, 0}, {650, 1000}}", "Class": "SolidGraphic"}, "ImageCounter": 123, "GraphDocumentVersion": 6, "ImageList": [], "LinksVisible": "NO", "CanvasSize": "{650, 1000}", "ColumnAlign": 1, "Orientation": 2, "ImageLinkBack": [], "LayoutInfo": {"neatoSeparation": 0.0, "circoSeparation": 0.0, "circoMinDist": 18.0, "layoutEngine": "dot", "twopiSeparation": 0.0, "Animate": "NO"}, "VPages": 2, "InterfaceInfo": {"PageInspectorPageSize": 47.0}, "OriginVisible": "NO", "ReadOnly": "NO", "UniqueID": 1, "PageBreaks": "NO", "WindowInfo": {"ZoomValues": [["Canvas 1", 0.0, 1.0]], "ExpandedCanvases": [], "CurrentSheet": 0, "RightSidebar": false, "Frame": "{{23, 39}, {1210, 839}}", "SidebarWidth": 304, "Zoom": 0.7310000061988831, "FitInWindow": true, "Sidebar": true, "OutlineWidth": 142, "ListView": false}, "GridInfo": {"MinorGridColor": {"a": "0.3", "w": "0.666667"}}, "KeepToScale": false, "MasterSheets": []}')

    pdfs = [f for f in listdir(dir_name) if isfile(join(dir_name, f)) and f[-3:] == "pdf"]

    columns = 4
    size = 100

    for i, file_name in enumerate(pdfs):
        new_file_name = "image%s.pdf" % i

        data["ImageLinkBack"].append({})
        data["ImageList"].append(new_file_name)

        width, height = get_size(join(dir_name, file_name))

        col_num = (i % columns)
        row_num = (i - (i % columns)) / columns

        data["CanvasSize"] = "{%s, %s}" % ((col_num + 1) * size + 50, (row_num + 1) * size + 50)

        data["GraphicsList"].append(
            {'Bounds': '{{%s, %g}, {%s, %s}}' % (col_num * size + 50, row_num * size + 50, width, height),
             'Class': 'ShapedGraphic',
             'ID': i,
             'ImageID': i,
             'Shape': 'Rectangle',
             'Style': {'fill': {'Draws': 'NO'},
                       'shadow': {'Draws': 'NO'},
                       'stroke': {'Draws': 'NO'}}}
        )

        copyfile(join(dir_name, file_name), join(palette_name, new_file_name))

    plistlib.writePlist(data, join(palette_name, 'data.plist'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate an OmniGraffle stencil containing the images in a directory.')
    parser.add_argument('image_directory', help='directory of images')
    parser.add_argument('palette_name', help='name for the output stencil file')

    args = parser.parse_args()

    convert_directory_to_stencil(args.image_directory, args.palette_name)
