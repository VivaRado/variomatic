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
max_radius = 200
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
		'''
		perps.append([
				[_perp[0],_perp[1]],
				[_perp[2],_perp[3]],
				[_perp_b[0],_perp_b[1]],
				[_perp_b[2],_perp_b[3]]
			])
		'''
		# [[169, -56], [4, 56], [8365, -5609], [-8191, 5609]]

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
										#print(t_point_itm)
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
								#print(simp, len(temp_conf))
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
def tc_get_pca(t_contour,simp_level,conf_inx,pos):
	#
	if pos == "p":
		#
		get_pos = 0
		#
	elif pos == "c":
		#
		get_pos = 1
		#
	elif pos == "a":
		#
		get_pos = 2
		#
	#
	return t_contour["perp_simp"][simp_level][conf_inx][get_pos]
	#
#
def tc_get_point_b_coord(t_contour, simp_level, coordinate):
	#
	return [d for d in list(t_contour["graphs"][simp_level].values()) if d['coord'] == coordinate][0]
	#
#
def tc_get_simp_conf_b_coord(t_contour, simp_level, coordinate):
	#
	confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate][0]
	confine_index = t_contour["confines_simp"][simp_level].index(confine_from_coord)
	#
	return confine_index, confine_from_coord
	#
#
def get_perp(ct, rep):
	#
	if rep == "virt":
		#
		list_x = [ct[0][0],ct[1][0]]
		list_y = [ct[0][1],ct[1][1]]
		#
	elif rep == "real":
		#
		list_x = [ct[2][0],ct[3][0]]
		list_y = [ct[2][1],ct[3][1]]
		#
	#
	#
	return list_x, list_y
	#
#
def get_tc(instances, inx):
	#
	for instance in instances:
		#
		for letter in instances[instance]:
			#
			for contour in instances[instance][letter]:
				#
				t_contour = instances[instance][letter][contour]
				#
				inst_inx = t_contour["inst"]
				#
				if inx == inst_inx:
					#
					return t_contour # this
					#
				#
				else:
					pass
				#
	#
#
def draw_cts(t_contour):
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
		simp_level = simplification[x]
		#
		if x == 0: # example one level 0 of simplification / removing will run whole simplification list
			#
			for z in y: # points
				#
				t_coord = flipCoordPath([z],False,True)[0]
				#
				#graph_point_from_coord = tc_get_point_b_coord(t_contour,simp_level,t_coord)
				#
				conf_inx, conf_dat = tc_get_simp_conf_b_coord(t_contour,simp_level,t_coord)
				#
				pca_crd_c = tc_get_pca(t_contour,simp_level,conf_inx,"c")
				#
				list_x, list_y = get_perp(pca_crd_c, "virt")
				#
				line = lines.Line2D(list_x,list_y, lw=1., color=t_color, alpha=0.4)
				#
				t_gca.add_line(line)
				#
				#__point = t_coord#list(_a_instance["graph_data"]["sort_by_length"].values())[iter_point]["coord"]
				#points_arr = get_points_around(__point,points_a,points_b,l_s, a_items, b_items, ax, bax,_plt, _color)
				#
				print(pca_crd_c)
