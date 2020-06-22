import os
import sys
import time
import plistlib
from copy import deepcopy
import xml.etree.ElementTree as ET
import collections
import pprint
import numpy as np
import itertools as it
from collections import OrderedDict

import matplotlib
#
matplotlib.use("TkAgg")
# Important Other: qt4agg, GTK3Agg 
# Fail to run both settings window and plotting. or have issues in sizing the windows.
# That is why meticulous work is being put in to separating the plotting process
# and the actual solver. Please bear with me.
#
from matplotlib import pyplot as plt
#plt.switch_backend("qt4agg")
import matplotlib.patches as mpatches
import matplotlib.lines as lines
#
# pip3 install PyQt5
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
run_specific = "a"
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
max_radius = 800
clip_point_count = 7 
diff_limit = 3
#

def most_occuring(v,inx, keep_opp_inx=False):
	#
	l = []
	opp = []
	#
	for x in v:
		#
		l.append(x[inx])
		#
		if keep_opp_inx:
			#
			opp.append(x[keep_opp_inx])
			#
		#
	#
	# remove dups
	s = []
	s_opp = []

	for i in l:
		if i not in s:
			#
			s.append(i)
			#
			if keep_opp_inx:
				#
				s_opp.append(opp[l.index(i)])
				#
			#
		#
	#
	count = []
	#
	# get count
	for x in s:
		#
		counted = l.count(x)
		#
		if keep_opp_inx:
			#
			get_opp = s_opp[s.index(x)]
			#
			count.append([x,get_opp,counted])
			#
		else:
			#
			count.append([x,counted])
			#
	#
	return count
#

def combiner(inst_s,inst_t ):
	#
	_val_smp = 0
	#
	s_grad_s = inst_s[0]["matching"][_val_smp]#.matched
	#
	s_grad_t = inst_t[0]["matching"][_val_smp]#.matched
	#
	# iterate point by point and count occurences for each sgrad
	#
	mo_s = []
	mo_t = []
	#
	for k,v in s_grad_s.items():
		#
		mst_occ = most_occuring(v,1)
		#
		# 
		if len(mst_occ) > 0:
				
			for x in mst_occ:
				#
				count = x[1] - ((len(mst_occ[1:])) + 1) #devaluate diluted matches
				#
				x[1] = count
			#

		#
		t_m_o = [mst_occ[0]]
		#
		for x in t_m_o:
			#
			x.append("ab")
			#
		#
		mo_s.append([k,t_m_o])
		#
	#
	for k,v in s_grad_t.items():
		#
		mst_occ = most_occuring(v,1)
		#
		# 
		if len(mst_occ) > 0:
				
			for x in mst_occ:
				#
				count = x[1] - ((len(mst_occ[1:])) + 1) #devaluate diluted matches
				#
				x[1] = count
			#

		#
		t_m_o = [mst_occ[0]]
		#
		for x in t_m_o:
			#
			x.append("ba")
			#
		#
		mo_t.append([k,t_m_o])
		#
	#
	mo_s.sort()
	mo_t.sort()
	#
	if debug:
		print("S")
		pprint.pprint(mo_s)
		print("T")
		pprint.pprint(mo_t)
	#
	#
	m_lon = max([mo_s,mo_t], key=len)
	m_sho = min([mo_s,mo_t], key=len)
	#
	if debug:
			
		print("longest list")
		pprint.pprint(m_lon)
		print("---")
		pprint.pprint(m_sho)
	#
	# Source to Target Plot 
	#
	_g_i_s_s = inst_s.initial_coords_strt_a
	_g_i_s_t = inst_s.initial_coords_strt_b
	#
	c_mo_s = [c[0] for c in mo_s]
	#
	all_conn = OrderedDict()
	#
	for x in mo_s:
		#
		c_s = x[0]
		c_t = x[1][0][0]
		coord_s = _g_i_s_s[c_s-1]
		coord_t = _g_i_s_t[c_t-1]
		certainty = x[1][0][1]
		#
		if repr([c_s,c_t,c_t,c_s]) not in all_conn.keys():
			
			#draw.label(coord_s, x[0], cax, 8, 20, "b")
			#draw.label(coord_t, x[1][0][0], cax, 8, 20, "r")

			all_conn[repr([c_s,c_t,c_t,c_s])] = [["st",coord_s,coord_t,certainty, [c_s,c_t]]]

		else:

			all_conn[repr([c_s,c_t,c_t,c_s])].append(["st",coord_s,coord_t,certainty, [c_s,c_t]])

		# #
		'''
		draw.draw_circle_on_coord(coord_s, cax, (certainty+1)/2, "b", True, False, '["g_s":'+str(c_s)+',"g_t":'+str(c_t)+',"coords":['+str(coord_s)+','+str(coord_t)+'],"certainty":'+str(certainty)+']')
		draw.draw_circle_on_coord(coord_t, cax, (certainty+1)/2, "r", True, False, '["g_s":'+str(c_t)+',"g_t":'+str(c_s)+',"coords":['+str(coord_t)+','+str(coord_s)+'],"certainty":'+str(certainty)+']')#'["g_s":'+str(c_t)+',"coords":'+str(coord_t)+',"certainty":'+str(certainty)+']')
		#
		_p = mpatches.ConnectionPatch( coord_s, coord_t,"data", lw=((certainty+1)*5)/20, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=2, alpha=0.5, color="b",label='Label')
		cax.add_patch(_p)
		'''
		#
	#
	# Target to Source Plot 
	#
	_g_i_s_s = inst_s.initial_coords_strt_a
	_g_i_s_t = inst_s.initial_coords_strt_b
	#
	c_mo_s = [c[0] for c in mo_s]
	#
	for x in mo_t:
		#
		c_s = x[1][0][0]
		c_t = x[0]
		coord_s = _g_i_s_s[c_s-1]
		coord_t = _g_i_s_t[c_t-1]
		certainty = x[1][0][1]
		#
		if repr([c_s,c_t,c_t,c_s]) not in all_conn.keys():
			
			#draw.label(coord_s, x[0], cax, 8, -20, "r")
			#draw.label(coord_t, x[1][0][0], cax, 8, -20, "b")

			all_conn[repr([c_s,c_t,c_t,c_s])] = [["ts",coord_t,coord_s,certainty,[c_s,c_t]]]

		else:

			all_conn[repr([c_s,c_t,c_t,c_s])].append(["ts",coord_t,coord_s,certainty,[c_s,c_t]])

		#
		'''
		draw.draw_circle_on_coord(coord_t, cax, (certainty+1)/2, "b", True, False, '["g_s":'+str(c_t)+',"g_t":'+str(c_s)+',"coords":['+str(coord_t)+','+str(coord_s)+'],"certainty":'+str(certainty)+']')
		draw.draw_circle_on_coord(coord_s, cax, (certainty+1)/2, "r", True, False, '["g_s":'+str(c_s)+',"g_t":'+str(c_t)+',"coords":['+str(coord_s)+','+str(coord_t)+'],"certainty":'+str(certainty)+']')
		#
		_p = mpatches.ConnectionPatch( coord_t, coord_s,"data", lw=((certainty+1)*5)/20, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=2, alpha=0.5, color="r",label='Label')
		cax.add_patch(_p)

		'''
		#
	#
	if debug:
		pprint.pprint(all_conn)
	#
	# get most certain
	#
	certain_midpoints = []
	certain_points = []
	#
	for k,v in all_conn.items():
		#
		if len(v) > 1:
			#
			if v[0][1] == v[1][2] and v[0][2] == v[1][1]:
				#
				cert_mid = midpoint(v[0][1],v[1][1])
				#
				total_cetainty = (v[0][3] + v[1][3])/2
				#
				certain_points.append([v[0][1],v[1][1], total_cetainty, v[0][4]])
				#
				certain_midpoints.append(cert_mid)
				#
		#
	#
	'''
	if debug:
		#
		print("ALL CONNECTED ITEMS")
		#
		pprint.pprint(all_conn)
		#
	#
	for x in certain_midpoints:
		#
		draw.draw_circle_on_coord(x, cax, 5, "g")
		#
	#
	'''
	#
	return certain_points
	#
