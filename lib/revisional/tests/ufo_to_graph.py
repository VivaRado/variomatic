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

from fontParts.world import *
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
#
from context import sample
from pnt import *
from geom import *
#
import draw
#
from fitCurves import *
#
debug = False
offset_y = 0
offset_x = 0
dir_path = os.path.dirname(os.path.realpath(__file__))
#
sys.path.insert(0, os.path.join(dir_path,'helpers'))
#
from graph import Graph
#
font_path_r = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
font_path_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
#
print(font_path_r)
print(font_path_b)
color = ["red","blue","green","cyan", "magenta", "orange", "yellow"]
#
g = Graph()
g.addVertex(1,[10,100])
#
print(g)
#
for x in g.getVertices():
	#
	#t = tuple(v.id for v in g.getVertex(x).connectedTo.keys())
	#
	print(x)
	v = g.getVertex(x).crd
	print(v)

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
def make_glyph(_g_dat,_name):
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
	#print(f_g.box)
	#
	return f_g
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
#
class vrmstart():

	def __init__(self, g_data_a, plt_num, inst_num, cont_num):
		super(vrmstart, self).__init__()
		self.made_letters = {}
		self.m_instances = {}
		self.g_data_a = g_data_a
		#self.g_data_b = g_data_b
		self.plt_num = plt_num
		self.agreed_matches = collections.OrderedDict()
		self.sgrad = collections.OrderedDict()
		self.inst_num = inst_num
		self.cont_num = cont_num
		
	#
	#
	def make_instance_contours(self, inst, num):
		#
		#c = num
		x = self.g_data_a
		#for x in [self.g_data_a, self.g_data_b]:
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
		self.made_letters = {
			"glyph":made_g,
			"box": made_g.box, # (left_x,bottom_y,y_top,x_right)
			"box_center": [x_mm, y_mm],
			"cont":num,
			"inst":inst,
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
		#c = c + 1
		#
		#
		get_box_center_diff_x = self.made_letters["box_center"][0]# - self.made_letters[1]["box_center"][0]
		#get_box_center_diff_y = self.made_letters[0]["box_center"][1] - self.made_letters[1]["box_center"][1]
		#
		#
		# d = 0
		# for let, val in self.made_letters.items():
		# 	#
		# 	f_g = self.made_letters[d]["glyph"]
		# 	#
		# 	if d == 1:
		# 		#
		# 		f_g.moveBy((get_box_center_diff_x, get_box_center_diff_y))
		# 		#
		# 		f_g.changed()
		# 		#
		# 	#
		# 	d = d + 1
		# 	#
		# # #
		#i = num
		#
		#for x in [self.g_data_a, self.g_data_b]:
		#
		root = ET.fromstring(x)
		#
		g_name = root.attrib['name']
		#
		made_g = self.made_letters["glyph"]
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
		self.made_letters["coords"]["orig"] = g_orig
		self.made_letters["coords"]["graph"] = g_strt_coord
		self.made_letters["coords"]["strt"] = g_strt
		#
		#i = i + 1
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
run_specific = "a"
#
inst  = 0
#
insts = [font_path_r, font_path_b]
#
var_inst = {}
#
for u in insts:
	#
	with open(os.path.join(u,'contents.plist'), 'rb') as f:
		#
		pl = plistlib.load(f)
		#
		for x in pl.items():
			#
			if run_specific != "":
				#
				if run_specific == x[1].split(".glif")[0]:
					#
					#print ('\n'+tcolor.WARNING + "RUNNING: " + run_specific + tcolor.ENDC)
					#
					print(x)
					is_file_a = os.path.isfile(os.path.join(u,x[1]))
					#is_file_b = os.path.isfile(os.path.join(font_path_b,x[1]))
					#
					if is_file_a:# and is_file_b:
						#
						root_a = ET.parse( os.path.join(u,x[1]) ).getroot()
						#root_b = ET.parse( os.path.join(font_path_b,x[1]) ).getroot()
						#
						conts = {}
						#
						dist_sorted_a = get_distance_sorted_contours(root_a)
						#dist_sorted_b = get_distance_sorted_contours(root_b)
						#
						#
						for y in range(len(dist_sorted_a)):
							#
							c_a = dist_sorted_a[y]
							#c_b = dist_sorted_b[y]
							#
							if c_a:# and c_b:
								#
								input_contours = [c_a]
								#
								_p_st = vrmstart(c_a,0,insts,y)
								#
								conts[y] = _p_st.make_instance_contours(inst, y)
								#
								points = np.asarray(conts[y]["coords"]["strt"])
								#
								conts[y]["beziers"] = fitCurve(points, 0)
								#
								print(conts[y]["box_center"])
								#
								conts[y]["graph"] = _p_st.make_topo(conts[y], color[inst])
								#
									#
								#
						#
						var_inst[inst] = conts
						#var_inst[inst]["name"] = u
						#
						for k,v in conts.items():
							#
							_a = 0
							#
							if v["inst"] > 0:
								#
								_a = 1
								#
							#
							print('-------------------')
							print(v["cont"],v["inst"])
							print(v["cont"]+v["inst"]+_a)
							#
							draw.draw_instance_graphs_c(v["cont"]+_a+v["inst"], v)
							#
		#pprint.pprint(var_inst)
	
	inst = inst + 1
			
plt.show()
		#
		#time.sleep(10)
