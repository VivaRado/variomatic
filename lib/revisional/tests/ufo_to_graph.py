import os
import sys
import time
import plistlib
from copy import deepcopy
import xml.etree.ElementTree as ET
import collections
import pprint
import numpy as np
from collections import OrderedDict
from matplotlib import pyplot as plt
#

#

#
from context import sample
from pnt import *
from geom import *
import draw
from fitCurves_b import *
#
from contour_holder import ContourHolder
from graph_constructor import GraphConstructor
#
debug = False
#
dir_path = os.path.dirname(os.path.realpath(__file__))
#
sys.path.insert(0, os.path.join(dir_path,'helpers'))
#
color = ["red","blue","green","cyan", "magenta", "orange", "yellow"]
#

#



#
font_instance_a = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
font_instance_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
#
run_specific = "a"
instance_list = [font_instance_a, font_instance_b]
simplification = [0]
#
inst_counter = 0
instance_dict = {}
#
'''
ContourHolder
	ContourNormalizer
GraphConstructor
GraphEvaluator
InstanceMatcher
	PointNormalizer
'''
#
for font_inst in instance_list:
	#
	with open(os.path.join(font_inst,'contents.plist'), 'rb') as f:
		#
		pl = plistlib.load(f)
		#
		for pl_itm in pl.items():
			#
			t_pl = pl_itm[1]
			#
			if run_specific != "":
				#
				if run_specific == t_pl.split(".glif")[0]:
					#
					file_exists = os.path.isfile(os.path.join(font_inst, t_pl))
					#
					if file_exists:
						#
						CH = ContourHolder(os.path.join(font_inst, t_pl), debug)
						#
						glyph = CH.get(inst_counter,"glyph")
						#
						# corner, asym-smooth-point, sym-smooth-point
						'''
						Vertice Types:

							Smooth Vertice (or Curve Vertice) 
								represented by a green, round Vertice symbol 
								indicates a smooth connection between two curve segments.
							Tangent Vertice 
								represented by a violet, triangular Vertice symbol 
								indicates a smooth connection between a curve segment and a straight segment.
							Sharp Vertice (or Corner Vertice) 
								represented by a red, square Vertice symbol 
								indicates a sharp connection between any segment types.
							
						Connection Types:
							Sharp connection
								At a sharp connection, the two connected segments (curve and curve or straight segment and curve) are absolutely free in their angle relative to each other at the connecting node.

							Smooth connection
								At a smooth connection, the direction of the straight segment and the control vector of a curve or the control vectors of two sequential curves are kept collinear (lie on the same straight line), i.e. the angle between the two segments at the node is fixed at 180 degrees.
						'''
						#
						g_orig_coord = CH.get_glif_coord(glyph,'get_type')
						#
						print(g_orig_coord)
						#
						
						contours = {}
						#
						for cnt in range(CH.len):
							#
							GC = GraphConstructor(CH,instance_list,cnt, inst_counter, simplification, debug)
							#
							contours[cnt] = GC.initiate_instance(inst_counter, cnt, CH)
							#
							points = np.asarray(contours[cnt]["coords"]["strt"])
							#
							#contours[cnt]["beziers"] = #OrderedDict()
							#contours[cnt]["graph"] = #OrderedDict()
							#
							#print(contours[cnt]["beziers"])
							# store simplification presense matrix
							#
							for simp in simplification:
								#
								contours[cnt]["beziers"] = fitCurve(points, float(simp)**2)
								#
								contours[cnt]["graph"] = GC.make_instance_topo(contours[cnt], color[inst_counter], simp)
								#
						#
						instance_dict[inst_counter] = contours
						#
						for k,v in contours.items():
							#
							draw.draw_instance_graphs_c(v)
							#
						#
					#
				#
			#
		#
	#
	inst_counter = inst_counter + 1
	#
			
plt.show()