#
#plt.figure(frameon=False)

#

def make_ct_perp(coord_ct, cen_c, cfn):
	#
	perpendic = []
	recumbent = []
	#
	for coords in coord_ct:
		#
		#print("---")
		#print(coords)
		#
		x = coords[0]
		y = coords[1]
		#
		# perpendicular to center
		#
		_perp_virtual= getPerpCoord(cen_c[0], cen_c[1], x, y, 100) # perpendicular center to coordinate
		_perp_actual = getPerpCoord(cen_c[0], cen_c[1], x, y, 10000) # perpendicular to center to coordinate
		#
		perpendic.append([
			[_perp_virtual[0],_perp_virtual[1]],[_perp_virtual[2],_perp_virtual[3]],
			[_perp_actual[0], _perp_actual[1]], [_perp_actual[2], _perp_actual[3]]
		])

		'''
		sta_a = lt_p[1][0]
		end_a = lt_p[1][1]
		sta_b = lt_p[1][2]
		end_b = lt_p[1][3]
		'''

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
	# pre to ante line
	#
	_p = coord_ct[0]
	_c = coord_ct[1]
	_a = coord_ct[2]
	#
	#pa_angle = get_angle(_p,_a) 
	#
	pa_mov_seg = move_segment(_p,_a, _c)
	pa_scl_seg = scale_segment(pa_mov_seg[0], pa_mov_seg[1], 20)
	#
	recumbent.append([_c,pa_mov_seg,pa_scl_seg]) # center to coordinate
	#
	return [perpendic,recumbent]
	#
#
class CenterTransfer(object):
	"""
	A 2D bounding box
	"""
	def __init__(self, __point, inst_items, points_lenw):

		self.__point = __point
		self.inst_items = inst_items
		self.points_lenw = points_lenw
		self.matched_source = []
		#
	#
	def set_confines(self):
		#
		t_fnl_d = max_radius#math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) + 50 # target_first_and_last_distance
		p_d = 0
		#
		for k,v in self.points_lenw.items():
			#
			if k!=(0,0):
				#
				t_a_coord = self.points_lenw.get(self.inst_items[p_d])["coord"]
				t_a_order = self.points_lenw.get(self.inst_items[p_d])["order"]
				#
				t_circle = [t_a_coord,t_fnl_d]
				#
				contains = in_circle(self.__point,t_circle)
				#
				if contains:
					#
					t_a_dist = math.hypot(t_a_coord[0]-self.__point[0], t_a_coord[1]-self.__point[1])
					#
					#print(t_a_order)
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
		# print("---")
		# print(get_point_inx_line(len(self.points_lenw), self.search_center[3], 'p') )
		# print(self.search_center[3])
		# print(get_point_inx_line(len(self.points_lenw), self.search_center[3], 'a') )
		# #
		# print(self.ms_pn_s)
		#
		if toget == "c":
			#
			return self.search_center
			#
		elif toget == "p":
			#
			#print(get_point_inx_line(len(self.points_lenw), self.search_center[3], 'p') )
			#
			#found = [c for c in self.ms_pn_s if c[3] == get_point_inx_line(len(self.points_lenw), self.search_center[3], "p")]
			#
			#print(found)
			#
			return next(c for c in self.ms_pn_s if c[3] == get_point_inx_line_base(len(self.points_lenw), self.search_center[3], "p", 1))
			#
		elif toget == "a":
			#
			return next(c for c in self.ms_pn_s if c[3] == get_point_inx_line_base(len(self.points_lenw), self.search_center[3], "a", 1))
			#

	def get_confines(self):
		#
		return [self.get_confine("p"), self.get_confine("c"), self.get_confine("a")]
		#


#
class ContourManager(object):
	"""
	
	"""
	def __init__(self, instances):
		#
		self.inst = instances
		#
	#
	def get_tc(self, inx):
		#
		contours = []
		#
		for instance in self.inst:
			#
			for letter in self.inst[instance]:
				#
				for contour in self.inst[instance][letter]:
					#
					t_contour = self.inst[instance][letter][contour]
					#
					inst_inx = t_contour["inst"]
					#
					if inx == inst_inx:
						#
						contours.append(t_contour)
						#return t_contour # this
						#
					#
					else:
						pass
					#
		return contours 
	#
	def tc_get_simp_conf_b_coord(self, t_contour, simp_level, coordinate):
		#
		confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate][0]
		confine_index = t_contour["confines_simp"][simp_level].index(confine_from_coord)
		#
		return confine_index, confine_from_coord
		#
	#
	'''
	def tc_get_point_inx_lenw_to_cnt(self, t_contour, simp_level, coordinate):
		#
		point_coords = [d['coord'] for d in list(t_contour["graphs"][simp_level].values())]
		#
		print("---")
		print(point_coords)
		print(coordinate)
		#
		point_index = point_coords.index(coordinate)
		#
		return point_index
		#
	#
	'''
	def get_tc_points(self, tc, simp_level):
		#
		return tc["simplified"][simp_level]
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
				pipl.append([ir[j],ir[i]])
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
#
def get_points_around(__point, points_a,points_b, l_s):
	#
	matched_target = []
	#
	for z in l_s:
		#
		p_c = 0
		t_psca_coord = z[1][1]#points_b.get(a_items[p_c])["coord"]
		#
		found_p = False
		#
		for v in points_b:
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
				if contains:
					#
					found_p = True
					#
					t_b_dist = math.hypot(t_b_coord[0]-__point[0], t_b_coord[1]-__point[1])
					#
					new_match = [t_b_dist,t_b_coord,p_c,t_b_order,max_radius]
					#
					if new_match not in matched_target:
						#
						matched_target.append(new_match)
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

