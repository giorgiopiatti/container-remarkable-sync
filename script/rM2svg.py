#!/usr/bin/env python3
#
# Script for converting reMarkable tablet ".rm" files to SVG image.
# Based on rM2svg from
#
#    https://github.com/lschwetlick/maxio/tree/master/tools
#
# Format appears to be as follows:
#
#  header: 'reMarkable .lines file, version=3          '
#  4 bytes integer: number of layers
#  for each layer:
#      4 bytes integer: number of strokes
#      for each stroke:
#          4 bytes integer: pen
#          4 bytes integer: colour
#          4 bytes: unknown
#          4 bytes floating point: width
#          4 bytes integer: number of segments
#          for each segment:
#              6 floating point numbers: x, y, pressure, title, unknown, unknown
#
#
# Eric S Fraga
import sys
import struct
import os.path
import argparse


__prog_name__ = "rm2svg"
__version__ = "0.0.2"


# Size
default_x_width = 1404
default_y_width = 1872

# Mappings
stroke_colour = {
    0: "black",
    1: "grey",
    2: "white",
}
'''stroke_width={
    0x3ff00000 : 2,
    0x40000000 : 4,
    0x40080000 : 8,
}'''


def main():
    parser = argparse.ArgumentParser(prog=__prog_name__)
    parser.add_argument('--height',
                        help='Desired height of image',
                        type=float,
                        default=default_y_width)
    parser.add_argument('--width',
                        help='Desired width of image',
                        type=float,
                        default=default_x_width)
    parser.add_argument("-i",
                        "--input",
                        help=".rm input file",
                        required=True,
                        metavar="FILENAME",
                        # type=argparse.FileType('r')
                        )
    parser.add_argument("-o",
                        "--output",
                        help="prefix for output files",
                        required=True,
                        metavar="NAME",
                        # type=argparse.FileType('w')
                        )
    parser.add_argument("-c",
                        "--coloured_annotations",
                        help="Colour annotations for document markup.",
                        action='store_true',
                        )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    if not os.path.exists(args.input):
        parser.error('The file "{}" does not exist!'.format(args.input))

    rm2svg(args.input, args.output, args.coloured_annotations,
           args.width, args.height)


