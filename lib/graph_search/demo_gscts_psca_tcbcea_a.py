#
import os
import time
import json
import pprint
import difflib
import fontTools
import numpy as np
import collections
from pylab import *
from rdp import rdp
from bezier import *
from tkinter import *

import networkx as nx
import itertools as it
from numpy import array
from fitCurves import *
from simple_path import *
from fontParts.world import *
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from svgPathPen import SVGPathPen
from itertools import combinations
import xml.etree.ElementTree as ET
from collections import OrderedDict
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from networkx.readwrite import json_graph
from networkx.algorithms import isomorphism
from svgpathtools import parse_path as pt_parse_path
from svgpath2mpl import parse_path as mpl_parse_path
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
#
from glyph_strings import *
#

hide_labels = False

color = ["red","blue"]


#################################
#################################
#################################
import math

def dot(v,w):
	x,y = v
	X,Y = w
	return x*X + y*Y# + z*Z

def length(v):
	x,y = v
	return math.sqrt(x*x + y*y)

def vector(b,e):
	x,y = b
	X,Y = e
	return (X-x, Y-y)

def unit(v):
	x,y = v
	mag = length(v)
	return (x/mag, y/mag)

def distance(p0,p1):
	return length(vector(p0,p1))

def scale(v,sc):
	x,y = v
	return (x * sc, y * sc)

def add(v,w):
	x,y = v
	X,Y = w
	return (x+X, y+Y)

# Malcolm Kesson 16 Dec 2012

def pnt2line(pnt, start, end):
	line_vec = vector(start, end)
	pnt_vec = vector(start, pnt)
	line_len = length(line_vec)
	line_unitvec = unit(line_vec)
	pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
	t = dot(line_unitvec, pnt_vec_scaled)    
	if t < 0.0:
		t = 0.0
	elif t > 1.0:
		t = 1.0
	nearest = scale(line_vec, t)
	dist = distance(nearest, pnt_vec)
	nearest = add(nearest, start)
	return (dist, nearest)

#
def area(corners):
	#
	n = len(corners) # of corners
	area = 0.0
	for i in range(n):
		j = (i + 1) % n
		area += corners[i][0] * corners[j][1]
		area -= corners[j][0] * corners[i][1]
	area = abs(area) / 2.0
	#
	return area
	#
#################################
#################################
#################################


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
	s_circle = plt.Circle(v_c, rad, color=_color, alpha=0.5, lw=1, fill=_fill)
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
	for z in difference:
		#
		#print("ignore", z[2])
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
		#

	#
	return ignore_num
	#
def get_agreements(_p, _ag_a):
	#
	ret_matching = []
	#
	for k,v in _ag_a.items():
		#
		#print(v[0], _p)
		#
		if v[0] == _p:
			#
			found_match = True
			#
			#print(k,v)
			#ret_matching.append(True)
			#
			return v[1][0]
			#
		#
		#
	#
def get_agreed(_p, _ag_a): #, _ag_b, points_a, points_b
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
	if len(ret_matching) == 0:
		#
		return False
		#
	#
def getPerpCoord(aX, aY, bX, bY, length):
	vX = bX-aX
	vY = bY-aY
	#print(str(vX)+" "+str(vY))
	if(vX == 0 or vY == 0):
		return 0, 0, 0, 0
	mag = math.sqrt(vX*vX + vY*vY)
	vX = vX / mag
	vY = vY / mag
	temp = vX
	vX = 0-vY
	vY = temp
	cX = bX + vX * length
	cY = bY + vY * length
	dX = bX - vX * length
	dY = bY - vY * length
	return int(cX), int(cY), int(dX), int(dY)

def drawLine2P(x,y,xlims,ax):
	_xrange = np.arange(xlims[0],xlims[1],0.1)
	A = np.vstack([x, np.ones(len(x))]).T
	k, b = np.linalg.lstsq(A, y)[0]
	ax.plot(_xrange, k*_xrange + b, 'k')

def make_ct(to_ct, cen_c, ax):
	#
	perps = []
	#
	for coords in to_ct:
		#
		x = coords[0]
		y = coords[1]
		#
		#_perp = getPerpCoord(cen_c[0], cen_c[1], x, y, 10000)
		_perp = getPerpCoord(cen_c[0], cen_c[1], x, y, 10000)
		#
		#_perp_virtual = getPerpCoord(cen_c[0], cen_c[1], x, y, 50)
		_perp_virtual = getPerpCoord(cen_c[0], cen_c[1], x, y, 50)
		#
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
		#prp2 = mpatches.ConnectionPatch([_perp_b_virtual[0],_perp_b_virtual[1]],[_perp_b_virtual[2],_perp_b_virtual[3]],"data",arrowstyle='<->,head_width=.15,head_length=.15', lw=0.5, color="g")
		#prp2 = mpatches.ConnectionPatch([cen_c[0], cen_c[1]],[x, y],"data",arrowstyle='<->,head_width=.15,head_length=.15', lw=0.5, color="g")
		#prp2.set_linestyle((0, (8,2)))
		#ax.add_patch(prp2)
		#
		perps.append([[_perp[0],_perp[1]],[_perp[2],_perp[3]],[_perp_b[0],_perp_b[1]],[_perp_b[2],_perp_b[3]]])
		#
	#
	return perps
	#

