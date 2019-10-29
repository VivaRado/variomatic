import xml.etree.ElementTree as ET
from svgPathPen import SVGPathPen
from svgpathtools import parse_path as pt_parse_path

def writeGlyphPath(glyph, get_d = False):
	#
	path_d = ''
	svgGlyphAttrib = {}
	#
	if glyph.box:
		t_x = glyph.box[3]
		t_y = glyph.box[2]
	else:
		t_x = 0
		t_y = 0
	#
	if get_d:
		#
		pen = SVGPathPen(glyph)
		glyph.draw(pen)
		pathCommands = pen.getCommands()
		#
		path = pt_parse_path(pathCommands)
		#
		rev_path = path.d()
		#
		return rev_path
		#
	else:
		#
		path_d = _writeD(glyph, svgGlyphAttrib, t_x, t_y)
		#
		svgGlyph = ET.Element("path", attrib=svgGlyphAttrib )
		#
		return svgGlyph
		#
	#
#	
def _writeD(glyph, attrib, _x, _y):

	pen = SVGPathPen(glyph)
	glyph.draw(pen)
	pathCommands = pen.getCommands()
	#
	if pathCommands:
		#
		path = pt_parse_path(pathCommands)
		#
		rev_path = path.d()
		#
		flip_path = formatPath(flipPath(parsePath(rev_path), horizontal=True, vertical=False))
		#
		attrib["d"] = flip_path
		#
	else:
		#
		attrib["d"] = "Z"
		#
	return flip_path
