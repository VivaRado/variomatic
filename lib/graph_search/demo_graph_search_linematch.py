#
import os
import time
import json
import pprint
import fontTools
import numpy as np
import collections
import collections
from pylab import *
from bezier import *
from tkinter import *
import networkx as nx
from numpy import array
from fitCurves import *
from simple_path import *
from fontParts.world import *
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from svgPathPen import SVGPathPen
from itertools import combinations
import xml.etree.ElementTree as ET
from collections import OrderedDict
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from networkx.readwrite import json_graph
from svgpathtools import parse_path as pt_parse_path
from svgpath2mpl import parse_path as mpl_parse_path
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
#
from glyph_strings import *
#

color = ["red","blue"]

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

offset_y = 700
offset_x = 50

#
found_item = [330, -600]
#
def move_figure(f,w,h, x, y):
	"""Move figure's upper left corner to pixel (x, y)"""
	backend = matplotlib.get_backend()
	if backend == 'TkAgg':
		#print('TkAgg')
		f.canvas.manager.window.wm_geometry("%dx%d+%d+%d" % (w,h, x, y))
	elif backend == 'WXAgg':
		print('WXAgg')
		print('NO RESIZE FUNTION FOR WINDOW')
		f.canvas.manager.window.SetPosition((x, y))
		#f.canvas.manager.window.SetSize((1, 2))
	else:
		print('C')
		print('NO RESIZE FUNTION FOR WINDOW')
		# This works for QT and GTK
		# You can also use window.setGeometry
		f.canvas.manager.window.move(x, y)
#
def circle_point_distance( point1, point2):
	return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

#
def in_circle( point, circle):
	origin, radius = circle
	return radius >= circle_point_distance(point, origin)
#
def draw_circle_on_coord(coords, ax, rad, _color, _fill=True):
	#
	v_c = coords
	#
	#
	s_circle = plt.Circle(v_c, rad, color=_color, alpha=0.5, lw=0.5, fill=_fill)
	#
	#
	ax.add_patch(s_circle)
	#
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
	#difference = list(set(t_contents) - set(l_t))
	#
	print("===")
	print(t_contents)
	print(l_t)
	#
	for z in difference:
		#
		print("ignore", z[2])
		ignore_num.add(z[2])
		#

	#
	return ignore_num
	#
def do_rule_check(inst_num,t_coords,t_contents,l_t, _f_pip):
	#
	ag_a = _f_pip[0]["agreed"]
	ag_b = _f_pip[1]["agreed"]
	#
	ignore_num = set()
	#
	'''
	for each agreed, see if match exists in another agreed and compare the distance,
	if the distance in the other agreed is smaller, add to ignore.
	?leave the smallest distance, remove the other?
	'''
	#
	#
	for x in t_contents:
		#
		#print(x)
		#
		x_dist = x[0]
		x_num = x[2]
		#
		ni = int(not(inst_num))
		#
		for k,v in _f_pip[ni]["agreed"].items():
			#
			for y in v[1:]:
				#
				if len(y) > 0:
					#
					y_num = y[0][2]
					y_dist = y[0][0]
					#
					if x_num == y_num:
						#
						if y_dist < x_dist:
							#
							ignore_num.add(y_num)# 888
							#
						#
			#
	#

	#
	return ignore_num
	#
def get_agreed(_p, _ag_a, _ag_b, points_a, points_b):
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
					print('=----')
					print(x[0])
					print(v[0])
					#
					found_match = True
					#
					print(_ag_b[x[0][2]][1][0])
					#points_a = _a_instance["graph_data"]["sort_by_length"]#[1:]
					#new_dict = [a for a, b in points_a.items() if item_next_coord == b["coord"]][0]
					#
					ret_matching.append(True)
					#print ("MATCHES")
					#
					return True
					#break
					#
				#lse:
					#

					#ret_matching = [_p[0],_p[1], False]
					#
					#print ("NO MATCHES")
					#
			#
		#
	#
	if len(ret_matching) == 0:
		#
		return False
		#
	#