def get_ctx_len (lines, point, ax):
	#
	print('=++++++++++++++++++++++++')
	print(lines)
	# for x,y in lines.items():
	# 	#
	# 	print('=+++++++++++++++++++++')
	# 	print(y)
	prp1 = mpatches.ConnectionPatch([point[0], point[1]],[lines[1][0],lines[1][1]],"data", lw=2, color="red")
		#
	ax.add_patch(prp1)	
		#
	#
#
def is_increment(l):
	#
	if l[2] == l[1]+1 == l[0]+2:
		#
		return True
		#
	else:
		#
		return False
		#
	#
#

def is_increment_s(l):
	#
	if l[1] == l[0]+1:
		#
		return True
		#
	else:
		#
		return False
		#
	#
#
#
def barycentric(tri):
	#
	centerX = (tri[0][0] + tri[1][0] + tri[2][0]) / 3;
	centerY = (tri[0][1] + tri[1][1] + tri[2][1]) / 3;
	#
	return [centerX,centerY]
	#
#
def find_three(p,s,a):
	#
	_all = set(p) + set(s) + set(a)
	#
	print("######################################################")
	print("######################################################")
	print("######################################################")
	print("######################################################")
	print("######################################################")
	print(_all)
	print("######################################################")
	print("######################################################")
	print("######################################################")
	print("######################################################")
	print("######################################################")
	#

