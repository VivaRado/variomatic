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
run_specific = "X_"
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
max_radius = 300
clip_point_count = 7
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
		#confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate][0]
		#
		confine_from_coord_get = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate]
		if len(confine_from_coord_get) > 0:
			#
			confine_from_coord = confine_from_coord_get[0]
			#
			confine_index = t_contour["confines_simp"][simp_level].index(confine_from_coord)
			#
			return confine_index, confine_from_coord
		#
		else:
			#
			return False, False
			#
		#
	#
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
		
		#if _plt:
			#
		#	circl = plt.Circle(t_psca_coord, max_radius, color=_color[0], fill=False, alpha=0.5, lw=0.5)
			
		#	circl.set_radius(max_radius)
		#	circl.set_linestyle((0, (2,4)))
			
		#	ax.add_patch(circl)
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
						#if _plt:
							#
						#	pp1 = mpatches.ConnectionPatch(z[1][1],t_b_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
						#	pp1.set_linestyle((0, (2,4)))
						#	ax.add_patch(pp1)
						#	draw.draw_circle_on_coord(t_b_coord, ax, 2, "g")
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

# AKA Solver Number One
def TreeGenerator(instances, inst_intpl_lst, simp_levels):
	#
	inst_data = []
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
				try:
					

					gc_b = list(tc_inst_b[inst_inx]["graphs"][_val_smp].values())[-1]["coord"]
					#
					points_a = CM.get_tc_points(t_contour,_val_smp)
					points_b = CM.get_tc_points(tc_inst_b[cont_inx],_val_smp)
					#
					for p in points_a:#list(tc_inst_a["graphs"][0].values()):
						#
						__point = flipCoordPath([p],False,True)[0] # flipCoordPath accepts and returns list of points so need to pass list and to get 0
						#
						print('------------')
						print(__point, p)
						#
						try:
							
							conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,__point)
							#
							if conf_inx != False:
								
								#
								lt_p = t_contour["perp_simp"][_val_smp][conf_inx]
								#
								l_s = [conf_dat]
								#
								sta_a = lt_p[1][0]
								end_a = lt_p[1][1]
								sta_b = lt_p[1][2]
								end_b = lt_p[1][3]
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
								print(inst_inx)
								print(tc_inst_b[inst_inx]["graphs"][_val_smp])
								#
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
										"max_radius":		max_radius
										}
									#
									if _val_smp not in t_contour["matching"].keys():
										#
										t_contour["matching"][_val_smp] = []
										#
									#
									if new_match not in t_contour["matching"][_val_smp]:
										#
										t_contour["matching"][_val_smp].append(new_match)
										#
									#
							
						except Exception as e:
							
							pass
							#
							'''
						except Exception as e:
							#
							print('POINT MATCHING EXCEPTION')
							print(e)
							#
							pass
							#
							'''
				except Exception as e:
					print("graph exception")
					pass
					
				
						
				#
			#
		#
	#
#
def find_best_ctt(matches,smp,pnt):
	#
	result = []
	#
	for e in matches[smp]:
		if e["gpi"] == pnt:
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
		#
	#
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
'''
def psca_glif_line_inx(psca):
	#
	res = []
	#
	for x in psca:
		#
		res.append([y[1] for y in x])
		#
	#
	return res
	#
'''
#