def do_line_check(_a_instance, _b_instance, l_s, l_t, ms_pn_s, mt_pn_s, scp_s, scp_t, _f):
	#
	_a_ag = _a_instance["agreed"]
	points_a = _a_instance["graph_data"]["sort_by_length"]
	_b_ag = _b_instance["agreed"]
	points_b = _b_instance["graph_data"]["sort_by_length"]
	#
	r_c_a = do_rule_not_on_line( mt_pn_s, l_t)
	r_c_b = do_rule_not_on_line( ms_pn_s, l_s)
	#
	print("l_s", l_s)
	print("l_t", l_t)
	#
	ignore_num = set()
	#
	for x in r_c_a:
		#
		ignore_num.add(x)
		#
	#
	i = 0
	u = 0
	#
	rule_check_exists_better = do_rule_check(_a_instance["inst"],_b_instance["coords"]["strt"], l_t, l_t, _f.m_instances) # rule check over existing agreed generated by the initial graph searches.
	#
	for r in rule_check_exists_better:
		#
		pass
		#ignore_num.add(r)
		#
	#
	l_t_d = [x[2] for x in mt_pn_s]
	l_s_d = [x[2] for x in ms_pn_s]
	l_t_p = [x[3] for x in mt_pn_s]
	l_s_p = [x[3] for x in ms_pn_s]
	#
	l_t_z = sorted(list(zip(l_t_d, l_t_p)), key=lambda x: x[1])
	l_s_z = sorted(list(zip(l_s_d, l_s_p)), key=lambda x: x[1])
	#
	print('===================================================================')
	print(l_s)
	print(l_t)
	print("EXISTS BETTER")
	print(rule_check_exists_better)
	print('--')
	print(l_t_z)
	print(scp_t[0])
	print(r_c_a)

	print('--')
	print(l_s_z)
	print(scp_s[0])
	print(r_c_b)
	#
	iter_line = scp_s[0]
	iter_match = l_s_z
	iter_agg_a = _b_ag
	iter_agg_b = _a_ag
	iter_a = points_b
	iter_b = points_a
	#
	s_longest = len(scp_s[0]) < len(scp_t[0])
	#
	if s_longest:
		#
		iter_line = scp_t[0]
		iter_match = l_t_z
		iter_agg_a = _a_ag
		iter_agg_b = _b_ag
		iter_a = points_a
		iter_b = points_b
		#
	#
	matching_lines = []
	#
	for x in iter_line:
		#
		inx_m = [s for s in iter_match if x == s[1]][0]
		#
		print("===============>", x)
		matching_bool = get_agreed(inx_m, iter_agg_a, iter_agg_b, iter_a, iter_b)
		#
		matching_lines.append(matching_bool)
		# print('==========')
		# print(_a_ag)
		# print('===')
		# print(_b_ag)
		#
		#
	#
	print('++++++++++++')
	print(matching_lines)
	#
	for ls in l_s:
		#
		if i < len(l_s) -1:
			#
			s_degs = angle(ls[1],l_s[i+1][1])
			#
			print("edge_s: ", ls[2], l_s[i+1][2], "degs: ", s_degs)
			#
			for lt in l_t:
				#
				if u < len(l_t) -1:	
					#
					t_degs = angle(lt[1],l_t[u+1][1])
					#
					print("edge_t: ", lt[2], l_t[u+1][2], "degs: ", t_degs)
					#
					#
					print("DEGS ============")
					print(s_degs, t_degs)
					#
				#	
				u = u + 1
				#
			#
		#
		i = i + 1
		#
	#
	return ignore_num
	#
#
def midpoint(p1, p2):
	return [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]

def angle(p1, p2):
	degs = math.degrees(math.atan2(p1[1]-p2[1], p1[0]-p2[0]))
	return int(degs)

def label(xy, text, tx):
	#y = xy[1] # shift y-value for label so that it's below the artist
	_text = str(text)+'°'
	tx.text(xy[0],xy[1], text, ha="center", family='monospace', rotation=text, size=6, bbox=dict( boxstyle="round",ec=(1, 1, 1,0.3),fc=(1, 1, 1,0.3)))
	#