# AKA Solver Number One
def TreeGenerator(instances, inst_intpl_lst, simp_levels):
	#
	inst_data = []
	#
	run_cttpa = False
	#
	for intpair in inst_intpl_lst:
		#
		print("TG RUN FOR", intpair)
		#
		in_a = intpair[0]
		in_b = intpair[1]
		#
		CM = ContourManager(instances)
		#
		tc_inst_a = CM.get_tc(in_a)
		tc_inst_b = CM.get_tc(in_b)
		#
		inst_data.append(len(tc_inst_a))
		#
		'''
		Iterate every graph point of instance A except graph center,
		for every A_point create a circle of max radius and get instance B points that are in that circle,
		for every INCIRCLED_point found create a ct branch to current A_point perpendicular infinite to graph center.

		'''
		#
		for t_contour in tc_inst_a:
			#
			inst_inx = t_contour["inst"]
			cont_inx = t_contour["cont"]
			#
			t_plot_a = plt.figure(t_contour["plot_num"])
			ax = t_plot_a.gca()
			t_plot_b = plt.figure(tc_inst_b[cont_inx]["plot_num"])
			bax = t_plot_b.gca()
			#
			#
			
			for _val_smp in simp_levels:
				#
				points_a = CM.get_tc_points(t_contour,_val_smp)
				points_b = CM.get_tc_points(tc_inst_b[cont_inx],_val_smp)
				#
				for p in points_a:#list(tc_inst_a["graphs"][0].values()):
					#
					__point = flipCoordPath([p],False,True)[0] # flipCoordPath accepts and returns list of points so need to pass list and to get 0
					#
					#conf_dat = [d for d in t_contour["confines_simp"][_val_smp] if d[1][1] == list(__point)][0]
					#conf_inx = t_contour["confines_simp"][_val_smp].index(conf_dat)
					conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,list(__point))
					#
					if run_cttpa == False:
						
						# change to relative to pca from perpendicular
						
						lt_p = t_contour["perp_simp"][_val_smp][conf_inx]
						sta_a = lt_p[1][0]
						end_a = lt_p[1][1]
						sta_b = lt_p[1][2]
						end_b = lt_p[1][3]
						
					else:
						#
						lt_p = t_contour["recu_simp"][_val_smp][conf_inx][0]
						#print(lt_p)
						sta_a = lt_p[1][0]
						end_a = lt_p[1][1]
						sta_b = lt_p[2][0]
						end_b = lt_p[2][1]
					#
					l_s = [conf_dat]
					#
					#
					all_match = []
					all_match_len = []
					#
					points_arr = get_points_around(__point,points_a,points_b,l_s)
					#
					l_t = points_arr
					#
					l_t = rotate_points(l_t, len(points_b)) # review if nessessary 
					#
					# graph center of instance b
					#gc_b = list(tc_inst_b[inst_inx]["graphs"][_val_smp].values())[-1]["coord"]
					gc_b = list(tc_inst_b[cont_inx]["graphs"][_val_smp].values())[-1]["coord"]
					#
					#t_contour = cnt
					#
					confine_from_coord = [d for d in t_contour["confines_simp"][_val_smp] if d[1][1] == __point][0]
					glyph_point_index = t_contour["confines_simp"][_val_smp].index(confine_from_coord)
					#
					for lt in l_t:
						#
						lt_crd = lt[1]
						lt_x = lt_crd[0]
						lt_y = lt_crd[1]
						#
						pnt_dist_a = pnt2line([lt_x,lt_y], sta_a, end_a) # point, sta_a, end
						pnt_dist_b = pnt2line([lt_x,lt_y], sta_b, end_b) # point, sta_a, end
						#
						# distance of those positions from current point ? review
						t_a_dist = math.hypot(__point[0]-lt_x, __point[1]-lt_y)
						t_b_dist = int(math.hypot(__point[0]-pnt_dist_b[1][0], __point[1]-pnt_dist_b[1][1]))
						#
						t_b_c_dist = math.hypot(gc_b[0]-lt_x, gc_b[1]-lt_y)
						t_a_c_dist = math.hypot(gc_b[0]-__point[0], gc_b[1]-__point[1])
						#
						pnt_dist_a = list(pnt_dist_a)
						pnt_dist_a.insert(1, t_a_dist)
						#
						# area
						tri = [__point,list(pnt_dist_b[1]),lt_crd]
						_area = area(tri)
						#
						center_m_point = distance(gc_b,lt_crd)
						center_s_point = distance(gc_b,__point)
						sm_point = distance(lt_crd,__point)
						#
						m_angle = get_angle_b(gc_b,lt_crd)
						s_angle = get_angle_b(gc_b,__point)
						#
						#
						#print(pnt_dist_a)
						# get travel distance on the line to that point
						#print(__point, lt_crd)
						#
						# gather ct matching data
						#
						new_match = {
							"point_graph_inx":	(lt[2],lt[3]), 
							"pnt_dist_a": 		pnt_dist_a, #
							"pnt_dist_b":		pnt_dist_b, # pre _area check conflict
							"area":				_area,
							"pnt_crd":			[__point[0],__point[1]], 
							"lt_crd":			lt_crd, #
							"t_b_dist":			t_b_dist,
							"t_dist":			abs(abs(t_b_c_dist) - abs(t_a_c_dist)),
							"center_dist":		abs(center_m_point - center_s_point),
							"angle":			abs(m_angle-s_angle),
							"sm_point":			sm_point,
							"calc_a":			_area+pnt_dist_a[0]+abs(center_m_point - center_s_point)+abs(m_angle-s_angle)+sm_point,
							"tri":				tri,
							"lt":				lt,
							"gpi":				glyph_point_index,
							"max_radius":		max_radius,
							"instance_pair":	[in_a, in_b]
							}
						#
						if _val_smp not in t_contour["matching"].keys():
							#
							t_contour["matching"][_val_smp] = []
							t_contour["matching_best_area"][_val_smp] = []
							#
						#
						if new_match not in t_contour["matching"][_val_smp]:
							#
							t_contour["matching"][_val_smp].append(new_match)
							#
						#
					#
				#
			#
		#
	#
#
def find_ctt_for_pnt_smp_pair(matches,smp,pnt,intpair):
	#
	result = []
	#
	for e in matches[smp]:
		if e["gpi"] == pnt and intpair == e["instance_pair"]:
			result.append(e)

	return result
	#
#
def get_seq(li):
	seq_lists = []
	#
	for idx,item in enumerate(li):
		#
		if not idx or item-1 != seq_lists[-1][-1]:
			
			seq_lists.append([item])
		else:

			seq_lists[-1].append(item)
	#
	return seq_lists
	#
#
def get_limits(_lst):
	#
	_min = min(_lst)
	_max = max(_lst)
	#
	return [_min, _max]
