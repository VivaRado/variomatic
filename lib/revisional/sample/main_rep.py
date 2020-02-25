# -*- coding: utf-8 -*-
#
import os
import math
import time
import json
import pprint
import difflib
import plistlib
import fontTools
import numpy as np
import collections
from pylab import *
from rdp import rdp
from tkinter import *
import networkx as nx
import itertools as it
from numpy import array
from copy import deepcopy
from ast import literal_eval
from threading import Thread
from fontParts.world import *
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from itertools import zip_longest
from itertools import combinations
import xml.etree.ElementTree as ET
from itertools import islice, chain
from collections import OrderedDict
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from networkx.readwrite import json_graph
from networkx.algorithms import isomorphism
from svgpathtools import parse_path as pt_parse_path
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
#
#
dir_path = os.path.dirname(os.path.realpath(__file__))
# for standalone (python3 ../main.py)
sys.path.insert(0, os.path.join(dir_path,'helpers'))
# for tests (python ../tests/test_advanced.py)
sys.path.insert(0, os.path.abspath(os.path.join(dir_path, '..', 'sample')))
#
from combine_log import combine_log
from helpers import helpers
from colors import tcolor
from pnt import *
from gpathwrite import *
import draw
from geom import *
from shapely_simp import *
from fitCurves import *
from simple_path import *
from svgPathPen import SVGPathPen
from svgpath2mpl import parse_path as mpl_parse_path
#
from glyph_strings import *
#
from contour_holder import ContourHolder
from graph_constructor import GraphConstructor
#
from argparse import ArgumentParser
#
#
parser = ArgumentParser()
parser.add_argument("-a", "--instance_a", dest="instance_a",
                    help="Source instance A", metavar="FILE")
parser.add_argument("-b", "--instance_b", dest="instance_b",
                    help="Source instance B", metavar="FILE")
parser.add_argument("-l", "--log_output", dest="log_output",
                    help="Output Directory", metavar="FILE")
parser.add_argument("-g", "--specific_glyph", dest="specific_glyph",
                    help="Run Specific Glyph", metavar="value")

parser.add_argument("-s", "--start_glyph_num", dest="start_glyph_num",
                    help="Start Glyph Number", metavar="value")
parser.add_argument("-e", "--end_glyph_num", dest="end_glyph_num",
                    help="End Glyph Number", metavar="value")
#
args = parser.parse_args()
#
#
hide_labels = True
#
color = ["red","blue"]
#
offset_y = 700
offset_x = 50
#
max_radius = 800 # initially important now obsolete and stable at a normal radius that encompasses almost the whole contour.
#
# important for precision, matching is better when the agnostic target line is bigger 
# if a letter is less than 7 points this must be adjusted to 5 with diff limit 3
clip_point_count = 7 
diff_limit = 3
#
'''

simplification seed

for simplification 0 to 7 most letters dont change much, but after that the letters change and get deformed.
It depends on the number of points but the general observation 
is that there should be more steps on the non deformed area than in the deformed

so 0,1,2,3,4,5,6,7 that is 8
and 10,11,12,13,14,15 that is 6

Observing where the most deformation happens would help to understand a seed
but i thing for most cases 0,7 with 10,15 would work ok.
The bigger the seed the longer it takes. 
You could run simplification [0,1] when testing

'''
#
'''
Known issues:

	* the contour sorting fails for non line travel distance sortable, 
	as it tries to calculate the travel distance, of each contour and sort.
	for example the inner part of the letter "O" from the outer, is a smaller travel distance
	in both instances. Where this is not true for glyphs like "=".
	A approximate position or centroid or barycentric of the contour points,
	in the glyphs will probably have to be taken into account.

	* if end start is in the uncertain lines, final green matching line doesn't visually close.

	* if triangle matching and inline check fails for uncertain lines... well there is no matching.
	
 	* at the moment there is no final line in a usable list, it is though plotted as green for certain and lime for uncertain basic_cleanup and match_uncertain_tris.
	
	* this script doesn't do curved bezier contour analysis, it does straight point position comparison across simplification levels. In further iterations we will improve to do bezier contour comparison.

	* as it doesn't do curved bezier contour analysis, there is a very small chance the certainty matching gives incorrect matching. But if this happens, there is a chance there are move issues than just that and those issues will be directly visible.

	* adding curved bezier contour analysis will result in 100% matching and cleanup. In respectfully similar contours. Do not expect this to work with two random letters, there is no morphing.

	* the script solves only two instances against each other, there is no multiple instance support at this moment.

	* this code needs a strong cleanup.

	* networkx should be removed.

'''
#
_simplification_seed = [0,1]#list(range(0,7))+list(range(10,15))# or [0,1,4,5,6,7,8,20,21]
#
#
start_simpl = 0
start_point = 0
#
debug = False
#
# Visualizing the Matching
#
show_travel_distance_a = False
show_triangle_matching_a = False
show_triangle_matching_b = False
show_triangle_matching_c = False
show_center_transfer_a = False
show_center_transfer_b = False
show_unc_triangle_matching_a = False
show_unc_triangle_matching_b = False
show_unc_triangle_matching_bar_c = False
show_unc_triangle_matching_d = False
show_unc_target_triangle_plots = False
show_unc_source_triangle_plots = False
show_unc_source_line_ends = True
show_unc_target_line_ends = True
show_uncertain_line_end_connections = False
show_uncertain_source_small_length = False
show_uncertain_target_small_length = False
show_uncertain_dashed_source = False
show_uncertain_dashed_target = False
#
show_low_uncertainty_lines = True
show_mid_uncertainty_lines = True
show_high_uncertainty_lines = False
#
#
def get_change(current, previous):
	if current == previous:
		return 0
	try:
		return (abs(current - previous) / previous) * 100.0
	except ZeroDivisionError:
		return float('inf')
		
def list_intersection(lst1, lst2): 
	#
	lst3 = [x for x in lst1 if x not in lst2]
	#
	return lst3 
#
def get_from_comb_plot(crd,cmb,inst):
	#
	if inst == 0:
		#
		opp_inst = 1
		#
	else:
		#
		opp_inst = 0
		#
	#
	for x in cmb:
		#
		if x[opp_inst] == crd:
			#
			return x[inst]
			#
		#
	#
#
def combine_gap_one_seq(seq_lists, strt_a, strt_b, comb_plot):
	#
	comb_list = []
	#
	sl_c = seq_lists.copy()
	#
	list_change = False
	#
	gap_mend = []
	#
	for idx,item in enumerate(seq_lists):
		#
		if idx+1 != len(seq_lists):
			#
			last_sq = sl_c[idx][-1]
			first_next_sq = sl_c[idx+1][0]
			#
			if last_sq + 1 == first_next_sq - 1:
				#
				#
				crd_s = strt_a[last_sq-1:first_next_sq]
				#
				t_inx_st = strt_b.index(get_from_comb_plot(crd_s[0],comb_plot,1))
				t_inx_nd = strt_b.index(get_from_comb_plot(crd_s[-1],comb_plot,1))+1
				#
				crd_t = strt_b[t_inx_st:t_inx_nd]
				#

				#
				if debug:
					#
					print("GETTING COORD RANGE SOURCE RANGE")
					print(last_sq)
					print(first_next_sq)
					#
					print("GETTING COORD RANGE SOURCE")
					print(crd_s)
					print(crd_t)
					print('-')
					pprint.pprint(strt_b)
					#
				if len(crd_s) == len(crd_t):
					#
					# Combine consistent len diff of one point
					#
					sl_c[idx].append(last_sq + 1)
					#
					gap_mend.append(last_sq + 1)
					#
					list_change = True
					#
					# update combiner plot
					comb_plot.insert(idx+1,[crd_s[1],crd_t[1],10,[last_sq+1,strt_b.index(crd_t[1])]])
					#
				
				# probable needed additional check:
				# if not equal but smaller or equal to 2 points in between, 
				# get the best one sided matching that is higher 
				# than the lowest match available in combplot from all connected items  points
			#
		#
	#
	flat_list = [item for sublist in sl_c for item in sublist]
	sl_c = get_seq(flat_list)
	#
	if debug:
		
		print("INITIAL SEQ LIST")
		pprint.pprint(seq_lists)
		#
		print("SLC")
		pprint.pprint(sl_c)
		#
		print("AFTER SAME LEN CHECK MEND AND MERGE")
		#
		print(sl_c)
		#
	#
	new_seq_lists = sl_c.copy()
	#
	for idx,item in enumerate(new_seq_lists):
		#
		if debug:
			#
			print("--")
			print(item)
			#
		#
		if idx != len(new_seq_lists)-1:
			#
			last_sq = sl_c[idx][-1]
			first_next_sq = sl_c[idx+1][0]
			#
			#
			if last_sq + 1 == first_next_sq - 1:
				#
				if debug:
					print("FOUND", last_sq + 1)
				#
				# Patch inconsistent len diff of one point
				#
				if len(comb_list)>0:
					#
					if idx == comb_list[-1][-1]:
						#
						#
						crd_s = strt_a[last_sq-1:first_next_sq]
						#
						t_inx_st = strt_b.index(get_from_comb_plot(crd_s[0],comb_plot,1))
						t_inx_nd = strt_b.index(get_from_comb_plot(crd_s[-1],comb_plot,1))+1
						#
						crd_t = strt_b[t_inx_st:t_inx_nd]
						#
					else:
						#
						comb_list.append( [idx,idx+1])
						#
						if debug:
							print("B", idx,idx+1)
						#
					#
				else:
					#
					comb_list.append( [idx,idx+1])
					#
					if debug:
						print("C", idx,idx+1)
					#
				#
			else:
				#
				comb_list.append([idx])
				#
				if debug:
					print("D", idx)
				#
			#
		else:
			#
			if idx not in [j for i in comb_list for j in i]:
				#
				comb_list.append([idx])
				#
				if debug:
					print("E", idx)
				#
			#	
		#
	#
	#
	comb_range = []
	#
	for x in comb_list:
		#
		if len(x) > 1:
			#
			comb_range.append([x[0],x[-1]])
			#
		else:
			#
			comb_range.append(x)
			#
		#
	#
	#
	sl_c_new = []
	#
	for t in comb_range:
		#
		if len(t)>1:
			#
			l = sl_c[t[0]:t[1]+1]
			#
			flat_list = [item for sublist in l for item in sublist]
			#
			sl_c_new.append(flat_list) 
			#
		else:
			#
			sl_c_new.append(sl_c[t[0]])
			#
	#
	#
	if debug:
		#
		print("AFTER COMB RANGE MERGE")
		print(sl_c_new)
		print("C LIST")
		print(comb_list)
		print("C RANGE")
		print(comb_range)
		print("C NEW")
		print(sl_c_new)
		print("C LIST")
		print(comb_list)
		print("C RANGE")
		print(comb_range)
		print("C NEW")
		print(sl_c_new)
		#
	#
	if len(sl_c_new) == 0:
		#
		if list_change == True:
			#
			return [new_seq_lists,gap_mend,comb_plot]
			#
		else:
			#
			return [seq_lists,gap_mend,comb_plot]
		#
	else:
		#
		return [sl_c_new,gap_mend,comb_plot]
		#

#
def check_point_order_on_line(keep_opp_points, vrm_data_a_a, vrm_data_a_b):
	m_inxs = []
	keep_opp_points_inline = []
	#
	for kp in keep_opp_points:
		#
		temp_inxs = []
		#
		for y in kp:
			#
			inst_a_p_crd = y[0]
			inst_b_p_crd = y[1]
			#
			inst_a_p_inx = vrm_data_a_a.index(inst_a_p_crd)
			inst_b_p_inx = vrm_data_a_b.index(inst_b_p_crd)
			#
			temp_inxs.append([inst_a_p_inx, inst_b_p_inx])
			#
		#
		m_inxs.append(temp_inxs)
		#
	#
	if debug:
		#
		print("INDEXES")
		pprint.pprint(m_inxs)
		#
	#
	_p = 0
	#
	for xs in m_inxs:
		#
		_c = 0
		#
		prev_inx_a = 0
		prev_inx_b = 0
		#
		tmp_keep = []
		#
		for y in xs:
			#
			#
			has_error = False
			#
			cur_inx_a = y[0]
			cur_inx_b = y[1]
			#
			if _c > 0:
				#
				if _c+1 < len(xs):
					#
					if debug:
						#
						print("HAS NEXT", y)
						#
					#
					prev_inx_a = xs[_c+1][0]
					prev_inx_b = xs[_c+1][1]
					#
					if (prev_inx_a > cur_inx_a and prev_inx_b < cur_inx_b) or (prev_inx_a < cur_inx_a and prev_inx_b > cur_inx_b):
						#
						linx_first_s = xs[0][0]+1
						linx_last_s = xs[-1][0]+1
						linx_first_t = xs[0][1]+1
						linx_last_t = xs[-1][1]+1
						#
						if debug:
								
							print(cur_inx_a+1)
							print(cur_inx_b+1)
							print("-")
							print(linx_first_s, linx_last_s)
							print(linx_first_t, linx_last_t)
							print("OUT OF LINE", y)
						#
						has_error = True
						#
					#
				#
				else:
					#
					if debug:
						#
						print('IS LAST', y)
						#
					#
				#
			#
			if has_error == False:
				#
				inst_a_p_inx = vrm_data_a_a[cur_inx_a]
				inst_b_p_inx = vrm_data_a_b[cur_inx_b]
				#
				tmp_keep.append([inst_a_p_inx, inst_b_p_inx])
				#
			#
			#
			_c = _c + 1
			#
		#
		keep_opp_points_inline.append(tmp_keep)
		#
		_p = _p + 1
		#
	#
	return keep_opp_points_inline
	#
#
def combiner(inst_s,inst_t, cax):
	# 
	s_grad_s = inst_s.matched
	#
	s_grad_t = inst_t.matched
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
		draw.draw_circle_on_coord(coord_s, cax, (certainty+1)/2, "b", True, False, '["g_s":'+str(c_s)+',"g_t":'+str(c_t)+',"coords":['+str(coord_s)+','+str(coord_t)+'],"certainty":'+str(certainty)+']')
		draw.draw_circle_on_coord(coord_t, cax, (certainty+1)/2, "r", True, False, '["g_s":'+str(c_t)+',"g_t":'+str(c_s)+',"coords":['+str(coord_t)+','+str(coord_s)+'],"certainty":'+str(certainty)+']')#'["g_s":'+str(c_t)+',"coords":'+str(coord_t)+',"certainty":'+str(certainty)+']')
		#
		_p = mpatches.ConnectionPatch( coord_s, coord_t,"data", lw=((certainty+1)*5)/20, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=2, alpha=0.5, color="b",label='Label')
		cax.add_patch(_p)
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
		draw.draw_circle_on_coord(coord_t, cax, (certainty+1)/2, "b", True, False, '["g_s":'+str(c_t)+',"g_t":'+str(c_s)+',"coords":['+str(coord_t)+','+str(coord_s)+'],"certainty":'+str(certainty)+']')
		draw.draw_circle_on_coord(coord_s, cax, (certainty+1)/2, "r", True, False, '["g_s":'+str(c_s)+',"g_t":'+str(c_t)+',"coords":['+str(coord_s)+','+str(coord_t)+'],"certainty":'+str(certainty)+']')
		#
		_p = mpatches.ConnectionPatch( coord_t, coord_s,"data", lw=((certainty+1)*5)/20, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=2, alpha=0.5, color="r",label='Label')
		cax.add_patch(_p)
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
	return certain_points
	#
#
def get_best_match(matches, crd, inx):
	#
	got_ms = []
	#
	for x in matches:
		#
		if x[inx+1] == crd:
			#
			got_ms.append(x)
			#
		#
	#
	return sorted(got_ms, key = lambda x: x[0])[0]
	#
#
#
def add_missing(lstlen, inx_s,crt_s):
	#
	total = []
	missing = []
	#
	for x in range(lstlen+1):
		#
		if x+1 in inx_s:
			#
			get_inx = inx_s.index(x+1)
			#
			total.append([inx_s[get_inx],crt_s[get_inx]])
			#
		else:
			#
			if x+1 > lstlen:
				pass
			else:

				total.append([x+1,0])
				missing.append([x+1])
			#
		#
	#
	return [total, missing]
	#
#
def certainty_limit(lst, len_points):
	#
	accepted = []
	rejected = []
	c = 0
	#
	inx_s = [item[0] for item in lst]
	crt_s = [item[1] for item in lst]
	#
	min_crt_s = min(crt_s)
	max_crt_s = max(crt_s)
	#
	#
	# Certainty limits
	cert_l = (((min_crt_s + max_crt_s) / 2) - len(_simplification_seed) / 3)
	cert_h = max_crt_s#cert_l * 3
	#
	print("MINMAX", min_crt_s, max_crt_s, "LOWEST L", cert_l, "HIGHEST G", cert_h)
	#
	for x in lst: 
		#
		if x[1]>= cert_l and x[1]<= cert_h: 
			#
			accepted.append([x[0], x[1]])
			#
		elif x[1]<= cert_l:
			#
			cur_pnt_inx = inx_s[c]
			#
			p_pnt = get_point_inx(len_points, c, 'p')
			a_pnt = get_point_inx(len_points, c, 'a')
			#
			#print(cur_pnt_inx, 'inx')
			#
			if p_pnt in crt_s and a_pnt in crt_s:
				#
				if crt_s[p_pnt] >= cert_l and crt_s[a_pnt] >= cert_l and crt_s[c] > min_crt_s:
					#
					if [x[0],x[1]] not in accepted:
						#
						accepted.append([x[0], x[1]])
						#
					#
				#
				else:
					#
					rejected.append([x[0], x[1]])
					#
				#
		#
		c+= 1 

	return [accepted,rejected]