#
#
def get_points_around(__point, points_a,points_b, l_s, ax, bax, _plt=False, _color=False):
	#
	#
	matched_target = []
	
	#
	#center_a = points_a.get(a_items[-1])["coord"]
	#
	for z in l_s:
		#
		p_c = 0
		t_psca_coord = z[1][1]#points_b.get(a_items[p_c])["coord"]
		#
		
		if _plt:
			#
			circl = plt.Circle(t_psca_coord, max_radius, color=_color[0], fill=False, alpha=0.5, lw=0.5)
			
			circl.set_radius(max_radius)
			circl.set_linestyle((0, (2,4)))
			
			ax.add_patch(circl)
		#
		
		found_p = False
		#
		for v in points_b:
			#
			#
			#if k!=(0,0):
			#
			contains = False
			#
			c_rad = 0
			for x in range(max_radius):
				#
				t_circle = [t_psca_coord,c_rad]
				#
				t_b_coord = flipCoordPath([v],False,True)[0]#["coord"]
				t_b_order = points_b.index(v)#.get(b_items[p_c])["order"]
				#
				contains = in_circle(t_b_coord,t_circle)
				#
				#print("- CHECK IN CIRCLE - contains")
				#print(t_b_coord, contains)
				#
				if contains:
					#
					#
					found_p = True
					#
					#Path = mpath.Path
					#
					t_b_dist = math.hypot(t_b_coord[0]-__point[0], t_b_coord[1]-__point[1])
					#
					new_match = [t_b_dist,t_b_coord,p_c,t_b_order]
					#
					if new_match not in matched_target:
						#
						matched_target.append(new_match)
						#
						if _plt:
							#
							pp1 = mpatches.ConnectionPatch(z[1][1],t_b_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
							pp1.set_linestyle((0, (2,4)))
							ax.add_patch(pp1)
							draw.draw_circle_on_coord(t_b_coord, ax, 2, "g")
							#
						#
					break
				#
				c_rad = c_rad + 1
				#
			#
			p_c = p_c + 1
			#
			#
		#
	#
	sorted_cont_target = sorted(matched_target, key = lambda x: x[3])#sorted(matched_target)
	#
	return sorted_cont_target
	#
#
def rotate_points(sorted_cont_target, len_points, is_sequence=False):
	#
	if is_sequence:
		#
		c = [j for i in is_sequence for j in i]
		#
	else:
		#
		c = [el[3] for el in sorted_cont_target]
		orders_true = collections.deque(sorted_cont_target)
		#
	#
	orders = collections.deque(c)
	#
	l_inx = len_points#len(points)
	#
	index_of_last = False
	#
	#
	if l_inx in c:
		#
		index_of_last = c.index(l_inx)
		#
	#
	if index_of_last and 1 in c :
		#
		if is_sequence:
			#
			seq_lists = is_sequence
			#
		else:
			#
			seq_lists = get_seq(c)
			#
		#
		for x in seq_lists:
			#
			if l_inx in x:
				#
				rotation = len(x)
				#
				orders.rotate(rotation)
				#
				if is_sequence:
					#
					pass
					#
				else:
					#
					orders_true.rotate(rotation)
					#
			#
		#
	#
	if is_sequence:
		#
		return list(orders)
		#
	else:
		#
		return list(orders_true)
		#
	#
#

def TreeEvaluator(instances, inst_intpl_lst):
	#
	# instance permutation
	#
	#print(inst_intpl_lst)
	#
	for intpair in inst_intpl_lst:
		#
		in_a = intpair[0]
		in_b = intpair[1]
		#
		tc_inst_a = get_tc(instances, in_a)
		tc_inst_b = get_tc(instances, in_b)
		#
		draw_cts(tc_inst_a)
		draw_cts(tc_inst_b)
		#
		points_a = tc_inst_a["simplified"][0]
		points_b = tc_inst_b["simplified"][0]
		#
		t_plot_a = plt.figure(tc_inst_a["plot_num"])
		ax = t_plot_a.gca()
		#
		t_plot_b = plt.figure(tc_inst_b["plot_num"])
		bax = t_plot_b.gca()
		#
		inst_inx = tc_inst_a["inst"]
		cont_inx = tc_inst_a["cont"]
		#
		t_plot = plt.figure(tc_inst_a["plot_num"])
		t_gca = t_plot.gca()
		t_color = color[inst_inx]
		#
		__point = list(tc_inst_a["graphs"][0].values())[0]["coord"] # running for point zero
		#
		conf_inx, conf_dat = tc_get_simp_conf_b_coord(tc_inst_a,0,list(__point))
		#
		lt_p = tc_inst_a["perp_simp"][0][conf_inx]
		#
		l_s = [conf_dat]
		#
		#pca_crd_c = tc_get_pca(t_contour,0,conf_inx,"c")
		#
		sta_a = lt_p[1][0]
		end_a = lt_p[1][1]
		sta_b = lt_p[1][2]
		end_b = lt_p[1][3]
		#
		all_match = []
		all_match_len = []
		#
		points_arr = get_points_around(__point,points_a,points_b,l_s, ax, bax,plt, t_color)
		#
		l_t = points_arr
		#
		l_t = rotate_points(l_t, len(points_b))
		#
		__cent_b = list(tc_inst_b["graphs"][simp].values())[-1]["coord"]
		#
		#print(__cent_b)
		#
		for cts in tc_inst_a["confines_simp"][0][conf_inx]:
			#
			for lt in l_t:
				#
				lt_x = lt[1][0]
				lt_y = lt[1][1]
				#
				pnt_dist_a = pnt2line([lt_x,lt_y], sta_a, end_a) # point, sta_a, end
				pnt_dist_b = pnt2line([lt_x,lt_y], sta_b, end_b) # point, sta_a, end
				#
				t_a_dist = math.hypot(cts[1][0]-lt_x, cts[1][1]-lt_y)
				t_b_c_dist = math.hypot(__cent_b[0]-lt_x, __cent_b[1]-lt_y)
				t_a_c_dist = math.hypot(__cent_b[0]-cts[1][0], __cent_b[1]-cts[1][1])
				#
				pnt_dist_a = list(pnt_dist_a)
				#
				pnt_dist_a.insert(1, t_a_dist)
				#
				if plt:
					#
					# one level tree branch distance from points of instance b to confine centers extended perpendicular line to center of graph.
					#
					list_x, list_y = [lt_x, pnt_dist_b[1][0]],[lt_y, pnt_dist_b[1][1]]
					line = lines.Line2D(list_x,list_y, lw=1., color="g", alpha=0.4)
					t_gca.add_line(line)
					#
					# lines met on line from center to current point
					_p_g = getPerpCoord(cts[1][0], cts[1][1],pnt_dist_b[1][0], pnt_dist_b[1][1], 5)
					prp1 = mpatches.ConnectionPatch([_p_g[0],_p_g[1]],[_p_g[2],_p_g[3]],"data", lw=0.2, color="g")
					t_gca.add_patch(prp1)
					#
					prp1 = mpatches.ConnectionPatch([lt_x, lt_y],[pnt_dist_a[2][0],pnt_dist_a[2][1]],"data", lw=0.2, color="r")
					#
					t_gca.add_patch(prp1)	
					#
					prp1 = mpatches.ConnectionPatch([lt_x,lt_y],[__cent_b[0],__cent_b[1]],"data", lw=0.2, color="k")
					#
					t_gca.add_patch(prp1)	
		#
	#
	# dummy access confine data for pnt2line against perpendicular of center recumbent
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
initiate_drawing = IterDraw(total_list, GC, plt, simplification)
#
initiate_drawing.run()
#
'''
TreeEvaluator is part of the solver it appears here because of drawing priority, for demonstration only.
As it contains the identification of the CT lines for each instance to run against the other instances and find 
points that are triangulated according to solver criteria.
'''
TreeEvaluator(total_list, intpl_list)
#
plt.show()
#
'''
Pre-Processor
	ContourHolder
		ContourNormalizer
	GraphConstructor
Solver
	TreeEvaluator
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