def do_line_check(_a_instance, _b_instance, l_s, l_t, ms_pn_s, mt_pn_s, scp_s, scp_t, _f, ax, bax, ls_p, lt_p, iter_point, ghost_points):
	#
	_a_ag = _a_instance["agreed"]
	points_a = _a_instance["graph_data"]["sort_by_length"]
	_b_ag = _b_instance["agreed"]
	points_b = _b_instance["graph_data"]["sort_by_length"]
	#
	r_c_a = do_rule_not_on_line( mt_pn_s, l_t)
	r_c_b = do_rule_not_on_line( ms_pn_s, l_s)
	#
	print("===================================")
	print("+++++++++++++++++++++++++++++++++++")
	print(r_c_a)
	print(r_c_b)
	print("+++++++++++++++++++++++++++++++++++")
	print("===================================")
	#
	# Center Transfer Method
	cen_a = list(points_a.items())[-1] 
	cen_b = list(points_b.items())[-1]
	#

	ignore_num = set()
	#
	#
	i = 0
	u = 0
	#
	#rule_check_exists_better = do_rule_check(_a_instance["inst"],_b_instance["coords"]["strt"], l_t, l_t, _f.m_instances) # rule check over existing agreed generated by the initial graph searches.
	##
	#for r in rule_check_exists_better:
		#
	#	pass
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
	iter_ls = l_s
	iter_lt = l_t
	iter_line = scp_s[0]
	iter_match = l_s_z
	iter_agg_a = _b_ag
	iter_agg_b = _a_ag
	iter_a = points_b
	iter_b = points_a
	#
	s_longest = len(scp_s[0]) > len(scp_t[0])
	#
	if s_longest:
		#
		iter_ls = l_t
		iter_lt = l_s
		iter_line = scp_t[0]
		iter_match = l_t_z
		iter_agg_a = _a_ag
		iter_agg_b = _b_ag
		iter_a = points_a
		iter_b = points_b
		#
	#
	matching_lines = []
	for x in iter_line:
		#
		inx_m = [s for s in iter_match if x == s[1]][0]
		#
		matching_bool = get_agreed(inx_m, iter_agg_a) # , iter_agg_b, iter_a, iter_b
		#
		matching_lines.append(matching_bool)
		#
	#
	'''
	Source
	Target

	SC = Search Center
	P = Pre
	A = Ante
	MP = Match Pre
	MA = Match Ante
	fMP = Following Match Pre
	pMP = Preceding Match Ante
	Col = “Collinear”
	x = Extra Point
	'''
	_SC = l_s[1]
	_P = l_s[0]
	_A = l_s[2]
	_MP = get_agreements(_P[1], _a_ag)
	_MA = get_agreements(_A[1], _a_ag)
	# fMP = 
	# pMP = 
	
	cen_c = cen_a[1]["coord"]
	sc_c = _SC[1]
	#
	to_ct = [
		_P[1],
		_SC[1],
		_A[1]
	]
	#
	perps_plot = make_ct(to_ct, cen_c, ax)
	#
	per_ct = []
	#
	c = 0
	#
	for cts in to_ct:
		#
		#draw_circle_on_coord([cts[0],cts[1]], bax, 2, "r")
		#
		sta_a = perps_plot[c][0]
		end_a = perps_plot[c][1]
		sta_b = perps_plot[c][2]
		end_b = perps_plot[c][3]
		#
		all_match = []
		all_match_len = []
		#
		draw_circle_on_coord(sta_a, ax, 1, "orange")
		#
		for lt in lt_p:
			#
			lt_x =lt[1][0]
			lt_y = lt[1][1]
			#
			draw_circle_on_coord([lt_x,lt_y], ax, 1, "orange")
			#
			#
			pnt_dist_a = pnt2line([lt_x,lt_y], sta_a, end_a) # point, sta_a, end
			pnt_dist_b = pnt2line([lt_x,lt_y], sta_b, end_b) # point, sta_a, end
			#
			#
			# lines met on line from center to current point
			_p_g = getPerpCoord(cts[0], cts[1],pnt_dist_b[1][0], pnt_dist_b[1][1], 5)
			prp1 = mpatches.ConnectionPatch([_p_g[0],_p_g[1]],[_p_g[2],_p_g[3]],"data", lw=0.5, color="g")
			ax.add_patch(prp1)
			# distance of those positions from current point
			t_b_dist = int(math.hypot(cts[0]-pnt_dist_b[1][0], cts[1]-pnt_dist_b[1][1]))
			#
			label([_p_g[0],_p_g[1]], t_b_dist, ax)
			#
			#
			t_a_dist = math.hypot(cts[0]-lt_x, cts[1]-lt_y)
			#
			pnt_dist_a = list(pnt_dist_a)
			#
			pnt_dist_a.insert(1, t_a_dist)
			#
			pnt_dist_a = tuple(pnt_dist_a)
			#
			new_match = [(lt[2],lt[3]), pnt_dist_a, [cts[0],cts[1]], [lt_x,lt_y], t_b_dist]
			#
			if new_match not in all_match:
				#
				all_match.append(new_match)
				#
			#
			prp1 = mpatches.ConnectionPatch([lt_x, lt_y],[pnt_dist_a[2][0],pnt_dist_a[2][1]],"data", lw=0.2, color="r")
			#
			ax.add_patch(prp1)	
			#
		#
		print("=======================++++++++++++++++")
		print("=======================++++++++++++++++")
		print("=======================++++++++++++++++")
		print(all_match)
		#
		for x in all_match:
			#
			l1 = x[2]
			l2 = x[1][2]
			l3 = x[3]
			#
			_area = area([l1,l2,l3])
			#
			x.insert(2, _area)
			x.insert(3, x[2]+x[1][0]+x[1][1])
			#
		#
		print("==================================")
		print("==================================")
		print("==================================")
		print("==================================")
		print("==================================")
		pprint.pprint(x)
		#
		#sorted_all_match = sorted(all_match, key=lambda x: x[3]+x[1][0])[:3]
		sorted_all_match = sorted(all_match, key=lambda x: x[3]+x[1][0])[:3]
		#
		for x in sorted_all_match:
			#
			print(x)
			#
			l1 = x[4]
			l2 = x[1][2]
			l3 = x[5]
			#
			t1 = plt.Polygon([l1,l2,l3], color='g',alpha=0.1)
			ax.add_patch(t1)
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
	#
	print('============================')
	print(iter_lt)
	print('============================')
	print("SC: ",_SC)
	print("Pre: ",_P)
	print("Ante: ",_A)
	print("MPre: ",_MP)
	print("MAnte: ",_MA)
	print('============================')
	print('============================')
	#
	#
	ctm_Pre = per_ct[0]
	ctm_SC = per_ct[1]
	ctm_SC_c = per_ct[1].copy()
	ctm_Ante = per_ct[2]
	#
	#ctm_SC_c = sorted(ctm_SC_c, key=lambda x: x[6])#sorted(ctm_SC_c,)
	#
	A_bar_orig = barycentric([_P[1],_SC[1],_A[1]])
	#
	print("==============")
	print("barycentric CENTER")
	print(A_bar_orig)
	
	print("==============")
	#
	print("PRE TRI ============================================")
	print("PRE TRI ============================================")
	print("PRE TRI ============================================")
	print("PRE TRI ============================================")
	print("PRE TRI ============================================")
	print(ctm_Pre)
	print(ctm_SC_c)
	print(ctm_Ante)
	#
	
	#
	triangle_comparisson(ax,bax,l_s, l_t, ctm_Pre,ctm_SC_c,ctm_Ante,to_ct, iter_point, A_bar_orig, ghost_points)
	#

	c = 0
	#

	per_ct[1] = sorted(per_ct[1], key=lambda x: x[1][0])
	
	for m in ctm_SC:
		#
		ctms = [ctm_Pre,ctm_Ante]
		#
		for _ctm in ctms:
			#
			x = 0
			#
			if m[0] == _ctm[0][0]:
				#
				try:
					if m[1][0] > _ctm[0][1][0]:
						
						#del ctm_SC_c[c]
						print("IGNORING FIRST IN ANTE OR PRE", m[0][0])
						ignore_num.add(m[0][0])
					#
				except Exception:
					pass
				#
		for z in r_c_a:
			#
			print("IGNORING NOT ON LINE", z)
			ignore_num.add(z)
			#
		#
		c = c + 1
		#

	# #
	print("PER_CT_LINES")
	print("PRE MATCHES:")
	pprint.pprint(per_ct[0])
	print("SC MATCHES:")
	pprint.pprint(ctm_SC_c)
	print("ANTE MATCHES:")
	pprint.pprint(per_ct[2])
	
	print("MATCH ========================================= ")

	#if len(ctm_SC_c) > 0:
		
	#	print(ctm_SC_c[0])
	#
	for p in ctm_Pre:
		#
		print(ctm_SC[0])
		#
		if p[0][0] != ctm_SC[0][0][0]:
			ignore_num.add(p[0][0])
		#
	#
	G1 = nx.Graph()
	G2 = nx.Graph()
	#
	node_color_map_a = []
	node_color_map_b = []
	#
	coord_lt_p =[]
	coord_l_s =[]
	#
	for x in range(len(lt_p)):
		#
		coord_lt_p.append(lt_p[x][1])
		#
	#
	for x in range(len(l_s)):
		#
		coord_l_s.append(l_s[x][1])
		#
	#
	lt_p_rdp = rdp(coord_lt_p, epsilon=5)
	l_s_rdp = rdp(coord_l_s, epsilon=5)
	#
	return ignore_num
	#
