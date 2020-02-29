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
							#t_contour = contours[cnt]
							points = np.asarray(contours[cnt]["coords"]["strt"])
							#
							contours[cnt]["simplified"] = OrderedDict()
							#
							for simp in simplification:
								#
								simplified_points = simplif(points, simp)
								#
								contours[cnt]["simplified"][simp] = simplified_points
								#
							#
							inst_inx = contours[cnt]["inst"]
							cont_inx = contours[cnt]["cont"]
							#
							t_color = color[inst_inx]
							#
							GC.make_instance_topo(contours[cnt], t_color,0)
							#draw.draw_instance_graphs_c(contours[cnt])
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

initiate_drawing.run()
#

#
for instance in total_list:
	#
	for letter in total_list[instance]:
		#
		for contour in total_list[instance][letter]:
			#
			t_contour = total_list[instance][letter][contour] # this
			points_len = t_contour["graph_data"]["sort_by_length"]
			#
			a_items = []
			#
			for k,v in points_len.items():
				#
				a_items.append(k)
				#
			#
			matched_source = []
			#
			__point = list(points_len.values())[0]["coord"]
			#
			f_p_x = __point[0]
			f_p_y = __point[1]
			#
			t_fnl_d = 300#math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) + 50 # target_first_and_last_distance
			#
			p_d = 0
			for k,v in points_len.items():
				#
				if k!=(0,0):
					#
					t_a_coord = points_len.get(a_items[p_d])["coord"]
					t_a_order = points_len.get(a_items[p_d])["order"]
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
			f_s = next(c for c in ms_pn_s if c[1] == __point)
			f_pre = next(c for c in ms_pn_s if c[3] == get_point_inx_line(len(points_len), f_s[3], "p"))
			f_ant = next(c for c in ms_pn_s if c[3] == get_point_inx_line(len(points_len), f_s[3], "a"))
			l_s = [f_pre,f_s,f_ant]
			#
			_SC = l_s[1]
			_P = l_s[0]
			_A = l_s[2]
			#
			cen_a = list(points_len.items())[-1]
			cen_c = cen_a[1]["coord"]
			#
			sc_c = _SC[1]
			#
			to_ct = [
				_P[1],
				_SC[1],
				_A[1]
			]
			#
			t_plot = draw.get_gca(t_contour["plot_num"], plt)
			#
			draw.draw_circle_on_coord(__point, t_plot, 15, "g", False)
			#
			perps_plot = make_ct(to_ct, cen_c, t_plot, True)
			#
			#print(perps_plot)
			#
			#do_ct_sort(_f,__point, to_ct,perps_plot, l_t,t_plot,t_plot, _plt, True)
			#t_contour[instance][letter][contour]["graph_data"]
			#sl = t_contour["graph_data"]#["sort_by_length"]
			#print(sl)
			#
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