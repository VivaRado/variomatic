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
import matplotlib.patches as mpatches
#
debug = False
#
dir_path = os.path.dirname(os.path.realpath(__file__))
#
sys.path.insert(0, os.path.join(dir_path,'helpers'))
#
from context import sample
from pnt import *
from geom import *
import draw
#
from shapely_simp import *
from fitCurves_b import *
from colors import tcolor
from colors import color
#
from contour_holder import ContourHolder
from graph_constructor import GraphConstructor
from iter_draw import IterDraw
#
font_instance_a = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
font_instance_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
font_instance_c = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
#
run_specific = "x"
instance_list = [font_instance_a, font_instance_b]
simplification = list(range(0,50))#[0,1,2,3,4,5,6,7,8,9,10]
#
inst_num = 0
plt_num = 0
instance_dict = {}
total_list = {}
CH = {}
GC = {}
#
def get_point_inx_line(numpoints, num, loc):
	#
	#
	if loc == "p":
		#
		if num == 1:
			#
			return numpoints - 1
			#
		#
		else:
			#
			return num - 1
			#
	elif loc == "a":
		#
		if num - 1 == numpoints:
			#
			#
			return 1
			#
		#
		else:
			#
			#
			if num != numpoints - 1:
				#
				return num + 1
				#
			else:
				#
				return 1
				#
			#
		#
	#
#
def make_ct_perp(coord_ct, cen_c):
	#
	perps = []
	perps_virt = []
	#
	for coords in coord_ct:
		#
		x = coords[0]
		y = coords[1]
		#	
		_perp = getPerpCoord(cen_c[0], cen_c[1], x, y, 10000)
		_perp_b = getPerpCoord(_perp[0],_perp[1],x,y, 10000)
		#
		perps_virt.append([cen_c, [x,y]])
		perps.append([[_perp[0],_perp[1]],[_perp[2],_perp[3]],[_perp_b[0],_perp_b[1]],[_perp_b[2],_perp_b[3]]])
		#
	#
	return [perps,perps_virt]
	#
#
class CenterTransfer(object):
	"""
	A 2D bounding box
	"""
	def __init__(self, __point, inst_items, points_len):

		self.__point = __point
		self.inst_items = inst_items
		self.points_len = points_len
		self.matched_source = []
		#
	#
	def set_confines(self):
		#
		t_fnl_d = 300#math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) + 50 # target_first_and_last_distance
		p_d = 0
		#
		for k,v in self.points_len.items():
			#
			if k!=(0,0):
				#
				t_a_coord = self.points_len.get(self.inst_items[p_d])["coord"]
				t_a_order = self.points_len.get(self.inst_items[p_d])["order"]
				#
				t_circle = [t_a_coord,t_fnl_d]
				#
				contains = in_circle(self.__point,t_circle)
				#
				if contains:
					#
					t_a_dist = math.hypot(t_a_coord[0]-self.__point[0], t_a_coord[1]-self.__point[1])
					#
					self.matched_source.append([t_a_dist,t_a_coord,p_d, t_a_order])
					#
				p_d = p_d + 1
			#
		#
		self.ms_pn_s = sorted(self.matched_source, key = lambda x: x[3])
		#
		self.search_center = next(c for c in self.ms_pn_s if c[1] == self.__point)
		#
		return self.ms_pn_s
		#
	def get_confine(self, toget):
		#
		if toget == "c":
			#
			return self.search_center
			#
		elif toget == "p":
			#
			return next(c for c in self.ms_pn_s if c[3] == get_point_inx_line(len(self.points_len), self.search_center[3], "p"))
			#
		elif toget == "a":
			#
			return next(c for c in self.ms_pn_s if c[3] == get_point_inx_line(len(self.points_len), self.search_center[3], "a"))
			#

	def get_confines(self):
		#
		return [self.get_confine("p"), self.get_confine("c"), self.get_confine("a")]
		#