#
def rotate_center_clip(rotated_seq, cent, len_points, clip):
	#
	l = rotated_seq
	#
	if len_points in rotated_seq and 1 in rotated_seq:
		#
		lst_l = []
		lst_r = []
		#
		end_inx = rotated_seq.index(len_points)
		start_inx = rotated_seq.index(1)
		#
		if end_inx + 1 == start_inx:
			#
			lst_l = rotated_seq[:start_inx]
			lst_r = rotated_seq[start_inx:]
			#
			lim_l = get_limits(lst_l)
			lim_r = get_limits(lst_r)
			#
			new_r = list(range(lim_r[0], lim_r[1]+1))
			new_l = list(range(lim_l[0], lim_l[-1]+1))
			#
			l = new_l + new_r
			#
		#
	#
	else:
		#
		l = list(range(1, len_points))
		#
		if cent not in l:
			#
			l = list(range(1, len_points+1))
			#
			#return False
		#	#
		#
	#
	#print(l.index(cent))
	#
	_cent = int((len(l)/2)) - int(l.index(cent))#int((len(l)/2) + l.index(cent) +1)
	#
	d = collections.deque(l)
	d.rotate(_cent)
	#
	centered = list(d)#l[cent:] + l[:cent]
	#
	centered_clip = centered.copy()
	#
	#
	if len(centered) % 2 == 0:
		#
		clip = clip + 1
		#
	#
	while len(centered_clip) > clip:	

		if len(centered_clip) != clip:

			del centered_clip[len(centered_clip)-1:]

		if len(centered_clip) != clip:
			
			del centered_clip[:1]
	#
	if len(centered) % 2 == 0:
		#
		del centered_clip[:1]
		#
	#
	return centered_clip
	#
#

def get_num_seq_from_ctt_matches(sorted_all_match, points_b):
	#
	#
	seq_points = []
	#
	for x in sorted_all_match:
		#
		
		#
		point_num = x['lt'][2] + 1
		#
		seq_points.append(point_num)
		#
	#
	seq_lists = get_seq(seq_points)
	#
	#print(seq_lists)
	#-----------------------------------
	rotated_seq = rotate_points([],len(points_b),seq_lists)
	rot_seq = sorted(rotate_points([],len(points_b),seq_lists))
	#psca_m_ginx = psca_glif_line_inx(t_m)
	#

	#
	return rot_seq
	#
#
def get_psca_ct_target_matches(per_ct):
	#
	per_ct_points = [[],[],[]]
	#
	y = 0
	#
	for x in per_ct:
		#
		#
		for z in x:
			#
			#print(z[0])
			#
			per_ct_points[y] = z
			#
		#
		y = y + 1
		#
	#
	return per_ct_points
	#
#
def get_line_multi_ct_aggregate(l_p,l_c,l_a):
	#
	s = [l_p, l_c, l_a]
	#
	s_i = [[0,1,2], [0,1,2], [0,1,2]]
	#
	perm = list(it.product(*s))
	perm_i = list(it.product(*s_i))
	#
	#print(s)
	#
	results = []
	#
	for p in perm:
		#
		unique_data = set(x for l in p for x in l)
		# 
		result = []
		#
		for x in unique_data:
			#
			total = -1
			#
			z = 0
			#
			for y in p:
				#
				if x in y:
					#
					total = total + 1
					#
				#
				z = z + 1
				#

				#
			#
			#
			result.append(total)
			#
		#
		results.append(result)
		#
	#
	#
	sum_results = []
	#
	o = 0
	#
	for u in results:
		#
		sum_results.append([o,sum(u),perm_i[o], sum(perm_i[o])])
		#
		o = o + 1
		#
	#
	sorted_sum_results = sorted(sum_results, key = lambda x: x[1] - sum(x[2]), reverse=True)
	#
	item = perm[sorted_sum_results[0][0]]
	#
	#
	return item
	#
#
def merge_overlap(a, b):
	#
	index = 0
	for i in range(len(b), 0, -1):
		#if everything from start to ith of b is the 
		#same from the end of a at ith append the result
		if b[:i] == a[-i:]:
			index = i
			break

	return a + b[index:]
#
#
def get_aggregate_line(blm, len_points, len_line):
	#
	inc_ghost = None
	#
	psc = [[f,s] for f in blm[1] for s in blm[0]]
	pa =  [[f,s] for f in blm[0] for s in blm[2]]
	sca = [[f,s] for f in blm[1] for s in blm[2]]
	#
	blm_prm = [
		psc,
		pa,
		sca
	]
	#
	all_res = []
	all_psca = []
	#
	for z in blm_prm:
		#
		c_res = []
		#
		for x in z:
			#
			if x[0] == x[1]:
				#
				c_res.append(x[0])
				#
		#
		all_res.append(c_res)
		#
		all_psca.append(len(c_res))
		#
	#
	#
	m_PSC = all_psca[0]
	m_PA = all_psca[1]
	m_SCA = all_psca[2]
	#
	best_center = blm[1][int(len(blm[1])/2)]
	#
	if debug:
		#
		print("BEST CENTER ===============")
		print(best_center)
		#
	#
	if (m_PSC <= diff_limit and m_PA <= diff_limit): #or (m_PSC <= diff_limit or m_PA <= diff_limit):
		#
		#
		res = merge_overlap(blm[1],blm[2])
		#
		inc_ghost = 0
		#
	elif (m_PSC <= diff_limit and m_SCA <= diff_limit): #or (m_PSC <= diff_limit or m_SCA <= diff_limit):
		#
		#
		res = merge_overlap(blm[0],blm[2])
		#
		best_center = res[int(len(res)/2)]
		#
		inc_ghost = 1
		#
	elif (m_PA <= diff_limit and m_SCA <= diff_limit): #or (m_PA <= diff_limit or m_SCA <= diff_limit):
		#
		#
		res = merge_overlap(blm[0],blm[1])
		#
		inc_ghost = 2
		#
	else:
		#
		res = blm[1]
		#
	#
	# Limit line to len 7
	#
	seq_lists = get_seq(res)
	rot_cent = rotate_center_clip(seq_lists, best_center, len_points, clip_point_count)
	#
	#
	return [rot_cent, inc_ghost]
	#