#
def midpoint(p1, p2):
	return [(p1[0]+p2[0])/2, (p1[1]+p2[1])/2]

def angle(p1, p2, rads=False):
	
	_rads = math.atan2(p1[1]-p2[1], p1[0]-p2[0])

	if rads == True:
		#
		_res = _rads
		#
	else:
		#
		_res = int(math.degrees(_rads))
		#
	return _res

def label(xy, text, tx):
	#
	#y = xy[1] # shift y-value for label so that it's below the artist
	_text = str(text)+'°'
	tx.text(xy[0],xy[1], text, ha="center", family='monospace', rotation=text, size=6, bbox=dict( boxstyle="round",ec=(1, 1, 1,0.3),fc=(1, 1, 1,0.3),alpha=0.4))
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
	
	#
	#
	print("=======================================================")
	print("=======================================================")
	print("=======================================================")
	print("=======================================================")
	print("SEQUENCE LISTS")
	print(seq_lists)
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
			print('INSTANCE BBBBBBBBBBBBBBBB')
			print('biggest_line==============')
			print(biggest_line)
			print(coords[0])
			print(coords[0][3])
			result = [element for element in coords if element[3] == all_nums[0]]
			print("--------------------====-------")
			print(result)
			print("----------------------------")
			print(coords)
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
			print(sorted_total)
			#
			line_start_point = result[0][3]# coords[0][3]
			print(line_start_point)
		#
	else:
		#
		print('INSTANCE AAAAAAAAAAAAAAAAAA')
		print(coords)
		print(coords[0][3])
		line_start_point = coords[0][3]
		#
	#
	#inx_ignore = [seq_lists.index(ls) for ls in seq_lists if line_start_point not in ls]
	#
	#print("ignore_indexes", inx_ignore)
	print("line_start_point", line_start_point)
	#
	ignore_set = set()
	#
	if len(seq_lists) != 0:

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
				if srt_num not in scp and inum == 0:
					#
					ignore_set.add(x[2])
					#

		#
		#ni = int(not(inum))

		#
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print("LINE ===========")
		print(scp,ignore_set)
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
def plot_region_line(tx, coords, _c, scp, all_points):
	#
	'''
	Draw lines only for points that are in sequence.
	'''
	#
	i = 0
	first_ploted = False
	#
	coord_line = []
	#
	#
	#
	for x in coords:
		#
		print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
		print(x)
		#
		if i == len(coords)-1:
			pass
		else:
			#
			srt_num = x[3]
			end_num = coords[i][3]
			#
			#if coords[i+1][3] in scp:
				#
				#
			_p = mpatches.ConnectionPatch(x[1],coords[i+1][1],"data", lw=1, arrowstyle='->,head_width=.15,head_length=.15', shrinkB=7, color=_c,label='Label')
			tx.add_patch(_p)
			#
		#if x[3] in scp:
		# if i == len(coords)-1:
		# 	#
		# 	#if coords[i][3] in scp:
		# 	#
		# 	coord_line.append(x)
		# 	#
		# 	#
		# else:
		# 	#
		# 	if coords[i+1][3] in scp:
		# 		#
		# 		coord_line.append(x)
		# 		#
		#
		coord_line.append(x)
		#
		i = i + 1
		#
	#
	print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
	print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
	print(coord_line)
	#
	return coord_line
	#
