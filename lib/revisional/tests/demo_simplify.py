import os
from context import sample

from numpy import array
from bezier import *
from fitCurves_c import *
#from fitCurves_d import *
from tkinter import *


import time

from rdp import rdp

import fontTools
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString#, writeGlyphToString, _glifTreeFromString

from fontParts.world import *

from matplotlib import pyplot as plt

import numpy as np
#
from pylab import *
import matplotlib.pyplot as plt
#
from svgPathPen import SVGPathPen
from svgpathtools import parse_path as pt_parse_path
from simple_path import *
#
import xml.etree.ElementTree as ET
#
from svgpath2mpl import parse_path as mpl_parse_path
#
import matplotlib.patches as mpatches
import matplotlib.path as mpath
#
from collections import OrderedDict

import collections

#
glifData_comp = """
<glyph name="a" format="1">
  <advance width="452"/>
  <unicode hex="0061"/>
  <outline>
	<contour>
	  <point x="305" y="335" type="curve"/>
	  <point x="305" y="411"/>
	  <point x="274" y="434"/>
	  <point x="198" y="434" type="curve"/>
	  <point x="207" y="510" type="line"/>
	  <point x="358" y="510"/>
	  <point x="415" y="461"/>
	  <point x="415" y="307" type="curve" smooth="yes"/>
	  <point x="415" y="0" type="line"/>
	  <point x="360" y="-8"/>
	  <point x="302" y="-11"/>
	  <point x="235" y="-11" type="curve" smooth="yes"/>
	  <point x="121" y="-11"/>
	  <point x="29" y="28"/>
	  <point x="29" y="156" type="curve" smooth="yes"/>
	  <point x="29" y="253" type="line" smooth="yes"/>
	  <point x="29" y="355"/>
	  <point x="92" y="401"/>
	  <point x="165" y="401" type="curve" smooth="yes"/>
	  <point x="215" y="401"/>
	  <point x="276" y="378"/>
	</contour>
	<contour>
	  <point x="305" y="253" type="line"/>
	  <point x="294" y="260"/>
	  <point x="242" y="288"/>
	  <point x="196" y="288" type="curve" smooth="yes"/>
	  <point x="166" y="288"/>
	  <point x="141" y="277"/>
	  <point x="141" y="239" type="curve" smooth="yes"/>
	  <point x="141" y="174" type="line" smooth="yes"/>
	  <point x="141" y="124"/>
	  <point x="153" y="91"/>
	  <point x="244" y="91" type="curve" smooth="yes"/>
	  <point x="260" y="91"/>
	  <point x="306" y="95"/>
	  <point x="305" y="95" type="curve"/>
	</contour>
  </outline>
</glyph>

"""

glifData = """
<glyph name="a" format="1">
  <advance width="452"/>
  <unicode hex="0061"/>
  <outline>
	<contour>
	  <point x="305" y="335" type="curve"/>
	  <point x="305" y="411"/>
	  <point x="274" y="434"/>
	  <point x="198" y="434" type="curve"/>
	  <point x="207" y="510" type="line"/>
	  <point x="358" y="510"/>
	  <point x="415" y="461"/>
	  <point x="415" y="307" type="curve" smooth="yes"/>
	  <point x="415" y="0" type="line"/>
	  <point x="360" y="-8"/>
	  <point x="302" y="-11"/>
	  <point x="235" y="-11" type="curve" smooth="yes"/>
	  <point x="121" y="-11"/>
	  <point x="29" y="28"/>
	  <point x="29" y="156" type="curve" smooth="yes"/>
	  <point x="29" y="253" type="line" smooth="yes"/>
	  <point x="29" y="355"/>
	  <point x="92" y="401"/>
	  <point x="165" y="401" type="curve" smooth="yes"/>
	  <point x="215" y="401"/>
	  <point x="276" y="378"/>
	</contour>
  </outline>
</glyph>

"""