#
'''
def get_coord_range_finder(c_match, traces, coords, _dir, _center, bax, _plt):
	#
	got_point = get_point_inx_by_coord(c_match[1], coords)
	#
	if _dir == "p":
		#
		_w = "CCW"
		_c = "orange"
		#
	else:
		#
		_w = "CW"
		_c = "purple"
		#
	#
	tracing_coords = []
	tracing_rec = []
	#
	#
	for y in traces:
		#
		print("-----?")
		print(len(coords), y[0])
		#
		try:
			#
			#
			get_moving_inx_p = get_point_inx_line_base(len(coords), y[0], _dir, 0)
			#
			coord_moving_p = next(c for c in coords if coords.index(c) == get_moving_inx_p)
			#
			got_moving = get_coord_range(coords, c_match[1], 1, _dir, y[1])
			#
				#
			tracing_coords.append([y,got_moving])
				#
		except Exception as e:
			#
			pass
	#
	for x in tracing_coords:
		#
		x[1][0].insert(0,coords[got_point-1])
		x[1][1].insert(0,got_point)
		#
	#
	#
	for x in tracing_coords:
		#
		dist = 0
		#
		trace_coords = x[1][0]
		#
		i = 0
		#
		for y in trace_coords:
			#
			if i != len(trace_coords)-1:
				#
				got_point_t = get_point_inx_by_coord(trace_coords[i+1], coords)
				#
				#
				travel_difficulty = 0
				#
				if got_point_t > got_point and _w == "CCW" or got_point_t < got_point and _w == "CW":
				# 	#
					travel_difficulty = 100
					#
				# else:
				travel_mid = midpoint(y,trace_coords[i+1])
				dist_cent = distance(_center, travel_mid)
				#
				dist = dist + (distance(y,trace_coords[i+1])) + travel_difficulty# + (travel_difficulty / distance(y,trace_coords[i+1])))
				#
			#
			i = i + 1
		#
		x.append(dist)
		#
	#
	if debug:
		#
		print ('\n'+tcolor.WARNING + "DISTANCE FROM: " + repr([got_point,coords[got_point-1]]) + tcolor.ENDC)
	#
	for y in tracing_coords:
		#
		if debug:
			#
			print (tcolor.WARNING + str(_w)+' TO: '+ str(y[0]) +' IS: '+ str(y[2])+ tcolor.ENDC)
			#
		# source point, target point, distance
		tracing_rec.append([got_point,y[0][0],y[2]])
		#
	#
	if  _plt:
		
		if show_travel_distance_a:
			#
			for x in tracing_coords:
				#
				plot_line(bax, x[1][0], _c, _plt)
				#

	#
	return tracing_rec
	#
'''
#
def get_point_inx_line_base(numpoints, num, loc, base):
	#
	'''
	base added as when num == 0 on "p" cant gather confines - works with base 1
	this way i can use this function in coord_range, works with base 0
	'''
	#
	if loc == "p":
		#
		if num == base:
			#
			return numpoints - 1
			#
		#
		else:
			#
			if num - 1 != numpoints:
				#
				return num - 1
				#
			else:
				#
				return 0
				#
			#
		#
	elif loc == "a":
		#
		if num - 1 == numpoints:
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
				return base 
				#
			#
		#
	#
#
#

def get_coord_range(coords, p_coords, _range, _dir, move_until = False):
	#
	# Gathers coordinates according to _range (int) and _dir ("pre","ante"), 
	# from given coordinate and list of coordinates, taking into account circularity.
	#
	gathered_coords = []
	gathered_inx = []
	#
	last_point = p_coords
	#
	if move_until != False:
		#
		_range = len(coords)
		#
	#
	# get current start point in opp
	cur_inx = coords.index(last_point)
	get_moving_inx_p = get_point_inx_line_base(len(coords), cur_inx, "p", 0)
	current_coord_start_opp = get_point_inx_line_base(len(coords), get_moving_inx_p, "a", 0)
	moving_coord_current_start_opp = next(c for c in coords if coords.index(c) == current_coord_start_opp)
	#
	for x in range(_range):
		#
		cur_inx = coords.index(last_point)
		#
		get_moving_inx = get_point_inx_line_base(len(coords), cur_inx, _dir, 0)
		#
		moving_coord = next(c for c in coords if coords.index(c) == get_moving_inx)
		#
		gathered_coords.append(moving_coord)
		#
		last_point = moving_coord
		#
		if move_until != False:
			#
			if moving_coord == move_until:
				#
				break
				#
			#
		#
	#
	for x in gathered_coords:
		#
		gathered_inx.append(coords.index(x)+1)
		#
	# 
	return [gathered_coords, gathered_inx, [current_coord_start_opp,moving_coord_current_start_opp]]
	#
#
def get_point_inx_by_coord(coord, points):
	#
	is_ghost = False
	#
	for x in points:
		#
		if x == coord:
			#
			return points.index(x) + 1
			#is_ghost = True
			#
		#
	#
#
#
'''
def get_distance_from_trace(tc_inst_a, tc_inst_b, p_coords, t_match, __cent_b,bax,_plt, cont_inx, _val_smp):
	#
	__cent_b = list(tc_inst_b[cont_inx]["graphs"][_val_smp].values())[-1]["coord"]
	#
	initial_coords_a = tc_inst_a[cont_inx]["coords"]["graph"]
	initial_coords_b = tc_inst_b[cont_inx]["coords"]["graph"]
	#
	got_point = get_point_inx_by_coord(p_coords, initial_coords_a)
	#
	checkrange = []
	#
	# Get two steps forward and two steps back for every ctm match for per_ct item (t_match)
	s_pre = get_coord_range(initial_coords_a, p_coords, 2, "p")
	
	s_ant = get_coord_range(initial_coords_a, p_coords, 2, "a")
	
	#
	print("---------s_pre")
	print(s_pre)
	print("---------s_ant")
	print(s_ant)
	#

	# See if those coordinates have been matched
	#
	t_match_pre = []
	t_match_ant = []
	#
	for sp in s_pre[1]:
		#
		print("----")
		print(sp)
		#
		p_sgrad_matched = _f.matched.get(sp, None)
		#
		p_t_m_o = None
		#
		if p_sgrad_matched != None:
			#
			p_t_m_o = most_occuring(p_sgrad_matched,1)
			#
			if p_t_m_o != None:
				#
				t_match_pre.append(p_t_m_o[0])
				#
			#
	
	for sa in s_ant[1]:
		#
		a_sgrad_matched = _f.matched.get(sa, None)
		#
		a_t_m_o = None
		#
		if a_sgrad_matched != None:
			#
			a_t_m_o = most_occuring(a_sgrad_matched,1,True)
			#
			if a_t_m_o != None:
				#
				t_match_ant.append(a_t_m_o[0])
				#
			#
	
	#
	# / 
	#
	#
	got_match = None
	#
	for x in initial_coords_b:
		#
		t_p = get_point_inx_by_coord(x, initial_coords_b)
		#
		if t_p == t_match[1]:
			#
			got_match = [t_match[0], x]
			#
		#
	#
	coord_dist_result = []
	#
	if len(t_match_pre) > 0:
		#
		trace_coords_p = []
		#
		for mtp in t_match_pre:
			#
			trace_coords_p.append([mtp[0],initial_coords_b[mtp[0]-1]])
			#
		#
		t_coords_p = get_coord_range_finder(got_match, trace_coords_p, initial_coords_b, "p", __cent_b, bax,_plt)
		#
		coord_dist_result.extend(t_coords_p)
		#
	#
	
	if len(t_match_ant) > 0:
		#
		trace_coords_a = []
		#
		for mtp in t_match_ant:
			#
			trace_coords_a.append([mtp[0],initial_coords_b[mtp[0]-1]])
			#
		#
		t_coords_a = get_coord_range_finder(got_match, trace_coords_a, initial_coords_b, "a", __cent_b, bax,_plt)
		#
		coord_dist_result.extend(t_coords_a)
		#
	#
	#
	dist_list_sum = []
	#
	for x in coord_dist_result:
		#
		dist_list_sum.append(x)
		#
		#
	#
	#
	return coord_dist_result
	#
'''

#