#
def get_point_line(coords, _c, _f, inum):
	#
	ag_a = _f.m_instances[0]["agreed"]
	ag_b = _f.m_instances[1]["agreed"]
	#
	seq_points = []
	#
	print(coords)
	#
	for x in coords:
		#
		point_num = x[3]
		#
		seq_points.append(point_num)
		#
	#
	seq_points.sort()
	#
	seq_lists = []
	for idx,item in enumerate(seq_points):
		#
		if not idx or item-1 != seq_lists[-1][-1]:
			seq_lists.append([item])
		else:
			seq_lists[-1].append(item)
		#
	#
	line_start_point = coords[0][3]
	#
	print("======================================")
	print("======================================")
	print(line_start_point)
	#print(ag_b)
	print("======================================")
	#
	inx_ignore = [seq_lists.index(ls) for ls in seq_lists if line_start_point not in ls]
	#
	print("ignore_indexes", inx_ignore)
	#
	ignore_set = set()
	#
	inx_seq = [seq_lists.index(ls) for ls in seq_lists if line_start_point in ls][0]
	#
	scp = seq_lists[inx_seq] # seq_contains_point
	#
	#
	if len(scp) > 1:
		#
		i = 0
		#
		for x in coords:
			#
			#if i < len(coords) -1:
			#
			#
			srt_num = x[3]
			end_num = coords[i][3]
			next_num = coords[i+1][3]
			#
			print('>>')
			print(x[2])
			#
			if srt_num not in scp:
				#
				ignore_set.add(x[2])
				#
	#
	print("-----------------------------------")
	print(seq_lists)
	print('==================')
	print(scp)
	print('==================')
	ni = int(not(inum))
	#
	return [scp,ignore_set]
	#
def plot_region_line(tx, coords, _c, scp):
	#
	'''
	Draw lines only for points that are in sequence.
	'''
	#
	i = 0
	first_ploted = False
	#
	
	for x in coords:
		#
		if i < len(coords) -1:
			#
			#
			srt_num = x[3]
			end_num = coords[i][3]
			next_num = coords[i+1][3]
			#
			if srt_num in scp:
				#
				if i > 0 and first_ploted == False: # if the first line has not been ploted
					#
					pass
					#
				else:
					#
					if end_num+1 == next_num: # if the first line is in series
						#
						if i == 0:
							#
							first_ploted = True
							#
						#
						_p = mpatches.ConnectionPatch(x[1],coords[i+1][1],"data", lw=1, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=5, color=_c,label='Label')
						tx.add_patch(_p)
						#
						_midpoint = midpoint(x[1],coords[i+1][1])
						_degs = angle(x[1],coords[i+1][1])
						#
						label(_midpoint, _degs, tx)
			#
		i = i + 1
		#
	#