glifData_a_reg = '''
<glyph name="a" format="1">
  <advance width="458"/>
  <unicode hex="0061"/>
  <outline>
	<contour>
	  <point x="422" y="0" type="line"/>
	  <point x="350" y="-7"/>
	  <point x="298" y="-11"/>
	  <point x="266" y="-11" type="curve" smooth="yes"/>
	  <point x="196" y="-11"/>
	  <point x="140" y="2"/>
	  <point x="99" y="28" type="curve" smooth="yes"/>
	  <point x="58" y="54"/>
	  <point x="37" y="101"/>
	  <point x="37" y="169" type="curve" smooth="yes"/>
	  <point x="37" y="252" type="line" smooth="yes"/>
	  <point x="37" y="318"/>
	  <point x="60" y="362"/>
	  <point x="106" y="385" type="curve" smooth="yes"/>
	  <point x="128" y="396"/>
	  <point x="156" y="402"/>
	  <point x="190" y="402" type="curve" smooth="yes"/>
	  <point x="253" y="402"/>
	  <point x="322" y="379"/>
	  <point x="366" y="346" type="curve"/>
	  <point x="366" y="383"/>
	  <point x="355" y="412"/>
	  <point x="334" y="434" type="curve" smooth="yes"/>
	  <point x="323" y="445"/>
	  <point x="305" y="454"/>
	  <point x="282" y="459" type="curve" smooth="yes"/>
	  <point x="263" y="464"/>
	  <point x="239" y="466"/>
	  <point x="211" y="466" type="curve"/>
	  <point x="214" y="509" type="line"/>
	  <point x="245" y="509"/>
	  <point x="272" y="507"/>
	  <point x="295" y="502" type="curve" smooth="yes"/>
	  <point x="320" y="497"/>
	  <point x="340" y="489"/>
	  <point x="356" y="479" type="curve" smooth="yes"/>
	  <point x="386" y="458"/>
	  <point x="405" y="434"/>
	  <point x="412" y="406" type="curve" smooth="yes"/>
	  <point x="419" y="378"/>
	  <point x="422" y="342"/>
	  <point x="422" y="298" type="curve" smooth="yes"/>
	  <point x="422" y="220" type="line"/>
	  <point x="422" y="126" type="line"/>
	</contour>
  </outline>
</glyph>

'''

glifData_a_thn = '''
<glyph name="a" format="1">
  <advance width="458"/>
  <unicode hex="0061"/>
  <outline>
	<contour>
	  <point x="422" y="0" type="line"/>
	  <point x="350" y="-7"/>
	  <point x="298" y="-11"/>
	  <point x="266" y="-11" type="curve" smooth="yes"/>
	  <point x="196" y="-11"/>
	  <point x="140" y="2"/>
	  <point x="99" y="28" type="curve" smooth="yes"/>
	  <point x="58" y="54"/>
	  <point x="37" y="101"/>
	  <point x="37" y="169" type="curve" smooth="yes"/>
	  <point x="37" y="210" type="line"/>
	  <point x="37" y="252" type="line" smooth="yes"/>
	  <point x="37" y="316"/>
	  <point x="61" y="360"/>
	  <point x="110" y="384" type="curve" smooth="yes"/>
	  <point x="135" y="396"/>
	  <point x="166" y="402"/>
	  <point x="203" y="402" type="curve" smooth="yes"/>
	  <point x="271" y="402"/>
	  <point x="350" y="381"/>
	  <point x="403" y="346" type="curve"/>
	  <point x="403" y="389"/>
	  <point x="389" y="424"/>
	  <point x="361" y="452" type="curve" smooth="yes"/>
	  <point x="339" y="472"/>
	  <point x="306" y="485"/>
	  <point x="260" y="489" type="curve" smooth="yes"/>
	  <point x="245" y="490"/>
	  <point x="229" y="490"/>
	  <point x="212" y="490" type="curve"/>
	  <point x="214" y="509" type="line"/>
	  <point x="278" y="509"/>
	  <point x="325" y="499"/>
	  <point x="356" y="479" type="curve" smooth="yes"/>
	  <point x="386" y="458"/>
	  <point x="405" y="434"/>
	  <point x="412" y="406" type="curve" smooth="yes"/>
	  <point x="419" y="378"/>
	  <point x="422" y="342"/>
	  <point x="422" y="298" type="curve" smooth="yes"/>
	  <point x="422" y="92" type="line"/>
	</contour>
  </outline>
</glyph>
'''

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

offset_y = 700
offset_x = 50