#
#
# Pre-Processor
#
for font_inst in instance_list:
	#
	total_list[inst_num] = {}
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
				glyph_name = t_pl.split(".glif")[0]
				#
				if run_specific == glyph_name:
					#
					file_exists = os.path.isfile(os.path.join(font_inst, t_pl))
					#
					if file_exists:
						#
						CH = ContourHolder(os.path.join(font_inst, t_pl), debug)
						#
						cont_counter = CH.len
						#
						for cnt in range(CH.len):
							#
							glyph = CH.get(cnt,"glyph")
							#
							total_list[inst_num][glyph] = {}
							#
							g_orig_coord = CH.get_glif_coord(glyph,'get_type')
							#
							contours = total_list[inst_num][glyph]
							#
							GC = GraphConstructor(CH,instance_list,cnt, inst_num, simplification, plt_num, debug)
							#
							contours[cnt] = GC.initiate_instance(inst_num, cnt, CH)
							#
							t_contour = contours[cnt]
							#
							points = np.asarray(contours[cnt]["coords"]["strt"])
							#
							contours[cnt]["simplified"] = OrderedDict()
							contours[cnt]["graphs"] = OrderedDict()
							contours[cnt]["graphs_data"] = OrderedDict()
							#
							inst_inx = contours[cnt]["inst"]
							cont_inx = contours[cnt]["cont"]
							#
							t_color = color[inst_inx]
							#
							for simp in simplification:
								#
								simplified_points = simplif(points, simp)
								#
								contours[cnt]["simplified"][simp] = simplified_points
								done_topo = GC.make_instance_topo_b(contours[cnt], t_color,simp)
								contours[cnt]["graphs"][simp] = done_topo[0]
								contours[cnt]["graphs_data"][simp] = done_topo[1]
								#
							#
							contours[cnt]["confines"] = []
							contours[cnt]["confines_simp"] = OrderedDict()
							contours[cnt]["perps"] = []
							contours[cnt]["perps_simp"] = OrderedDict()
							contours[cnt]["perps_virt"] = []
							contours[cnt]["perps_virt_simp"] = OrderedDict()
							#
							for simp in simplification:
								points_len = contours[cnt]["graphs"][simp]
								#
								inst_items = []
								#
								re_points_len = OrderedDict()
								#
								for k,v in points_len.items():
									#
									#
									inst_items.append(k)
									#
								#
								temp_conf = []
								temp_perp = []
								temp_perpvirt = []
								#
								for t_point_itm in list(points_len.values()):
									#
									if t_point_itm['node'] > 0:
										#
										try:
											CT = CenterTransfer(t_point_itm["coord"],inst_items,points_len)
											CT.set_confines()
											cfn = CT.get_confines()
											#
											contours[cnt]["confines"].append(cfn)
											temp_conf.append(cfn)
											#
											coord_ct = [item[1] for item in cfn] # to_ct
											#
											cen_a = list(points_len.items())[-1]
											cen_c = cen_a[1]["coord"]
											#
											perps_plot = make_ct_perp(coord_ct, cen_c)
											#
											contours[cnt]["perps"].append(perps_plot[0])
											temp_perp.append(perps_plot[0])
											contours[cnt]["perps_virt"].append(perps_plot[1])
											temp_perpvirt.append(perps_plot[1])
										except Exception as e:
											pass
											
										#
										#
								#
								print(simp, len(temp_conf))
								#
								contours[cnt]["confines_simp"][simp] = temp_conf#contours[cnt]["confines"]
								contours[cnt]["perps_simp"][simp] = temp_perp#contours[cnt]["perps"]
								contours[cnt]["perps_virt_simp"][simp] = temp_perpvirt#contours[cnt]["perps_virt"]
								#
							#
							#
							plt_num = plt_num + 1
							#
						#
					#
				#
			#
		#
	#
	inst_num = inst_num + 1
	#
#

#pprint.pprint(total_list)
#

#
# Solver
#
'''

'''
#
# Post-Processor
#
initiate_drawing = IterDraw(total_list, GC, plt)
#
initiate_drawing.run()
#
plt.show()
#
'''
Pre-Processor
	ContourHolder
		ContourNormalizer
	GraphConstructor
Solver
	GraphEvaluator
	InstanceMatcher
		PointNormalizer
Post-Processor
	IterDraw
'''
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
'''
total_list = {
	instance_int:{
		"glyph_name":{
			contours:{
				"simplified":{
					"simplification_integer":{
						[x,y],[x,y]...
					},
					"simplification_integer":{},
					...
				},
				"glyph":{}
			}
		}
	}
}
'''