def get_num_seq_from_ctt_matches(sorted_all_match, points_b):
	#
	#
	seq_points = []
	#
	for x in sorted_all_match:
		#
		
		#
		point_num = x['lt'][2]
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
		#print(graph_b_crd)
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
				#print("LENWISE CONTOURS")
				#print(tc_inst_b[in_b][_val_smp])
				#
				points_a = CM.get_tc_points(t_contour,_val_smp)
				points_b = CM.get_tc_points(tc_inst_b[cont_inx],_val_smp)
				#
				for p in points_a:#list(tc_inst_a["graphs"][0].values()):
					#
					__point = flipCoordPath([p],False,True)[0] # flipCoordPath accepts and returns list of points so need to pass list and to get 0
					#
					conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,list(__point))
					#
					if conf_inx != False:
						
						# for every confine point, get best matching opposite instance points 
						# pass to triangle matching
						# make probable line
						# collect cumulative probable lines for all levels of simplification
						#
						try:
							#
							confine_from_coord_get = [d for d in t_contour["confines_simp"][_val_smp] if d[1][1] == __point]
							if len(confine_from_coord_get) > 0:
								#
								confine_from_coord = confine_from_coord_get[0]
								#

								glyph_point_index = t_contour["confines_simp"][_val_smp].index(confine_from_coord)
								#
								#conf_inx, conf_dat = CM.tc_get_simp_conf_b_coord(t_contour,_val_smp,list(__point))
								#
								#print("confine from coord")
								#print(confine_from_coord)
								#
								tct_ = [
									[],
									[],
									[]
								]
								#
								_c = 0
								#
								for y in confine_from_coord:
									#
									local_pnt = y[2]
									#
									#print(local_pnt)
									#
									t_m = find_best_ctt(t_contour["matching"],_val_smp,local_pnt)
									#
									#sorted_all_match = sorted(t_m, key=lambda x: x['area']+x['pnt_dist_a'][0]+x['center_dist']+x['angle']+x['sm_point'])[:3]
									#sorted_all_match = sorted(t_m, key=lambda x: x['area']+x['pnt_dist_a'][0]+x['center_dist']+x['angle']+x['sm_point'])[:3]
									sorted_all_match = sorted(t_m, key=lambda x: x['area']+x['pnt_dist_a'][0]+x['center_dist']+x['angle']+x['sm_point'])[:2]
									#

									#
									got_seq_match = get_num_seq_from_ctt_matches(sorted_all_match,points_b)
									#
									#
									if _val_smp not in t_contour["ctt_match_lt"].keys():
										#
										t_contour["ctt_match_lt"][_val_smp] = {}
										#
									#
									if glyph_point_index not in t_contour["ctt_match_lt"][_val_smp].keys():
										#
										print("ADDING MATCHES")
										#
										t_contour["ctt_match_lt"][_val_smp][glyph_point_index] = {}
										t_contour["ctt_match_lt"][_val_smp][glyph_point_index]["matches"] = sorted_all_match # maybe is equating multiple times...
										
										t_contour["ctt_match_lt"][_val_smp][glyph_point_index]["sequences"] = [
											[],
											[],
											[]
										]
										#
									#
									if got_seq_match not in tct_[_c]:
										#
										#t_contour["ctt_match_lt"][_val_smp][_c].append(new_match)
										tct_[_c].append(got_seq_match)
										#
									#
									_c = _c + 1
									#
								#
								# update each confine item with matching target sequence
								#
								ct_t_m = get_psca_ct_target_matches(tct_)
								#
								_c = 0
								fliped_points_b = flipCoordPath(points_b,False,True)
								
								#
								for x in ct_t_m:
									#
									x_center = x[int(len(x)/2)]
									#
									rs_p = rotate_center_clip(x, x_center, len(points_b)+1, clip_point_count)
									#
									# new_match = {	
									# 	"gpi":glyph_point_index,
									# 	"inx_ins":in_a,
									# 	"inx_ins_opp":in_b,
									# 	"inx_cnt":cont_inx,
									# 	"plot_num":t_contour["plot_num"],
									# 	"plot_num_opp":tc_inst_b[cont_inx]["plot_num"],
									# 	"best_sorted":sorted_all_match, # remove after proper certain target line implementation (probable line)
									# 	"seq_match":rs_p
									# }
									pnts = []
									#
										
									#
									for gm in rs_p:
										#
										#
										pnts.append(fliped_points_b[gm-1])
										#
										#print("GOT PNTS")
										#print(pnts)
										#t_contour["ctt_match_lt"][_val_smp][glyph_point_index]["sequence_point_crd"] = pnts # maybe is equating multiple times...
									#
									#
									new_match_b = {	
										"gpi":glyph_point_index,
										"inx_ins":in_a,
										"inx_ins_opp":in_b,
										"inx_cnt":cont_inx,
										"plot_num":t_contour["plot_num"],
										"plot_num_opp":tc_inst_b[cont_inx]["plot_num"],
										#"best_sorted":sorted_all_match, # remove after proper certain target line implementation (probable line)
										"seq_match":rs_p,
										"point_seq":pnts
									}
									#
									#
									#if new_match_b not in t_contour["ctt_match_lt"][_val_smp][glyph_point_index]["sequences"][_c]:
										#
										#t_contour["confines_simp"][_val_smp][glyph_point_index][_c].append(new_match)
										#t_contour["ctt_match_lt"][_val_smp][_c] = new_match
									t_contour["ctt_match_lt"][_val_smp][glyph_point_index]["sequences"][_c] = new_match_b
										#
										#print("ADDING sequences")
										#print(new_match_b["seq_match"])
										#
									#
									_c = _c + 1
									#
							#
						except Exception as e:
							#
							print(e)
							print('TREE EVALUATOR EXCEPTION')
							#
							pass
							#
					else:
						#
						pass
						#t_confine = t_contour["confines_simp"][_val_smp][glyph_point_index]
						#
						#print(tc_inst_b)
						#
						#
					#
				#
				#print(t_contour["ctt_match_lt"][_val_smp])
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
						print(cont_counter)
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
							contours[cnt]["matching_best"] = OrderedDict()
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
											print(e)
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