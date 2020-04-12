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
import matplotlib.lines as lines
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
simplification = list(range(0,3))#[0,1,2,3,4,5,6,7,8,9,10]
#
inst_num = 0
plt_num = 0
instance_dict = {}
total_list = {}
CH = {}
GC = {}
#
def do_ct_sort_a(_f, __point,to_ct,perps_plot, lt_p,ax,bax, _plt, travel_sort = False):
	#
	#
	_b_instance = _f.m_instances[1]
	#
	#__cent_b = list(_b_instance["graph_data"]["sort_by_length"].values())[-1]["coord"]
	#
	per_ct = []
	#
	c = 0
	#
	for cts in to_ct:
		#
		sta_a = perps_plot[c][0]
		end_a = perps_plot[c][1]
		sta_b = perps_plot[c][2]
		end_b = perps_plot[c][3]
		#
		all_match = []
		all_match_len = []
		#
		#
		for lt in lt_p:
			#
			lt_x = lt[1][0]
			lt_y = lt[1][1]
			#
			pnt_dist_a = pnt2line([lt_x,lt_y], sta_a, end_a) # point, sta_a, end
			pnt_dist_b = pnt2line([lt_x,lt_y], sta_b, end_b) # point, sta_a, end
			#
			if _plt:
			#
				# lines met on line from center to current point
				_p_g = getPerpCoord(cts[0], cts[1],pnt_dist_b[1][0], pnt_dist_b[1][1], 5)
				prp1 = mpatches.ConnectionPatch([_p_g[0],_p_g[1]],[_p_g[2],_p_g[3]],"data", lw=0.5, color="g")
				ax.add_patch(prp1)
			# distance of those positions from current point
			#t_b_dist = int(math.hypot(cts[0]-pnt_dist_b[1][0], cts[1]-pnt_dist_b[1][1]))
			#
			#
			# t_a_dist = math.hypot(cts[0]-lt_x, cts[1]-lt_y)
			# t_b_c_dist = math.hypot(__cent_b[0]-lt_x, __cent_b[1]-lt_y)
			# t_a_c_dist = math.hypot(__cent_b[0]-cts[0], __cent_b[1]-cts[1])
			# #
			# pnt_dist_a = list(pnt_dist_a)
			# #
			# pnt_dist_a.insert(1, t_a_dist)
			# #
			# pnt_dist_a = tuple(pnt_dist_a)
			# #
			# _area = area([[cts[0],cts[1]],pnt_dist_a[2],[lt_x,lt_y]])
			# #
			# center_m_point = distance([__cent_b[0], __cent_b[1]],[lt_x,lt_y])
			# center_s_point = distance([__cent_b[0], __cent_b[1]],__point)
			# sm_point = distance([lt_x,lt_y],__point)
			# #
			# m_angle = get_angle_b([__cent_b[0], __cent_b[1]],[lt_x,lt_y])
			# s_angle = get_angle_b([__cent_b[0], __cent_b[1]],__point)
			# #
			
			#
			# new_match = [
			# 	(lt[2],lt[3]), 
			# 	pnt_dist_a, #
			# 	_area,
			# 	_area,
			# 	[cts[0],cts[1]], 
			# 	[lt_x,lt_y], #
			# 	t_b_dist,
			# 	abs(abs(t_b_c_dist) - abs(t_a_c_dist)),
			# 	abs(center_m_point - center_s_point),
			# 	abs(m_angle-s_angle),
			# 	sm_point,
			# 	_area+pnt_dist_a[0]+abs(center_m_point - center_s_point)+abs(m_angle-s_angle)+sm_point
			# 	]
			# #
			# #
			# if new_match not in all_match:
			# 	#
			# 	all_match.append(new_match)
			# 	#
			# #
			# if _plt:
			# 	#
			# 	if show_center_transfer_b == True:
						
			# 		prp1 = mpatches.ConnectionPatch([lt_x, lt_y],[pnt_dist_a[2][0],pnt_dist_a[2][1]],"data", lw=0.2, color="r")
			# 		#
			# 		ax.add_patch(prp1)	
			# 		#
			# 		prp1 = mpatches.ConnectionPatch([lt_x,lt_y],__point,"data", lw=1, color="k")
			# 		#
			# 		ax.add_patch(prp1)	
			#
		#
		# sorted_all_match = sorted(all_match, key=lambda x: x[3]+x[1][0]+x[8]+x[9]+x[10])[:3]
		# #
		# #
		# for x in sorted_all_match:
		# 	#
		# 	#
		# 	l1 = x[4]
		# 	l2 = x[1][2]
		# 	l3 = x[5]
		# 	#
		# 	if _plt:
		# 		#
		# 		poly = plt.Polygon([l1,l2,l3], color='g',alpha=0.1)
		# 		ax.add_patch(poly)
		# 		#
		# 		dst1 = mpatches.ConnectionPatch([cts[0], cts[1]],[x[1][0],x[1][1]],"data", lw=0.4, color="g")
		# 		#
		# 		ax.add_patch(dst1)
		# 	#
		#
		#per_ct.append(sorted_all_match)
		#
		c = c + 1
		#
	
	#
	return per_ct
	#
		
	#

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
	perpendic = []
	recumbent = []
	#
	for coords in coord_ct:
		#
		x = coords[0]
		y = coords[1]
		#	
		_perp_virtual= getPerpCoord(cen_c[0],  cen_c[1], x, y, 100) # perpendicular center to coordinate
		_perp_actual = getPerpCoord(cen_c[0],  cen_c[1], x, y, 10000) # perpendicular to center to coordinate
		#
		recumbent.append([cen_c, [x,y]]) # center to coordinate
		perpendic.append([
			[_perp_virtual[0],_perp_virtual[1]],[_perp_virtual[2],_perp_virtual[3]],
			[_perp_actual[0], _perp_actual[1]], [_perp_actual[2], _perp_actual[3]]
		])
		#
	#
	return [perpendic,recumbent]
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
							contours[cnt]["perp"] = []
							contours[cnt]["perp_simp"] = OrderedDict()
							contours[cnt]["recu"] = []
							contours[cnt]["recu_simp"] = OrderedDict()
							#
							for simp in simplification:
								#
								points_lenw = contours[cnt]["graphs"][simp]
								#
								inst_items = []
								#
								re_points_len = OrderedDict()
								#
								for k,v in points_lenw.items():
									#
									inst_items.append(k)
									#
								#
								temp_conf = []
								temp_perp = []
								temp_recu = []
								#
								for t_point_itm in list(points_lenw.values()):
									#
									if t_point_itm['node'] > 0:
										#
										print(t_point_itm)
										#
										try:
											#
											CT = CenterTransfer(t_point_itm["coord"],inst_items,points_lenw)
											CT.set_confines()
											cfn = CT.get_confines()
											#
											contours[cnt]["confines"].append(cfn)
											temp_conf.append(cfn)
											#
											coord_ct = [item[1] for item in cfn] # to_ct
											#
											cen_a = list(points_lenw.items())[-1]
											cen_c = cen_a[1]["coord"]
											#
											_perp,_recu = make_ct_perp(coord_ct, cen_c)
											#
											contours[cnt]["perp"].append(_perp)
											temp_perp.append(_perp)
											contours[cnt]["recu"].append(_recu)
											temp_recu.append(_recu)
											#
										except Exception as e:
											#
											pass
											#
										#
								#
								print(simp, len(temp_conf))
								#
								contours[cnt]["confines_simp"][simp] = temp_conf#contours[cnt]["confines"]
								contours[cnt]["perp_simp"][simp] = temp_perp#contours[cnt]["perps"]
								contours[cnt]["recu_simp"][simp] = temp_recu#contours[cnt]["perps_virt"]
								#
								'''
								get points around confines for each instance for each contour for each simplification level
								'''
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
def get_instance_permutation():
	#
	ir = list(range(0,len(instance_list))) # instance range
	#
	pipl = [] # permuted interpolation list
	#
	for i in range(len(ir)):
		for j in range(i,len(ir)):
			if ir[j] == ir[i]:
				#print ('Skipping')
				pass
			else:
				pipl.append([ir[i],ir[j]])
	#
	return pipl
	#
