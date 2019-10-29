import networkx as nx
from networkx.readwrite import json_graph
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

from gpathwrite import *
from svgpath2mpl import parse_path as mpl_parse_path

color = ["red","blue"]
offset_y = 700
offset_x = 50
hide_labels = False
#
def label(xy, text, tx, _size=5, _pos=10, _color = "k"):
	#
	#_text = text
	#print(xy[0],xy[1])
	#tx.text(xy[0],xy[1], text, ha="center", family='monospace', rotation=text, size=6, bbox=dict( boxstyle="round",ec=(1, 1, 1,0.3),fc=(1, 1, 1,0.3),alpha=0.4))
	tx.text(xy[0],xy[1]+_pos, text, color=_color, ha="center", family='monospace', size=_size, bbox=dict( boxstyle="round",ec=(1, 1, 1,0.3),fc=(1, 1, 1,0.3),alpha=0.4))
	#

def draw_circle_on_coord(coords, ax, rad, _color, _fill=True, _return=False):
	#
	v_c = coords
	#
	s_circle = plt.Circle(v_c, rad, color=_color, alpha=0.2, lw=1, fill=_fill)
	#
	if _return == True:
		#
		return s_circle
		#
	else:
		#
		ax.add_patch(s_circle)
		#

#
def draw_points_b(points,item_next_coord,_color,plots):
	#
	for k,v in points.items():
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
			plots.add_patch(v["circle"])
			#
		#
	#

#
def init_plots(_plt, plt_num):
	#
	#
	if plt_num == 0:
		#
		_plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
		#
		plt_nums = [0,1]
		#
	else:
		#
		plt_nums = [2,3]
		#
	#
	_a_plt = _plt.figure(plt_nums[0])
	_b_plt = _plt.figure(plt_nums[1])
	#_c_plt = _plt.figure(plt_num)
	#
	_a_plt.tight_layout()
	_b_plt.tight_layout()
	#_c_plt.tight_layout()
	#
	ax = _a_plt.gca()
	bax = _b_plt.gca()
	#cax = _c_plt.gca()
	#t = get_t(ax)
	#
	return [ax,bax]
	#

def init_plot_comb(_plt):
	#
	#
	_plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
	#
	_c_plt = _plt.figure(4)
	#
	_c_plt.tight_layout()
	#
	cax = _c_plt.gca()
	#
	return cax
	#

def get_t(ax):
	#
	t = mpl.transforms.Affine2D().translate(offset_x,-offset_y) + ax.transData
	#
	return t
	#
#

def move_figure(f,w,h, x, y):
	"""Move figure's upper left corner to pixel (x, y)"""
	backend = mpl.get_backend()
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
def draw_instance_graphs(_self):
	#
	_movepos = 500
	#
	plt_num = _self.plt_num
	#
	if plt_num == 0:
		#
		plt_nums = [0,1]
		#
	else:
		#
		plt_nums = [2,3]
		#
	#
	x = 0 
	#
	for i in plt_nums:
		#
		t_plt = plt.figure(i)
		#
		x_move = _movepos + 45
		y_move = _movepos + 150
		#
		if i == 0 or i == 2:
			#
			x_move = 0

		if i == 0 or i == 1:

			y_move = 0
			#
		#
		glyph_path = writeGlyphPath(_self.m_instances[x]["glyph"], True)
		parse_mpl = mpl_parse_path(glyph_path)
		#
		move_figure(t_plt, _movepos, _movepos+100,x_move,y_move)
		#
		draw_topo(_self.m_instances[x], t_plt, x, parse_mpl)
		#
		x = x + 1
		#
	#
def draw_topo(instance, _plt, i, glyph_path):
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
	
	
	patch = mpatches.PathPatch(glyph_path, facecolor="none", edgecolor=_color, fill=False, lw=0.4)
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