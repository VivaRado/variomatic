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
#
from networkx import *
from networkx.readwrite import json_graph
from networkx.algorithms import isomorphism
#
from fontParts.world import *
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
#
from context import sample
from pnt import *
from geom import *
import draw
from fitCurves_b import *
#
debug = False
offset_y = 0
offset_x = 0
dir_path = os.path.dirname(os.path.realpath(__file__))
#
sys.path.insert(0, os.path.join(dir_path,'helpers'))
#
color = ["red","blue","green","cyan", "magenta", "orange", "yellow"]
#
class ContourNormalizer(object):
	"""
	Get contours ordered and unidirectional from path string
	"""
	def __init__(self, path):
		#
		root = ET.parse( path ).getroot()
		#
		split_conts = self.split_contours_to_glifs(root)
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
			made_g = self.make_glyph(str_g,g_name)
			#
			made_g = self.orient_contour_direction(made_g)
			#
			self.made_g = made_g
			#
			g_strt_coord = self.get_glif_coord(made_g,'corner')
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
			dist_sorted.append([dist, str_g, made_g])
			#
		#
		dist_sorted_sort = sorted(dist_sorted, key = lambda x: x[0], reverse=True) # largest first
		#
		self.sorted = dist_sorted_sort
		#
		if debug:
			#
			print("SORT BY DISTANCE")
			print(dist_sorted_sort)
			#
		#
	#
	def get_glif_coord(self, made_g, _type):
		#
		p_arr = []
		#
		for contour in made_g:
			#
			for point in contour.points:
				#
				if _type == 'corner':
					#	
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
		#
		return p_arr
		#
	#
	def orient_contour_direction(self, g):
		#
		for contour in g:
			#
			if contour.clockwise == False:
				#
				contour.reverse()
				#
			#
		#
		g.update()
		#
		return g
		#
	#
	def split_contours_to_glifs(self, root):
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
					#
					pass
					#
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
			#
			else:
				pass
			#
		#
		return cont_glif
		#
	#
	def make_glyph(self, _g_dat,_name):
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
	def get(self, inx, _type):
		#
		if _type == "string":
			#
			to_get = 1
			#
		elif _type == "glyph":
			#
			to_get = 2
			#
		#
		return [item[to_get] for item in self.sorted][inx]

	@property
	def len(self):
		return len(self.sorted)

#
class BoundingBox(object):
	"""
	A 2D bounding box
	"""
	def __init__(self, points):
		if len(points) == 0:
			raise ValueError("Can't compute bounding box of empty list")
		self.minx, self.miny = float("inf"), float("inf")
		self.maxx, self.maxy = float("-inf"), float("-inf")
		for x, y in points:
			# Set min coords
			if x < self.minx:
				self.minx = x
			if y < self.miny:
				self.miny = y
			# Set max coords
			if x > self.maxx:
				self.maxx = x
			elif y > self.maxy:
				self.maxy = y
	@property
	def width(self):
		return self.maxx - self.minx
	@property
	def height(self):
		return self.maxy - self.miny
	@property
	def value_mid(self):
		#
		_mx_x = self.maxx
		_mn_x = self.minx
		_mx_y = self.maxy
		_mn_y = self.miny
		#
		mid_x = (_mx_x + _mn_x) / 2
		mid_y = (_mx_y + _mn_y) / 2
		#
		return [mid_x,mid_y]
		#
	def __repr__(self):
		#
		return "BoundingBox({}, {}, {}, {})".format(
			self.minx, self.maxx, self.miny, self.maxy)


class GraphConstructor():

	def __init__(self, dist_sort_cont, inst_num, cont_num):
		super(GraphConstructor, self).__init__()
		self.made_letters = {}
		self.m_instances = {}
		self.dist_sort_cont = dist_sort_cont
		self.g_data_a = self.dist_sort_cont.get(cont_num,"string")
		#self.plt_num = plt_num
		self.agreed_matches = collections.OrderedDict()
		self.sgrad = collections.OrderedDict()
		self.inst_num = inst_num
		self.cont_num = cont_num
		#
	#
	def initiate_instance(self, inst, num, CN ):
		#
		glyph = CN.get(num,"glyph")
		#
		g_strt_coord = CN.get_glif_coord(glyph,'corner')
		g_orig_coord = CN.get_glif_coord(glyph,'original')
		#
		bbox = BoundingBox(g_orig_coord)
		#
		x_mm = bbox.value_mid[0]
		y_mm = bbox.value_mid[1]
		#
		g_orig = flipCoordPath(g_orig_coord,False,True)
		g_strt = flipCoordPath(g_strt_coord,False,True)
		#
		self.instance = {
			"glyph":glyph,
			"box": bbox,
			"box_center": [x_mm, y_mm],
			"cont":num,
			"inst":inst,
			"coords":{
				"orig": g_orig,
				"strt": g_strt,
				"graph": g_strt_coord
				},
			"graph":None,
			"graph_json":{},
			"agreed":{},
			"surfaced":{}
		}
		#
		return self.instance
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
		#
		list_of_tuples = list(tuple(x) for x in myPath)
		#
		return list_of_tuples
		#
	#
	def make_instance_topo(self, f_g, _color):
		#
		l_tp = self.bez_to_list(f_g["beziers"])
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
			#
			node_color_map = []
			edge_width_map = []
			node_width_map = []
			edge_color_map = []
			edge_label_map = {}
			node_label_map = {}
			node_order_map = OrderedDict()
			#
			if f_g["graph"] != None:
				#
				_g = f_g["graph"]
				_g.clear()
				#
			else:
				#
				f_g["graph"] = nx.Graph()
				_g = f_g["graph"]
				#
			#
			x_mm = f_g["box"].value_mid[0]
			y_mm = f_g["box"].value_mid[1]
			#
			g_coord_flip_simp = g_coord_flip.copy()
			g_coord_flip.insert(0,[x_mm,y_mm])
			#
			for x in range(len(g_coord_flip)):
				#
				_g.add_edge(0,x)
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
			pos = nx.get_node_attributes(_g,'pos')
			#
			edge_lengths = self.get_edge_lengths(_g, pos)
			sorted_length = sorted(edge_lengths.items(), key=lambda k: k[1]['len'], reverse=True)
			sort_by_length = OrderedDict(sorted_length)
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
font_instance_a = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
font_instance_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
#
run_specific = "a"
instance_list = [font_instance_a, font_instance_b]
simplification = 0
#
inst_counter = 0
instance_dict = {}
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
						CN = ContourNormalizer(os.path.join(font_inst, t_pl))
						#
						contours = {}
						#
						for cnt in range(CN.len):
							#
							GC = GraphConstructor(CN,instance_list,cnt)
							#
							contours[cnt] = GC.initiate_instance(inst_counter, cnt, CN)
							#

							points = np.asarray(contours[cnt]["coords"]["strt"])
							#
							#
							contours[cnt]["beziers"] = fitCurve(points, float(simplification)**2)
							#
							contours[cnt]["graph"] = GC.make_instance_topo(contours[cnt], color[inst_counter])
							#
						#
						instance_dict[inst_counter] = contours
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
				#
			#
		#
	#
	inst_counter = inst_counter + 1
	#
			
plt.show()