#
#
def coord_key_name(coords):
	return ', '.join(str(inc) for inc in coords)
#
def do_rule_not_on_line(t_contents,l_t):
	#
	ignore_num = set()
	#
	difference = [x for x in t_contents if x not in l_t]
	#
	for z in difference:
		#
		ignore_num.add(z[2])
		#
	#
	return ignore_num
	#
#
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
#
def ev_psca_pos(itm, psca_ginx):
	#
	inx = 0
	#
	for x in psca_ginx:
		#
		if itm in x:
			#
			inx = inx + x.index(itm) + 1
			#
		#
	#
	return inx
	#
def line_agnostic_probable(seq,psca_ginx):
	#
	all_before = []
	#
	if 1 in seq:
		#
		tinx = seq.index(1)
		all_before = seq[:tinx]
		#
	#
	c_seq = seq.copy()
	#
	seq_sorted = sorted(c_seq)
	#
	res = [0] * len(c_seq)
	#
	for x in c_seq:
		#
		inx = c_seq.index(x)
		#
		res[inx] = res[inx] + ev_psca_pos(x, psca_ginx)
		#
	#
	res_init_inx = [] 
	#
	y = 0
	#
	for x in res:
		#
		if x != 0:
			#
			res_init_inx.append(c_seq[y])
			#
		#
		y = y + 1
		#
	#
	seq_lists = get_seq(res_init_inx)
	#
	biggest_line = max(seq_lists, key=lambda coll: len(coll))
	#
	return biggest_line
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
def get_agreements(_p, _ag_a):
	#
	ret_matching = []
	#
	for k,v in _ag_a.items():
		#
		#
		if v[0] == _p:
			#
			found_match = True
			#
			return v[1][0]
			#
		#
	#
def get_agreed(_p, _ag_a):
	#
	ret_matching = []
	#
	for k,v in _ag_a.items():
		#
		found_match = False
		#
		for x in v[1:]:
			#
			if found_match == False:
				#
				if [x[0][2],x[0][3]] == [_p[0],_p[1]]:
					#
					found_match = True
					#
					ret_matching.append(True)
					#
					return True
					#
				#
			#
		#
	#
	if len(ret_matching) == 0:
		#
		return False
		#
	#
#
def make_ct(to_ct, cen_c, ax, _plt):
	#
	perps = []
	#
	for coords in to_ct:
		#
		x = coords[0]
		y = coords[1]
		#
		_perp = getPerpCoord(cen_c[0], cen_c[1], x, y, 10000)
		#
		_perp_virtual = getPerpCoord(cen_c[0], cen_c[1], x, y, 50)
		#
		if _plt:
			
			pp1 = mpatches.ConnectionPatch(cen_c,[x,y],"data", lw=0.5, color="g")
			ax.add_patch(pp1)
			#
			prp1 = mpatches.ConnectionPatch([_perp_virtual[0],_perp_virtual[1]],[_perp_virtual[2],_perp_virtual[3]],"data",arrowstyle='<->,head_width=.15,head_length=.15', lw=0.5, color="g")
			prp1.set_linestyle((0, (8,2)))
			ax.add_patch(prp1)
			#

		#
		_perp_b = getPerpCoord(_perp[0],_perp[1],x,y, 10000)
		_perp_b_virtual = getPerpCoord(_perp[0],_perp[1],x,y, 50)
		#
		perps.append([[_perp[0],_perp[1]],[_perp[2],_perp[3]],[_perp_b[0],_perp_b[1]],[_perp_b[2],_perp_b[3]]])
		#
	#
	return perps
	#
#
def do_comparison( _f, per_ct, l_s, l_t, scp_s, ax, bax, iter_point, _plt, ignore_sgrad):
	#
	iter_line = scp_s[0]
	#
	_SC = l_s[1]
	_P = l_s[0]
	_A = l_s[2]
	#
	sc_c = _SC[1]
	#
	to_ct = [
		_P[1],
		_SC[1],
		_A[1]
	]
	#
	ctm_Pre = per_ct[0]
	ctm_SC = per_ct[1]
	ctm_SC_c = per_ct[1].copy()
	ctm_Ante = per_ct[2]
	#
	A_bar_orig = barycentric([_P[1],_SC[1],_A[1]])
	#
	if _plt:
		#
		poly = plt.Polygon([_P[1],_SC[1],_A[1]], color='r',alpha=0.5, linewidth=0.5)
		ax.add_patch(poly)
		#
	#
	triangle_comparison(_f, ax,bax,l_s, l_t, ctm_Pre,ctm_SC_c,ctm_Ante,to_ct, iter_point, A_bar_orig, _plt, ignore_sgrad)
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
	#
#
def get_point_line(coords, _c, _f, inum, points):
	#
	seq_points = set()
	#
	#
	for x in coords:
		#
		point_num = x[3]
		#
		seq_points.add(point_num)
		#
	#
	seq_points = sorted(list(seq_points))
	#
	seq_lists = get_seq(seq_points)
	scp = []
	#
	line_start_point = []
	#
	if inum == 1:
		#
		if len(seq_lists) != 0:
				
			#
			biggest_line = max(seq_lists, key=lambda coll: len(coll))
			#
			all_nums = sorted([j for i in seq_lists for j in i])
			#
			result = [element for element in coords if element[3] == all_nums[0]]
			#
			total_results = []
			#
			for a in coords:
				#
				if a not in total_results:
					#
					total_results.append(a)
					#
				#
			#
			for a in result:
				#
				if a not in total_results:
					#
					total_results.append(a)
					#
				#
			#
			sorted_total = sorted(total_results, key = lambda x: x[3])
			#
			#
			line_start_point = result[0][3]
			#
		#
	else:
		#
		line_start_point = coords[0][3]
		#
	#
	ignore_set = set()
	#
	return [scp,ignore_set]
	#
def get_next_num (i, coords):
	#
	if i == len(coords)-1:
		#
		return 0
		#
	else:

		return i
	#

def plot_line(tx, coords, _c, _plt):
	#
	i = 0
	#
	for x in coords:
		#
		#
		if i != len(coords)-1:
			#
			if _plt:
				#
				if i == len(coords) -2:
					#
					_width = '.5'
					_shrink = 2
					#
				else:
					#
					_width = '.15'
					_shrink = 7
					#
				#
				_p = mpatches.ConnectionPatch(x,coords[i+1],"data", lw=1, arrowstyle='->,head_width='+_width+',head_length='+_width, shrinkB=_shrink, color=_c)
				tx.add_patch(_p)
				#
			#
		#
		i = i + 1
		#
	#
#
def plot_certainty_line(tx, coords, _c, _plt):
	#
	i = 0
	#
	while i < len(coords)-1:
		#
		x = coords[i]
		#
		if _plt:
			#
			# show start point for matching
			if i == 0:
				#
				draw.draw_circle_on_coord(x[0], tx, 10, "green", False)
				draw.draw_circle_on_coord(x[1], tx, 10, "green", False)
				#
			#
			_p = mpatches.ConnectionPatch(midpoint(x[0], x[1]),midpoint(coords[i+1][0], coords[i+1][1]),"data", lw=2, alpha=0.5, color=_c)
			tx.add_patch(_p)
			#
			_p = mpatches.ConnectionPatch( x[0], x[1],"data", lw=2, alpha=0.5, color="purple", arrowstyle='<->,head_width=.15,head_length=.15', shrinkB=2,label='Label')
			tx.add_patch(_p)
			#
		#
		#
		i += 1
		#
	#
#
def plot_regular_line(tx, coords, _c, _plt):
	#
	i = 0
	#
	for x in coords:
		#
		if i != len(coords)-1:
			#
			if _plt:
				#
				_p = mpatches.ConnectionPatch(x, coords[i+1],"data", lw=1, alpha=0.5, color=_c,linestyle="--",arrowstyle='->,head_width=.15,head_length=.15', shrinkB=7)
				tx.add_patch(_p)
				#
			#
		#
		i = i + 1
		#
	#
#

def plot_region_line(tx, coords, _c, _plt):
	#
	i = 0
	first_ploted = False
	#
	coord_line = []
	#
	for x in coords:
		#
		#
		if i == len(coords)-1:
			pass
		else:
			#
			if _plt:
				#
				_p = mpatches.ConnectionPatch(x[1],coords[i+1][1],"data", lw=1, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=7, color=_c,label='Label')
				tx.add_patch(_p)
				#
			#
		#
		coord_line.append(x)
		#
		i = i + 1
		#
	#
	#
	return coord_line
	#
#
#
def get_point_inx(numpoints, num, loc): # confusion ensues
	#
	#
	if loc == "p":
		#
		if num == 0:
			#
			return numpoints
			#
		#
		else:
			#
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
		if num == 0:
			#
			return num + 1
			#
		#
		else:
			#
			if num == numpoints-1:
				#
				return 0
				#
			else:
				#
				return num + 1
				#
			#
		#
	#
#

