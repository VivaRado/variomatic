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
def do_rule_check(inst_num,t_coords,t_contents, _f_pip):
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
							ignore_num.add(y_num)
							#
						#
					#
				#
			#
		#
	#
	return ignore_num
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
	points = _b_instance["graph_data"]["sort_by_length"]
	item_next_coord = list(_a_instance["graph_data"]["sort_by_length"].values())[iter_point]["coord"]
	#
	if len(list(points.items())) > iter_point:
		#
		c_items = []
		#
		for k,v in points.items():
			#
			c_items.append(k)
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
		t_contents = []
		#
		if _plt:
			#
			draw_circle_on_coord(item_next_coord, ax, 15, "g", False)
			#
		#
		for k,v in points.items():
			#
			#
			if k!=(0,0):
				#
				c_rad = 0
				#
				contains = False
				#
				#
				max_radius = 150
				#
				for x in range(max_radius):
					#
					t_coord = points.get(c_items[p_c])["coord"]
					#
					t_circle = [t_coord,c_rad]
					#
					contains = in_circle(item_next_coord,t_circle)
					#
					if contains:
						#
						Path = mpath.Path
						#
						t_dist = math.hypot(t_coord[0]-item_next_coord[0], t_coord[1]-item_next_coord[1])
						#
						t_contents.append([t_dist,t_coord,p_c])
						#
						if _plt:

							pp1 = mpatches.ConnectionPatch(t_coord,item_next_coord,"data", linestyle= "dashed", lw=0.5, color=_color[0])
							pp1.set_linestyle((0, (2,4)))
							ax.add_patch(pp1)
							draw_circle_on_coord(t_coord, ax, 5, "g")
							
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
		sorted_cont = sorted(t_contents)
		# get current node number lengthwise
		points_a = _a_instance["graph_data"]["sort_by_length"]
		new_dict = [a for a, b in points_a.items() if item_next_coord == b["coord"]][0]
		t_node = list(points_a.keys()).index(new_dict)
		#
		ignore_num = set()
		#
		#if _plt:
			#
		#	ignore_num = do_rule_check(_b_instance["inst"],_b_instance["coords"]["strt"], sorted_cont, _f.m_instances) # rule check over existing agreed generated by the initial graph searches.
			#
		#
		c_sorted_cont = sorted_cont.copy()
		#
		for z in sorted_cont:
			#
			if z[2] in ignore_num: #or t_node in ignore_num:
				#
				draw_circle_on_coord(z[1], bax, 10, "r", False)
				#
				c_sorted_cont.remove(z)
				#
			#
		#
		if _plt:
			#
			for x in c_sorted_cont:
				#
				draw_circle_on_coord(x[1], bax, 20, "g", False)
				#
			#
		#
		if _plt:
			#
			if len(c_sorted_cont) > 0:
				#
				sorted_first = c_sorted_cont[0][1]
				#
				draw_circle_on_coord(sorted_first, bax, 20, "g")
				#
			#
		#
		else:
			#
			_a_instance["agreed"][t_node] = [item_next_coord,c_sorted_cont]
			_f.pip.agreed_matches[t_node] = [item_next_coord,c_sorted_cont]
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
	'''
	def scalePath(self, p, w_x, w_y):
		#
		
		defs = p
		for i in range(len(p)):
			if w_x > 0:
				defs[i][0] *= w_x
				print()
			elif w_y > 0:
				defs[i][1] *= w_y
			# elif defs[3][i] == 'r':         # radius parameter
				# 	params[i] *= x
				# elif defs[3][i] == 's':         # sweep-flag parameter
				# 	if x*y < 0:
				# 		params[i] = 1 - params[i]
				# elif defs[3][i] == 'a':         # x-axis-rotation angle
				# 	if y < 0:
				# 		params[i] = - params[i]
		return p

	'''

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
	def center_glyphs(self, f_g):
		#
		print(f_g)
		#
		# Center Glyphs
		
		#
		#print(x_mm, y_mm)
		#
		# #
		# Do scale
		# #
		#####################
		'''
		scale = 1
		#
		if f_g.width < 443:
			#
			#
		#
		print(scale)
		#
		f_g.changed()
		#
		print('=-_______')
		#
		print(f_g)
		'''
		#
		#####################
		#
		# #
		# Do move
		# #
		#####################
		#
		scale = 1
		#
		if f_g.width < 443:
			#
			scale = (443 / f_g.width)
			#
			#f_g.scaleBy((scale, 1), f_g.width/2)
			f_g.scaleBy((scale, 1), non)
			f_g.changed()
			#
			#f_g.moveBy((26/2, 0))
			#f_g.changed()
			#

			#f_g.changed()
			#
			#f_g.moveBy((26, 0))
			#
			#
		#
		print('=-_______')
		#
		print(f_g)
		#
		#####################
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
		print("box_diff")
		print(get_box_diff_x, get_box_diff_y)
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
		#
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
		#
		for edge in _g.edges():
			#
			startnode=edge[0] 
			endnode=edge[1]
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
				edge_width_map.append(1)
				node_width_map.append(70)
				#
			#
			pos=nx.get_node_attributes(_g,'pos')
			#
			edge_lengths = self.get_edge_lengths(_g, pos)
			#
			sort_by_length = OrderedDict(sorted(edge_lengths.items(), key=lambda k: k[1]['len'], reverse=True))
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
					if i  == n:
						#
						if k != (0,0):
							#
							edge_label_map[k] = str(v["len"])
							node_label_map[v["node"]] = str(n)
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
			f_g["graph_data"] = {
				#"pos":pos,
				"node_color_map":node_color_map,
				"edge_width_map":edge_width_map,
				"node_width_map":node_width_map,
				"edge_color_map":edge_color_map,
				"edge_label_map":edge_label_map,
				"node_label_map":node_label_map,
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
		self.spinbox.insert(0,0)
		self.spinbox.pack()
		label_iter = Label(frame, text='Iteration')
		label_iter.pack()
		self.rad_search_box = Spinbox(frame, width=8, from_=0, to=1000000, command=self.onSpinBoxValueChange)
		self.rad_search_box.insert(0,0)
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
		ax.plot(simp_xPts,simp_yPts,color=_color,lw=0.2)
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
		_movepos = 500
		#
		for i in range(len(self.m_instances.items())):
			#
			t_plt = plt.figure(i)
			#
			move_figure(t_plt, 500, 700,i*_movepos,500)
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
	_p = pip(gd_garamond_bld, gd_garamond_reg)
	#
	o = MainObject(_p)
	o.run()

	
