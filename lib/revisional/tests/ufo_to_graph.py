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
debug = False
#
dir_path = os.path.dirname(os.path.realpath(__file__))
#
sys.path.insert(0, os.path.join(dir_path,'helpers'))
#
from tkinter import *
#
#
from context import sample
from pnt import *
from geom import *
import draw
#
from shapely_simp import *
from fitCurves_b import *
from colors import tcolor
#
from contour_holder import ContourHolder
from graph_constructor import GraphConstructor
#
color = ["red","blue","green","cyan", "magenta", "orange", "yellow"]
#

#



#
font_instance_a = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Regular.ufo', 'glyphs') )
font_instance_b = os.path.abspath(os.path.join(dir_path, '..', 'input_data', 'AGaramondPro-Bold.ufo', 'glyphs') )
#
run_specific = "a"
instance_list = [font_instance_a, font_instance_b]
simplification = list(range(0,50))#[0,1,2,3,4,5,6,7,8,9,10]
#
inst_counter = 0
instance_dict = {}
#
'''
ContourHolder
	ContourNormalizer
GraphConstructor
GraphEvaluator
InstanceMatcher
	PointNormalizer
'''
#
class IterDraw(object):
	"""docstring for IterDraw"""
	def __init__(self, instances):
		super(IterDraw, self).__init__()
		self.instances = instances
		self.run_sp = 'a'

		#
	#
	def run(self):
		#
		root = Tk()
		#
		# if self.plt_num == 0:
		# 	#
		root.geometry("100x100+1600+0")
		# 	#
		# else:
		# 	#
		# 	root.geometry("100x100+1700+0")
		# 	#
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
		if self.run_sp != "":
			#
			self.spinbox.delete(0,"end")
			self.spinbox.insert(0,0)
			self.rad_search_box.delete(0,"end")
			self.rad_search_box.insert(0,0)
			#
		self.redraw()
		#
		#
	#
	def on_matching_value_change(self):
		#
		#self.init_instances() # repeat in case of simplification
		#
		self.redraw()
		#
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

		for x in self.instances: # instance
			#
			for y in self.instances[x]: # letter
				#
				for z in self.instances[x][y]: # contour
					#
					inst_inx = self.instances[x][y][z]["inst"]
					cont_inx = self.instances[x][y][z]["cont"]
					#
					#print("INST INX", inst_inx)
					#print("CNT INX", cont_inx)
					#print("SIMP VALUE", val_simplification)
					#
					if int(val_simplification) in self.instances[x][y][z]["simplified"].keys():
						#

						#
						print("---")
						print(val_simplification, self.instances[x][y][z]["simplified"][int(val_simplification)])
						#
						#self.instances[x][y][z] = GC.make_instance_topo(self.instances[x][y][z], color[inst_inx],0)
						self.instances[x][y][z]["graph"] = None
						self.instances[x][y][z] = GC.make_instance_topo(self.instances[x][y][z], color[inst_inx],int(val_simplification))
						#
						print("GRAPH", self.instances[x][y][z]["graph"])
						#
						draw.draw_instance_graphs_c(self.instances[x][y][z])

	def redraw(self):
		#
		self.make_iter(0,0,plt)
		#
		plt.show(block = False)
		#
#
total_list = {}
#
'''
total_list = {
	instance_int:{
		"glyph_name":{
			contours
		}
	}
}
'''
#
for font_inst in instance_list:
	#
	total_list[inst_counter] = {}
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
						#
						CH = ContourHolder(os.path.join(font_inst, t_pl), debug)
						#
						glyph = CH.get(inst_counter,"glyph")
						#
						total_list[inst_counter][glyph] = {}
						#
						g_orig_coord = CH.get_glif_coord(glyph,'get_type')
						#
						#print(g_orig_coord)
						#
						contours = total_list[inst_counter][glyph]
						#
						for cnt in range(CH.len):
							#
							GC = GraphConstructor(CH,instance_list,cnt, inst_counter, simplification, debug)
							#
							contours[cnt] = GC.initiate_instance(inst_counter, cnt, CH)
							#
							points = np.asarray(contours[cnt]["coords"]["strt"])
							#
							contours[cnt]["simplified"] = OrderedDict()
							#
							for simp in simplification:
								#
								simplified_points = simplif(points, simp)
								#
								contours[cnt]["simplified"][simp] = simplified_points#fitCurve(points, float(simp)**2)
								#
							#
						#
					#
				#
			#
		#
	#
	inst_counter = inst_counter + 1
	#
#
#pprint.pprint(total_list)
initiate_drawing = IterDraw(total_list)
#
initiate_drawing.run()
#
plt.show()
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