def abort(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def rm2svg(input_file, output_name, coloured_annotations=False,
           x_width=default_x_width, y_width=default_y_width):

    if coloured_annotations:
        global stroke_colour
        stroke_colour = {
            0: "blue",
            1: "red",
            2: "white",
            3: "yellow"
        }

    # Read the file in memory. Consider optimising by reading chunks.
    with open(input_file, 'rb') as f:
        data = f.read()
    offset = 0

    # Is this a reMarkable .lines file?
    expected_header = b'reMarkable .lines file, version=3          '
    if len(data) < len(expected_header) + 4:
        abort('File too short to be a valid file')

    fmt = '<{}sI'.format(len(expected_header))
    header, nlayers = struct.unpack_from(fmt, data, offset)
    offset += struct.calcsize(fmt)
    # print('header={} nlayers={}'.format(header, nlayers))
    if header != expected_header or nlayers < 1:
        abort('Not a valid reMarkable file: <header={}> <nlayers={}'.format(
            header, nlayers))

    output = open(output_name, 'w')
    # BEGIN Notebook
    output.write(
        '<svg xmlns="http://www.w3.org/2000/svg" height="{}" width="{}">'.format(y_width, x_width))
    output.write('''
        <script type="application/ecmascript"> <![CDATA[
            var visiblePage = 'p1';
            function goToPage(page) {
                document.getElementById(visiblePage).setAttribute('style', 'display: none');
                document.getElementById(page).setAttribute('style', 'display: inline');
                visiblePage = page;
            }
        ]]> </script>
    ''')

    # Iterate through pages (There is at least one)
    output.write('<g id="p1" style="display:inline">')

    # Iterate through layers on the page (There is at least one)
    for layer in range(nlayers):
        # print('New layer')
        fmt = '<I'
        (nstrokes,) = struct.unpack_from(fmt, data, offset)
        offset += struct.calcsize(fmt)

        # print('nstrokes={}'.format(nstrokes))
        # Iterate through the strokes in the layer (If there is any)
        for stroke in range(nstrokes):
            fmt = '<IIIfI'
            pen, colour, i_unk, width, nsegments = struct.unpack_from(
                fmt, data, offset)
            offset += struct.calcsize(fmt)
            # print('pen={} colour={} i_unk={} width={} nsegments={}'.format(pen,colour,i_unk,width,nsegments))
            opacity = 1
            last_x = -1.
            last_y = -1.
            # if i_unk != 0: # No theory on that one
            #print('Unexpected value at offset {}'.format(offset - 12))
            if pen == 0 or pen == 1:
                pass  # Dynamic width, will be truncated into several strokes
            elif pen == 2 or pen == 4:  # Pen / Fineliner
                width = 32 * width * width - 116 * width + 107
                width *= 2
            elif pen == 3:  # Marker
                width = 64 * width - 112
                opacity = 0.9
                width *= 1.5
            elif pen == 5:  # Highlighter
                width = 30
                opacity = 0.2
                if coloured_annotations:
                    colour = 3
            elif pen == 6:  # Eraser
                opacity = 0.
            elif pen == 7:  # Pencil-Sharp
                width = 16 * width - 27
                opacity = 0.9
            elif pen == 8:  # Erase area
                opacity = 0.
            else:
                print('Unknown pen: {}'.format(pen))
                opacity = 0.

            width /= 2.3  # adjust for transformation to A4

            #print('Stroke {}: pen={}, colour={}, width={}, nsegments={}'.format(stroke, pen, colour, width, nsegments))
            output.write('<polyline style="fill:none;stroke:{};stroke-width:{:.3f};opacity:{}" points="'.format(
                stroke_colour[colour], width, opacity))  # BEGIN stroke

            # Iterate through the segments to form a polyline
            for segment in range(nsegments):
                fmt = '<ffffff'
                xpos, ypos, pressure, tilt, i_unk2, j_unk2 = struct.unpack_from(
                    fmt, data, offset)
                offset += struct.calcsize(fmt)
                # print('(x,y)=({},{})'.format(xpos,ypos))
                #xpos += 60
                #ypos -= 20
                ratio = (y_width/x_width)/(1872/1404)
                if ratio > 1:
                    xpos = ratio*((xpos*x_width)/1404)
                    ypos = (ypos*y_width)/1872
                else:
                    xpos = (xpos*x_width)/1404
                    ypos = (1/ratio)*(ypos*y_width)/1872
                if pen == 0:
                    if 0 == segment % 8:
                        segment_width = (5. * tilt) * (6. * width - 10) * \
                            (1 + 2. * pressure * pressure * pressure)
                        #print('    width={}'.format(segment_width))
                        output.write('" />\n<polyline style="fill:none;stroke:{};stroke-width:{:.3f}" points="'.format(
                            stroke_colour[colour], segment_width))  # UPDATE stroke
                        if last_x != -1.:
                            # Join to previous segment
                            output.write(
                                '{:.3f},{:.3f} '.format(last_x, last_y))
                        last_x = xpos
                        last_y = ypos
                elif pen == 1:
                    if 0 == segment % 8:
                        segment_width = (10. * tilt - 2) * (8. * width - 14)
                        segment_opacity = (pressure - .2) * (pressure - .2)
                        #print('    width={}, opacity={}'.format(segment_width, segment_opacity))
                        output.write('" /><polyline style="fill:none;stroke:{};stroke-width:{:.3f};opacity:{:.3f}" points="'.format(
                            stroke_colour[colour], segment_width, segment_opacity))  # UPDATE stroke
                        if last_x != -1.:
                            # Join to previous segment
                            output.write(
                                '{:.3f},{:.3f} '.format(last_x, last_y))
                        last_x = xpos
                        last_y = ypos

                # BEGIN and END polyline segment
                output.write('{:.3f},{:.3f} '.format(xpos, ypos))

            output.write('" />\n')  # END stroke

    # Overlay the page with a clickable rect to flip pages
    output.write(
        '<rect x="0" y="0" width="{}" height="{}" fill-opacity="0"/>'.format(x_width, y_width))
    output.write('</g>')  # Closing page group
    output.write('</svg>')  # END notebook
    output.close()


if __name__ == "__main__":
    main()