#
found_item = [330, -600]
#
class simp():

	def __init__(self, g_data):
		super(simp, self).__init__()
		self.g_data = g_data
		self.sgrad = collections.OrderedDict()
		
	def flipCoordPath(self, p, horizontal, vertical):
		#
		res = []
		#
		for x,y in p:
			#
			if horizontal:
				#
				pass
				#
			else:
				#
				if y < 0:
					#
					y = abs(y)
					#
				else:
					#
					if y == 0:
						y = y
					else:
						y = -abs(y)
					#
				#
			if vertical:
				#
				pass
				#
			else:
				#
				if x < 0:
					#
					x = abs(x)
					#
				else:
					#
					if x == 0:
						x = x
					else:
						x = -abs(x)
					#
				#
			#
			res.append([x,y])
			#
		#
		return res

	def get_glif_coord(self, f_g, _type):
		#
		#
		p_arr = []
		#
		for contour in f_g:
			#
			for point in contour.points:
				#
				if _type == 'corner':
						
					if point.type != 'offcurve':
						#
						p_arr.append([point.x+offset_x, point.y-offset_y])
						#
				#
				else:
					#
					p_arr.append([point.x+offset_x, point.y-offset_y])
					#

			#
		#
		return p_arr
		#
	#
	def make_let(self):
		#
		_let = "a"
		f = NewFont()
		g = f.newGlyph(_let)
		pen = g.getPointPen()
		glyph_result = readGlyphFromString(self.g_data, glyphObject=g, pointPen=pen)
		#
		f_g = f[_let]
		#
		return f_g
		#
	#
	def bez_to_list(self, coords=False):
		#
		if coords:
			#
			do_coords = coords
			#
		else:
			#
			do_coords = self.coordinates
			#
		myPath = []
		for x in do_coords:
			#
			for y in x:
				#
				y_l = y.tolist()
				#
				if y_l not in myPath:
					#
					myPath.append(y_l)
					#
				#
			#

		list_of_tuples = list(tuple(x) for x in myPath)
		#
		return list_of_tuples
		#
	#
	def simplification_gradient(self):
		#
		'''
		Create an SGrad

		SGrad is a list of coodinate evaluation on their persistance across the simplification
		'''
		#
		l_tp = self.bez_to_list()
		#
		for c in l_tp:
			#
			#
			coord_name = '-'.join(str(v) for v in c)
			###print(c,coord_name)
			#
			if coord_name in self.sgrad.keys():
				#
				self.sgrad[coord_name] = self.sgrad[coord_name] + 1
				#
			else:
				#
				self.sgrad[coord_name] = 1
				#
			#
		#
	
	def draw_plot(self, f_g):
		#
		l_tp = self.bez_to_list()
		#
		g_coord_flip = self.flipCoordPath(l_tp,False,True)
		#
		plt.clf()
		#
		ax = plt.gca()
		#
		self.svg_path_orig = writeGlyphPath(f_g, True)
		parse_mpl = mpl_parse_path(self.svg_path_orig)
		patch = mpatches.PathPatch(parse_mpl, facecolor="none", edgecolor="blue", fill=False, lw=0.4)
		t = mpl.transforms.Affine2D().translate(offset_x,-offset_y) + ax.transData
		#
		patch.set_transform(t)
		ax.add_patch(patch)
		#
		simp_xPts,simp_yPts=zip(*g_coord_flip)
		ax.plot(simp_xPts,simp_yPts,color='blue',lw=0.2)
		#
		plt.show()
		#
	#
	#