#
def do_rad_search(_f, _a_instance, _b_instance, iter_point, _plt=False, _color=False):
	#
	if _plt:
		#
		_a_plt = _plt.figure(0)
		_b_plt = _plt.figure(1)
		#
		ax = _a_plt.gca()
		bax = _b_plt.gca()
		t = get_t(ax)
	#
	points_a = _a_instance["graph_data"]["sort_by_length"]
	points_b = _b_instance["graph_data"]["sort_by_length"]
	#
	item_next_coord = list(_a_instance["graph_data"]["sort_by_length"].values())[iter_point]["coord"]
	#
	if len(list(points_b.items())) > iter_point:
		#
		a_items = []
		#
		for k,v in points_a.items():
			#
			a_items.append(k)
		#
		b_items = []
		#
		for k,v in points_b.items():
			#
			if k!=(0,0):

				b_items.append(k)
				#
				if _plt:
					#
					if k!=(0,0):
						#
						v_c = v["coord"]
						#
						v["circle"] = plt.Circle(item_next_coord, 15, color=_color[0], fill=False, alpha=0.5, lw=0.5)
						#
						v["circle"].set_radius(0)
						v["circle"].set_linestyle((0, (2,4)))
						#
						ax.add_patch(v["circle"])
						#
					#
				#
		#
		p_c = 0
		#
		matched_target = []
		matched_source = []
		#
		if _plt:
			#
			draw_circle_on_coord(item_next_coord, ax, 15, "g", False)
			#
		#
		for k,v in points_b.items():
			#
			if k!=(0,0):
				#
				c_rad = 0
				#
				contains = False
				#
				#
				max_radius = 200 # max radius is the furthest distance between two points in all the instances.
				#
				t_b_coord = points_b.get(b_items[p_c])["coord"]
				t_b_order = points_b.get(b_items[p_c])["order"]
				#
				for x in range(max_radius):
					#
					#
					t_circle = [t_b_coord,c_rad]
					#
					contains = in_circle(item_next_coord,t_circle)
					#
					if contains:
						#
						Path = mpath.Path
						#
						t_b_dist = math.hypot(t_b_coord[0]-item_next_coord[0], t_b_coord[1]-item_next_coord[1])
						#
						matched_target.append([t_b_dist,t_b_coord,p_c,t_b_order])
						#
						if _plt:
							#
							pp1 = mpatches.ConnectionPatch(t_b_coord,item_next_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
							pp1.set_linestyle((0, (2,4)))
							ax.add_patch(pp1)
							draw_circle_on_coord(t_b_coord, ax, 5, "g")
							#
						#
						break
						#	
					else:
						#
						if _plt:
							#
							v["circle"].set_radius(c_rad)
							#
						#
						c_rad = c_rad + 1
						#
					#
				#
				if contains == False:
					#
					if _plt:
						#
						v["circle"].set_visible(False) # hide circles that didnt find the point because of max radius
						#
					#
				#
			#
			p_c = p_c + 1
			#
		#
		#
		sorted_cont_target = sorted(matched_target)
		#
		# get most distant target match distance from search center
		f_p_x = item_next_coord[0]#
		f_p_y = item_next_coord[1]#sorted_cont[0][1][1]
		l_p_x = sorted_cont_target[-1][1][0]
		l_p_y = sorted_cont_target[-1][1][1]
		f_p_b_x = sorted_cont_target[0][1][0]
		f_p_b_y = sorted_cont_target[0][1][1]
		#
		t_fnl_d = math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) # target_first_and_last_distance
		#
		if _plt:
			#
			# Draw circle and first point to most distant point radius line for instance a
			pp1 = mpatches.ConnectionPatch(item_next_coord,sorted_cont_target[-1][1],"data", lw=0.5, color="g")
			ax.add_patch(pp1)
			draw_circle_on_coord(item_next_coord, ax, t_fnl_d, "g", False)
			# Draw coverage circle and point circle based on most distant data of matches from a on instance b
			draw_circle_on_coord([f_p_x,f_p_y], bax, 5, "r")
			draw_circle_on_coord([f_p_x,f_p_y], bax, t_fnl_d, "r", False)
			#
		#
		# Get instance B points contained in circle from a most distant
		p_d = 0
		for k,v in points_a.items():
			#
			if k!=(0,0):
				t_a_coord = points_a.get(a_items[p_d])["coord"]
				t_a_order = points_a.get(a_items[p_d])["order"]
				#
				t_circle = [t_a_coord,t_fnl_d]
				#
				contains = in_circle(item_next_coord,t_circle)
				#
				if contains:
					#
					t_a_dist = math.hypot(t_a_coord[0]-item_next_coord[0], t_a_coord[1]-item_next_coord[1])
					#
					matched_source.append([t_a_dist,t_a_coord,p_d, t_a_order])
					#
				p_d = p_d + 1
			#
		#
		#
		
		ignore_num = set()
		rule_check_exists_better = set()
		rule_check_line_match = set()
		#
		scp_s = [[],set()]
		scp_t = [[],set()]
		#
		if _plt:
			#
			# sorted by length number
			ms_pn_s = sorted(matched_source, key = lambda x: x[3])
			mt_pn_s = sorted(matched_target, key = lambda x: x[3])
			#
			s_ip_inx = ms_pn_s.index(next(c for c in ms_pn_s if c[2] == iter_point))#np.where(s_ip_np[2]==iter_point)#[idx_s for idx_s, s in enumerate(ms_pn_s) if iter_point == int(s[2])][0]
			t_ip_inx = mt_pn_s.index(sorted_cont_target[0])#mt_pn_s.index(next(c for c in mt_pn_s if c[2] == iter_point))#np.where(t_ip_np[2]==iter_point)#[idx_t for idx_t, t in enumerate(mt_pn_s) if iter_point == int(t[2])][0]
			#
			l_s = ms_pn_s[s_ip_inx:] # get all after current iterated point in source
			l_t = mt_pn_s[t_ip_inx:] # get all after current iterated point in target
			#
			scp_s = get_point_line(l_s, "r", _f, 0)
			scp_t = get_point_line(l_t, "r", _f, 1)
			#
			plot_region_line(ax, l_s, "r", scp_s[0])
			plot_region_line(bax, l_t, "b", scp_t[0])
			#
			rule_check_line_match = set(list(do_line_check(_a_instance, _b_instance, l_s, l_t, ms_pn_s, mt_pn_s, scp_s, scp_t, _f))+list(scp_s[1])+list(scp_t[1])) # rule check over existing agreed generated by the initial graph searches.
			#
		# get current node number lengthwise
		points_a = _a_instance["graph_data"]["sort_by_length"]#[1:]
		new_dict = [a for a, b in points_a.items() if item_next_coord == b["coord"]][0]
		#
		#
		c_sc_s = sorted_cont_target.copy()
		#
		if _plt:
			
			
			ignore_num = set(list(rule_check_exists_better) + list(rule_check_line_match) ) #+ list(rule_check_not_on_line))

			for z in sorted_cont_target:
				#
				if z[2] in rule_check_exists_better: #or t_node in ignore_num:
					#
					draw_circle_on_coord(z[1], bax, 10, "r", False)
					#
					if z in c_sc_s:
						#
						c_sc_s.remove(z)
						#
				#
				if z[2] in rule_check_line_match: #or t_node in ignore_num:
					#
					draw_circle_on_coord(z[1], bax, 10, "yellow", False)
					#
					if z in c_sc_s:
						#
						c_sc_s.remove(z)
						#
				#
				# if z[2] in rule_check_not_on_line: #or t_node in ignore_num:
				# 	#
				# 	draw_circle_on_coord(z[1], bax, 10, "r", False)
				# 	#
				# 	if z in c_sc_s:
				# 		#
				# 		c_sc_s.remove(z)
				# 		#
				# 	#
				#
		#
		if _plt:
			#
			for x in c_sc_s:
				#
				draw_circle_on_coord(x[1], bax, 20, "g", False)
				#
			#
		#
		t_node = list(points_a.keys()).index(new_dict)
		#
		if _plt:
			#
			if len(c_sc_s) > 0:
				#
				sorted_first = c_sc_s[0][1]
				#
				draw_circle_on_coord(sorted_first, bax, 20, "g")
				#
			#
		#
		else:
			#
			_a_instance["agreed"][t_node] = [item_next_coord,c_sc_s]
			_f.pip.agreed_matches[t_node] = [item_next_coord,c_sc_s]
			#
		#