'''
def travel_sort(per_ct, tc_inst_a, tc_inst_b, __point, cont_inx, _val_smp, bax, _plt):
	#
	__cent_b = list(tc_inst_b[cont_inx]["graphs"][_val_smp].values())[-1]["coord"]
	#
	#if travel_sort == True:
	#
	#if debug:
		#
	#	print("===")
	#pprint.pprint(per_ct[0])
		#
	closest_travel_p = []
	closest_travel_sc = []
	closest_travel_a = []
	#
	for x in per_ct[0]:
		#
		print('----0')
		print(x)
		# (tc_inst_a, tc_inst_b, p_coords, t_match, __cent_b,bax,_plt, cont_inx, _val_smp)
		
		dist_trace = get_distance_from_trace(tc_inst_a, tc_inst_b,__point, x['point_graph_inx'], __cent_b,bax,_plt, cont_inx, _val_smp )
		#
		print(dist_trace)
		#
		
		closest_travel_p.extend(dist_trace)
		#
		if debug:
			#
			print("TRAVEL T DISTANCE TRACE", dist_trace)
		
		
	#
	for x in per_ct[1]:
		#
		print('----1')
		print(x)
		#
		
		dist_trace = get_distance_from_trace(tc_inst_a, tc_inst_b,__point, x['point_graph_inx'], __cent_b,bax,_plt, cont_inx, _val_smp )
		#
		closest_travel_sc.extend(dist_trace)
		#
		if debug:
			#
			print("TRAVEL SC DISTANCE TRACE", dist_trace)
		#
		
	#
	for x in per_ct[2]:
		#
		print('----2')
		print(x)
		#
		
		dist_trace = get_distance_from_trace(tc_inst_a, tc_inst_b,__point, x['point_graph_inx'], __cent_b,bax,_plt, cont_inx, _val_smp )
		#
		closest_travel_a.extend(dist_trace)
		#
		if debug:
			#
			print("TRAVEL A DISTANCE TRACE", dist_trace)
		
	#
	
	sorted_travel_dist_p = sorted(closest_travel_p, key=lambda x: x[2])
	sorted_travel_dist_sc = sorted(closest_travel_sc, key=lambda x: x[2])
	sorted_travel_dist_a = sorted(closest_travel_a, key=lambda x: x[2])
	#
	if debug:
		#
		print("COSTST")
		print(closest_travel_sc)
		#
		print("SORT")
		pprint.pprint(sorted_travel_dist_sc)
		#
	#
	sord_p = [item[0] for item in sorted_travel_dist_p]
	sord_sc = [item[0] for item in sorted_travel_dist_sc]
	sord_a = [item[0] for item in sorted_travel_dist_a]
	#
	if debug:
		#
		print("SORT ITEMS")
		pprint.pprint(sord_sc)
	#
	sord_p_unq = list(OrderedDict.fromkeys(sord_p))[:3]
	sord_sc_unq = list(OrderedDict.fromkeys(sord_sc))[:3]
	sord_a_unq = list(OrderedDict.fromkeys(sord_a))[:3]
	#
	if debug:
		#
		print("UNQ")
		pprint.pprint(sord_sc_unq)
	#
	
	#
	#return [per_ct, [sord_p_unq,sord_sc_unq, sord_a_unq]]
	#
	#
	st = init_ct_sort[1]
	#
	c_per_ct = per_ct_ng.copy()
	#
	res_p = [y for x in st[0] for y in per_ct_ng[0] if y[0][1] == x] 
	res_sc = [y for x in st[1] for y in per_ct_ng[1] if y[0][1] == x] 
	res_a = [y for x in st[2] for y in per_ct_ng[2] if y[0][1] == x] 
	#
	new_tct = [
		res_p,
		res_sc,
		res_a
	]
	#
	#if debug:
	#
	pprint.pprint(c_per_ct[1])
	print("===> NEW SC CT")
	pprint.pprint(new_tct[1])
	#
	#
	#per_ct_ng = new_tct
	#
	
	#
'''
#
def test_seek_line(to_ctt, tc_a, tc_b, _val_smp, _cnt_inx):
	#
	def dir_point(points, crd, _dir, _len):
		#
		travel_set = []
		#
		for x in range(_len):
			#
			_p = tuple(flipCoordPath([crd],False,True)[0])
			_p_inx = points.index(_p)
			_p_inx_moving = get_point_inx_line_base(len(points), _p_inx, _dir, 0)
			#
			print(_p_inx)
			#
			try:
				#
				_p_moving = next(c for c in points if points.index(c) == _p_inx_moving)
				#
				#return [_p_inx_moving, flipCoordPath([_p_moving],False,True)[0] ]
				travel_set.append([_p_inx_moving, flipCoordPath([_p_moving],False,True)[0] ])
				#
			except Exception as e:
				#
				#return [None,None]
				travel_set.append([None,None])
				#
			#
	#
	'''
	From Each PCA Confine Matches (3 for each or more)
	Find which series corresponds to each other as beeing on the same line on the opposite instance.

	Logic:

		Start from C Matches (M_C)

			For each M_C:
				
				for length of M_A (arbitrary):

					move one forward on the opposite instance line

						is this point (M_A_1) in M_A (Ante Matches)?

							if yes:

								append M_A_1B

							if not:

								this point must be on another line area

				for length of M_P (arbitrary):

					move one backward on the opposite instance line
					
						is this point in M_P (Pre Matches)?		

							if yes:

								prepend M_P_1

							if not:

								this point must be on another line area				

	'''
	#
	m_p = to_ctt[0]
	m_c = to_ctt[1]
	m_a = to_ctt[2]
	#

	pnts_smp_b = tc_b[_cnt_inx]["simplified"][_val_smp]
	#
	all_lines = []
	#
	for c in m_c:
		#
		#
		_c = tuple(flipCoordPath([c],False,True)[0]) # flip horizontal and tuple coord for pnts list find
		#
		# (coords, p_coords, _range, _dir, move_until = False)
		c_range_ant_crds,c_range_ant_inxs,curr_start_opp_a = get_coord_range(pnts_smp_b,_c, 2, 'a')
		c_range_pre_crds,c_range_pre_inxs,curr_start_opp_p = get_coord_range(pnts_smp_b,_c, 2, 'p')
		#
		# add starting coordinate to line
		found_line = [flipCoordPath([curr_start_opp_a[1]],False,True)[0]]
		#
		#
		if c == [144.0, -14.0]:
			print("MC")
			print(c)
			print("MOVE ANTE")
			print(c_range_ant_crds)
			print("MOVE PRE")
			print(c_range_pre_crds)
			
			#print("->", seek_a_inx)
			#print("<-", seek_p_inx)
			
			print("SEEK ANTE")
			#
			print(curr_start_opp_a)
			print(curr_start_opp_p)
			#
			print("---------------------------------")
			print(c_range_ant_inxs)
			print(c_range_pre_inxs)
			#
		
		#
		#
		for s_a_crd in c_range_ant_crds:
			#
			_s_a_crd = list(flipCoordPath([s_a_crd],False,True)[0]) # flip and list
			#
			for a in m_a:
				#
				match = (a == _s_a_crd)
				#
				#
				if (a == _s_a_crd):
					'''
					if c == [250.0, 414.0]:
						print(a, _s_a_crd, match)
					'''
					found_line.append(a)
				#
			#
		'''
		if c == [250.0, 414.0]:
			print("SEEK PRE")
		'''
		#
		for s_p_crd in c_range_pre_crds:
			#
			_s_p_crd = list(flipCoordPath([s_p_crd],False,True)[0]) # flip and list
			#
			for p in m_p:
				#
				match = (p == _s_p_crd)
				#
				#
				if (p == _s_p_crd):
					'''
					if c == [250.0, 414.0]:
						print(p, _s_p_crd, match)
					'''
					found_line.insert(0,p)
					#
				#
			#
		#
		all_lines.append(found_line)
		#
		#if c == [250.0, 414.0]:
		'''
		print("SEEK PRE")
		#
		for p in m_p:
			#
			if [seek_p_inx, seek_p_crd] != [None,None]:
				#
				print(p, seek_p_crd)
				#
			#
		#
		'''
	#
	# longest line in terms of items
	longest = all_lines[sorted([(i,len(l)) for i,l in enumerate(all_lines)], key=lambda t: t[1])[-1][0]]
	#
	'''
	print("FOUND LINES")
	print(all_lines)
	print("LONGEST PARTICIPANT LINE")
	print(longest)
	'''
	#
	return longest
	#