#
tc_reg = [[206.0, 10.0], [198.0, 86.0], [251.0, 92.0], [280.0, 107.0], [291.0, 120.0], [300.0, 141.0], [304.0, 182.0], [283.0, 159.0], [258.0, 142.0], [219.0, 126.0], [191.0, 120.0], [147.0, 119.0], [129.0, 122.0], [102.0, 131.0], [74.0, 149.0], [55.0, 170.0], [42.0, 193.0], [34.0, 216.0], [29.0, 245.0], [29.0, 386.0], [33.0, 412.0], [42.0, 440.0], [60.0, 470.0], [85.0, 494.0], [117.0, 512.0], [155.0, 524.0], [205.0, 531.0], [295.0, 531.0], [415.0, 521.0], [415.0, 180.0], [410.0, 138.0], [399.0, 99.0], [378.0, 63.0], [354.0, 41.0], [330.0, 28.0], [273.0, 13.0], [206.0, 10.0]]
tc_thn = [[214.0, 10.0], [211.0, 53.0], [253.0, 55.0], [290.0, 62.0], [314.0, 71.0], [334.0, 85.0], [348.0, 103.0], [358.0, 124.0], [364.0, 147.0], [365.0, 171.0], [329.0, 149.0], [290.0, 133.0], [258.0, 124.0], [213.0, 117.0], [167.0, 117.0], [140.0, 121.0], [114.0, 129.0], [82.0, 148.0], [66.0, 164.0], [53.0, 184.0], [43.0, 210.0], [38.0, 235.0], [37.0, 375.0], [41.0, 403.0], [50.0, 433.0], [69.0, 466.0], [91.0, 487.0], [127.0, 507.0], [170.0, 521.0], [234.0, 530.0], [299.0, 530.0], [422.0, 520.0], [422.0, 181.0], [417.0, 132.0], [407.0, 95.0], [395.0, 75.0], [378.0, 56.0], [340.0, 30.0], [305.0, 18.0], [279.0, 13.0], [214.0, 10.0]]


class MainObject:

	def __init__(self, _simp):
		self.simp = _simp

	def run(self):
		root = Tk()

		frame = Frame(root, relief=SUNKEN, borderwidth=1)
		frame.pack(side=LEFT, fill=Y)
		label = Label(frame, text='Max Error')
		label.pack()
		self.spinbox = Spinbox(frame, width=8, from_=0.0, to=1000000.0, command=self.onSpinBoxValueChange)
		self.spinbox.insert(0, 0)
		self.spinbox.pack()
		#
		self.points = []
		#
		self.draggingPoint = None

		self.redraw()

		root.mainloop()

	def onSpinBoxValueChange(self):
		self.redraw()

	def redraw(self):
		#
		f_g = self.simp.make_let()
		#
		g_coord_corner = self.simp.get_glif_coord(f_g, 'corner')
		g_coord = self.simp.get_glif_coord(f_g, 'original')
		g_coord_reg_flip = self.simp.flipCoordPath(g_coord,False,True)
		g_coord_corner_flip = self.simp.flipCoordPath(g_coord_corner,False,True)
		#
		points = np.asarray(g_coord_corner_flip)
		#
		simplified_points = fitCurve(points, float(self.spinbox.get())**2)
		#
		print(simplified_points)
		print('-----<')
		#
		self.simp.coordinates = simplified_points
		self.simp.shape = g_coord_reg_flip
		#
		self.simp.simplification_gradient()
		self.simp.draw_plot(f_g)
		#

if __name__ == '__main__':


	a_reg_sgrad = collections.OrderedDict()
	a_thn_sgrad = collections.OrderedDict()


	a_reg_sgrad = [('472-700', 9),
			 ('316.0-711.0', 9),
			 ('149.0-672.0', 9),
			 ('87.0-531.0', 9),
			 ('87.0-448.0', 9),
			 ('156.0-315.0', 9),
			 ('240.0-298.0', 9),
			 ('416.0-354.0', 9),
			 ('384.0-266.0', 9),
			 ('332.0-241.0', 6),
			 ('261.0-234.0', 9),
			 ('264.0-191.0', 9),
			 ('345.0-198.0', 6),
			 ('406.0-221.0', 9),
			 ('462.0-294.0', 9),
			 ('472.0-402.0', 5),
			 ('472.0-480.0', 9),
			 ('472.0-574.0', 9)]

	a_thn_sgrad = [('472-700', 10),
			 ('316.0-711.0', 10),
			 ('149.0-672.0', 10),
			 ('87.0-531.0', 10),
			 ('87.0-490.0', 1),
			 ('87.0-448.0', 10),
			 ('160.0-316.0', 10),
			 ('253.0-298.0', 10),
			 ('453.0-354.0', 10),
			 ('411.0-248.0', 10),
			 ('310.0-211.0', 7),
			 ('262.0-210.0', 9),
			 ('264.0-191.0', 10),
			 ('406.0-221.0', 10),
			 ('462.0-294.0', 10),
			 ('472.0-402.0', 10),
			 ('472.0-608.0', 10)]
	#
	_p = simp(glifData_a_reg)
	#
	o = MainObject(_p)
	o.run()

	