#
def GraphEvaluator(instances, inst_intpl_lst):
	#
	# instance permutation
	#
	for intpair in inst_intpl_lst:
		#
		in_a = intpair[0]
		in_b = intpair[1]
		#
	#
	# dummy access confine data for pnt2line against perpendicular of center recumbent
	#
	for instance in instances:
		#
		for letter in instances[instance]:
			#
			for contour in instances[instance][letter]:
				#
				t_contour = instances[instance][letter][contour] # this
				#
				inst_inx = t_contour["inst"]
				cont_inx = t_contour["cont"]
				#
				t_plot = plt.figure(t_contour["plot_num"])
				t_gca = t_plot.gca()
				t_color = color[inst_inx]
				#
				for x,y in t_contour["simplified"].items():
					#
					print("-------------------")
					print(x,y)
					print(inst_inx, cont_inx)
					#
					simp_level = simplification[x]
					#
					if x == 0: # example one level 0 of simplification / removing will run whole simplification list
						#
						for z in y: # points
							#
							t_c = flipCoordPath([z],False,True)[0]
							graph_point_from_coord = [d for d in list(t_contour["graphs"][simp_level].values()) if d['coord'] == t_c][0]
							#
							print ( graph_point_from_coord ) 
							#
							point_inx = y.index(z)+1
							#
							print("_______")
							#print(t_contour["confines_simp"][simp_level][1])
							confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == t_c][0]
							inx_conf = t_contour["confines_simp"][simp_level].index(confine_from_coord)
							#
							perp_from_inx = t_contour["perp_simp"][simp_level][inx_conf]
							ct_c = perp_from_inx[1]
							#
							list_x = [ct_c[0][0],ct_c[1][0]]
							list_y = [ct_c[0][1],ct_c[1][1]]
							#
							line = lines.Line2D(list_x,list_y, lw=5., color='r', alpha=0.4)
							#
							t_gca.add_line(line)
							#
							print(z, perp_from_inx, confine_from_coord, graph_point_from_coord)
							#
						#
					#
#
intpl_list = get_instance_permutation()
#
print("INTERPOLATION LIST")
print(intpl_list)
#
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
'''
GraphEvaluator is part of the solver it appears here because of drawing priority, for demonstration only.
As it contains the identification of the CT lines for each instance to run against the other instances and find 
points that are triangulated according to solver criteria.
'''
GraphEvaluator(total_list, intpl_list)
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
				contour_int:{
					"simplified":{
						"simplification_integer":{
							[x,y],[x,y]...
						},
						...
					},
					"graphs":{
						"simplification_integer":{
							NXgraph...
						},
						...
					},
					"graphs_data":{
						"simplification_integer":{
							NXgraph...
						},
						...
					},					
					"confines_simp":{
						"simplification_integer":{
							[pre,cnt,ant]...
						},
						...
					},
					"perp_simp":{
						"simplification_integer":{
							[pre,cnt,ant]...
						},
						...
					},
					"recu_simp":{
						"simplification_integer":{
							[pre,cnt,ant]...
						},
						...
					}
				},
				...
			},
			...
		},
		...
	},
	...
}
'''