#

class pip():

	def __init__(self, g_data_a, g_data_b):
		super(pip, self).__init__()
		self.made_letters = {}
		self.m_instances = {}
		self.g_data_a = g_data_a
		self.g_data_b = g_data_b
		self.agreed_matches = collections.OrderedDict()
		self.sgrad = collections.OrderedDict()
	#
	#
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
	#
	#
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
	#
	def make_glyph(self,_g_dat,_name):
		#
		_let = _name
		f = NewFont()
		g = f.newGlyph(_let)
		pen = g.getPointPen()
		glyph_result = readGlyphFromString(_g_dat, glyphObject=g, pointPen=pen)
		#
		#
		f_g = f[_let]
		#
		
		#
		return f_g
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
			made_g = self.make_glyph(x,g_name)
			#
			g_strt_coord = self.get_glif_coord(made_g, 'corner')
			g_coord_flip = self.flipCoordPath(g_strt_coord,False,True)
			x_mm = self.value_mid(g_coord_flip, 0)
			y_mm = self.value_mid(g_coord_flip, 1)
			#
			self.made_letters[c] = {
				"glyph":made_g,
				"box": [x_mm, y_mm],
				"inst":c,
				"coords":{
					"orig": None,
					"strt": None
					},
				"graph":None,
				"graph_json":{},
				"agreed":{}
			}
			#
			c = c + 1
			#
		#
		get_box_diff_x = self.made_letters[0]["box"][0] - self.made_letters[1]["box"][0]
		get_box_diff_y = self.made_letters[0]["box"][1] - self.made_letters[1]["box"][1]
		#
		d = 0
		for let, val in self.made_letters.items():
			#
			f_g = self.made_letters[d]["glyph"]
			#
			if d == 1:
				#
				#pass
				f_g.moveBy((get_box_diff_x, get_box_diff_y))
				#f_g.scaleBy((get_box_diff_x + 0.04, get_box_diff_y), origin=None)
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
			made_g = self.made_letters[i]["glyph"]#self.make_glyph(x,g_name)
			#
			g_strt_coord = self.get_glif_coord(made_g, 'corner')
			g_coord_flip = self.flipCoordPath(g_strt_coord,False,True)
			x_mm = self.value_mid(g_coord_flip, 0)
			y_mm = self.value_mid(g_coord_flip, 1)
			#
			g_orig_coord = self.get_glif_coord(made_g, 'original')
			g_strt_coord = self.get_glif_coord(made_g, 'corner')
			#
			g_orig = self.flipCoordPath(g_orig_coord,False,True)
			g_strt = self.flipCoordPath(g_strt_coord,False,True)
			#
			self.made_letters[i]["coords"]["orig"] = g_orig
			self.made_letters[i]["coords"]["strt"] = g_strt
			#
			i = i + 1
			#
		#
		
		return self.made_letters
		#
	#
	def bez_to_list(self, coords=False):
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

	def value_mid(self, inputlist, pos):

		_mx = max([sublist[pos] for sublist in inputlist])
		_mn = min([sublist[pos] for sublist in inputlist])
		#
		mid = (_mx + _mn) / 2
		#
		return mid

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
		l_tp = self.bez_to_list(f_g["beziers"])
		#
		g_coord_flip = self.flipCoordPath(l_tp,False,True)
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
			x_mm = self.value_mid(g_coord_flip, 0)
			y_mm = self.value_mid(g_coord_flip, 1)
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
				node_width_map.append(70)
				#
			#
			pos=nx.get_node_attributes(_g,'pos')
			#
			edge_lengths = self.get_edge_lengths(_g, pos)
			#
			sorted_length = sorted(edge_lengths.items(), key=lambda k: k[1]['len'], reverse=True)
			#
			#sorted_length_remove_zero = [i for i in edge_lengths if i["node"] == 0]
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
							#
							edge_label_map[k] = str(v["len"])
							node_label_map[v["node"]] = str(n)
							#
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
					#	
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
# center of bounding box
def cntr(x1, y1, x2, y2):
	return x1+(x2-x1)/2, y1+(y2-y1)/2