#
def get_mean_distance_points(points_s):
	#
	mean_distances = []
	#
	for x in points_s:
		#
		mean_distances.append( x['pnt_dist_a'][0] + x['area'] )
		#
	#
	average = sum(mean_distances) / len(mean_distances)
	#
	n = 0.5
	output = [x for x in mean_distances if abs(x - average) < np.std(mean_distances) * n or x < average ]
	#
	print("---------")
	print(mean_distances)
	print(output)
	#featured = sorted(filesToWrite, key=lambda k: ("myKey" not in k, k.get("myKey", None)))
	return sorted(points_s, key=lambda x: (x['pnt_dist_a'][0]+ x['area'] in output), reverse=True)
	#
#
def TreeEvaluator(instances, inst_intpl_lst, simp_levels):
	#
	inst_data = []
	#
	for intpair in inst_intpl_lst:
		#
		print("TE RUN FOR", intpair)
		#
		in_a = intpair[0]
		in_b = intpair[1]
		#
		CM = ContourManager(instances)
		#
		tc_inst_a = CM.get_tc(in_a)
		tc_inst_b = CM.get_tc(in_b)
		#
		inst_data.append(len(tc_inst_a))
		#
		#graph_b_crd = tc_inst_b[0]["coords"]["graph"]
		##print(graph_b_crd)
		#
		for t_contour in tc_inst_a:
			#
			inst_inx = t_contour["inst"]
			cont_inx = t_contour["cont"]
			#
			t_plot_a = plt.figure(t_contour["plot_num"])
			tgca_a = t_plot_a.gca()
			t_plot_b = plt.figure(tc_inst_b[cont_inx]["plot_num"])
			tgca_b = t_plot_b.gca()
			#
			t_color = color[inst_inx]
			#
			for _val_smp in simp_levels:
				#
				points_a = CM.get_tc_points(t_contour,_val_smp)
				points_b = CM.get_tc_points(tc_inst_b[cont_inx],_val_smp)
				#
				for p in points_a:#list(tc_inst_a["graphs"][0].values()):
					#
					__point = flipCoordPath([p],False,True)[0] # flipCoordPath accepts and returns list of points so need to pass list and to get 0
					#
					#conf_dat = [d for d in t_contour["confines_simp"][_val_smp] if d[1][1] == list(__point)][0]
					#conf_inx = t_contour["confines_simp"][_val_smp].index(conf_dat)
					#
					conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,list(__point))
					confine_from_coord = conf_dat
					glyph_point_index = conf_inx
					fliped_points_b = flipCoordPath(points_b,False,True)
					#
					tct_ = [
						[],
						[],
						[]
					]
					#
					t_m = find_ctt_for_pnt_smp_pair(t_contour["matching"],_val_smp,conf_inx, intpair)
					sorted_all_match = sorted(t_m, key=lambda x: x['area']+x['pnt_dist_a'][0])[:6]
					#sorted_all_match = sorted(t_m, key=lambda x: (x['area'],x['pnt_dist_a'][0],x['center_dist'],x['angle'],x['sm_point']))[:3]
					#sorted_all_match = sorted(t_m, key=lambda x: (x['area'],x['pnt_dist_a'][0],x['center_dist'],x['angle'],x['sm_point']))[:3]
					#
					# clip points that are too far based on mean point distance
					#sorted_all_match = sorted(t_m, key=lambda x: x['area'] )[:3]#
					#sorted_all_match = get_mean_distance_points(sorted_mean_distance)[:3]#sorted(t_m, key=lambda x: (x['area']+x['pnt_dist_a'][0]))[:3]
					#
					#
					#
					for e in t_contour["matching"][_val_smp]:
						#
						if e["gpi"] == conf_inx and intpair == e["instance_pair"]:
							#
							if e in sorted_all_match:
								#
								if e not in t_contour["matching_best_area"][_val_smp]:
									#
									t_contour["matching_best_area"][_val_smp].append(e)
									#
								#
							#
						#
					#
					# confines are stored with the same index of points 
					#
				#
				################################################################# START
				

				if _val_smp not in t_contour["ctt_match_lt"].keys():
					#
					t_contour["ctt_match_lt"][_val_smp] = OrderedDict()
					#
					if 'sequences' not in t_contour["ctt_match_lt"][_val_smp].keys():
						#
						t_contour["ctt_match_lt"][_val_smp] = {"sequences":OrderedDict()}
						#
					#
				#
				points_a = CM.get_tc_points(t_contour,_val_smp)
				points_b = CM.get_tc_points(tc_inst_b[cont_inx],_val_smp)
				#
				points_a_f = flipCoordPath(points_a,False,True)
				points_b_f = flipCoordPath(points_b,False,True)
				#
				print("doing",intpair)
				#
				for _p in points_a_f:
					#
					conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,list(_p))
					#
					if conf_inx not in t_contour["ctt_match_lt"][_val_smp]["sequences"].keys():
						#
						t_contour["ctt_match_lt"][_val_smp]["sequences"][conf_inx] = []
						#
					#
					coord_ct = [item[1] for item in t_contour["confines_simp"][_val_smp][conf_inx]]
					#
					to_ctt = [
						[],
						[],
						[]
					]
					#
					to_ctt_m = [
						[],
						[],
						[]
					]
					#
					for x in t_contour["matching_best_area"][_val_smp]:
						#
						#
						if intpair == x['instance_pair']:
							#
							if x["pnt_crd"] == coord_ct[0]: # Pre
								#
								to_ctt[0].append(x["lt_crd"])
								to_ctt_m[0].append(x)
								#print("P",x["lt_crd"])
								#
							#
							if x["pnt_crd"] == coord_ct[1]: # Center
								#
								to_ctt[1].append(x["lt_crd"])
								to_ctt_m[1].append(x)
								#print("C",x["lt_crd"])
								#
							#
							if x["pnt_crd"] == coord_ct[2]: # Ante
								#
								to_ctt[2].append(x["lt_crd"])
								to_ctt_m[2].append(x)
								#print("A",x["lt_crd"])
								#
							#
					#
					# do standard clear operations
					#
					'''
					to_ctt_clean= [
						[],
						[],
						[]
					]
					#
					m_p = to_ctt[0].copy()
					m_c = to_ctt[1].copy()
					m_a = to_ctt[2].copy()
					#
					print("BESTAREA")
					best_p = sorted(to_ctt_m[0], key=lambda x: x["area"] )[0]["area"]
					best_a = sorted(to_ctt_m[2], key=lambda x: x["area"] )[0]["area"]
					print(best_a, best_p)
					#
					for c in m_c:
						#
						print("------------------")
						print(c)
						#
						for x in to_ctt_m[0]: # pre
							#
							if x["lt_crd"] == c:
								#
								print(x["area"], best_p)
								#
								if x["area"] > best_p:
									#
									print("----P")
									#print(x)
									print(c)
									print(m_c)
									#
									if c in to_ctt[1]:
										#
										print("REMOVE P", c)
										to_ctt[1].remove(c)
										#
									#
									break
									#to_ctt_clean[1].append(c)
									#
									#
							#
						#
						for x in to_ctt_m[2]: # ante
							#
							if x["lt_crd"] == c:
								#
								print(x["area"], best_a)
								#
								if x["area"] > best_a:
									#
									print("----A")
									#print(x)
									print(c)
									print(m_c)
									#
									if c in to_ctt[1]:
										#
										print("REMOVE A", c)
										to_ctt[1].remove(c)
										#
										break
										#
									#
									#to_ctt_clean[1].append(c)
									#
							#
						#
					#
					print("---->")
					print(to_ctt)
					#print(m_c)
					#to_ctt[1] = m_c
					#print(to_ctt_clean)
					#
					'''
					#pass_lines = []
					#
					#if intpair == [0,1]:
						
					pass_lines = test_seek_line(to_ctt, tc_inst_a, tc_inst_b, _val_smp, cont_inx)
					#
					new_match_b = {	
						"gpi":conf_inx,
						"pnt_crd":__point,
						"inx_ins":in_a,
						"inx_ins_opp":in_b,
						"inx_cnt":cont_inx,
						"plot_num":t_contour["plot_num"],
						"plot_num_opp":tc_inst_b[cont_inx]["plot_num"],
						"ctt_lt": to_ctt,
						#"best_sorted":sorted_all_match, # remove after proper certain target line implementation (probable line)
						#"seq_match":abs_sequence,
						#"point_seq":pnts,
						"lines": pass_lines,
						"instance_pair": [in_a, in_b]
					}
					#
					if new_match_b not in t_contour["ctt_match_lt"][_val_smp]["sequences"][conf_inx]:
						
						t_contour["ctt_match_lt"][_val_smp]["sequences"][conf_inx].append(new_match_b)

					#
					#
					
				#
				################################################################# END
				#



					# Get abstract point traces from CTT matches, store in tct format (P,C,A)
					#
					'''
					_x = 0
					for y in confine_from_coord:
						#
						local_pnt = y[2]
						#

						#
						got_seq_match = get_num_seq_from_ctt_matches(sorted_all_match,points_b)
						#
						tct_[_x] = got_seq_match
						per_ct[_x] = sorted_all_match
						#
						_x = _x + 1
						#
					#
					'''
					
					#
					#travel_sort(per_ct, tc_inst_a, tc_inst_b, __point, cont_inx, _val_smp, tgca_b, plt)
					
					
					# Attempt to make reasonable lines from all the (P,C,A) traces.
					'''
						NOT ENOUGH, NEEDS PRVIOUS VERSIONS TRAVEL DISTANCE SORT OR OTHER SOLUTION 
						TO CLIP POINTS THAT COME BACK AS GOOD CTT BUT ARE POSITIONED ON A LOOPING LINE
						
					'''
					#
					#abs_sequence = []
					#pnts = []
					#temp_rs_p = []
					
					#
					'''
					for x in tct_:
						#
						x_center = x[int(len(x)/2)]
						#
						for z in x:
							#
							
							#
							rs_p = rotate_center_clip(x, z, len(points_b)+1, clip_point_count-2)
							#
							temp_rs_p.append(rs_p)
							#
							#
						
							#print(x,rs_p)
					#
					blm_ct_multi = get_line_multi_ct_aggregate([temp_rs_p[0]],[temp_rs_p[1]],[temp_rs_p[2]])
					#
					get_agg = get_aggregate_line(blm_ct_multi, len(points_b), clip_point_count)
					#
					abs_sequence = get_agg[0]
					#
					# Get point coordinates for aggregate line
					#
					for gm in get_agg[0]:
						#
						pnts.append(fliped_points_b[gm-1])
						#
					#
					'''
					#
					
				#
			#
		#
	#
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
							contours[cnt]["matching"] = OrderedDict()
							contours[cnt]["matching_best_area"] = OrderedDict()
							contours[cnt]["simplified"] = OrderedDict()
							contours[cnt]["graphs"] = OrderedDict()
							contours[cnt]["confines"] = []
							contours[cnt]["confines_simp"] = OrderedDict()
							contours[cnt]["perp"] = []
							contours[cnt]["perp_simp"] = OrderedDict()
							contours[cnt]["recu"] = []
							contours[cnt]["recu_simp"] = OrderedDict()
							contours[cnt]["graphs_data"] = OrderedDict()
							contours[cnt]["ctt_match_lt"] = OrderedDict()
							contours[cnt]["ctt_match_seq"] = OrderedDict()
							#
							t_contour = contours[cnt]
							#
							points = np.asarray(contours[cnt]["coords"]["strt"])
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
										#try:
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
										_perp,_recu = make_ct_perp(coord_ct, cen_c, cfn)
										#
										contours[cnt]["perp"].append(_perp)
										temp_perp.append(_perp)
										contours[cnt]["recu"].append(_recu)
										temp_recu.append(_recu)
										#
								#
								#print(simp, len(temp_conf))
								#
								contours[cnt]["confines_simp"][simp] = temp_conf#contours[cnt]["confines"]
								contours[cnt]["perp_simp"][simp] = temp_perp#contours[cnt]["perps"]
								contours[cnt]["recu_simp"][simp] = temp_recu#contours[cnt]["perps_virt"]
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
#
intpl_list = get_instance_permutation()
#
# Solver
#
TreeGenerator(total_list, intpl_list, simplification)
#
TreeEvaluator(total_list, intpl_list, simplification)
#
# Post-Processor
#
ITD = IterDraw(total_list, GC, plt, simplification)
#
ITD.run()
#
#
'''
TreeGenerator is part of the solver it appears here because of drawing priority, for demonstration only.
As it contains the identification of the CT lines for each instance to run against the other instances and find 
points that are triangulated according to solver criteria.
'''
#
plt.show()
#
'''
Pre-Processor
	ContourHolder
		ContourNormalizer
	GraphConstructor
Solver
	TreeGenerator
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