def get_point_inx_line_b(numpoints, num, loc):
	#
	#
	if loc == "p":
		#
		#
		if num == 0:
			#
			#
			return 1
			#
		#
		else:
			#
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
				return 0
				#
			#
		#
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
def get_points_around(__point, points_a,points_b, l_s, a_items, b_items, ax, bax, _plt=False, _color=False):
	#
	#
	matched_target = []
	
	#
	center_a = points_a.get(a_items[-1])["coord"]
	#
	for z in l_s:
		#
		p_c = 0
		t_psca_coord = z[1]#points_b.get(a_items[p_c])["coord"]
		#
		if _plt:
			#
			#
			circl = plt.Circle(t_psca_coord, max_radius, color=_color[0], fill=False, alpha=0.5, lw=0.5)
			#
			circl.set_radius(max_radius)
			circl.set_linestyle((0, (2,4)))
			#
			ax.add_patch(circl)
		#
		found_p = False
		#
		for k,v in points_b.items():
			#
			#
			if k!=(0,0):
				#
				contains = False
				#
				c_rad = 0
				for x in range(max_radius):
					#
					t_circle = [t_psca_coord,c_rad]
					#
					t_b_coord = points_b.get(b_items[p_c])["coord"]
					t_b_order = points_b.get(b_items[p_c])["order"]
					#
					contains = in_circle(t_b_coord,t_circle)
					#
					if contains:
						#
						found_p = True
						#
						Path = mpath.Path
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
								pp1 = mpatches.ConnectionPatch(z[1],t_b_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
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
def evaluate_psca(_P,_SC,_A, iter_point):
	#
	__p = [c[0][1] for c in _P]
	__sc = [c[0][1] for c in _SC]
	__a = [c[0][1] for c in _A]
	#
	if debug:
		
		print ('\n'+tcolor.WARNING + "EVALUATE PSCA: " + tcolor.ENDC)
		pprint.pprint(__p)
		pprint.pprint(__sc)
		pprint.pprint(__a)
	#
	c_a__p = __p
	c_a__sc = __sc
	c_a__a = __a
	#
	incs = []
	#
	for x in __p:
		#
		for y in c_a__sc:
			#
			for z in c_a__a:
				#
				if x!=y and y!=z and z!=x:
					#
					if [x,y,z] not in incs:
						#
						incs.append([x,y,z])	
						#
					#
				#
				else:
					#
					pass
					#
				#
			#
	#
	return incs
	#
#
def move_tri(tri,move):
	#
	moved_tri = []
	#
	for t in tri:
		#
		moved_tri.append(list(np.array(t) - move))
		#
	#
	return moved_tri
	#
#
def get_order_by_coord(_coord, points):
	#
	for k,v in points.items():
		#
		t_a_coord = v["coord"]
		t_a_order = v["order"]
		#
		if _coord == t_a_coord:
			return t_a_order
		#
	#
def compare_match_tris_sgrad(_f, iter_coord, tris):
	#
	iter_point_s = _f.initial_coords_a.index(iter_coord) + 1
	#
	matched = _f.matched
	sgrad_tris = []
	#
	_m = []
	#
	for k,v in matched.items():
		#
		if debug:
			#
			print(iter_point_s, k)
			#
		#
		if k == iter_point_s:
			#
			_m_t = [item[1] for item in v]
			#
			_m_t = set(_m_t)
			#
			_m.append([k,_m_t])
		#
	#
	tri_ghost = []
	#
	for x in tris:
		#
		tri_inx = []
		#
		for y in x:
			#
			if y in _f.initial_coords_b:
				#
				edge_inx_t = _f.initial_coords_b.index(y) + 1
				#
				tri_inx.append(edge_inx_t)
			else:
				#
				edge_inx_s = _f.initial_coords_a.index(y) + 1
				#
				tri_ghost.append(x)
				#
			#
		#
		#
		for y in _m:
			#
			if tri_inx[1] in y[1]:
				#
				#
				sgrad_tris.append(x)
				#
			#
		#
	#
	return sgrad_tris + tri_ghost
	#

def triangle_comparison(_f, ax,bax,l_s,l_t,ctm_Pre,ctm_SC_c,ctm_Ante, to_ct, iter_point, A_bar_orig, _plt, ignore_sgrad):
	#
	# get the first 10
	#
	ctm_SC_c = sorted(ctm_SC_c, key=lambda x: x[2])[:10]
	#
	# limit triangles
	ev_psca = evaluate_psca(ctm_Pre,ctm_SC_c,ctm_Ante, iter_point)
	#
	# ADD TO EV PSCA
	#
	if debug:
		#
		print("TRIS FROM PLOTED")
		print("===============================")
		#
	#
	points_lt = [item[3] for item in l_t]
	ploted_permut = it.combinations(points_lt, 3)
	#
	#
	for x in ploted_permut:
		#
		if x not in ev_psca:
			#
			if debug:
				#
				print("ADDING",x,"TO EV PSCA")
				#
			#
			ev_psca.append(x)
			#
		#
	#
	#
	l1 = l_s[0][1]
	l2 = l_s[1][1]
	l3 = l_s[2][1]
	#
	# get triangle orientation
	#
	s_pa_mid = midpoint(l1,l3)
	s_ca_mid = midpoint(l2,l3)
	s_pc_mid = midpoint(l1,l2)
	#
	#
	s_pa_ang = get_angle_b(l1,l3)
	s_ca_ang = get_angle_b(l2,l3)
	#
	#
	s_ta_cpa = get_angle_b(l2,s_pa_mid)
	s_ta_pca = get_angle_b(l1,s_ca_mid)
	s_ta_acp = get_angle_b(l3,s_pc_mid)
	#
	# Get barycentric extended lengths for source
	#
	s_bl_cpa = distance(s_pa_mid,A_bar_orig)
	s_bl_pca = distance(s_ca_mid,A_bar_orig)
	s_bl_acp = distance(s_pc_mid,A_bar_orig)
	#
	#
	__p_coord = list(_f.m_instances[0]["graph_data"]["sort_by_length"].values())[iter_point]["coord"]
	#
	#
	if _plt:
		
		# draw.draw_circle_on_coord(s_pa_mid, ax, 2, "r")
		# draw.draw_circle_on_coord(s_ca_mid, ax, 2, "r")
		# draw.draw_circle_on_coord(s_pc_mid, ax, 2, "r")
		#
		if show_triangle_matching_b == True:
			#
			pp1 = mpatches.ConnectionPatch(l2,s_pa_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="w")
			ax.add_patch(pp1)
			pp1 = mpatches.ConnectionPatch(l1,s_ca_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="w")
			ax.add_patch(pp1)
			pp1 = mpatches.ConnectionPatch(l3,s_pc_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="w")
			ax.add_patch(pp1)
			#
			# Triangle Matching Markings

			draw.draw_circle_on_coord(l2, ax, 1, "k")
			draw.draw_circle_on_coord(s_pa_mid, ax, 1, "k")
			pp1 = mpatches.ConnectionPatch(l2,s_pa_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=1, color="k")
			ax.add_patch(pp1)

			draw.draw_circle_on_coord(l1, ax, 1, "k")
			draw.draw_circle_on_coord(s_ca_mid, ax, 1, "k")
			pp1 = mpatches.ConnectionPatch(l1,s_ca_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=1, color="k")
			ax.add_patch(pp1)

			draw.draw_circle_on_coord(l3, ax, 1, "k")
			draw.draw_circle_on_coord(s_pc_mid, ax, 1, "k")
			pp1 = mpatches.ConnectionPatch(l3,s_pc_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=1, color="k")
			ax.add_patch(pp1)
		#
	#
	match_triangles = []
	#
	ghost_triangles = []
	############################### 
	# Make Polygons from Target PSCA
	for x in ev_psca:
		#
		#
		tl1 = [s for s in l_t if x[0] == s[3]]
		tl2 = [s for s in l_t if x[1] == s[3]]
		tl3 = [s for s in l_t if x[2] == s[3]]
		#
		if debug:
			#
			print("FROM EV PSCA")
			print("===============================")
			print(tl1)
			print(tl2)
			print(tl3)
		#
		if len(tl1) != 0 and len(tl2) != 0 and len(tl3) != 0:
			#
			l_tl1 = tl1[0]
			l_tl2 = tl2[0]
			l_tl3 = tl3[0]
			#
			match_triangles.append([l_tl1[1],l_tl2[1],l_tl3[1]])
			#
			#
			# for y in _f.ghosts:
			# 	#
			# 	#tl1 = [s for s in l_t if x[0] == s[3]]
			# 	#tl3 = [s for s in l_t if x[2] == s[3]]
			# 	#
			# 	ghost_triangles.append([y,l_tl2[1],l_tl3[1]])
			# 	ghost_triangles.append([l_tl1[1],y,l_tl3[1]])
			# 	ghost_triangles.append([l_tl1[1],l_tl2[1],y])
	#
	if debug:
		#
		print("MATCH TRIANGLES")
		print("===============================")
		pprint.pprint(match_triangles)
		#
	#
	#match_triangles = match_triangles
	#
	cord_sc = to_ct[1]
	#
	match_polygons = []
	#
	############################### 
	# Make Polygons from Target PSCA
	for x in ev_psca:
		#
		#
		tl1 = [s for s in l_t if x[0] == s[3]]
		tl2 = [s for s in l_t if x[1] == s[3]]
		tl3 = [s for s in l_t if x[2] == s[3]]
		#
		#
		if len(tl1) != 0 and len(tl2) != 0 and len(tl3) != 0:
			#
			l_tl1 = tl1[0]
			l_tl2 = tl2[0]
			l_tl3 = tl3[0]
			#
			match_polygons.append([l_tl1[1],l_tl2[1],l_tl3[1]]) 
			match_polygons.append([l_tl3[1],l_tl1[1],l_tl2[1]]) # triangle spamming
			match_polygons.append([l_tl2[1],l_tl3[1],l_tl1[1]]) # triangle spamming
			#
			if _plt:
				#
				poly = plt.Polygon([l_tl1[1],l_tl2[1],l_tl3[1]], color='b',alpha=0.1, linewidth=0.5)
				bax.add_patch(poly)
			#

		#
	#
	dedupe_match_polygons = []
	#
	for t_tri in match_polygons:
		#
		if t_tri not in dedupe_match_polygons:
			#
			dedupe_match_polygons.append(t_tri)
			#
		#
	#
	dd_match_polygons = dedupe_match_polygons + ghost_triangles
	#
	match_final_polygons = dd_match_polygons
	#s_area = area([l1,l2,l3])
	if _plt:
		#
		match_final_polygons = compare_match_tris_sgrad(_f,__p_coord, dd_match_polygons)
	#
	match_barycentric = []
	#
	# if len(match_final_polygons) == 0:
	# 	#
	# 	draw.draw_circle_on_coord(l2, bax, 15, "orange")
	# 	#
	# 	match_final_polygons = dd_match_polygons
	# 	#
	#
	s_ord = _f.initial_coords_a.index(__p_coord) + 1
	#
	
	for t_tri in match_final_polygons:
		#
		now_bar = barycentric(t_tri)
		#
		A_bar_np = np.array(A_bar_orig)
		now_bar_np = np.array(now_bar)
		diff_bar = A_bar_np-now_bar_np
		#
		o_tri = [l1,l2,l3]
		s_tri = move_tri([l1,l2,l3], diff_bar)
		A_bar = move_tri([A_bar_orig], diff_bar)[0]
		#
		#
		# Get target triangle orientation
		# 
		t_pa_mid = midpoint(t_tri[0],t_tri[2])
		t_ca_mid = midpoint(t_tri[1],t_tri[2])
		t_pc_mid = midpoint(t_tri[0],t_tri[1])
		#
		t_ta_cpa = get_angle_b(t_tri[1],t_pa_mid)
		t_ta_pca = get_angle_b(t_tri[0],t_ca_mid)
		t_ta_acp = get_angle_b(t_tri[2],t_pc_mid)
		#
		#
		# Get barycentric extended lengths
		#
		t_bl_cpa = distance(t_pa_mid,now_bar)
		t_bl_pca = distance(t_ca_mid,now_bar)
		t_bl_acp = distance(t_pc_mid,now_bar)
		#
		# Draw triangle barycentric extended lines
		#
		if _plt:

			if show_triangle_matching_a == True:				

				pp1 = mpatches.ConnectionPatch(t_tri[1],t_pa_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
				bax.add_patch(pp1)
				pp1 = mpatches.ConnectionPatch(t_tri[0],t_ca_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
				bax.add_patch(pp1)
				pp1 = mpatches.ConnectionPatch(t_tri[2],t_pc_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
				bax.add_patch(pp1)
				#
				poly = plt.Polygon(s_tri, color='r',alpha=0.02, linewidth=0.5)
				bax.add_patch(poly)
				#
				#
				draw.draw_circle_on_coord(A_bar, bax, 2, "r")
				draw.draw_circle_on_coord(now_bar, bax, 1, "b")
				#
			if show_triangle_matching_c == True:		

				# Triangle Matching Markings
				draw.draw_circle_on_coord(t_tri[1], bax, 2, "k")
				draw.draw_circle_on_coord(t_pa_mid, bax, 2, "k")
				pp1 = mpatches.ConnectionPatch(t_tri[1],t_pa_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
				bax.add_patch(pp1)

				draw.draw_circle_on_coord(t_tri[0], bax, 2, "k")
				draw.draw_circle_on_coord(t_ca_mid, bax, 2, "k")
				pp1 = mpatches.ConnectionPatch(t_tri[0],t_ca_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
				bax.add_patch(pp1)

				draw.draw_circle_on_coord(t_tri[2], bax, 2, "k")
				draw.draw_circle_on_coord(t_pc_mid, bax, 2, "k")
				pp1 = mpatches.ConnectionPatch(t_tri[2],t_pc_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
				bax.add_patch(pp1)
			#
		#
		s_sc = o_tri[1]
		t_sc = t_tri[1]
		#
		cumulative_point_distance = distance(o_tri[0], t_tri[0]) + distance(o_tri[1], t_tri[1]) + distance(o_tri[2], t_tri[2])
		upsell_sgrad_occuring = 0
		#
		for k,v in _f.matched.items():
			#
			if k == s_ord:
				#
				p_t_m_o = most_occuring(v,1)
				got_point = get_point_inx_by_coord(t_sc, _f.initial_coords_b)
				#
				if debug:
					#
					print("MATCHED SGRAD CLEANUP")
					#
					print(__p_coord, p_t_m_o, k, s_ord, got_point, t_sc)
				#
				for x in p_t_m_o:
					#
					if x[0] == got_point:
						#
						#m_point = get_point_inx_by_coord(t_sc, _f.initial_coords_b)
						#
						upsell_sgrad_occuring = -(x[1] * 10)
						#
						if debug:
							#
							print(p_t_m_o, got_point, s_ord, upsell_sgrad_occuring)
					#
				#
			#
		#
		#
		if _plt:
			#
			pp1 = mpatches.ConnectionPatch(s_sc,t_sc,"data", lw=0.2, color="gray")
			bax.add_patch(pp1)
			#
		match_barycentric.append([
			match_final_polygons.index(t_tri),
			# barycentric extension angle and reverse
			abs(s_ta_cpa-t_ta_cpa),#get_angle_c(t_ta_cpa,s_ta_cpa), #  
			abs(s_ta_pca-t_ta_pca),#get_angle_c(t_ta_pca,s_ta_pca), #  
			abs(s_ta_acp-t_ta_acp),#get_angle_c(t_ta_acp,s_ta_acp), #  
			# barycentric extension length
			abs(s_bl_cpa-t_bl_cpa),
			abs(s_bl_pca-t_bl_pca),
			abs(s_bl_acp-t_bl_acp),
			#
			distance(A_bar,now_bar),			
			#
			cumulative_point_distance,
			upsell_sgrad_occuring
			#
			])
		#
		if _plt:
			for p in t_tri:
				#
				pp1 = mpatches.ConnectionPatch(now_bar,p,"data", lw=0.2, color="b")
				bax.add_patch(pp1)
			#
		#
	#
	diff_list = []
	#
	sorted_tri_orient = sorted(match_barycentric, key=lambda x: ((x[1] + x[2] + x[3])+(x[4] + x[5] + x[6] + x[7] + x[8]), x[9]) )# sort according to triangle orientation, get first 3
	#
	sorted_tri_sgrad = []
	#
	do_add = True
	#
	for y in sorted_tri_orient:
		#
		#
		if _plt:
			#
			if y[7] in ignore_sgrad:
				#
				do_add = False
				#
			
			if debug:
				#
				print("sorted_tris")
				print([l_tl1[1],l_tl2[1],l_tl3[1]])
				print(ignore_sgrad)
			#
		#
		sorted_tri_sgrad.append(y)
		#
	#
	if debug:
			
		pprint.pprint(ignore_sgrad)
		print('===============')
		pprint.pprint(sorted_tri_sgrad)
		print('===============')
		pprint.pprint(match_final_polygons)
		#
		
		#print("ALL GHOSTS", ghost_points)
		#
	#
	if len(sorted_tri_sgrad) > 0:
		#
		best_m = match_final_polygons[sorted_tri_sgrad[0][0]]
		#
		if _plt:

			poly = plt.Polygon([best_m[0],best_m[1],best_m[2]], color='b',alpha=0.5, linewidth=0.5)
			bax.add_patch(poly)
			#
		#check_not_ghost = check_coord_ghost(best_m[1], ghost_points)
		#
		#if check_not_ghost == False:
		#
		if _plt:

			draw.draw_circle_on_coord(best_m[1], bax, 20, "g")
		#
		got_point = get_point_by_coord(best_m[1], l_t)
		#
		#
		
		#__p_ord = #list(_f.m_instances[0]["graph_data"]["sort_by_length"].values())[iter_point]["order"]
		#
		#
		#t_ord = 0
		t_ord = _f.initial_coords_b.index(best_m[1]) + 1
		s_ord = _f.initial_coords_a.index(__p_coord) + 1
		#
		got_p = [__p_coord,best_m[1], t_ord ]#[[__point,got_point[2]],got_point]
		#
		if _plt == False:

			if s_ord in _f.matched.keys():
				#
				#print ("k_T")
				#
				if got_p not in _f.matched[s_ord]:
					#
					_f.matched_circles.append(got_p)
					#
				#
				_f.matched[s_ord].append([_f.current_simp, t_ord, __p_coord, best_m[1] ])
				#
			else:
				#print ("k_F")
				#
				_f.matched.update({s_ord:[[_f.current_simp, t_ord, __p_coord, best_m[1] ]]})
				#
			#
		
		#
		# else:
		# 	#
		# 	if _plt:

		# 		draw.draw_circle_on_coord(best_m[1], bax, 15, "purple")
		# 	#
	else:
		#
		if debug:
			#
			print("RETURNING BEST FROM CT")
			#
			#
			pprint.pprint(ctm_SC_c)
			#
		#
		best_m = ctm_SC_c[0][5]
		#
		t_ord = _f.initial_coords_b.index(best_m) + 1
		#
		got_p = [__p_coord,best_m, t_ord ]#[[__point,got_point[2]],got_point]
		#
		if _plt == False:

			if s_ord in _f.matched.keys():
				#
				#print ("k_T")
				#
				if got_p not in _f.matched[s_ord]:
					#
					_f.matched_circles.append(got_p)
					#
				#
				_f.matched[s_ord].append([_f.current_simp, t_ord, __p_coord, best_m[1] ])
				#
			else:
				#print ("k_F")
				#
				_f.matched.update({s_ord:[[_f.current_simp, t_ord, __p_coord, best_m[1] ]]})
				#
			#
		#
		if _plt:

			draw.draw_circle_on_coord(best_m, bax, 15, "orange")
		
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
def get_point_by_coord(coord, points):
	#
	is_ghost = False
	#
	for x in points:
		#
		targ = x[1]
		#
		if targ == coord:
			#
			return x
			#
		#
	#
#
#
def similiarity(L_1, L_2):
	L_1 = set(str(w) for w in L_1)
	L_2 = set(str(w) for w in L_2)

	to_match = L_1.difference( L_2)
	against = L_2.difference(L_1)
	for w in to_match:
		res = difflib.get_close_matches(w, against)
		if len(res):
			against.remove( res[0] )
	return (len(L_2)-len(against)) / (len(L_1))
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
	for x in range(_range):
		#
		cur_inx = coords.index(last_point)
		#
		get_moving_inx_p = get_point_inx_line_b(len(coords), cur_inx, _dir)
		#
		pre_p_inx_n = next(c for c in coords if coords.index(c) == get_moving_inx_p)
		#
		gathered_coords.append(pre_p_inx_n)
		#
		last_point = pre_p_inx_n
		#
		if move_until != False:
			#
			if pre_p_inx_n == move_until:
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
	return [gathered_coords, gathered_inx]
	#
#

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
		try:
			#
			#
			get_moving_inx_p = get_point_inx_line_b(len(coords), y[0], _dir)
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
#
#
def get_trace_from_inx(inx, coords):
	#
	return coords.index(inx)
	#
#
def get_distance_from_trace(_f, p_coords, t_match, __cent_b,bax,_plt):
	#
	_f.initial_coords_a = _f.m_instances[0]["coords"]["graph"]
	_f.initial_coords_b = _f.m_instances[1]["coords"]["graph"]
	#
	got_point = get_point_inx_by_coord(p_coords, _f.initial_coords_a)
	#
	checkrange = []
	#
	# Get two steps forward and two steps back for every ctm match for per_ct item (t_match)
	s_pre = get_coord_range(_f.initial_coords_a, p_coords, 2, "p")
	
	s_ant = get_coord_range(_f.initial_coords_a, p_coords, 2, "a")
	
	#
	#
	#
	# See if those coordinates have been matched
	#
	t_match_pre = []
	t_match_ant = []
	#
	for sp in s_pre[1]:
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
	for x in _f.initial_coords_b:
		#
		t_p = get_point_inx_by_coord(x, _f.initial_coords_b)
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
			trace_coords_p.append([mtp[0],_f.initial_coords_b[mtp[0]-1]])
			#
		#
		t_coords_p = get_coord_range_finder(got_match, trace_coords_p, _f.initial_coords_b, "p", __cent_b, bax,_plt)
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
			trace_coords_a.append([mtp[0],_f.initial_coords_b[mtp[0]-1]])
			#
		#
		t_coords_a = get_coord_range_finder(got_match, trace_coords_a, _f.initial_coords_b, "a", __cent_b, bax,_plt)
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
#
def do_ct_sort(_f, __point,to_ct,perps_plot, lt_p,ax,bax, _plt, travel_sort = False):
	#
	#
	_b_instance = _f.m_instances[1]
	#
	__cent_b = list(_b_instance["graph_data"]["sort_by_length"].values())[-1]["coord"]
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
			t_b_dist = int(math.hypot(cts[0]-pnt_dist_b[1][0], cts[1]-pnt_dist_b[1][1]))
			#
			#
			t_a_dist = math.hypot(cts[0]-lt_x, cts[1]-lt_y)
			t_b_c_dist = math.hypot(__cent_b[0]-lt_x, __cent_b[1]-lt_y)
			t_a_c_dist = math.hypot(__cent_b[0]-cts[0], __cent_b[1]-cts[1])
			#
			pnt_dist_a = list(pnt_dist_a)
			#
			pnt_dist_a.insert(1, t_a_dist)
			#
			pnt_dist_a = tuple(pnt_dist_a)
			#
			_area = area([[cts[0],cts[1]],pnt_dist_a[2],[lt_x,lt_y]])
			#
			center_m_point = distance([__cent_b[0], __cent_b[1]],[lt_x,lt_y])
			center_s_point = distance([__cent_b[0], __cent_b[1]],__point)
			sm_point = distance([lt_x,lt_y],__point)
			#
			m_angle = get_angle_b([__cent_b[0], __cent_b[1]],[lt_x,lt_y])
			s_angle = get_angle_b([__cent_b[0], __cent_b[1]],__point)
			#
			
			#
			new_match = [
				(lt[2],lt[3]), 
				pnt_dist_a, #
				_area,
				_area,
				[cts[0],cts[1]], 
				[lt_x,lt_y], #
				t_b_dist,
				abs(abs(t_b_c_dist) - abs(t_a_c_dist)),
				abs(center_m_point - center_s_point),
				abs(m_angle-s_angle),
				sm_point,
				_area+pnt_dist_a[0]+abs(center_m_point - center_s_point)+abs(m_angle-s_angle)+sm_point
				]
			#
			#
			if new_match not in all_match:
				#
				all_match.append(new_match)
				#
			#
			if _plt:
				#
				if show_center_transfer_b == True:
						
					prp1 = mpatches.ConnectionPatch([lt_x, lt_y],[pnt_dist_a[2][0],pnt_dist_a[2][1]],"data", lw=0.2, color="r")
					#
					ax.add_patch(prp1)	
					#
					prp1 = mpatches.ConnectionPatch([lt_x,lt_y],__point,"data", lw=1, color="k")
					#
					ax.add_patch(prp1)	
			#
		#
		sorted_all_match = sorted(all_match, key=lambda x: x[3]+x[1][0]+x[8]+x[9]+x[10])[:3]
		#
		#
		for x in sorted_all_match:
			#
			#
			l1 = x[4]
			l2 = x[1][2]
			l3 = x[5]
			#
			if _plt:
				#
				poly = plt.Polygon([l1,l2,l3], color='g',alpha=0.1)
				ax.add_patch(poly)
				#
				dst1 = mpatches.ConnectionPatch([cts[0], cts[1]],[x[1][0],x[1][1]],"data", lw=0.4, color="g")
				#
				ax.add_patch(dst1)
			#
		#
		per_ct.append(sorted_all_match)
		#
		c = c + 1
		#
	if travel_sort == True:
		#
		if debug:
			#
			print("===")
			pprint.pprint(per_ct)
			#
		closest_travel_p = []
		closest_travel_sc = []
		closest_travel_a = []
		#
		for x in per_ct[0]:
			#
			dist_trace = get_distance_from_trace(_f,__point, x[0], __cent_b,bax,_plt )
			#
			closest_travel_p.extend(dist_trace)
			#
			if debug:
				#
				print("TRAVEL T DISTANCE TRACE", dist_trace)
		#
		for x in per_ct[1]:
			#
			dist_trace = get_distance_from_trace(_f,__point, x[0], __cent_b,bax,_plt )
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
			dist_trace = get_distance_from_trace(_f,__point, x[0], __cent_b,bax,_plt )
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
		return [per_ct, [sord_p_unq,sord_sc_unq, sord_a_unq]]
		#
	else:
		#
		return per_ct
		#
		
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
			per_ct_points[y].append(z[0])
			#
		#
		y = y + 1
		#
	#
	return per_ct_points
	#
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
#
def get_limits(_lst):
	#
	_min = min(_lst)
	_max = max(_lst)
	#
	return [_min, _max]
#

def get_points_glif_sorted(points_b, b_items, __point):
	#
	points_glif_sorted = []
	#
	p_d = 0
	#
	for k,v in points_b.items():
		#
		if k!=(0,0):
			#
			t_a_coord = points_b.get(b_items[p_d])["coord"]
			t_a_order = points_b.get(b_items[p_d])["order"]
			#
			t_a_dist = math.hypot(t_a_coord[0]-__point[0], t_a_coord[1]-__point[1])
			#
			points_glif_sorted.append([t_a_dist,t_a_coord,p_d, t_a_order])
			#
			p_d = p_d + 1
		#
	#
	points_glif_sorted = sorted(points_glif_sorted, key=lambda x: x[3])
	#
	return points_glif_sorted
	#
#
def get_points_agg_based(glif_sorted, agg):
	#
	points_agg_sorted = []
	#
	for y in agg:
		#
		match = [x for x in glif_sorted if x[3] == y][0]
		#
		match.append("real")
		#
		points_agg_sorted.append(match)
		#
	#
	return points_agg_sorted
	#
#
def get_coord_from_inst(_f, inst):
	#
	_inst = _f.m_instances[inst]["graph_data"]["sort_by_length"]
	#
	_items = []
	#
	_sort_order = OrderedDict(sorted(_inst.items(), key=lambda x: x[1]['order']))
	#
	i = 1
	#
	for k,v in _sort_order.items():
		#
		if k!=(0,0):
			#
			_items.append([i,v["coord"]])
			#
			#
			i = i + 1
			#
	#
	#_items.reverse()
	#
	return _items
	#
#
def test_line_sgrad(_f, to_ct, abs_best_line):
	#
	a_items = get_coord_from_inst(_f, 0)
	b_items = get_coord_from_inst(_f, 1)
	#
	if debug:
			
		print("--0----")
		print(to_ct)
		print(abs_best_line)
		print("A")
		pprint.pprint(a_items)
		print("B")
		pprint.pprint(b_items)
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
def merge_order_unique(a,b):
	#
	m_a = min(a)
	m_b = min(b)
	#
	if m_a > m_b:
		#
		iter_l = b
		iter_m = a
		#
	else:
		#
		iter_l = a
		iter_m = b
		#
	#
	return merge_overlap(iter_l,iter_m)
	#
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
def compare_sgrad(_f, s_c):
	#
	t_m_o = []
	#
	for k,v in _f.matched.items():
		#
		if k == s_c[1]:
			#
			t_m_o = most_occuring(v,1)
			#
			#
		#
	#
	ignore_list_tot = []
	#
	for k,v in _f.matched.items():
		#
		#print ( "CHECK", k )
		#
		_k = k
		#
		if _k != s_c[1]:
			#
			all_content = [el[1] for el in v]
			#
			#ignore_list_a = []
			#
			for x in t_m_o:
				#
				if x[0] in all_content:
					#
					#
					x_m_o = most_occuring(v, 1)
					#
					cont_t = [el[0] for el in t_m_o]
					cont_x = [el[0] for el in x_m_o]
					#
					#
					intx = [list(x) for x in set(tuple(x) for x in cont_t).intersection(set(tuple(x) for x in cont_x))]
					#
					all_intx = []
					#
					#
					for z in intx: # might be more? no chances if it has multiple intersections, solving for multiple.
						#
						val_t_m_o = []
						val_x_m_o = []
						#
						for _i in t_m_o:
							#
							if _i[0] == z:
								#
								val_t_m_o = _i[1] - (len(cont_t) - 1) # devaluate mixed by least occuring len
								#
								#s_c[1].append(val_t_m_o)
								#
								all_intx.append([s_c[1], val_t_m_o, z])
								#
							#
						#
						for _i in x_m_o:
							#
							if _i[0] == z:
								#
								val_x_m_o = _i[1]
								#
								#_k.append(val_t_m_o)
								#
								all_intx.append([_k, val_x_m_o, z])
								#
							#
						#
					#
					all_intx.sort(key = lambda x: x[1], reverse=True)
					#
					most_accurate = all_intx[0]
					#

					if s_c[1] != most_accurate[0]:
						#
						#
						ignore_list = [el[2] for el in all_intx[1:]]
						#
						#
						ignore_list_tot.extend(ignore_list)
						#
					#
				#
			#
		#ignore_list_tot.append(ignore_list_a)
	if debug:
		#
		print("------------------ IGNORE SINCE BETTER MATCH EXISTS")
		print(ignore_list_tot)
		#
	return ignore_list_tot
	#
#
def do_rad_search(_f, _a_instance, _b_instance, iter_point, _plt=False, _color=False):
	#
	#
	points_a = _a_instance["graph_data"]["sort_by_length"]
	points_b = _b_instance["graph_data"]["sort_by_length"]
	__point = list(_a_instance["graph_data"]["sort_by_length"].values())[iter_point]["coord"]
	#

	#
	if _plt:
		#
		plots = draw.init_plots(_plt, _f.plt_num)
		#
		if debug:
			#
			print('PLOT NUMS')
			print(_f.plt_num)
		#
		_f.plots = plots
		#
		ax = plots[0]
		bax = plots[1]
		#
		draw.draw_points_b(points_b,__point,_color,ax)
		draw.draw_circle_on_coord(__point, ax, 15, "g", False)
		#
	else:
		#
		ax = False
		bax = False
		#
	#
	a_items = []
	b_items = []
	#
	for k,v in points_a.items():
		#
		a_items.append(k)
		#
	#
	for k,v in points_b.items():
		#
		if k!=(0,0):
			#
			b_items.append(k)
			#
		#
	#
	if _plt:
		p_d = 0
		for k,v in points_a.items():
			#
			if k!=(0,0):
				t_a_coord = points_a.get(a_items[p_d])["coord"]
				#
				draw.label(t_a_coord, repr(t_a_coord), ax)
				#
				p_d = p_d + 1
				#
		p_d = 0
		for k,v in points_b.items():
			#
			if k!=(0,0):
				t_a_coord = points_b.get(b_items[p_d])["coord"]
				#
				draw.label(t_a_coord, repr(t_a_coord), bax)
				#
				p_d = p_d + 1
				#
	#
	matched_target = []
	matched_source = []
	#
	if _plt:
		#
		draw.draw_circle_on_coord(__point, ax, 15, "g", False)
		#
	#
	f_p_x = __point[0]
	f_p_y = __point[1]
	#
	t_fnl_d = max_radius#math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) + 50 # target_first_and_last_distance
	#
	p_d = 0
	for k,v in points_a.items():
		#
		if k!=(0,0):
			#
			t_a_coord = points_a.get(a_items[p_d])["coord"]
			t_a_order = points_a.get(a_items[p_d])["order"]
			#
			t_circle = [t_a_coord,t_fnl_d]
			#
			#
			contains = in_circle(__point,t_circle)
			#
			if contains:
				#
				t_a_dist = math.hypot(t_a_coord[0]-__point[0], t_a_coord[1]-__point[1])
				#
				matched_source.append([t_a_dist,t_a_coord,p_d, t_a_order])
				#
			p_d = p_d + 1
		#
	#
	ignore_num = set()
	#rule_check_exists_better = set()
	rule_check_line_match = set()
	#
	scp_s = [[],set()]
	scp_t = [[],set()]
	#
	#
	# sorted by length number
	ms_pn_s = sorted(matched_source, key = lambda x: x[3])
	#
	dist = lambda x, y: (x[1][0]-y[1][0])**2 + (x[1][1]-y[1][1])**2
	#
	f_s = next(c for c in ms_pn_s if c[2] == iter_point)
	#
	ignore_sgrad = []
	#
	if _plt:
		#
		print ('\n'+tcolor.WARNING + "COMPARE TO SGRAD" + tcolor.ENDC)
		#
		ignore_sgrad = compare_sgrad(_f, f_s)
		#
	#
	f_pre = next(c for c in ms_pn_s if c[3] == get_point_inx_line(len(points_a), f_s[3], "p"))
	f_ant = next(c for c in ms_pn_s if c[3] == get_point_inx_line(len(points_a), f_s[3], "a"))
	#
	s_ip_inx = ms_pn_s.index(f_s)
	#
	l_s = [f_pre,f_s,f_ant]
	#
	points_arr = get_points_around(__point,points_a,points_b,l_s, a_items, b_items, ax, bax,_plt, _color)
	#
	l_t = points_arr
	#
	l_t = rotate_points(l_t, len(b_items))
	#
	for p in l_t:
		#
		p.append("real")
		#
	#
	#
	#
	_SC = l_s[1]
	_P = l_s[0]
	_A = l_s[2]
	#
	
	cen_a = list(points_a.items())[-1]
	cen_c = cen_a[1]["coord"]
	sc_c = _SC[1]
	#
	to_ct = [
		_P[1],
		_SC[1],
		_A[1]
	]
	#
	#
	perps_plot = make_ct(to_ct, cen_c, ax, _plt)
	#
	scp_s = [[f_pre[3],f_s[3],f_ant[3]],set()]
	#
	plot_region_line(ax, l_s, "r", _plt)
	#
	init_ct_sort = do_ct_sort(_f,__point, to_ct,perps_plot, l_t,ax,bax, _plt, True)
	per_ct_ng = init_ct_sort[0]

	if _plt:
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
		if debug:
			#
			pprint.pprint(c_per_ct[1])
			print("===> NEW SC CT")
			pprint.pprint(new_tct[1])
			#
		#
		per_ct_ng = new_tct
		#
	#
	ct_t_m = get_psca_ct_target_matches(per_ct_ng)
	#
	if debug:
		#
		print ('\n'+tcolor.WARNING + "PSCA TARGET MATCHES FOR CT" + tcolor.ENDC)
		pprint.pprint(ct_t_m)
		#
	#
	seq_points = []
	#
	#
	for x in l_t:
		#
		point_num = x[3]
		#
		seq_points.append(point_num)
		#
	#
	seq_lists = get_seq(seq_points)
	#
	rotated_seq = rotate_points([],len(a_items),seq_lists)
	rot_seq = sorted(rotate_points([],len(a_items),seq_lists))
	psca_m_ginx = psca_glif_line_inx(ct_t_m)
	#ag_prob = line_agnostic_probable(rotated_seq,psca_m_ginx)
	#
	rs_p = rotate_center_clip(rotated_seq, ct_t_m[0][0][1], len(b_items)+1, clip_point_count)
	rs_p_b = rotate_center_clip(rotated_seq, ct_t_m[0][1][1], len(b_items)+1, clip_point_count)
	rs_p_c = rotate_center_clip(rotated_seq, ct_t_m[0][2][1], len(b_items)+1, clip_point_count)
	
	rs_sc = rotate_center_clip(rotated_seq, ct_t_m[1][0][1], len(b_items)+1, clip_point_count)
	rs_sc_b = rotate_center_clip(rotated_seq, ct_t_m[1][1][1], len(b_items)+1, clip_point_count)
	rs_sc_c = rotate_center_clip(rotated_seq, ct_t_m[1][2][1], len(b_items)+1, clip_point_count)
	
	rs_a = rotate_center_clip(rotated_seq, ct_t_m[2][0][1], len(b_items)+1, clip_point_count)
	rs_a_b = rotate_center_clip(rotated_seq, ct_t_m[2][1][1], len(b_items)+1, clip_point_count)
	rs_a_c = rotate_center_clip(rotated_seq, ct_t_m[2][2][1], len(b_items)+1, clip_point_count)
	#
	#
	if debug:
		#
		print ('\n'+tcolor.WARNING + "BEST TARGET LINE" + tcolor.ENDC)
		#
		print('BEST LINE PRE')
		print(rs_p)
		print('a')
		print(rs_p_b)
		print('b')
		print(rs_p_c)

		print('BEST LINE SC')
		print(rs_sc)
		print('a')
		print(rs_sc_b)
		print('b')
		print(rs_sc_c)

		print('BEST LINE ANTE')
		print(rs_a)
		print('a')
		print(rs_a_b)
		print('b')
		print(rs_a_c)
	#
	#
	blm_ct_multi = get_line_multi_ct_aggregate([rs_p,rs_p_b,rs_p_c],[rs_sc,rs_sc_b,rs_sc_c],[rs_a,rs_a_b,rs_a_c])
	#
	#
	get_agg_ct_multi = get_aggregate_line(list(blm_ct_multi), len(points_b), clip_point_count)
	#
	# Get Absolute best line aggregate
	#
	blm = [
		rs_p,
		rs_sc,
		rs_a
	]
	#
	get_agg = get_aggregate_line(blm, len(points_b), clip_point_count)
	#
	if _plt:
		
		if debug:
				
			print ('\n'+tcolor.OKGREEN + "BEST TARGET CT AGGREGATE LINE" + tcolor.ENDC)
			print(get_agg_ct_multi[0])
			print ('\n'+tcolor.OKGREEN + "BEST TARGET CT LINE" + tcolor.ENDC)
			print(get_agg[0])
	#
	if get_agg[0] != get_agg_ct_multi[0]:
		#
		abs_best_line = merge_order_unique(get_agg[0],get_agg_ct_multi[0])

		if debug:
				
			print ('\n'+tcolor.WARNING + "BEST LINE COMB PRECLIP" + tcolor.ENDC)
			print(abs_best_line)

		#
		if _plt:
			if debug:
					
				print ('\n'+tcolor.WARNING + "BEST LINE COMB" + tcolor.ENDC)
				print(abs_best_line)
		#
	#
	else:
		#
		abs_best_line = get_agg[0]
		#
	#
	#
	blm_test_sgrad = test_line_sgrad(_f,to_ct,abs_best_line)
	#
	if _plt:

		if debug:
			#
			print ('\n'+tcolor.OKGREEN + "ABSOLUTE BEST LINE" + tcolor.ENDC)
			print(abs_best_line)
			#
	#
	# Get graph points and order them as glif points
	#
	p_g_s = get_points_glif_sorted(points_b, b_items, __point)
	#
	# Get glif ordered points and create aggregate line coords according to best line
	#
	# Plot Aggregate according to best line
	p_agg = get_points_agg_based(p_g_s, get_agg[0])
	#
	if _plt:
		#
		lt_agg_ploted = plot_region_line(bax, p_agg, "b", _plt)
		#
	#
	#
	if _plt:
		
		if debug:
			#
			print ('\n'+tcolor.OKGREEN + "ABSOLUTE BEST LINE PLOTED" + tcolor.ENDC)
			pprint.pprint(lt_agg_ploted)
			#
	#
	per_ct = do_ct_sort(_f, __point, to_ct, perps_plot, l_t, ax,bax, _plt, False)
	#
	seq_points = []
	#
	do_l_check = do_comparison( _f, per_ct, l_s, p_agg, scp_s, ax, bax, iter_point, _plt, ignore_sgrad)
	#
	# get current node number lengthwise
	points_a = _a_instance["graph_data"]["sort_by_length"]#[1:]
	new_dict = [a for a, b in points_a.items() if __point == b["coord"]][0]
	#
#

def get_glif_coord(f_g, _type):
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
					p_arr.append([round(float(point.x+offset_x),1), round(float(point.y-offset_y),1)])
					#
			#
			else:
				#
				p_arr.append([round(float(point.x+offset_x),1), round(float(point.y-offset_y),1)])
				#

		#
	#
	return p_arr
	#
#
def make_glyph(_g_dat,_name):
	#
	_let = _name
	f = NewFont()
	g = f.newGlyph(_let)
	pen = g.getPointPen()
	glyph_result = readGlyphFromString(_g_dat, glyphObject=g, pointPen=pen)
	#
	f_g = f[_let]
	#
	return f_g
	#
#
def bez_to_list(coords=False):
	#
	do_coords = coords
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
class vrmstart():

	def __init__(self, g_data_a, g_data_b, plt_num, cont_num):
		super(vrmstart, self).__init__()
		self.made_letters = {}
		self.m_instances = {}
		self.g_data_a = g_data_a
		self.g_data_b = g_data_b
		self.plt_num = plt_num
		self.agreed_matches = collections.OrderedDict()
		self.sgrad = collections.OrderedDict()
		self.cont_num = cont_num
		
	#
	#
	def make_instances(self):
		#
		c = 0
		for x in [self.g_data_a, self.g_data_b]:
			#
			root = ET.fromstring(x)
			#
			g_name = root.attrib['name']
			#
			made_g = make_glyph(x,g_name)
			#
			for contour in made_g:
				#
				if contour.clockwise == False:
					#
					contour.reverse()
					#
				#
			#
			made_g.update()
			#
			g_strt_coord = get_glif_coord(made_g, 'corner')
			g_coord_flip = flipCoordPath(g_strt_coord,False,True)
			x_mm = value_mid(g_coord_flip, 0)
			y_mm = value_mid(g_coord_flip, 1)
			#
			self.made_letters[c] = {
				"glyph":made_g,
				"box": [x_mm, y_mm],
				"inst":c,
				"coords":{
					"orig": None,
					"strt": None,
					"graph": None
					},
				"graph":None,
				"graph_json":{},
				"agreed":{},
				"surfaced":{}
			}
			#
			c = c + 1
			#
		#
		get_box_diff_x = self.made_letters[0]["box"][0] - self.made_letters[1]["box"][0]
		get_box_diff_y = self.made_letters[0]["box"][1] - self.made_letters[1]["box"][1]
		#
		#
		d = 0
		for let, val in self.made_letters.items():
			#
			f_g = self.made_letters[d]["glyph"]
			#
			if d == 1:
				#
				f_g.moveBy((get_box_diff_x, get_box_diff_y))
				#
				f_g.changed()
				#
			#
			d = d + 1
			#
		# #
		i = 0
		#
		for x in [self.g_data_a, self.g_data_b]:
			#
			root = ET.fromstring(x)
			#
			g_name = root.attrib['name']
			#
			made_g = self.made_letters[i]["glyph"]
			#
			g_strt_coord = get_glif_coord(made_g, 'corner')
			g_coord_flip = flipCoordPath(g_strt_coord,False,True)
			x_mm = value_mid(g_coord_flip, 0)
			y_mm = value_mid(g_coord_flip, 1)
			#
			g_orig_coord = get_glif_coord(made_g, 'original')
			g_strt_coord = get_glif_coord(made_g, 'corner')
			#
			g_orig = flipCoordPath(g_orig_coord,False,True)
			g_strt = flipCoordPath(g_strt_coord,False,True)
			#
			self.made_letters[i]["coords"]["orig"] = g_orig
			self.made_letters[i]["coords"]["graph"] = g_strt_coord
			self.made_letters[i]["coords"]["strt"] = g_strt
			#
			i = i + 1
			#
		#
		return self.made_letters
		#
	#

	#
	def get_edge_lengths(self,_g, pos):
		#
		lengths=OrderedDict()
		#
		for edge in _g.edges():
			#
			startnode=edge[0] 
			endnode=edge[1]
			#
			lengths[edge]={"len":round(math.sqrt(((pos[endnode][1]-pos[startnode][1])**2)+((pos[endnode][0]-pos[startnode][0])**2)),2), "coord":pos[endnode], "node":endnode} #The distance
			#
		#
		return lengths
		#
	#
	def make_topo(self, f_g, _color):
		#
		l_tp = bez_to_list(f_g["beziers"])
		#
		g_coord_flip = flipCoordPath(l_tp,False,True)
		#
		if len(f_g["graph_json"]):
			#
			_g = json_graph.node_link_graph(f_g["graph_json"])
			f_g["graph"]
			_g.clear()
			#
		else:
			#if hasattr(self,'G'):
			if f_g["graph"] != None:
				#
				_g = f_g["graph"]#self.G
				_g.clear()
				#
			else:
				#
				f_g["graph"] = nx.Graph()
				_g = f_g["graph"]
				#
			#
			x_mm = value_mid(g_coord_flip, 0)
			y_mm = value_mid(g_coord_flip, 1)
			#
			g_coord_flip_simp = g_coord_flip.copy()
			#
			g_coord_flip.insert(0,[x_mm,y_mm])
			#
			node_color_map = []
			edge_width_map = []
			node_width_map = []
			edge_color_map = []
			edge_label_map = {}
			node_label_map = {}
			node_order_map = OrderedDict()
			#
			for x in range(len(g_coord_flip)):
				#
				_g.add_edge(0,x)
				#
				_g.add_node(x,pos=g_coord_flip[x])
				#
			#
			for x in range(len(g_coord_flip)):
				#
				node_color_map.append(_color)
				edge_color_map.append(_color)
				edge_width_map.append(0.3)
				node_width_map.append(140)
				#
			#
			pos=nx.get_node_attributes(_g,'pos')
			#
			edge_lengths = self.get_edge_lengths(_g, pos)
			#
			sorted_length = sorted(edge_lengths.items(), key=lambda k: k[1]['len'], reverse=True)
			#
			sort_by_length = OrderedDict(sorted_length)
			#
			#
			i = 0
			d = 0
			#
			sorted_nodes = []
			#
			for n in _g.nodes():
				#
				i = 0
				#
				for k, v in sort_by_length.items():
					#
					node_inx = g_coord_flip.index(pos[n])
					#
					#
					if i == n:
						#
						node_order_map[n] = node_inx
						#
						if k != (0,0):
							#
							edge_label_map[k] = str(v["len"])
							node_label_map[v["node"]] = str(n)+'\n'+str(k[1])
							#
							i = i + 1
							#
						else:
							#
							node_label_map[v["node"]] = 'c'
							#
						#
						sorted_nodes.append(v["node"])
					#
					i = i + 1
					#
				#
			#
			for k,v in sort_by_length.items():
				#
				sort_by_length[k]["order"] = node_order_map[k[1]]
				#
			#
			f_g["graph_data"] = {
				#"pos":pos,
				"node_color_map":node_color_map,
				"edge_width_map":edge_width_map,
				"node_width_map":node_width_map,
				"edge_color_map":edge_color_map,
				"edge_label_map":edge_label_map,
				"node_label_map":node_label_map,
				"node_order_map":node_order_map,
				"g_coord_flip_simp":g_coord_flip_simp,
				"sort_by_length":sort_by_length
			}
			#
			f_g["graph_json"] = json_graph.node_link_data(_g)
			#
		#
		return f_g
		#
	#
#
class variom:

	def __init__(self, _vrmstart, run_sp):

		super(variom, self).__init__()

		self.vrmstart = _vrmstart
		self.plt_num = _vrmstart.plt_num
		self.matched = collections.OrderedDict()
		self.ghosts = []
		self.current_values = []
		self.matched_circles = []
		self.initial_coords_a = []
		self.initial_coords_b = []
		self.initial_coords_strt_a = []
		self.initial_coords_strt_b = []
		self.plots = []
		self.run_sp = run_sp
		self.cont_num = _vrmstart.cont_num
		#
		self._simp = 0
		self._iter = 0
		#

	def init_instances(self,val_simplification = False,val_iteration = False, _plt = True):
		#
		#
		if val_simplification == False and val_iteration == False:
			#
			if self.run_sp != "":
				#
				val_simplification = self.spinbox.get()
				val_iteration = self.rad_search_box.get()
			else:
				#
				val_simplification = self._simp#self.spinbox.get()
				val_iteration = self._iter#self.rad_search_box.get()
				#
			#
		#
		#
		self.points = []
		#
		self.draggingPoint = None
		#
		self.m_instances = self.vrmstart.initiate_instance()
		#
		#
		for x in range(len(self.m_instances.items())):
			#
			points = np.asarray(self.m_instances[x]["coords"]["strt"])
			#
			self.current_simp = int(val_simplification)
			#
			self.m_instances[x]["beziers"] = fitCurve(points, float(val_simplification)**2)
			#
			self.m_instances[x]["graph"] = self.vrmstart.make_topo(self.m_instances[x], color[x])
			#

		#
	def run(self):
		#
		#
		if self.run_sp != "":
			#
			root = Tk()
			#
			if self.plt_num == 0:
				#
				root.geometry("100x100+1600+0")
				#
			else:
				#
				root.geometry("100x100+1700+0")
				#
			#
			frame = Frame(root, relief=SUNKEN, borderwidth=1)
			frame.pack(side=LEFT, fill=Y)
			label = Label(frame, text='Max Error')
			label.pack()
			self.spinbox = Spinbox(frame, width=8, from_=0.0, to=1000000.0, command=self.on_matching_value_change)
			self.spinbox.delete(0,"end")
			self.spinbox.insert(0,0)
			self.spinbox.pack()
			label_iter = Label(frame, text='Iteration')
			label_iter.pack()
			self.rad_search_box = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_matching_value_change)
			self.rad_search_box.delete(0,"end")
			self.rad_search_box.insert(0,0)
			self.rad_search_box.pack()
			#
		#
		self._simp = 0
		self._iter = 0
		#
		self.init_instances(0,0, False)
		#
		#val_simplification = self.spinbox.get()
		#val_iteration = self.rad_search_box.get()
		#
		_a_instance = self.m_instances[0]
		points = _a_instance["graph_data"]["sort_by_length"]
		#
		self.initial_coords_a = self.m_instances[0]["coords"]["graph"]
		self.initial_coords_b = self.m_instances[1]["coords"]["graph"]
		self.initial_coords_strt_a = self.m_instances[0]["graph_data"]["g_coord_flip_simp"]
		self.initial_coords_strt_b = self.m_instances[1]["graph_data"]["g_coord_flip_simp"]
		#
		if debug:
			#
			print("================================================")
			pprint.pprint(self.m_instances[1]["coords"]["graph"])
			pprint.pprint(len(self.m_instances[1]["coords"]["graph"]))
			#
		#
		coords = []
		#
		for k in list(points.values()):
			#
			coords.append([k["coord"],k["node"]])
			#
		#
		# 
		#self._simp = start_simpl
		#self._iter = start_point
		#
		print ('\n'+tcolor.OKGREEN + "INITIATING SIMPLIFICATION GRADIENT MATCH FOR SEED: "+ repr(_simplification_seed) + tcolor.ENDC)
		#
		for y in _simplification_seed:
			#
			for x in coords:
				#
				_a_instance = self.m_instances[0]
				points = _a_instance["graph_data"]["sort_by_length"]
				#
				for k in list(points.values()):
					#
					if k["coord"] == x[0]:
						#
						try:
							#
							self.init_instances(y,k["node"], False)
							#
							self.make_iter(y,k["node"], False)
							#
							self._simp = y
							self._iter = k["node"]
							#
							print ('                                                                    ', end='\r')
							print (tcolor.WARNING + "SIMPLIFICATION: " + str(y) + ", POINT:" +str(k["node"])+ tcolor.ENDC, end='\r')
							#
							#time.sleep(0.01)
							#
						except Exception:
							pass
		#
		print ('\n'+tcolor.OKGREEN + "SIMPLIFICATION GRADIENT MATCH RESULT" + tcolor.ENDC)
		#
		# AFTER INITIAL MATCHING

		#
		self.init_instances(start_simpl,start_point, plt)
		#
		if self.run_sp != "":
			#
			self.spinbox.delete(0,"end")
			self.spinbox.insert(0,start_simpl)
			self.rad_search_box.delete(0,"end")
			self.rad_search_box.insert(0,start_point)
			#
		self.redraw()
		#
		#
	#
	#
	def on_matching_value_change(self):
		#
		self.init_instances() # repeat in case of simplification
		#
		self.redraw()
		#

	def make_iter(self, val_simplification = False, val_iteration = False, _plt = False):
		#
		if _plt:
			#
			if self.run_sp != "":
				#
				print ('\n'+tcolor.WARNING + "MANUAL MATCH REVIEW:" + "\n\tSIMPLIFICATION: " + str(self.spinbox.get())+ "\n\tPOINT: " + str(self.rad_search_box.get()) + tcolor.ENDC)
				#
			else:
				#
				print ('\n'+tcolor.WARNING + "MATCH REVIEW:" + "\n\tSIMPLIFICATION: " + str(self._simp)+ "\n\tPOINT: " + str(self._iter) + tcolor.ENDC)
				#
		#
			
		if val_simplification == False and val_iteration == False:
			#
			if self.run_sp != "":
				#
				val_simplification = self.spinbox.get()
				val_iteration = self.rad_search_box.get()
				#
			#
			else:
				#
				val_simplification = self._simp
				val_iteration = self._iter
				#
		#
		for x in range(len(self.m_instances.items())):
			#
			x_points = np.asarray(self.m_instances[x]["coords"]["strt"])
			#
		#
		if _plt:
			#
			draw.draw_instance_graphs(self)
			#
		#
		_color = color[0]
		#
		_a_instance = self.m_instances[0]
		_b_instance = self.m_instances[1]
		#
		points = _b_instance["graph_data"]["sort_by_length"]
		iter_point = int(val_iteration)
		#
		if len(list(points.items())) > iter_point:
			#
			do_rad_search(self, _a_instance, _b_instance, iter_point, _plt, _color) # subsequent rad searches
			#
		#

	def redraw(self):
		#
		self.make_iter(0,0,plt)
		#
		if self.run_sp != "":
			#
			plt.show(block = False)
			#
		#

def crt_coords_plot_all(s_mc_line, comb_plot, len_points):
	#
	got_first = False
	got_last = False
	#
	plotlist = []
	#
	new_smc = []
	#
	for z in s_mc_line:
		#
		for x in z:
			#
			new_smc.append(x)
			#
		#
	#
	for x in s_mc_line:
		#
		crt_coords_plot = [[item[0]] for item in x]
		#
		i = 0
		#
		for y in crt_coords_plot:
			#
			get_comb_itm_by_crd = [item for item in comb_plot if item[0] == y[0]][0]
			opp_crd = get_comb_itm_by_crd[1]
			c_inx = get_comb_itm_by_crd[3][0]
			#
			if c_inx == len_points: # if last and first exist, loop point
				#
				if debug:
					#
					print("GOT LAST")
					print(c_inx, len_points)
					#
				got_last = True
				#
			if c_inx == 1: # if last and first exist, loop point
				#
				#
				if debug:
					#
					print("GOT FIRST")
					print(c_inx, len_points)
					#
				got_first = True
				#
			#
			pnt_inx_nums = [item for item in comb_plot if item[0] == y[0]][0][1]
			#
			#
			if debug:
				#
				print("OPP CRD", opp_crd, y)
				#
			#
			y.append(opp_crd)
			#
			i = i + 1
			#
		#
		# purely visual, so the certainty line plots the connection between first and last point if they exist in the totality of certain points.
		# assuming this can only happen at the last of the plot coords since we have them sorted, and only then got_last becomes true.
		#
		if got_first == True and got_last == True: # if last and first exist
			#
			get_first_crd = [item for item in comb_plot if item[3][0] == 1][0]
			#
			crt_coords_plot.append(get_first_crd) # add first coord to the end to be ploted
			#

		#
		plotlist.append(crt_coords_plot)
		#
		if debug:
			#
			print("Combiner Most Certain for Plot")
			pprint.pprint(crt_coords_plot)
			#
		#
	#
	return plotlist
	#
#
def get_dist_list(center_point, points, cax):
	#
	dist_list = []
	#
	for x in points:
		#
		_dist = distance(x,center_point)
		#
		dist_list.append([_dist,x])
		#
	#
	return dist_list
	#
#
class vrmcomb:
	#
	def __init__(self, vrm_data, name, run_sp, log_output):
		#
		if debug:
			#
			print("ALL VRM DATA ALL CONTOURS")
			pprint.pprint(vrm_data)
			#
		#
		self.vrm_data = vrm_data
		self._movepos = 550
		#
		self.run_sp = run_sp
		self.log_output = log_output
		#
		draw.init_plot_comb(plt)
		t_plt = plt.figure(4)
		cax = t_plt.gca()
		#
		self.t_plt = t_plt
		self.name = name
		#
		self.run_sp = run_sp
		#
		self.run_comb()
		#

	def run_comb(self):
		#
		if self.run_sp != "": # Not implemented
			#
			root = Tk()
			#
			root.geometry("100x100+1800+0")
			#
			frame = Frame(root, relief=SUNKEN, borderwidth=1)
			frame.pack(side=LEFT, fill=Y)
			#
			label_iter = Label(frame, text='Iteration')
			label_iter.pack()
			self.rad_search_box = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_combiner_value_change)
			self.rad_search_box.delete(0,"end")
			self.rad_search_box.insert(0,0)
			self.rad_search_box.pack()
			#
		#
		self.redraw_comb()
		#
	#
	def get_most_certain_lines(self, comb_plot, len_points, vrm_data):
		#
		#
		strt_a = vrm_data.initial_coords_strt_a
		strt_b = vrm_data.initial_coords_strt_b
		#
		#
		crd = [item[0] for item in comb_plot]
		inx = [item[3][0] for item in comb_plot]
		crt = [item[2] for item in comb_plot]
		#
		cic_s = list(zip (crd,inx,crt))
		#
		i = 0
		#
		#crd = [item[0] for item in cic_s]
		inx = [item[1] for item in cic_s]
		crt = [item[2] for item in cic_s]
		#
		#
		l_inxcrt = list(zip(inx,crt))
		missing_func = add_missing(len_points, inx,crt)
		l_inxcrt_m = missing_func[0]
		#
		cert_lim_func = certainty_limit(l_inxcrt_m, len_points)
		l_inxcrt_lm = cert_lim_func[0]
		cert_rejected = cert_lim_func[1]
		#
		if debug:
			#
			print("CERTAINTY ACCEPTED ???????????????????????????????????????????")
			pprint.pprint(l_inxcrt_lm)
			print("CERTAINTY REJECTED ???????????????????????????????????????????")
			pprint.pprint(cert_rejected)
			#

		#
		m_points = []
		seq_points = []
		seq_points_reject = []
		#
		for x in l_inxcrt_lm:
			#
			point_num = x[0]
			#
			seq_points.append(point_num)
			#
		#
		seq_lists = get_seq(seq_points)
		#
		crt_s_lm = [item[0] for item in l_inxcrt_lm]
		#
		if debug:
			print("SEQ LISTS")
			print(seq_lists)
		#
		#
		sq = 0
		#
		comb_checks = combine_gap_one_seq(seq_lists, strt_a, strt_b, comb_plot)
		new_seq_list_gap_one = comb_checks[0]
		gap_mend = comb_checks[1]
		comb_plot = comb_checks[2]
		#
		if debug:
			#
			print("NEW COMB PLOT")
			pprint.pprint(comb_plot)
			#
			print("NEW GAP MEND")
			pprint.pprint(gap_mend)
			#
		#
		crd = [item[0] for item in comb_plot]
		inx = [item[3][0] for item in comb_plot]
		crt = [item[2] for item in comb_plot]
		#
		cic_s = list(zip (crd,inx,crt))
		#
		new_cert_rej = []
		#
		for x in cert_rejected:
			#
			if x[0] not in gap_mend:
				#
				new_cert_rej.append(x)
				#
			#
			#
		#
		cert_rejected_list = [cr[0] for cr in new_cert_rej]
		#
		if debug:
			#
			print("SEQ LISTS GAP ONE")
			#
			print(new_seq_list_gap_one)
			#
			print("NEW CERT REJECTED")
			print(cert_rejected_list)
		#
		cert_line = []
		#
		for x in new_seq_list_gap_one:
			#
			#
			lm_seq = []
			#

			if len(x) == 1:
				#
				if x[0] not in cert_rejected_list:
					#
					if debug:
						#
						print("SINGULARITY REJECTED", x)
						#
					#
					m_points.append(x)
					#
					for z in cic_s:
						#
						print("-->")
						print(z, x[0])
						#
						if z[1] == x[0]:
							#
							print("GOT -->")
							print(z, x[0])
							#
							lm_seq.append(z)
							#
						#
					#
				#
				cert_line.append(lm_seq)
				#
			else:
				#
				for y in x:
					#
					for z in cic_s:
						#
						if z[1] == y:
							#
							lm_seq.append(z)
							#
						#
					#
				#
				cert_line.append(lm_seq)
				#
			#
		#
		missing_points_seq = [item[0] for item in sorted(missing_func[1] + m_points)]
		#
		seq_lists_missing = get_seq(missing_points_seq)
		#
		if debug:
			#
			print("CERTAINTY REJECTED SEQUENCES")
			pprint.pprint(seq_lists_missing)
			#
		remain_accepted = []
		#
		for x in seq_lists_missing:
			#
			for y in x:
				#
				if y not in cert_rejected_list:
					#
					remain_accepted.append(y)
					#
				#
			#
			#
		#
		if debug:
			print("REMAIN ACCEPTED")
			print(remain_accepted)
		#
		if debug:
			print("Certain")
			pprint.pprint(cert_line)
			#
		#
		return [cert_line, get_seq(cert_rejected_list), get_seq(cert_rejected_list), comb_plot]
		#
	def get_opp_certain_coords(self, comb_plot, cert_s):
		#
		opp_cert = []
		#
		for x in cert_s:
			#
			opp_cert_tmp = []
			#
			for z in x:
				#	
				for y in comb_plot:
					#
					#print(x)
					#print(y)
					#
					if z[0] == y[0]:
						#
						opp_cert_tmp.append((y[1],y[3][1],y[2]))
						#
					#
				#
			opp_cert.append(opp_cert_tmp)
			#
		#
		return opp_cert
		#

	def on_combiner_value_change(self):
		#
		self.redraw_comb()
		#
	#

	def uncertain_target_tris(self, vrm_a, vrm_b, matches, uncrt_s, s_tris, unc_ends, unc_t_ranges, cax, _plt):
		#
		_c = 'b'
		#
		tris_permut = []
		#
		for p in unc_t_ranges:
			#
			local_permut = []
			#
			#print("UNC MOV")
			#pprint.pprint(p)
			#
			p_mov = p[0]
			p_mid = p[1]
			#
			for p_p,p_a in it.product(p_mov,p_mov):
				#
				if p_p != p_a:
					#
					if [p_p, p_mid, p_a] not in local_permut:
						#
						local_permut.append([p_p, p_mid, p_a])
						#
					#
				#
			#
			tris_permut.append(local_permut)
			#
		#
		if show_unc_target_triangle_plots == True:
			#
			for t in tris_permut:
				#
				for x in t:
					#
					poly = plt.Polygon(x, color=_c,alpha=0.05, linewidth=0.2)
					cax.add_patch(poly)
					#
				#
			#
		# #
		if debug:
			#
			print("----=")
			pprint.pprint(unc_t_ranges)
			#
		#
		if show_uncertain_dashed_target:
			#
			for o in unc_t_ranges:
				#
				if debug:
					print("-->")
					print(o)
				#
				plot_regular_line(cax, o[0], _c, _plt)
				#
		#
		return [tris_permut, unc_t_ranges]
		#
	#

	#
	def uncertain_source_tris(self, vrm_a, vrm_b, uncrt_s_l, cax, _plt):
		#
		unc_area_polygons = []
		#
		_c = 'r'
		#
		for x in uncrt_s_l:
			#
			local_polygons = []
			#
			len_points = len(vrm_a.initial_coords_strt_a)
			#
			for y in x[0]:
				#
				_y = y
				#
				t_inx_p = get_point_inx(len_points, vrm_a.initial_coords_strt_a.index(_y), 'p')
				t_inx_a = get_point_inx(len_points, vrm_a.initial_coords_strt_a.index(_y), 'a')
				#
				t_crd_p = _y
				t_crd_a = vrm_a.initial_coords_strt_a[t_inx_a]
				#
				unc_md = x[1]
				#
				if x[0].index(y) < len(x[0]) - 1:
					#
					local_polygons.append([t_crd_p, unc_md, t_crd_a])
					#
					
				#
			#
			for p_p,p_a in it.product(x[0],x[0]):
				#
				if p_p != p_a:
					#
					if [p_p, x[1], p_a] not in local_polygons:
						#
						local_polygons.append([p_p, x[1], p_a])
						#
					#
				#
			#
			unc_area_polygons.append(local_polygons)
			#
		#
		if show_unc_source_triangle_plots == True:
			
			for x in unc_area_polygons:
				#
				for y in x:
					#
					poly = plt.Polygon(y, color=_c,alpha=0.1, linewidth=0.5)
					cax.add_patch(poly)
					#
				#
			#
		#
		if show_uncertain_dashed_source:
			#
			for o in uncrt_s_l:
				#
				if debug:
					print("-->")
					print(o)
				#
				plot_regular_line(cax, o[0], _c, _plt)
				#
			#
		#
		return unc_area_polygons
		#
	#
	def match_uncertain_tris(self, s_tris,t_tris,cax,_plt):
		#
		# similar triangle comparison function
		#
		_c = 'b'
		#
		all_best_tris = []
		#
		for x in range(len(s_tris)):
			#
			area_s_tris = s_tris[x]
			area_t_tris = t_tris[x]
			#
			for y in area_s_tris:
				#
				match_final_polygons = area_t_tris
				#
				match_barycentric = []
				#
				A_bar_orig = barycentric(y)
				#
				# get triangle orientation
				#
				s_pa_mid = midpoint(y[0],y[2])
				s_ca_mid = midpoint(y[1],y[2])
				s_pc_mid = midpoint(y[0],y[1])
				#
				#
				s_pa_ang = get_angle_b(y[0],y[2])
				s_ca_ang = get_angle_b(y[1],y[2])
				#
				#
				s_ta_cpa = get_angle_b(y[1],s_pa_mid)
				s_ta_pca = get_angle_b(y[0],s_ca_mid)
				s_ta_acp = get_angle_b(y[2],s_pc_mid)
				#
				# Get barycentric extended lengths for source
				#
				s_bl_cpa = distance(s_pa_mid,A_bar_orig)
				s_bl_pca = distance(s_ca_mid,A_bar_orig)
				s_bl_acp = distance(s_pc_mid,A_bar_orig)
				#
				#
				for t_tri in area_t_tris:
					#
					now_bar = barycentric(t_tri)
					#
					A_bar_np = np.array(A_bar_orig)
					now_bar_np = np.array(now_bar)
					diff_bar = A_bar_np-now_bar_np
					#
					o_tri = y
					s_tri = move_tri(y, diff_bar)
					A_bar = move_tri([A_bar_orig], diff_bar)[0]
					#
					#
					# Get target triangle orientation
					# 
					t_pa_mid = midpoint(t_tri[0],t_tri[2])
					t_ca_mid = midpoint(t_tri[1],t_tri[2])
					t_pc_mid = midpoint(t_tri[0],t_tri[1])
					#
					t_ta_cpa = get_angle_b(t_tri[1],t_pa_mid)
					t_ta_pca = get_angle_b(t_tri[0],t_ca_mid)
					t_ta_acp = get_angle_b(t_tri[2],t_pc_mid)
					#
					#
					# Get barycentric extended lengths
					#
					t_bl_cpa = distance(t_pa_mid,now_bar)
					t_bl_pca = distance(t_ca_mid,now_bar)
					t_bl_acp = distance(t_pc_mid,now_bar)
					#
					# Draw triangle barycentric extended lines
					#
					if _plt:

						if show_unc_triangle_matching_a == True:				

							pp1 = mpatches.ConnectionPatch(t_tri[1],t_pa_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
							cax.add_patch(pp1)
							pp1 = mpatches.ConnectionPatch(t_tri[0],t_ca_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
							cax.add_patch(pp1)
							pp1 = mpatches.ConnectionPatch(t_tri[2],t_pc_mid,"data", arrowstyle='->,head_width=.15,head_length=.15', lw=0.2, alpha=0.2, color="k")
							cax.add_patch(pp1)
							#
							poly = plt.Polygon(s_tri, color='r',alpha=0.02, linewidth=0.5)
							cax.add_patch(poly)
							#
							#
							draw.draw_circle_on_coord(A_bar, cax, 2, "r")
							draw.draw_circle_on_coord(now_bar, cax, 1, "b")
							#
						if show_unc_triangle_matching_b == True:		

							# Triangle Matching Markings
							draw.draw_circle_on_coord(t_tri[1], cax, 2, "k")
							draw.draw_circle_on_coord(t_pa_mid, cax, 2, "k")
							pp1 = mpatches.ConnectionPatch(t_tri[1],t_pa_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
							cax.add_patch(pp1)

							draw.draw_circle_on_coord(t_tri[0], cax, 2, "k")
							draw.draw_circle_on_coord(t_ca_mid, cax, 2, "k")
							pp1 = mpatches.ConnectionPatch(t_tri[0],t_ca_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
							cax.add_patch(pp1)

							draw.draw_circle_on_coord(t_tri[2], cax, 2, "k")
							draw.draw_circle_on_coord(t_pc_mid, cax, 2, "k")
							pp1 = mpatches.ConnectionPatch(t_tri[2],t_pc_mid,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=0.5, alpha=0.2, color="k")
							cax.add_patch(pp1)
						#
					#
					s_sc = o_tri[1]
					t_sc = t_tri[1]
					#
					cumulative_point_distance = distance(o_tri[0], t_tri[0]) + distance(o_tri[1], t_tri[1]) + distance(o_tri[2], t_tri[2])
					#
					if show_unc_triangle_matching_bar_c == True:
						#
						if _plt:
							#
							pp1 = mpatches.ConnectionPatch(s_sc,t_sc,"data", lw=0.2, color="gray")
							cax.add_patch(pp1)

							for p in t_tri:
								#
								pp1 = mpatches.ConnectionPatch(now_bar,p,"data", lw=0.2, color="b")
								cax.add_patch(pp1)
						#
					match_barycentric.append([
						match_final_polygons.index(t_tri),
						# barycentric extension angle and reverse
						abs(s_ta_cpa-t_ta_cpa),#get_angle_c(t_ta_cpa,s_ta_cpa), #  
						abs(s_ta_pca-t_ta_pca),#get_angle_c(t_ta_pca,s_ta_pca), #  
						abs(s_ta_acp-t_ta_acp),#get_angle_c(t_ta_acp,s_ta_acp), #  
						# barycentric extension length
						abs(s_bl_cpa-t_bl_cpa),
						abs(s_bl_pca-t_bl_pca),
						abs(s_bl_acp-t_bl_acp),
						#
						t_tri[1],
						distance(A_bar,now_bar),
						[(t_ta_cpa,s_ta_cpa)],
						((abs(s_ta_cpa-t_ta_cpa) + abs(s_ta_pca-t_ta_pca) + abs(s_ta_acp-t_ta_acp))+(abs(s_bl_cpa-t_bl_cpa) + abs(s_bl_pca-t_bl_pca) + abs(s_bl_acp-t_bl_acp))),
						#
						cumulative_point_distance
						#
						])
					#
				#
				diff_list = []
				#
				sorted_tri_orient = sorted(match_barycentric, key=lambda x: ((x[1] + x[2] + x[3])+(x[4] + x[5] + x[6])+(x[8] + x[11])) )# sort according to triangle orientation, get first 3
				#
				best_m = match_final_polygons[sorted_tri_orient[0][0]]
				#
				# ignore tris if surface area difference is large
				#
				s_area = area(best_m)
				t_area = area(y)
				#
				s_bar = barycentric(y)
				t_bar = barycentric(best_m)
				#
				area_difference = get_change(s_area, t_area)
				#
				if debug:
					#
					print("MATCHING IGNORE")
					print(s_area, t_area, get_change(s_area, t_area))
					print(distance(s_bar, t_bar))
					#
				#
				# Ignore if area difference is larger than 20%
				# this means that those points that don't match will be removed
				# also if the contours have large differences they probably won't match.
				# if the uncertain lines have big differences they probably won't match.
				#
				if area_difference <= 25:
					#
					if _plt:
						#
						#if [472.0, -706.0] in best_m: looking for specific coord
						#
						if show_unc_triangle_matching_d:
							#
							poly = plt.Polygon(best_m, color=_c,alpha=0.05, linewidth=0.5)
							cax.add_patch(poly)
							#
							draw.draw_circle_on_coord(s_bar, cax, 2, "k")
							draw.draw_circle_on_coord(t_bar, cax, 2, "k")
							#
							pp1 = mpatches.ConnectionPatch(s_bar,t_bar,"data",arrowstyle='->,head_width=.15,head_length=.15', lw=1, alpha=0.5, color="k")
							cax.add_patch(pp1)
							#
						#
					#
					if debug:
						#
						print("MATCH")
						print(y,best_m)
						#
					#
					all_best_tris.append([y,best_m])
					#
				#
			#
		return all_best_tris
	# t_ends, t_ends, 1, cax, t_plt)
	def uncertain_lines(self, _crd, mc_line, unc_ends, s_ends, t_ends, inst, cax, _plt):
		#
		def check_movement(st_y, nd_y, got_moving, all_cert):
			#
			#
			# see if gathered as uncertain coord range lines are stepping over certain lines. to determing fault in direction.
			#
			check_moving = got_moving.copy()
			check_moving.remove(st_y)
			check_moving.remove(nd_y)
			#
			inx_check = []
			#
			for x in check_moving:
				#
				inx_check.append( _crd.index(x) )
				#
			#
			inx_check_moving = []
			#
			for y in all_cert:
				#
				inx_check_moving.append( _crd.index(y) )
				#
			#
			if debug:
				print("GOT MOVING ==================================================")
				pprint.pprint(check_moving)
				#
				print("-inx check")
				pprint.pprint(inx_check)
				#
				print("-zm")
				pprint.pprint(inx_check_moving)
			#
			l = inx_check + inx_check_moving
			#
			flag = set([x for x in l if l.count(x) > 1])
			#
			if len(flag) > 0:
				#
				return False	
				#
			else:
				#
				return True
				#
			#
			#
		#
		def get_moving(st_y, nd_y, _dir):
			#
			# get coords from start to end, acknowledge circularity get just coords, ignore indexes array
			got_moving = get_coord_range(_crd, st_y, len(_crd), _dir,nd_y)[0] 
			# add first to start as get_coord_range ingores the first one st_y.
			
			#
			return got_moving
			#
		#
		
		unc_s_ranges = []
		#
		if inst == 0:
			#
			_c = 'r'
			#
		else:
			#
			_c = 'b'
			#
		#
		i = 0
		#
		for y in unc_ends:
			#
			#_crd = vrm_a.initial_coords_strt_a
			#
			st_y = y[0]
			nd_y = y[1]
			#
			mc = []
			#
			if debug:
				#
				pprint.pprint("MC LINE")
				#
				pprint.pprint(mc_line)
				print("Z---")
				print(y)
				print(unc_ends.index(y))
				#
			if unc_ends.index(y) in mc_line:
				#
				for z in mc_line[unc_ends.index(y)]:
					#
					mc.append(z[0])
					#
			_dir = 'a'
			got_moving = get_moving(st_y, nd_y, _dir)
			got_moving.insert(0,st_y)
			#
			dir_check = check_movement(st_y, nd_y, got_moving, mc)
			#
			if inst == 0:
				unc_md = s_ends[i][2]#[s_ends[i][2][0]+200, s_ends[i][2][1]+200]#[200,200]#midpoint(st_y, nd_y)#s_ends[i][2]#midpoint(st_y, nd_y)
			else:
				unc_md = t_ends[i][2]#[t_ends[i][2][0]+200, t_ends[i][2][1]+200]#[200,200]#midpoint(st_y, nd_y)#t_ends[i][2]#midpoint(st_y, nd_y)#s_ends[i][2] # get mid from source tris

				#if dir_check == False:
					#
				#	unc_md = s_ends[i][2]
					#
			
			#
			str_inx = _crd.index(st_y)
			end_inx = _crd.index(nd_y)
			#
			if debug:
				#
				print("START END INX -=========================")
				print(str_inx, end_inx)
				print(y)
				#
				#
				#
				print("CERTAIN ZIP---------------------")
				pprint.pprint(mc)
			#
			#
			#
			if dir_check == False:
				#
				got_moving = get_moving(nd_y, st_y, 'a')
				got_moving.reverse()
				
				got_moving.insert(len(got_moving),nd_y)
				#
				got_moving.reverse()
				#
			#
			unc_s_ranges.append([got_moving,unc_md])
			#
			if debug:
				#
				print(str_inx,end_inx)
				print("====>")
				print(got_moving)
				print("====")
				#
			i = i + 1
		#
		return unc_s_ranges
		#
	#
	def show_uncertain_line_ends(self, unc_lines, _c, cax, _plt):
		#
		for y in unc_lines:
			#
			st_y = y[0][0]
			nd_y = y[0][-1]
			#
			unc_md = midpoint(st_y, nd_y)
			#
			draw.draw_circle_on_coord(st_y, cax, 20, _c)
			draw.draw_circle_on_coord(nd_y, cax, 20, _c)
			#
			#
			if show_uncertain_line_end_connections:

				_p = mpatches.ConnectionPatch( st_y, nd_y,"data", lw=1, alpha=1, color="purple", arrowstyle='<->,head_width=.15,head_length=.15', shrinkB=2,label='Label')
				cax.add_patch(_p)
			#
		#
	#
	def uncertain_ends(self, _crd, matches, lines, cax, _plt, _deg):
		#
		unc_ends = []
		#
		if matches == False:
			#
			_c = 'r'
			#
		else:
			#
			_c = 'b'
			#
		#
		for x in lines:
			#
			len_points = len(_crd)
			#
			#if len(x) > 1:
					
			#
			if matches == False: # source
				#
				#_f = _crd[x[0]-1]
				#_l = _crd[x[-1]-1]
				if debug:
					print("--->")
					pprint.pprint(_crd)
					print("---")
					print(len(_crd))
					print(x[-1]-1)
				#

				#
				_f = _crd[x[0]-1]
				_l = _crd[x[-1]-1]
				#
				f_p_pnt = get_point_inx(len_points, _crd.index(_f), 'p')
				l_a_pnt = get_point_inx(len_points, _crd.index(_l), 'a')
				#
				if debug:
					
					print("EXT P")
					print(f_p_pnt)
					print("EXT A")
					print(l_a_pnt)
					#
				_f_ext = _crd[f_p_pnt] # extend one out
				_l_ext = _crd[l_a_pnt] # extend one out
				#
				_md = midpoint(_f_ext, _l_ext)
				#
				_ra_ = rotate_tri_match(_f_ext[0],_f_ext[1],_md[0], _md[1], _deg)
				#
				if show_unc_source_triangle_plots:
					#
					draw.draw_circle_on_coord(_ra_, cax, 5, "pink")
					#
				#
				unc_ends.append([_f_ext, _l_ext, _ra_])
				#
			else: # target
				#
				local_ends = []
				#
				if  debug:
						
					print("X lines")
					print(x)
					print(lines)
					#
				_f = _crd[x[0]-1]
				_l = _crd[x[-1]-1]
				#
				f_p_pnt = get_point_inx(len_points, _crd.index(_f), 'p')
				l_a_pnt = get_point_inx(len_points, _crd.index(_l), 'a')
				#
				if debug:
						
					print('L ENDS')
					print(local_ends)
				#
				for z in matches:
					#
					if z[3][0]-1 == f_p_pnt:
						#
						local_ends.append(z[1])
						#
					elif z[3][0]-1 == l_a_pnt:
						#
						local_ends.append(z[1])
						#
					#
				#
				if len(local_ends) >= 1:
						
					_md = midpoint(local_ends[0], local_ends[1])
					#
					#
					if debug:
							
						print('L ENDS AFTER')
						print(local_ends)
						#
						print("LC")
						print(local_ends[0],local_ends[1],_md[0], _md[1], _deg)
					#
					_ra_ = rotate_tri_match(local_ends[0][0],local_ends[0][1],_md[0], _md[1], _deg)
					#
					if show_unc_target_triangle_plots:
						#
						draw.draw_circle_on_coord(_ra_, cax, 5, "pink")
						#
					#
					unc_ends.append([local_ends[0],local_ends[1], _ra_])
				#
			#
		#
		return unc_ends
		#	
	#
	def find_in_tri_match_b(self, vrm_data_a, vrm_data_b, tris, inbe, inst):
		#
		#print("TRIS")
		#pprint.pprint(tris)
		#
		rel_l_tri_points = []
		rel_s_tri_points = []
		rel_rem_points = []
		rel_keep_tris = []
		most_met = []
		#
		if inst == 0:
			inst_opp = 1
		else:
			inst_opp = 0
		#
		for z in inbe:
			#
			i = 0
			#
			met_inbe = []
			#
			for x in tris:
				#
				l_rel_tris = x[inst]
				s_rel_tris = x[inst_opp]
				#
				if (i % 2) == 0: # even
					#
					lkup = 2 # ante
					#
				else: # odd
					#
					lkup = 0 # pre
					#

				if z == s_rel_tris[lkup]:
					#
					opp_tri_lkup = x
					#
					rel_keep_tris.append(opp_tri_lkup)
					#
					found_match = [opp_tri_lkup[0][lkup],opp_tri_lkup[1][lkup]]
					#
					met_inbe.append(found_match)
					#
					i = i + 1
					#
				else:
					#
					pass
					#
				#
			#
			if debug:
				#
				print("inbetween Points")
				pprint.pprint(met_inbe)
				#
			#
			most_met.append(met_inbe)
			#
		#
		most_met_count = []
		#
		#print("M A")
		#pprint.pprint(vrm_data_a.matched)
		#print("M B")
		#pprint.pprint(vrm_data_b.matched)
		#
		for x in most_met:
			#
			most_occ = sorted(most_occuring(x,0,1), key = lambda x: x[2], reverse=True)
			#
			if debug:
				#
				print("FULL MOST OCC")
				pprint.pprint(most_occ)
				#
			#
			if len(most_occ):
				#
				most_met_count.append([most_occ[0][0],most_occ[0][1]])
				#
			#
		#
		if debug:
			#
			print("PREV ANTE METHOD")
			pprint.pprint(rel_keep_tris)
			print("PREV ANTE METHOD MOST MET")
			pprint.pprint(most_met)
			print("PREV ANTE METHOD MOST MET COUNT")
			pprint.pprint(most_met_count)
			print("INBE")
			pprint.pprint(inbe)
			#
		#
		return most_met_count
		#
	#
	def basic_cleanup(self, s_unc_line, t_unc_line, unc_lines_s, s_mc_line, t_mc_line, get_cert_line_to_plot, cax, _plt):
		#
		fin_s_unc_line = []
		fin_t_unc_line = []
		#
		fin_unc_lines_s = []
		#
		#print("BASIC CLEANUP")
		#
		for l in range(len(s_unc_line)):
			#
			if l in s_unc_line and l in t_unc_line:
				#
				#
				s_line = s_unc_line[l][0]
				t_line = t_unc_line[l][0]
				#
				s_line_len = len(s_line)
				t_line_len = len(t_line)
				#
				if s_line_len == t_line_len: # uncertain lines in source and target have same length - passing
					#
					if debug:
						#
						print("FOUND UNCERTAIN LINE OF SAME LENGTH CATEGORIZING AS CERTAIN", l)
						#
					#
					add_certain = list(zip (s_line,t_line))
					#
					#if s_line_len > 3:
					#
					if show_mid_uncertainty_lines:
						#
						plot_certainty_line(cax, add_certain, 'aquamarine', plt)
						#
					#
					#
				else: # keep only different length lines
					#
					# ARE uncertain with 3 points in either line but not more.
					# certain to remove as inbetween is only 1.
					#
					# for more than 3 we pass it for triangle matching as we will need to determine 
					# which of the 2 remaining will have to be removed.
					#
					_lim_low = 3
					_lim_low_b = _lim_low + 1

					#
					if (s_line_len < _lim_low_b and t_line_len == _lim_low) or (t_line_len < _lim_low_b and s_line_len == _lim_low): 
						#
						bypass_single = []
						#
						for z in s_line:
							#
							draw.draw_circle_on_coord(z, cax, 2, "r")
							#
						for z in t_line:
							#
							draw.draw_circle_on_coord(z, cax, 2, "b")
							#
						#
						if s_line_len == _lim_low:
							#
							if debug:
								#
								print("FOUND UNCERTAIN SOURCE LINE OF SMALL LENGTH REMOVING EXCESS", l)
								#
							#
							s_pinb = s_line[1:s_line_len-1] # source points in between edges
							#
							#
							if show_uncertain_source_small_length:
								#
								for t in s_pinb:
									#
									draw.draw_circle_on_coord(t, cax, 20, "yellow")
									#
							#
							s_ints = list_intersection(s_line,s_pinb)
							#
							#print(s_ints)
							#
							add_certain = list(zip (s_ints,t_line))
							#
						elif t_line_len == _lim_low:
							#
							if debug:
								#
								print("FOUND UNCERTAIN TARGET LINE OF SMALL LENGTH REMOVING EXCESS", l)
								#
							#
							t_pinb = t_line[1:t_line_len-1]
							#
							#
							if show_uncertain_target_small_length:
								#
								for t in t_pinb:
									#
									draw.draw_circle_on_coord(t, cax, 20, "orange")
									#
							#
							t_ints = list_intersection(t_line,t_pinb)
							#
							add_certain = list(zip (s_line,t_ints))
							#
						#
						# Just plotting, proper positioning in the final line must be identified before joining to one.
						#
						if show_mid_uncertainty_lines:
							#
							plot_certainty_line(cax, add_certain, 'lime', plt)
							#
						#
					else:
						#
						if debug:
							#
							print("FOUND UNCERTAIN LINE OF DIFFERENT LENGTH KEEPING UNCERTAIN", l)
							#
						#
						fin_s_unc_line.append(s_unc_line[l])
						fin_t_unc_line.append(t_unc_line[l])
						#
						fin_unc_lines_s.append(unc_lines_s[l])
					#
			#
		#
		return [fin_s_unc_line, fin_t_unc_line, fin_unc_lines_s]
		#
	#
	def redraw_comb(self):
		#
		name = self.name
		_movepos = self._movepos
		t_plt = self.t_plt
		cax = t_plt.gca()
		cax.cla()
		#
		plt.axis('off')
		#
		_color = ['r', 'b']
		#
		for z in self.vrm_data:
			#
			cont = self.vrm_data.index(z)
			#
			vrm_data_a = z[1][0]
			vrm_data_b = z[1][1]
			#
			_g_d_s = [vrm_data_a.initial_coords_strt_a, vrm_data_a.initial_coords_strt_b]
			_g_p_s = [vrm_data_a.m_instances[0]["glyph"], vrm_data_a.m_instances[1]["glyph"]]
			#
			for x in vrm_data_a.initial_coords_strt_a:
				#
				draw.draw_circle_on_coord(x, cax, 2, "r")
				#
			#
			for x in vrm_data_a.initial_coords_strt_b:
				#
				draw.draw_circle_on_coord(x, cax, 2, "b")
				#
			#
			#
			for x in [0,1]:
				#
				draw.move_figure(t_plt, _movepos, _movepos+100,950,0)
				#
				glyph_path = writeGlyphPath(_g_p_s[x], True)
				parse_mpl = mpl_parse_path(glyph_path)
				#
				patch = mpatches.PathPatch(parse_mpl, facecolor="none", edgecolor=_color[x], fill=False, lw=0.5)
				t = mpl.transforms.Affine2D().translate(offset_x,-offset_y) + cax.transData
				#
				patch.set_transform(t)
				cax.add_patch(patch)
				#
				g_coord_flip_simp = _g_d_s[x]
				simp_xPts,simp_yPts=zip(*g_coord_flip_simp)
				cax.plot(simp_xPts,simp_yPts,color=_color[x],lw=0.2)
				#
			#
			comb_plot = combiner(vrm_data_a,vrm_data_b, cax)
			#
			len_strt_a = len(vrm_data_a.initial_coords_strt_a)
			len_strt_b = len(vrm_data_a.initial_coords_strt_b)
			#
			# Show contour start points
			draw.draw_circle_on_coord(vrm_data_a.initial_coords_strt_a[0], cax, 20, "red", False)
			draw.draw_circle_on_coord(vrm_data_a.initial_coords_strt_b[0], cax, 20, "blue", False)
			#
			cert_s = self.get_most_certain_lines(comb_plot, len_strt_a, vrm_data_a)
			#
			# Mended comb plot update
			#
			comb_plot = cert_s[3]
			#
			s_mc_line = cert_s[0]
			#
			#s_mc_line.append(([85.0, -621.0], 23, 11.0))
			#
			t_mc_line = self.get_opp_certain_coords(comb_plot, s_mc_line)
			#t_mc_line = cert_t[0]
			unc_lines_s = cert_s[1] 
			#unc_lines_t = cert_t[1]
			#unc_cert_rej = cert_s[2]
			#
			# Plot the certain lines
			#
			get_cert_line_to_plot = crt_coords_plot_all(s_mc_line, comb_plot, len_strt_a)
			#
			s_ends = self.uncertain_ends(vrm_data_a.initial_coords_strt_a, False,     unc_lines_s, cax, t_plt, -90)
			t_ends = self.uncertain_ends(vrm_data_a.initial_coords_strt_a, comb_plot, unc_lines_s, cax, t_plt, -90)
			#
			# _crd, unc_ends, inst, s_ends, t_ends, cax, _plt
			s_unc_line = self.uncertain_lines(vrm_data_a.initial_coords_strt_a, s_mc_line, s_ends, s_ends, t_ends, 0, cax, t_plt)
			t_unc_line = self.uncertain_lines(vrm_data_a.initial_coords_strt_b, t_mc_line, t_ends, s_ends, t_ends, 1, cax, t_plt) # s_ends
			#
			if debug:
				#
				#
				print("CERTAIN LINES GET---------------------")
				pprint.pprint(cert_s)
				print("CERTAIN SOURCE---------------------")
				pprint.pprint(s_mc_line)
				print("CERTAIN TARGET---------------------")
				pprint.pprint(t_mc_line)
				#
				
				print("SOURCE TARGET MOST CERTAIN")
				pprint.pprint(s_mc_line)
				#
				#
				print("Combiner Most Certain")
				pprint.pprint(comb_plot)
				#
				print("MISSING POINTS")
				pprint.pprint(unc_lines_s)
					#
				print("LINE ENDS")
				print("S ---")
				pprint.pprint(s_ends)
				print("ALL LINES")
				pprint.pprint(s_unc_line)
				print("T ---")
				pprint.pprint(t_ends)
				print("ALL LINES")
				pprint.pprint(t_unc_line)
				print("--------")
					#
			#
			bsc_clean = self.basic_cleanup(s_unc_line, t_unc_line, unc_lines_s, s_mc_line, t_mc_line, get_cert_line_to_plot, cax, t_plt)
			#
			#save_dir = os.path.join(self.log_output, name.split('.glif')[0]+'.json')
			#
			#with open(save_dir, 'w') as f:
			#	json.dump(comb_plot, f)
			#
			if show_low_uncertainty_lines:
				#
				#
				for z in get_cert_line_to_plot:
					#
					#
					plot_certainty_line(cax, z, 'g', plt)
					#
			#
			if debug:
				print("CERT TO PLOT ---------------------")
				pprint.pprint(get_cert_line_to_plot)
			#
			# 
			# HIGH UNCERTAINTY LINE SOLUTIONS START
			# 
			# Patchwork and not to be taken seriously.
			# From this point onward, the low and mid certainty matching is done,
			# the code attempts to somehow solve highly uncertain lines.
			# Solving this with curved bezier comparison will allow for complete automation of variable font cleanup for matching.
			# 
			fin_s_unc_line = bsc_clean[0]
			fin_t_unc_line = bsc_clean[1]
			#
			if debug:
				print("LINES ------")
				print("S")
				print(fin_s_unc_line)
				print("T")
				print(fin_t_unc_line)
			#
			if show_unc_source_line_ends:
				#
				self.show_uncertain_line_ends(fin_s_unc_line, 'r', cax, t_plt)
				#
			if show_unc_target_line_ends:
				#
				self.show_uncertain_line_ends(fin_t_unc_line, 'b', cax, t_plt)
				#
			#
			s_tris = self.uncertain_source_tris(vrm_data_a, vrm_data_b, fin_s_unc_line, cax, t_plt)
			#
			_t_tris_line = self.uncertain_target_tris(vrm_data_a, vrm_data_b, comb_plot,fin_t_unc_line, s_tris, t_ends, fin_t_unc_line,cax, t_plt)
			#
			t_tris = _t_tris_line[0]
			get_uncr_line_to_plot = _t_tris_line[1]
			#

			
			bm_tris = self.match_uncertain_tris(s_tris,t_tris,cax,t_plt)
			#
			# post tris
			#
			keep_opp_points = []
			removed_points = []
			#
			# test find closer

			#
			for l in range(len(fin_s_unc_line)):
				#
				f_s_line = fin_s_unc_line[l][0]
				f_t_line = fin_t_unc_line[l][0]
				#
				lon_line = max([f_s_line,f_t_line], key=len)
				sho_line = min([f_s_line,f_t_line], key=len)
				#
				sho_len = len(sho_line)
				lon_len = len(lon_line)
				sho_p_inb = sho_line[1:sho_len-1]
				lon_p_inb = lon_line[1:lon_len-1]
				#
				best_ms = []
				#
				if lon_line == f_s_line:
					#
					t_line = 0
					#
				else:
					#
					t_line = 1
					#
				#
				for x in sho_p_inb:
					#
					dist_l = sorted(get_dist_list(x, lon_p_inb, cax), key = lambda x: x[0])[0]
					#
					if t_line == 0:

						best_ms.append([dist_l[0],dist_l[1],x])

					else:

						best_ms.append([dist_l[0],x,dist_l[1]])

					#
				#
				
				sho_len = len(sho_line)
				lon_len = len(lon_line)
				sho_p_inb = sho_line[1:sho_len-1]
				lon_p_inb = lon_line[1:lon_len-1]
				#
				if debug:
						
					print("BEST Ms")
					pprint.pprint(best_ms)
					# print('M LON')
					print("LON Ms")
					pprint.pprint(lon_matches)
					# print('M LON')
					# print(lon_line)
					# print('M SHO')
					# print(sho_line)
					#
					#
					print("=================== is")
					print(t_line)
					#
				if len(best_ms) > 2:
					#
					sl_mrm = self.find_in_tri_match_b(vrm_data_a,vrm_data_b,bm_tris, sho_p_inb, t_line)
					#
				else:
					sl_mrm = []
					#
					for b in best_ms:
						#
						sl_mrm.append([b[1],b[2]])
						#
					#
				#
				#
				if debug:
					print("=================== is SL MRM")
					print(sl_mrm)
					#
				#
				if t_line == 0:
					#
					keep_opp_points.append([[lon_line[0],sho_line[0]]]+sl_mrm+[[lon_line[-1],sho_line[-1]]])
					#  
				else:
					#
					keep_opp_points.append([[sho_line[0],lon_line[0]]]+sl_mrm+[[sho_line[-1],lon_line[-1]]])
					#
				#
				rem_points = []
				#
			#
			# check order as matching can be mixed up after trimatch, mixed up order is a red flag for wrong match
			#
			keep_opp_points_inline = check_point_order_on_line(keep_opp_points, vrm_data_a.initial_coords_strt_a, vrm_data_a.initial_coords_strt_b)
			#

			#
			
			if debug:
				print('PA inter')
				pprint.pprint(keep_opp_points)
				print('PA inter inline')
				pprint.pprint(keep_opp_points_inline)
				#
			#
			if show_high_uncertainty_lines:
				
				for kopi in keep_opp_points_inline: # keep_opp_points_inline # fails on letter ""
					#
					for y in kopi:
						#
						draw.draw_circle_on_coord(y[0], cax, 5, "r")
						#
						draw.draw_circle_on_coord(y[1], cax, 5, "b")
						#
						_p = mpatches.ConnectionPatch( y[0], y[1],"data", lw=2, alpha=1, color="purple", arrowstyle='<->,head_width=.15,head_length=.15', shrinkB=2,label='Label')
						cax.add_patch(_p)
						#
						plot_certainty_line(cax, kopi, 'springgreen', plt)
					#
				#
				#
			#
			# 
			# HIGH UNCERTAINTY LINE SOLUTIONS END
			# 
			#
			#save_dir = os.path.join(self.log_output, name.split('.glif')[0]+'.svg')
			# 
			print ('\n'+tcolor.WARNING + "SAVING SVG MATCHING RESULT: " + tcolor.ENDC)
			#print('\n'+save_dir)
			#
		#
		#plt.figure(4).savefig(save_dir)

		if self.run_sp != "":
			#
			plt.show(block = False)
			#
		#


def get_distance_sorted_contours(root):
	#
	split_conts = split_contours_to_glifs(root)
	#
	if debug:
		#
		print("ALL CONTOURS ARE SPLIT TO GLIFS")
		print(split_conts)
		#
	#
	g_name = root.attrib['name']
	#
	dist_sorted = []
	#
	for s_c in split_conts:
		#
		str_g = ET.tostring(s_c).decode()
		#
		made_g = make_glyph(str_g,g_name)
		#
		g_strt_coord = get_glif_coord(made_g, 'corner')
		#
		dist = 0
		#
		i = 0
		#
		for y in g_strt_coord:
			#
			if i != len(g_strt_coord)-1:
				#
				dist = dist + (distance(y,g_strt_coord[i+1]))
				#
			#
			i = i + 1
			#
		#
		dist_sorted.append([dist, str_g])
		#
	#
	dist_sorted_sort = sorted(dist_sorted, key = lambda x: x[0], reverse=True) # largest first
	#
	if debug:
		#
		print("SORT BY DISTANCE")
		print(dist_sorted_sort)
		#
	#
	dist_conts = [item[1] for item in dist_sorted_sort]
	#
	if debug:
		print("GET CONTOURS FROM DISTANCE SORTED")
		print(dist_conts)
	#
	return dist_conts
	#
#
def split_contours_to_glifs(root):
	#
	'''
	iterate over the glif, remove everything but advance, unicode and outline
	bypass notdef, space .. probably other too
	get standalone glif letters with each contour one by one, 
	the whole data of the letter but with only one of the contours in it at a time
	'''
	#
	got = False
	#
	cont_glif = []
	got_contours = []
	#
	for item in root.iter():
		#
		contours = []
		contours_str = []
		#
		if item.tag == 'glyph':
			#
			if item.attrib['name'] in ['.notdef', 'space']:
				pass
			else:
				#
				for outline in item.findall('outline'):
					#
					for contour in outline.findall('contour'):
						#
						contour_str = contour#
						#
						contours.append(contour)
						contours_str.append(ET.tostring(contour).decode())
						#
					#
				#
				if len(contours):
					#
					for x in contours_str:
						#	
						root_ = deepcopy(root)
						#
						for _item in root_.iter():
							#
							for _tag in _item.iter():
								#
								if _tag.tag == 'lib':
									#
									_item.remove(_tag)
									#
								#
							#
							for outline in _item.findall('outline'):
								#
								for contour in outline.findall('contour'):
									#
									if ET.tostring(contour).decode() != x:
										#
										outline.remove(contour)
										#
									#
							#
						if root_ not in cont_glif:
							#
							cont_glif.append(root_)
								#
							#
					got = True
					#
				else:
					#
					largest_contour = None
					#
			#
		#
		else:
			pass
		
		#
	return cont_glif
	#
#
if __name__ == '__main__':
	#
	'''
	## Very basic example

	font = [glifData_a_reg,glifData_a_thn]
	#font = [gar_reg_c, gar_bld_c]
	#font = [gar_reg_b, gar_bld_b]
	#font = [gd_garamond_reg, gd_garamond_bld]
	#font = [gar_amp_reg, gar_amp_bld]
	#
	input_contours = font
	#
	_p_st = vrmstart(input_contours[0], input_contours[1],0,0)
	o_st = variom(_p_st)
	o_st.run()
	#
	time.sleep(1)
	#
	_p_ts = vrmstart(input_contours[1], input_contours[0],1,0)
	o_ts = variom(_p_ts)
	o_ts.run()
	#
	
	#
	plt.show()
	#
	#or iterate over a UFO font
	#
	'''
	
	#
	def run_vmatic(font_path_r, font_path_b, x, run_sp, log_output):
		#
		input_contours = []
		#
		is_file_a = os.path.isfile(os.path.join(font_path_r,x[1]))
		is_file_b = os.path.isfile(os.path.join(font_path_b,x[1]))
		#
		if is_file_a and is_file_b:
			#
			root_a = ET.parse( os.path.join(font_path_r,x[1]) ).getroot()
			root_b = ET.parse( os.path.join(font_path_b,x[1]) ).getroot()
			#
			dist_sorted_a = get_distance_sorted_contours(root_a)
			dist_sorted_b = get_distance_sorted_contours(root_b)
			#
			if len(dist_sorted_a) == len(dist_sorted_b):
				#
				var_glifs = []
				#
				for y in range(len(dist_sorted_a)):
					#
					c_a = dist_sorted_a[y]
					c_b = dist_sorted_b[y]
					#
					if c_a and c_b:
						#
						input_contours = [c_a, c_b]
						#
						_p_st = vrmstart(c_a, c_b,0,y)
						o_st = variom(_p_st, run_sp)
						o_st.run()
						#
						_p_ts = vrmstart(c_b, c_a,1,y)
						o_ts = variom(_p_ts, run_sp)
						o_ts.run()
						#
						var_glifs.append([[c_a, c_b],[o_st,o_ts]])
						#
				#
				if debug:
					#
					pprint.pprint(var_glifs)
					#
				#
				vrm_comb = vrmcomb(var_glifs, x[1], run_sp, log_output)
				#
			else:
				#
				print("CANNOT GET CONTOURS FOR INSTANCES GLIFS")
				#
			#
	#
	def run_vmatic_b(font_inst, t_pl, inst_counter, run_sp):
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
			GC = GraphConstructor(CH,instance_list,cnt,inst_counter, simplification, debug)
			#
			contours[cnt] = GC.initiate_instance(inst_counter, cnt, CH)
			#
			points = np.asarray(contours[cnt]["coords"]["strt"])
			#
			#print(contours[cnt]["beziers"])
			# store simplification presense matrix
			contours[cnt]["beziers"] = OrderedDict()
			#
			for simp in simplification:
				#
				print(simp)
				#
				# shapely simplify with preserve_topology
				simplified_points = simplif(points, float(simp))
				#
				#
				#contours[cnt]["beziers"][simp] = fitCurve(points, float(simp)**2)
				contours[cnt]["beziers"] = simplified_points#simplified_points(points, float(simp))
				#
				contours[cnt]["graph"] = GC.make_instance_topo(contours[cnt], color[inst_counter], simp)
				#

			#
			o_ts = variom(GC, run_sp)
			o_ts.run()
			#
		#
		instance_dict[inst_counter] = contours
		#
		# var_glifs = []
		# #
		# for y in range(len(dist_sorted_a)):
		# 	#
		# 	c_a = dist_sorted_a[y]
		# 	c_b = dist_sorted_b[y]
		# 	#
		# 	if c_a and c_b:
		# 		#
		# 		input_contours = [c_a, c_b]
		# 		#
		# 		# _p_st = vrmstart(c_a, c_b,0,y)
		# 		# o_st = variom(_p_st, run_sp)
		# 		# o_st.run()
		# 		#
		# 		#_p_ts = vrmstart(c_b, c_a,1,y)
		# 		#
		# 		var_glifs.append([[c_a, c_b],[o_st,o_ts]])
		# 		#
		# #
		# if debug:
		# 	#
		# 	pprint.pprint(var_glifs)
		# 	#
		#
		#vrm_comb = vrmcomb(var_glifs, x[1], run_sp, log_output)
		#
		#
		for k,v in contours.items():
			#
			_a = 0
			#
			if v["inst"] > 0:
				#
				_a = 1
				#
			#
			plot_window_number = v["cont"]+v["inst"]+_a
			#
			draw.draw_instance_graphs_c(plot_window_number, v)
			#
		#
		#
		# input_contours = []
		# #
		# is_file_a = os.path.isfile(os.path.join(font_path_r,x[1]))
		# is_file_b = os.path.isfile(os.path.join(font_path_b,x[1]))
		# #
		# if is_file_a and is_file_b:
		# 	#
		# 	root_a = ET.parse( os.path.join(font_path_r,x[1]) ).getroot()
		# 	root_b = ET.parse( os.path.join(font_path_b,x[1]) ).getroot()
		# 	#
		# 	dist_sorted_a = get_distance_sorted_contours(root_a)
		# 	dist_sorted_b = get_distance_sorted_contours(root_b)
		# 	#
		# 	if len(dist_sorted_a) == len(dist_sorted_b):
		# 		#
		# 		var_glifs = []
		# 		#
		# 		for y in range(len(dist_sorted_a)):
		# 			#
		# 			c_a = dist_sorted_a[y]
		# 			c_b = dist_sorted_b[y]
		# 			#
		# 			if c_a and c_b:
		# 				#
		# 				input_contours = [c_a, c_b]
		# 				#
		# 				_p_st = vrmstart(c_a, c_b,0,y)
		# 				o_st = variom(_p_st, run_sp)
		# 				o_st.run()
		# 				#
		# 				_p_ts = vrmstart(c_b, c_a,1,y)
		# 				o_ts = variom(_p_ts, run_sp)
		# 				o_ts.run()
		# 				#
		# 				var_glifs.append([[c_a, c_b],[o_st,o_ts]])
		# 				#
		# 		#
		# 		if debug:
		# 			#
		# 			pprint.pprint(var_glifs)
		# 			#
		# 		#
		# 		vrm_comb = vrmcomb(var_glifs, x[1], run_sp, log_output)
		# 		#
		# 	else:
		# 		#
		# 		print("CANNOT GET CONTOURS FOR INSTANCES GLIFS")
		# 		#
		# 	#
	#
	#
	#
	'''
	Figures at the end of run_specific show the last contour processed, not all contours processed.
	Could be configured to run just a specific contour i guess...

	The figure 5 that is the combiner shows all the contours processed

	Figure 0 - Instance e.g. regular to bold - the regular side - Just the last contour
	Figure 1 - Instance e.g. regular to bold - the bold side - Just the last contour
	Figure 2 - Instance e.g. bold to regular - the bold side - Just the last contour
	Figure 3 - Instance e.g. bold to regular - the regular side - Just the last contour
	Figure 4 - Instance regular all contours and instance bold all contours and their connections

	the files are stored in output data as "glyph_name".svg

	'''
	#
	faults = False
	#
	# if  args.instance_a is None or args.instance_b is None:
	# 	#
	# 	faults = True
	# 	#
	# 	print('=\n=> Please Provide Source UFO Instance Files (a and b): -a "/font_regular.ufo -b "/font_bold.ufo"\n=')	
	# 	#
	# if args.log_output is None:
	# 	#
	# 	faults = True
	# 	#
	# 	print('=\n=> Please Provide Log Directory for Output: -l "/log_output"\n=')	
		#
	if faults == False:
		#
		#font_path_r = os.path.abspath(os.path.join(args.instance_a, 'glyphs') )#os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
		#font_path_b = os.path.abspath(os.path.join(args.instance_b, 'glyphs') )#os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
		font_path_r = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
		font_path_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
		#
		
		i = 0
		#
		#print(args.specific_glyph)
		#
		'''
		if args.specific_glyph is None:

			#
			run_specific = ""
			#
			print('=\n=> To Run Specific Glyph: -g "H_"\n=')
			#
			if args.start_glyph_num is None or args.end_glyph_num is None:
				#
				print('=\n=> Start Glyph Number and End Glyph Number (-s from, -e to): -s 17 -e 117\n=')
				#
				start_from = 0#17
				max_items = len([f for f in os.listdir(font_path_r) 
					if f.endswith('.glif') and os.path.isfile(os.path.join(font_path_r, f))])
				#
				print('\n'+tcolor.WARNING + "Start Glyph Number and End Glyph Number not provided, Running all Glyphs: "+ str(start_from)+" to "+str(max_items)  + tcolor.ENDC)	
				#
			else:
				# if run specific, run only that letter, else take into account start_from and how many letters after that max_items
				start_from = int(args.start_glyph_num)#17
				max_items = int(args.end_glyph_num)#start_from + 100
				#
			#
		else:
		'''
		#
		#run_specific = 'a' # run a specific glyph by glif file name "H_", "a" ...
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
		run_specific_contour = 0 # Not Implemented, runs all contours sorted by distance traveled - total line length between points
		#
		print('\n'+tcolor.WARNING + "Running Specific Glyph: "+ str(run_specific)  + tcolor.ENDC)	
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
								run_vmatic_b(font_inst, t_pl, inst_counter, run_specific)
								#
								
						#
					#
				#
			#
			inst_counter = inst_counter + 1
			#
					
		'''
		with open(os.path.join(font_path_r,'contents.plist'), 'rb') as f:
			pl = plistlib.load(f)
			#
			for x in pl.items():
				#
				if run_specific != "":
					#
					if run_specific == x[1].split(".glif")[0]:
						#
						print ('\n'+tcolor.WARNING + "RUNNING: " + run_specific + tcolor.ENDC)
						#
						run_vmatic(font_path_r, font_path_b, x, run_specific, args.log_output)
						#
						#combine_log(args.log_output)
						#
						plt.show()
						#
						#
					else:
						#
						pass
						#
					#
				else:
					#
					if i < start_from:
						print('passing', x[1])
						pass
					else:
						#
						if i > max_items:
							#
							break
							#
						else:
							#
							try:
								#
								print ('\n'+tcolor.WARNING + "RUNNING: " + x[1] + tcolor.ENDC)
								#
								run_vmatic(font_path_r, font_path_b, x, run_specific, args.log_output)
								#
								#plt.show()
								#
							except Exception as e:
								#
								print ('\n'+tcolor.FAIL + "FAILED: " + x[1] + tcolor.ENDC)
								print (e)
								#
								pass
						#
					i = i + 1
				#
			#
		#
		'''
		if run_specific == "":
			#
			plt.close('all')
			#
		#
		#combine_log(args.log_output)
		#
	#
