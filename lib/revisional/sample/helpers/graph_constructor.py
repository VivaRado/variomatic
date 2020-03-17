import collections
from collections import OrderedDict
from networkx import *
from networkx.readwrite import json_graph
from networkx.algorithms import isomorphism
from geom import *

class GraphConstructor():

	def __init__(self, dist_sort_cont, inst_num, cont_num,inst_counter, simps, plt_num, debug):
		super(GraphConstructor, self).__init__()
		self.made_letters = {}
		self.m_instances = {}
		self.dist_sort_cont = dist_sort_cont
		self.g_data_a = self.dist_sort_cont.get(cont_num,"string")
		self.agreed_matches = collections.OrderedDict()
		self.sgrad = collections.OrderedDict()
		self.inst_num = inst_num
		self.cont_num = cont_num
		self.simps = simps
		self.plt_num = plt_num
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
			"graphs":{},
			"plot_num":self.plt_num,
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
	def get_sorted_from_graph(self,_g):
		#
		pos = nx.get_node_attributes(_g,'pos')
		#
		edge_lengths = self.get_edge_lengths(_g, pos)
		sorted_length = sorted(edge_lengths.items(), key=lambda k: k[1]['len'], reverse=True)
		sort_by_length = OrderedDict(sorted_length)
		#
		return sort_by_length
		#
	#
	def make_instance_topo(self, f_g, _color, simp):
		#
		#l_tp = self.bez_to_list(f_g["beziers"])
		#
		l_tp = f_g["simplified"][simp]#list(f_g["simplified"].values())[simp]
		# list()[simp]#self.bez_to_list(f_g["beziers"])
		#
		g_coord_flip = flipCoordPath(l_tp,False,True)
		#
		if f_g["graph"] != None:
			#
			_g = json_graph.node_link_graph(f_g["graph_json"])
			#f_g["graph"]
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
			sort_by_length = self.get_sorted_from_graph(_g)
			#
			pos = nx.get_node_attributes(_g,'pos')
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
	def make_instance_topo_b(self, f_g, _color, simp):
		#
		#l_tp = self.bez_to_list(f_g["beziers"])
		#
		l_tp = f_g["simplified"][simp]#list(f_g["simplified"].values())[simp]
		# list()[simp]#self.bez_to_list(f_g["beziers"])
		#
		g_coord_flip = flipCoordPath(l_tp,False,True)
		#

		#
		node_color_map = []
		edge_width_map = []
		node_width_map = []
		edge_color_map = []
		edge_label_map = {}
		node_label_map = {}
		node_order_map = OrderedDict()
		#
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
		sort_by_length = self.get_sorted_from_graph(_g)
		#
		pos = nx.get_node_attributes(_g,'pos')
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
		graph_data = {
			"node_color_map":node_color_map,
			"edge_width_map":edge_width_map,
			"node_width_map":node_width_map,
			"edge_color_map":edge_color_map,
			"edge_label_map":edge_label_map,
			"node_label_map":node_label_map,
			"node_order_map":node_order_map,
			"g_coord_flip_simp":g_coord_flip_simp,
			"sort_by_length":sort_by_length,
			"graph_json":json_graph.node_link_data(_g)
		}
		# f_g["graph_data"] = {
		# 	"node_color_map":node_color_map,
		# 	"edge_width_map":edge_width_map,
		# 	"node_width_map":node_width_map,
		# 	"edge_color_map":edge_color_map,
		# 	"edge_label_map":edge_label_map,
		# 	"node_label_map":node_label_map,
		# 	"node_order_map":node_order_map,
		# 	"g_coord_flip_simp":g_coord_flip_simp,
		# 	"sort_by_length":sort_by_length
		# }
		#
		return [sort_by_length, graph_data]
		#f_g["graph_json"] = json_graph.node_link_data(_g)
			#
		#
		#return f_g