#
def get_t(ax):
	#
	t = mpl.transforms.Affine2D().translate(offset_x,-offset_y) + ax.transData
	#
	return t
	#
#
class MainObject:

	def __init__(self, _pip):
		self.pip = _pip

	def init_instances(self):
		#
		self.points = []
		#
		self.draggingPoint = None
		#
		self.m_instances = self.pip.make_instances()
		#
		for x in range(len(self.m_instances.items())):
			#
			points = np.asarray(self.m_instances[x]["coords"]["strt"])
			#
			self.m_instances[x]["beziers"] = fitCurve(points, float(self.spinbox.get())**2)
			#
			self.m_instances[x]["graph"] = self.pip.make_topo(self.m_instances[x], color[x])
			#
		#
		for i in range(len(self.m_instances.items())):
			#
			ni = int(not(i))
			#
			len_sorted = self.m_instances[i]["graph_data"]["sort_by_length"]
			#
			_a_instance = self.m_instances[i]
			_b_instance = self.m_instances[ni]
			#
			ord_keys = list(len_sorted.keys())
			#
			for c in range(len(list(len_sorted.items()))):
				#
				if c != (0,0):
					#
					do_rad_search(self, _a_instance, _b_instance, c) # initial rad search to cover the agreed for each instances
					#
				#
			#
		#
		#
	def run(self):
		#
		root = Tk()
		#
		frame = Frame(root, relief=SUNKEN, borderwidth=1)
		frame.pack(side=LEFT, fill=Y)
		label = Label(frame, text='Max Error')
		label.pack()
		self.spinbox = Spinbox(frame, width=8, from_=0.0, to=1000000.0, command=self.onSpinBoxValueChange)
		self.spinbox.delete(0,"end")
		self.spinbox.insert(0,0)
		self.spinbox.pack()
		label_iter = Label(frame, text='Iteration')
		label_iter.pack()
		self.rad_search_box = Spinbox(frame, width=8, from_=0, to=1000000, command=self.onSpinBoxValueChange)
		self.rad_search_box.delete(0,"end")
		self.rad_search_box.insert(0,6)
		self.rad_search_box.pack()
		#
		self.init_instances()
		#
		self.redraw()
		#
		root.mainloop()
		#
	#
	def onSpinBoxValueChange(self):
		#
		self.init_instances() # repeat in case of simplification
		#
		self.redraw()

	def draw_topo(self, instance, _plt, i):
		#
		_color = color[i]
		#
		_g = json_graph.node_link_graph( instance["graph_json"] )
		_g_d = instance["graph_data"]
		#
		#
		_plt.clf()
		ax = _plt.gca()
		#
		node_width_map = _g_d["node_width_map"]
		node_color_map = _g_d["node_color_map"]
		edge_color_map = _g_d["edge_color_map"]
		edge_width_map = _g_d["edge_width_map"]
		edge_label_map = _g_d["edge_label_map"]
		node_label_map = _g_d["node_label_map"]
		g_coord_flip_simp = _g_d["g_coord_flip_simp"]
		sort_by_length = _g_d["sort_by_length"]
		# Draw Original
		self.svg_path_orig = writeGlyphPath(instance["glyph"], True)
		parse_mpl = mpl_parse_path(self.svg_path_orig)
		patch = mpatches.PathPatch(parse_mpl, facecolor="none", edgecolor=_color, fill=False, lw=0.4)
		t = mpl.transforms.Affine2D().translate(offset_x,-offset_y) + ax.transData
		#
		patch.set_transform(t)
		ax.add_patch(patch)
		#
		simp_xPts,simp_yPts=zip(*g_coord_flip_simp)
		ax.plot(simp_xPts,simp_yPts,color="gray",lw=0.2)
		#
		#
		pos=nx.get_node_attributes(_g,'pos')

		nx.draw(_g,pos,node_size=node_width_map, node_color = node_color_map, edge_color=edge_color_map, width=edge_width_map)
		#
		nx.draw_networkx_edge_labels(_g,pos,edge_labels=edge_label_map,font_size=7, font_family='monospace')
		nx.draw_networkx_labels(_g,pos,node_label_map,font_size=6, font_color='white', font_family='monospace', font_weight='bold')
		#
	def redraw(self):
		#
		for x in range(len(self.m_instances.items())):
			#
			points = np.asarray(self.m_instances[x]["coords"]["strt"])
			self.m_instances[x]["beziers"] = fitCurve(points, float(self.spinbox.get())**2)
			#
		#
		_movepos = 600
		#
		for i in range(len(self.m_instances.items())):
			#
			t_plt = plt.figure(i)
			#
			move_figure(t_plt, 600, 700,i*_movepos,600)
			#
			self.draw_topo(self.m_instances[i], t_plt, i)
			#
			ax = t_plt.gca()
			#
			_color = color[i]
			_glyph = self.m_instances[i]["glyph"]
			#	
			svg_path_orig = writeGlyphPath(_glyph, True)
			parse_mpl = mpl_parse_path(svg_path_orig)
			patch = mpatches.PathPatch(parse_mpl, facecolor="none", edgecolor=_color, fill=False, lw=0.4)
			#
		#
		_color = color[0]
		#
		_a_instance = self.m_instances[0]
		_b_instance = self.m_instances[1]
		#
		points = _b_instance["graph_data"]["sort_by_length"]
		iter_point = int(self.rad_search_box.get())
		#
		if len(list(points.items())) > iter_point:
			#
			do_rad_search(self, _a_instance, _b_instance, iter_point, plt, _color) # subsequent rad searches
			#
		#
		plt.show()
		#

if __name__ == '__main__':
	#
	#_p = pip(gd_garamond_bld, gd_garamond_reg)
	_p = pip(gd_garamond_bld, gd_garamond_reg)
	#
	o = MainObject(_p)
	o.run()

	