#
def get_line_inx(numpoints, num, loc):
	#
	print("POINTS", numpoints)
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
			print("A")
			#
			return 1
			#
		#
		else:
			#
			print("B")
			print(numpoints, num)
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
# (item_next_coord,points_b,l_s)
def get_points_around(item_next_coord, points_a,points_b, l_s, a_items, b_items, _plt, _color, ax, bax):
	#
	#
	matched_target = []
	max_radius = 50# compute max radius from thegeneral distances average
	#
	center_a = points_a.get(a_items[-1])["coord"]
	#
	print(a_items)
	print(points_a)
	print("--------------",center_a)
	#
	missing_points = []
	#
	for z in l_s:
		#
		#
		p_c = 0
		#v_c = v["coord"]
		if _plt:
			#
			t_psca_coord = z[1]#points_b.get(a_items[p_c])["coord"]
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
						#
						t_b_dist = math.hypot(t_b_coord[0]-item_next_coord[0], t_b_coord[1]-item_next_coord[1])
						#
						new_match = [t_b_dist,t_b_coord,p_c,t_b_order]
						#
						if new_match not in matched_target:
							
							matched_target.append(new_match)
							#
							if _plt:
								#
								pp1 = mpatches.ConnectionPatch(z[1],t_b_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
								pp1.set_linestyle((0, (2,4)))
								ax.add_patch(pp1)
								draw_circle_on_coord(t_b_coord, ax, 2, "g")
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
		if found_p == False:
			#
			if z not in missing_points:
				#
				missing_points.append(z)
				#
			print("ERROR FOUND NO POINT FOR",z)
			#
		#

		#
	#
	print("MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS")
	print("MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS")
	print("MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS")
	print("MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS, MISSING POINTS")
	print(missing_points)
	#
	sorted_cont_target = sorted(matched_target, key = lambda x: x[3])#sorted(matched_target)
	#
	return [sorted_cont_target, missing_points]
	#
#
def evaluate_psca(_P,_SC,_A, iter_point):
	#
	#print(_P)
	#
	#lpoint = [s for s in _SC if iter_point == s[0][0]][0]
	#lpoint_inx = lpoint[0][1]
	#
	#print('\t================')
	#print(lpoint)
	#print(lpoint_inx)
	#
	__p = [c[0][1] for c in _P]
	__sc = [c[0][1] for c in _SC]
	__a = [c[0][1] for c in _A]
	#
	#s_num = __p[0]
	#
	c_a__p = [x for x in __p if x != __sc[0]]
	c_a__sc = [x for x in __sc if x != __p[0]]
	c_a__a = [x for x in __a if x != __sc[0]]
	#c_b__p = [x for x in c_a__p if x not in __a]
	#
	incs = []
	#
	for x in __p:
		#
		for y in c_a__sc:
			#
			for z in c_a__a:
				#
				#
				is_inc = is_increment([x,y,z])
				is_inc_l = is_increment_s([x,y])
				is_inc_r = is_increment_s([y,z])
				#
				#print("\t###############################")
				#print(x,y,z,is_inc, is_inc_l,is_inc_r)
				#
				if x!=y and y!=z and z!=x:
					#
					if [x,y,z] not in incs:
						#
						#if is_inc_l or is_inc_r:
							
						incs.append([x,y,z])	
						#
					
					#
				#
				else:
					#
					print([x,y,z], "FAIL LINE")
					#

				#if is_inc: # increment without last or first point reset...
					#
			#
	#
	# print("###############################")
	# print("###############################")
	# pprint.pprint(incs)
	# #
	# print("P")
	# print(__p)
	# print("SC")
	# print(c_a__sc)
	# print("A")
	# print(c_a__a)
	# #
	#print(incs)
	if len(incs) > 0:
		#
		#print(incs[0][1])
		#
		best_match = [s for s in _SC if incs[0][1] == s[0][1]]
		#
		#print("BEST MATCH")
		#print(best_match)
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
def triangle_comparisson(ax,bax,l_s,l_t,ctm_Pre,ctm_SC_c,ctm_Ante, to_ct, iter_point, A_bar_orig, ghost_points):

	#
	ev_psca = evaluate_psca(ctm_Pre,ctm_SC_c,ctm_Ante, iter_point)
	#

	ctm_SC_c = sorted(ctm_SC_c, key=lambda x: x[2])
	
	
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print('\t============================??????')
	# print(ev_psca)
	# print('\t============================??????+++')
	# print(ctm_Pre,'\n', ctm_SC_c, '\n', ctm_Ante)
	# print('\t============================??>>>>>')
	# #
	match_polygons = []
	#
	############################### 
	# Make Polygons from Target PSCA
	for x in ev_psca:
		#
		tl1 = [s for s in l_t if x[0] == s[3]][0]
		tl2 = [s for s in l_t if x[1] == s[3]][0]
		tl3 = [s for s in l_t if x[2] == s[3]][0]
		#
		#
		# print("000000000000000000000000000")
		# print(l_t)
		# print(x)
		# print(tl1)
		# print('')
		# print(tl2)
		# print('')
		# print(tl3)
		#
		# is_sub = False
		# #
		# for y in match_polygons:
		# 	#
		# 	if tl1[1] in y and tl2[1] in y and tl3[1] in y:
		# 		is_sub = True
		# 		break
		# 	#
		# #
		# if is_sub == False:
			
		match_polygons.append([tl1[1],tl2[1],tl3[1]])
		#
		t1 = plt.Polygon([tl1[1],tl2[1],tl3[1]], color='b',alpha=0.02, linewidth=0.5)
		bax.add_patch(t1)
		#
		#print("000000000000000000000000000")
		#
	#
	############################### 
	# Make Polygon from Source PSCA
	#
	#
	l1 = l_s[0][1]
	l2 = l_s[1][1]
	l3 = l_s[2][1]
	#
	#move_tri(l1,l2,l3)
	#
	#print("============================================ANGLES")
	Pbcea = angle(A_bar_orig,to_ct[0], True)
	Sbcea = angle(A_bar_orig,to_ct[1], True)
	Abcea = angle(A_bar_orig,to_ct[2], True)
	aPbcea = angle(A_bar_orig,to_ct[0])
	aSbcea = angle(A_bar_orig,to_ct[1])
	aAbcea = angle(A_bar_orig,to_ct[2])
	#print("ANGLE Pbcea", Pbcea, aPbcea)
	#print("ANGLE Sbcea", Sbcea, aSbcea)
	#print("ANGLE Abcea", Abcea, aAbcea)
	#
	st_barextlen = []
	#
	for st in [l1,l2,l3]:
		#
		barextlen = distance(st,A_bar_orig)
		#
		st_barextlen.append(int(barextlen))
		#
	#
	s_area = area([l1,l2,l3])
	#
	match_barycentric = []
	#
	for t_tri in match_polygons:
		#
		now_bar = barycentric(t_tri)
		#
		#
		A_bar_np = np.array(A_bar_orig)
		now_bar_np = np.array(now_bar)
		diff_bar = A_bar_np-now_bar_np
		#
		o_tri = [l1,l2,l3]
		s_tri = move_tri([l1,l2,l3], diff_bar)
		A_bar = move_tri([A_bar_orig], diff_bar)[0]
		#s_tri = move_tri([to_ct[0],to_ct[1],to_ct[2]], diff_bar)[0]
		#
		t1 = plt.Polygon(s_tri, color='r',alpha=0.02, linewidth=0.5)
		bax.add_patch(t1)
		#
		#
		draw_circle_on_coord(A_bar, bax, 3, "r")
		#
		#
		draw_circle_on_coord(now_bar, bax, 1, "b")
		#
		for s_p in s_tri:
			#
			#print("=====", s_p, A_bar)
			#
			draw_circle_on_coord(s_p, bax, 1, "r")
			pp1 = mpatches.ConnectionPatch(A_bar,s_p,"data", lw=0.2, color="r")
			bax.add_patch(pp1)
			#
		# for c in to_ct:
		# 	#
		# 	pp1 = mpatches.ConnectionPatch(A_bar,c,"data", lw=0.5, color="r")
		# 	bax.add_patch(pp1)
		# 	#
		
		print(A_bar,t_tri)
		#
		#print("============================================ANGLES M")
		PMbcea = angle(now_bar,t_tri[0], True)
		SMbcea = angle(now_bar,t_tri[1], True)
		AMbcea = angle(now_bar,t_tri[2], True)
		aPMbcea = angle(now_bar,t_tri[0])
		aSMbcea = angle(now_bar,t_tri[1])
		aAMbcea = angle(now_bar,t_tri[2])
		#print("ANGLE PMbcea", PMbcea, aPMbcea)
		#print("ANGLE SMbcea", SMbcea, aSMbcea)
		#print("ANGLE AMbcea", AMbcea, aAMbcea)
		#
		match_angles = [PMbcea, SMbcea, AMbcea]
		match_ang = [aPMbcea, aSMbcea, aAMbcea]
		match_diffs = [ Pbcea - PMbcea, Sbcea - SMbcea, Abcea - AMbcea]
		match_tot = (Pbcea - PMbcea) + (Sbcea - SMbcea) + (Abcea - AMbcea)
		#
		tri_zip = zip(match_ang, [aPbcea, aSbcea, aAbcea])
		#
		is_similar_angle = []
		#
		for z in tri_zip:
			#
			is_similar_angle.append(math.isclose(z[0],z[1], abs_tol=30))
			#
			#print(">>>", z[0],z[1],math.isclose(z[0],z[1], abs_tol=30) )
			#
		#
		tt_barextlen = []
		#
		for tt in t_tri:
			#
			barextlen = distance(list(now_bar),tt)
			#
			tt_barextlen.append(int(barextlen))
			#
		#
		s_sc = o_tri[1]
		t_sc = t_tri[1]
		#
		t_area = area(t_tri)
		#
		is_sc_distance = distance(s_sc,t_sc)
		#
		#print(s_sc,'====',t_sc, '+++++', dist)
		#
		pp1 = mpatches.ConnectionPatch(s_sc,t_sc,"data", lw=0.2, color="gray")
		bax.add_patch(pp1)
		#
		#is_sc_distance = dist
		#
		#
		a = np.array(match_ang)
		b = np.array([aPbcea, aSbcea, aAbcea])
		c = a-b
		#
		match_barycentric.append([match_polygons.index(t_tri),match_angles, match_diffs, match_tot, match_ang, sum(c), is_similar_angle, is_sc_distance, abs(s_area - t_area), tt_barextlen, tt_barextlen[1]])
		# #
		for p in t_tri:
			#
			pp1 = mpatches.ConnectionPatch(now_bar,p,"data", lw=0.2, color="b")
			bax.add_patch(pp1)
			#
		#
	#
	diff_list = []
	#
	sorted_barmatch = sorted(match_barycentric, key=lambda x: (x[4] == [aPbcea, aSbcea, aAbcea], x[9] == st_barextlen, x[10] == st_barextlen[1], x[6]), reverse=True)#(x[1]-1Pbcea, x[1][1]-Sbcea, x[1][2]-Abcea))
	#
	print("====>>>", [aPbcea, aSbcea, aAbcea], st_barextlen, st_barextlen[1])
	pprint.pprint(sorted_barmatch)
	#
	
	try:
		
		best_m = match_polygons[match_barycentric.index(sorted_barmatch[0])]
		#
		print("best_match=============================")
		print(sorted_barmatch[0])
		print(best_m)
		print(best_m[1])

		check_not_ghost = check_coord_ghost(best_m[1], ghost_points)

		if check_not_ghost == False:
			#
			draw_circle_on_coord(best_m[1], bax, 15, "g")
			#
		else:
			#	
			draw_circle_on_coord(best_m[1], bax, 15, "r")
			#

		print("best_match=============================")
	except Exception as e:
		pass
	#
	###############################
#
def check_coord_ghost(best_point, ghost_points):
	#
	is_ghost = False
	#
	for x in ghost_points:
		#
		print("GHOST_POINT")
		#
		if x[1] == best_point:
			#
			print("ERROR BEST POINT DOESNT EXIST", best_point)
			#
			is_ghost = True
			#
		#
	#
	return is_ghost
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
		# snum = get_next_num(idx,points)
		# #
		# print(len(points) - 1 , idx, snum,item)
		# #
		if not idx or item-1 != seq_lists[-1][-1]:
			
			seq_lists.append([item])
		else:

			seq_lists[-1].append(item)
	#
	return seq_lists
	#
def rotate_points(sorted_cont_target, points):
	#
	c = [el[3] for el in sorted_cont_target]
	#
	orders = collections.deque(c)
	orders_true = collections.deque(sorted_cont_target)
	#
	l_inx = len(points)
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
		seq_lists = get_seq(c)
		# print(seq_lists)
		# print(l_inx)
		for x in seq_lists:
			#
			if l_inx in x:
				#
				rotation = len(x)
				#
				orders.rotate(rotation)
				orders_true.rotate(rotation)
				#
			#
		#
	#
	return list(orders_true)
	#
#
def fix_line (scp_t, points):
	#
	print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
	print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
	print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
	print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
	print(scp_t)
	#
	return scp_t
	#
#
def do_rad_search(_f, _a_instance, _b_instance, iter_point, _plt=False, _color=False):
	#
	#
	if _plt:
		#
		_plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
		#
		_a_plt = _plt.figure(0)
		_b_plt = _plt.figure(1)
		#
		_a_plt.tight_layout()
		_b_plt.tight_layout()
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
	#if len(list(points_b.items())) > iter_point:
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
					v["circle"] = plt.Circle(item_next_coord, 10, color=_color[0], fill=False, alpha=0.5, lw=0.5)
					#
					v["circle"].set_radius(0)
					v["circle"].set_linestyle((0, (2,4)))
					#
					ax.add_patch(v["circle"])
					#
				#
			#
	#
	
	#
	matched_target = []
	matched_source = []
	#
	if _plt:
		#
		draw_circle_on_coord(item_next_coord, ax, 15, "g", False)
		#
	#
	f_p_x = item_next_coord[0]#
	f_p_y = item_next_coord[1]#sorted_cont[0][1][1]
	#l_p_x = sorted_cont_target[-1][1][0]
	#l_p_y = sorted_cont_target[-1][1][1]
	#f_p_b_x = sorted_cont_target[0][1][0]
	#f_p_b_y = sorted_cont_target[0][1][1]
	#
	t_fnl_d = 200#math.hypot(f_p_x-l_p_x, f_p_y-l_p_y) + 50 # target_first_and_last_distance
	#
	p_d = 0
	for k,v in points_a.items():
		#
		if k!=(0,0):
			t_a_coord = points_a.get(a_items[p_d])["coord"]
			t_a_order = points_a.get(a_items[p_d])["order"]
			#
			t_circle = [t_a_coord,t_fnl_d]
			#
			#print(">>>",item_next_coord)
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
	ignore_num = set()
	#rule_check_exists_better = set()
	rule_check_line_match = set()
	#
	scp_s = [[],set()]
	scp_t = [[],set()]
	#
	if _plt:
		#
		# sorted by length number
		ms_pn_s = sorted(matched_source, key = lambda x: x[3])
		
		#
		dist = lambda x, y: (x[1][0]-y[1][0])**2 + (x[1][1]-y[1][1])**2
		#closest_b = min(mt_pn_s, key=lambda co: dist(co, [[],item_next_coord]) - co[3])
		#
		#print("CLOSEST B")
		#print(closest_b)
		#
		# print("ITERATED POINT")
		# print(iter_point)
		# print("MATCHED SOURCE")
		# print(ms_pn_s)
		#print("MATCHED TARGET")
		#print(mt_pn_s)
		#
		# print("==============")
		# print("==============")
		# print("==============")
		# print("==============")
		# print("==============")
		# print(iter_point)
		f_s = next(c for c in ms_pn_s if c[2] == iter_point)
		#print("PRE SC ANTE")
		#print(get_line_inx(len(points_a), f_s[3], "p"))
		#print(f_s)
		#print(get_line_inx(len(points_a), f_s[3], "a"))
		#
		f_pre = next(c for c in ms_pn_s if c[3] == get_line_inx(len(points_a), f_s[3], "p"))
		f_ant = next(c for c in ms_pn_s if c[3] == get_line_inx(len(points_a), f_s[3], "a"))
		#

		#
		#print("FOUND START")
		#print(f_pre)
		#print(">",f_s)
		#print(f_ant)
		#
		s_ip_inx = ms_pn_s.index(f_s)###next(c for c in ms_pn_s if c[2] == iter_point)####np.where(s_ip_np[2]==iter_point)#[idx_s for idx_s, s in enumerate(ms_pn_s) if iter_point == int(s[2])][0]
		#t_ip_inx = mt_pn_s.index(sorted_cont_target[0])#mt_pn_s.index(next(c for c in mt_pn_s if c[2] == iter_point))#np.where(t_ip_np[2]==iter_point)#[idx_t for idx_t, t in enumerate(mt_pn_s) if iter_point == int(t[2])][0]
		#
		l_s = [f_pre,f_s,f_ant]#ms_pn_s[s_ip_inx-1:] # get all after current iterated point in source, observer is minus one point
		#
		#
		points_arr = get_points_around(item_next_coord,points_a,points_b,l_s, a_items, b_items, _plt, _color, ax, bax)
		ghost_points = points_arr[1]
		#
		#_f.ghost_points = ghost_points
		#
		l_t = points_arr[0]
		#
		l_t = rotate_points(l_t, b_items)
		#
		for p in l_t:
			#
			p.append("real")
			#
		for g in ghost_points:
			#
			g.append("ghost")
			#
		#
		l_t = l_t + ghost_points
		#
		print("POINT ROTATE ===++++++++++++++++++++++++++++")
		print(l_t)
		# #
		# #l_t = mt_pn_s#[t_ip_inx-1:] # get all after current iterated point in target, minus one point
		# #
		# print("INDEXED SOURCE")
		# print(l_s)
		# print("INDEXED TARGET")
		# print(l_t)
		# #
		
		#
		scp_s = [[f_pre[3],f_s[3],f_ant[3]],set()]#get_point_line(l_s, "r", _f, 0)
		scp_t = get_point_line(l_t, "b", _f, 1, points_b)
		#
		scp_t = fix_line(scp_t, points_b)
		#
		# print("---------------POINTED SOURCE")
		# print(scp_s)
		# print("---------------POINTED TARGET")
		# print(scp_t)
		#
		mt_pn_s = sorted(l_t, key = lambda x: x[3])
		#
		ls_ploted = plot_region_line(ax, l_s, "r", scp_s[0],points_a)
		#lt_ploted = plot_region_line(bax, l_t_clip, "b", scp_t[0],points_b)
		#
		print("############################################")
		print("############################################")
		print("############################################")
		print("############################################")
		print(scp_t[0])
		#
		lt_ploted = plot_region_line(bax, l_t, "b", scp_t[0],points_b)
		#
		# print("PLOTED SOURCE")
		# print(ls_ploted)
		# print("PLOTED TARGET")
		# print(lt_ploted)
		# #
		#if len(l_s) > 2 and len(l_t) > 2: # if there is a line enough for comparisson
		#
		do_l_check = do_line_check(_a_instance, _b_instance, l_s, l_t, ms_pn_s, mt_pn_s, scp_s, scp_t, _f, ax, bax, ls_ploted, lt_ploted, iter_point, ghost_points)
		#
		# print("RESULTS")
		# print(do_l_check)
		#
		#rule_check_line_match = set(list(do_l_check)+list(scp_s[1])+list(scp_t[1])) # rule check over existing agreed generated by the initial graph searches.
		#
		#else:
			#
		#	rule_check_line_match = set()
			#

		#
	# get current node number lengthwise
	points_a = _a_instance["graph_data"]["sort_by_length"]#[1:]
	new_dict = [a for a, b in points_a.items() if item_next_coord == b["coord"]][0]
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
		#print("box_diff")
		#print(get_box_diff_x, get_box_diff_y)
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
			made_g = self.made_letters[i]["glyph"]
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
							#
							print(k)
							#
							edge_label_map[k] = str(v["len"])
							node_label_map[v["node"]] = str(n)+'\n'+str(k[1])
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
		root.geometry("100x100+1600+0")
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
		self.rad_search_box.insert(0,15)
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

		nx.draw(_g,pos,node_size=node_width_map, node_color = node_color_map, edge_color=edge_color_map, width=edge_width_map, node_shape='o')
		#
		if hide_labels == False:
			#
			nx.draw_networkx_edge_labels(_g,pos,edge_labels=edge_label_map,font_size=7, font_family='monospace', bbox=dict( boxstyle="round",ec=(1, 1, 1,0.3),fc=(1, 1, 1,0.3),alpha=0.4))
			#
		nx.draw_networkx_labels(_g,pos,node_label_map,font_size=5.5, font_color='white', font_family='monospace', font_weight='bold')
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
			move_figure(t_plt, _movepos, _movepos+100,i*_movepos+100,_movepos)
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
		#len_sorted = _a_instance["graph_data"]["sort_by_length"]
		#
		#do_surface_search(self, _a_instance, _b_instance, iter_point, len_sorted, plt) # initial rad search to cover the agreed for each instances
		#
		plt.show()
		#

if __name__ == '__main__':
	#
	_p = pip(gd_garamond_bld, gd_garamond_reg)
	#_p = pip(gar_bld_b, gar_reg_b)
	#_p = pip(glifData_a_reg, glifData_a_thn)
	#_p = pip(glifData_a_thn, glifData_a_reg)
	#
	o = MainObject(_p)
	o.run()

	
