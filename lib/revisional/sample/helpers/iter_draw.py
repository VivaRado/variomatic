#
import draw
import geom
from tkinter import *
from colors import color
#
class IterDraw(object):
	"""docstring for IterDraw"""
	def __init__(self, instances, GC, plt):
		super(IterDraw, self).__init__()
		self.instances = instances
		self.plt = plt
		self.GC = GC
		#self.run_sp = 'a'
		#
	#
	def run(self):
		#
		root = Tk()
		#
		root.geometry("100x100+1800+0")
		#
		frame = Frame(root, relief=SUNKEN, borderwidth=1)
		frame.pack(side=LEFT, fill=Y)
		label = Label(frame, text='Max Error')
		label.pack()
		self.val_smp = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_simplification_value_change)
		self.val_smp.delete(0,"end")
		self.val_smp.insert(0,0)
		self.val_smp.pack()
		label_iter = Label(frame, text='Iteration')
		label_iter.pack()
		self.val_pnt = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_point_value_change)
		self.val_pnt.delete(0,"end")
		self.val_pnt.insert(0,0)
		self.val_pnt.pack()
		#
		self._smp = 0
		self._pnt = 0
		#
		# if self.run_sp != "":
		# 	#
		# 	self.val_smp.delete(0,"end")
		# 	self.val_smp.insert(0,0)
		# 	self.val_pnt.delete(0,"end")
		# 	self.val_pnt.insert(0,0)
			#
		self.redraw(True, True)
		#
	#
	def on_simplification_value_change(self):
		#
		self.redraw(True, True)
		#
	#
	def on_point_value_change(self):
		#
		self.redraw(False, True)
		#
	#
	def make_iter(self, _val_smp, _val_pnt, redraw_smp, redraw_pnt, _plt=False):
		#
		if _val_smp == False and _val_pnt == False:
			#
			_val_smp = int(self.val_smp.get())
			_val_pnt = int(self.val_pnt.get())
			#
		#
		for instance in self.instances:
			#
			for letter in self.instances[instance]:
				#
				for contour in self.instances[instance][letter]:
					#
					t_contour = self.instances[instance][letter][contour] # this
					points_lenwise = list(t_contour["graph_data"]["sort_by_length"].values())
					inst_inx = t_contour["inst"]
					cont_inx = t_contour["cont"]
					#
					t_plot = draw.get_gca(t_contour["plot_num"], self.plt)
					t_color = color[inst_inx]
					#
					# Draw Graphs
					#
					if int(_val_smp) in t_contour["simplified"].keys():
						#
						# Recalculate Graph according to simplified match index if _val_smp is changed shown by redraw_smp = True
						#
						if redraw_smp:
							#
							t_contour["graph"] = None
							t_contour = self.GC.make_instance_topo(t_contour, t_color,_val_smp)
							#
						#
						draw.draw_instance_graphs_c(t_contour)
						#
					#
					# Draw Start Point (After Graph because erase plot)
					#
					contour_start_point = t_contour["coords"]["graph"][0]
					draw.draw_circle_on_coord(contour_start_point, t_plot, 20, t_color, False)
					#
					if redraw_pnt:
						#
						contour_t_pnt = points_lenwise[_val_pnt]["coord"]
						draw.draw_circle_on_coord(contour_t_pnt, t_plot, 12, t_color, False)
						#
						#t_simp = t_contour["simplified"][_val_smp]
						#contour_t_pnt = t_simp[_val_pnt-1]
						#
						#if len(t_simp) >= _val_pnt-1:
						#
						#print(self.instances[instance][letter][contour]["graph_data"])
						#
						#__point = list(t_contour["graph_data"]["sort_by_length"].values())[_val_pnt]["coord"]
						#
						#print(__point)
						#
						#g_coord_flip = geom.flipCoordPath([contour_t_pnt],False,True)
						#print(g_coord_flip)
						#
						#
						#
					#
					# if redraw_pnt:
					# 	#
					# 	contour_t_pnt = t_contour["coords"]["strt"][_val_pnt-1]
					# 	g_coord_flip = geom.flipCoordPath([contour_t_pnt],False,True)
					# 	#
					# 	draw.draw_circle_on_coord(g_coord_flip[0], t_plot, 15, t_color, False)
					# 	#

	def redraw(self, graph, ctt):
		#
		self.make_iter(0,0,graph,ctt,self.plt)
		#
		self.plt.show(block = False)
		#