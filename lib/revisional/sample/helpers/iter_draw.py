#
import draw
import geom
from tkinter import *
from colors import color
import pprint
import time
import matplotlib.lines as lines
#
def get_perp(ct, rep):
	#
	if rep == "virt":
		#
		list_x = [ct[0][0],ct[1][0]]
		list_y = [ct[0][1],ct[1][1]]
		#
	elif rep == "real":
		#
		list_x = [ct[2][0],ct[3][0]]
		list_y = [ct[2][1],ct[3][1]]
		#
	#
	#
	return list_x, list_y
	#
#

def tc_get_pca(t_contour,simp_level,conf_inx,pos):
	#
	if pos == "p":
		#
		get_pos = 0
		#
	elif pos == "c":
		#
		get_pos = 1
		#
	elif pos == "a":
		#
		get_pos = 2
		#
	#
	return t_contour["perp_simp"][simp_level][conf_inx][get_pos]
	#
#
#
class IterDraw(object):
	"""docstring for IterDraw"""
	def __init__(self, instances, GC, plt, simplification):
		super(IterDraw, self).__init__()
		self.instances = instances
		self.plt = plt
		self.GC = GC
		self.simplification = simplification
		#self.run_sp = 'a'
		#
	#
	def draw_cts(self, t_contour):
		#
		inst_inx = t_contour["inst"]
		cont_inx = t_contour["cont"]
		#
		t_plot = self.plt.figure(t_contour["plot_num"])
		t_gca = t_plot.gca()
		t_color = color[inst_inx]
		#
		for x,y in t_contour["simplified"].items():
			#
			simp_level = self.simplification[x]
			#
			if x == 0: # example one level 0 of simplification / removing will run whole simplification list
				#
				for z in y: # points
					#
					t_coord = geom.flipCoordPath([z],False,True)[0]
					#
					#graph_point_from_coord = tc_get_point_b_coord(t_contour,simp_level,t_coord)
					#
					conf_inx, conf_dat = self.tc_get_simp_conf_b_coord(t_contour,simp_level,t_coord)
					#
					pca_crd_c = tc_get_pca(t_contour,simp_level,conf_inx,"c")
					#
					list_x, list_y = get_perp(pca_crd_c, "virt")
					#
					line = lines.Line2D(list_x,list_y, lw=1., color=t_color, alpha=0.4)
					#
					t_gca.add_line(line)
	#
	def tc_get_simp_conf_b_coord(self, t_contour, simp_level, coordinate):
		#
		confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate][0]
		confine_index = t_contour["confines_simp"][simp_level].index(confine_from_coord)
		#
		return confine_index, confine_from_coord
		#
	#
	def run(self):
		#
		root = Tk()
		#
		root.geometry("100x100+1800+0")
		#
		frame = Frame(root, borderwidth=1)
		frame.pack(side='top')
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
		#root.update()
		# if self.run_sp != "":
		# 	#
		# 	self.val_smp.delete(0,"end")
		# 	self.val_smp.insert(0,0)
		# 	self.val_pnt.delete(0,"end")
		# 	self.val_pnt.insert(0,0)
			#
		self.redraw(True, True)
		#
		#root.mainloop()
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
		# if _val_smp == False and _val_pnt == False:
		# 	#
		# 	_val_smp = int(self.val_smp.get())
		# 	_val_pnt = int(self.val_pnt.get())
		# 	#
		# #
		for instance in self.instances:
			#
			for letter in self.instances[instance]:
				#
				for contour in self.instances[instance][letter]:
					#
					t_contour = self.instances[instance][letter][contour] # this
					#pprint.pprint(self.instances[instance][letter][contour])
					#
					#print(_val_smp)
					#
					points_lenwise = list(t_contour["graphs"][_val_smp].values())
					inst_inx = t_contour["inst"]
					cont_inx = t_contour["cont"]
					#
					#
					t_plot = _plt.figure(t_contour["plot_num"])
					#
					t_plot.clf()
					#
					t_gca = t_plot.gca()
					#t_plot = draw.get_gca(t_contour["plot_num"], self.plt)
					t_color = color[inst_inx]
					#
					# Draw Graphs
					#
					if _val_smp in t_contour["simplified"].keys():
						#
						# Show Graph according to simplified match index if _val_smp is changed shown by redraw_smp = True
						#
						#if redraw_smp:
							#
						c_graph = t_contour["graphs_data"][_val_smp]#self.GC.make_instance_topo(t_contour, t_color,_val_smp)
							#
						#
						draw.draw_instance_graphs_c(t_contour,c_graph)
						#
					#
					# Draw Start Point (After Graph because erase plot)
					#
					contour_start_point = t_contour["coords"]["graph"][0]
					#
					#print(contour_start_point)
					#
					draw.draw_circle_on_coord(contour_start_point, t_gca, 20, t_color, False)
					#
					#draw.draw_circle_on_coord(contour_start_point, t_gca, 20, t_color, False)
					#
					#print(t_contour["matching"])
					
					try:
						#print("CONFINES -----")
						#print(t_contour["confines_simp"][_val_smp])
						#
						coord_ct = [item[1] for item in t_contour["confines_simp"][_val_smp][_val_pnt]]
						#
						draw.plot_region_line(t_gca, coord_ct, t_color, _plt)
						#
						self.draw_cts(t_contour)
						
						for x in t_contour["matching"][_val_smp]:
							#
							print(">>>")
							pprint.pprint(x)
							#
							# ct branch		
							# [ lt_crd[0], pnt_dist_b[1][0] ], [ lt_crd[1], pnt_dist_b[1][1] ]
							list_x, list_y = [x[5][0], x[2][1][0]],[x[5][1], x[2][1][1]]
							# print(list_x,list_y)
							line = lines.Line2D(list_x,list_y, lw=1, color="g", alpha=0.4)
							t_gca.add_line(line)
							#
							poly = _plt.Polygon(x[12], color='green',alpha=0.05, linewidth=0.2)
							t_gca.add_patch(poly)
							#
							draw.draw_circle_on_coord(x[13][1], t_gca, 2, "g")
							#
							# circl = plt.Circle(x[13][1], x[13][4], color=t_color, fill=False, alpha=0.5, lw=0.5)
			
							# circl.set_radius(x[13][4])
							# circl.set_linestyle((0, (2,4)))
							
							# t_gca.add_patch(circl)
							#print("SIMP CONFINES")
							#print(t_contour["confines_simp"][_val_smp][_val_pnt])
							#print("SIMP CONFINES SING")
							#print(t_contour["confines"][_val_pnt])
							#
							#coord_ct = [item[1] for item in t_contour["confines"][_val_pnt]]
							#coord_ct = [item[1] for item in t_contour["confines_simp"][_val_smp][_val_pnt]]
							#
							#
							#
					except Exception as e:
						#
						print(e)
						#
						pass
						#
					#
					try:
						if redraw_pnt:
							#
							#print("REDRAW PNT")
							#
							draw.draw_circle_on_coord(contour_start_point, t_gca, 20, t_color, False)
							#
							contour_t_pnt = points_lenwise[_val_pnt]["coord"]
							draw.draw_circle_on_coord(contour_t_pnt, t_gca, 12, t_color, False)
							#
							t_simp = t_contour["simplified"][_val_smp]
							contour_t_pnt = t_simp[_val_pnt-1]
							#
							#__point = list(t_contour["graph_data"]["sort_by_length"].values())[_val_pnt]["coord"]
							__point = list(t_contour["graphs"][_val_smp].values())[_val_pnt]["coord"]
							#
							#print(__point)
							#
							g_coord_flip = geom.flipCoordPath([contour_t_pnt],False,True)
							print(g_coord_flip)
							#
							draw.draw_perp_recum(t_contour["recu_simp"][_val_smp][_val_pnt], t_gca)
							#
							coord_ct = [item[1] for item in t_contour["confines_simp"][_val_smp][_val_pnt]]
							#
							draw.plot_region_line(t_gca, coord_ct, t_color, _plt)
							#
							self.draw_cts(t_contour)
							
							for x in t_contour["matching"][_val_pnt]:
								#
								print(">>>")
								pprint.pprint(x)
								#
								# ct branch		
								# [ lt_crd[0], pnt_dist_b[1][0] ], [ lt_crd[1], pnt_dist_b[1][1] ]
								list_x, list_y = [x[5][0], x[2][1][0]],[x[5][1], x[2][1][1]]
								# print(list_x,list_y)
								line = lines.Line2D(list_x,list_y, lw=1, color="g", alpha=0.4)
								t_gca.add_line(line)
								#
								poly = _plt.Polygon(x[12], color='green',alpha=0.05, linewidth=0.2)
								t_gca.add_patch(poly)
								#
								draw.draw_circle_on_coord(x[13][1], t_gca, 2, "g")
								#
							#
					except Exception as e:
						pass
						
						#pprint.pprint(t_contour)
						#
						
							#
						#	print(x)
							#print("A MATCH")
							#print(y)
							#for z in y:
							#	print(z)
								# ct branch		# [ lt_crd[0], pnt_dist_b[1][0] ], [ lt_crd[1], pnt_dist_b[1][1] ]
								# list_x, list_y = [z[5][0], z[2][1][0]],[z[5][1], z[2][1][1]]
								# print(list_x,list_y)
								# line = lines.Line2D(list_x,list_y, lw=1, color="g", alpha=0.4)
								# t_gca.add_line(line)
							#
						#draw.plot_region_line(t_gca, coord_ct, t_color, _plt)
						#
						#_perp_actual = geom.getPerpCoord(prp[0][0], prp[0][1], prp[1][0], prp[1][1], 1000)
					#
					'''
					for x,y in t_contour["simplified"].items():
						#
						print("-------------------")
						print(x,y)
						print(inst_inx, cont_inx)
						#
						simp_level = self.simplification[x]
						#
						if x == 0: # example one level 0 of simplification / removing will run whole simplification list
							#
							for z in y: # points
								#
								t_c = geom.flipCoordPath([z],False,True)[0]
								graph_point_from_coord = [d for d in list(t_contour["graphs"][simp_level].values()) if d['coord'] == t_c][0]
								#
								point_inx = y.index(z)+1
								#
								confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == t_c][0]
								inx_conf = t_contour["confines_simp"][simp_level].index(confine_from_coord)
								#
								perp_from_inx = t_contour["perp_simp"][simp_level][inx_conf]
								ct_c = perp_from_inx[1]
								#
								list_x = [ct_c[0][0],ct_c[1][0]]
								list_y = [ct_c[0][1],ct_c[1][1]]
								#
								line = lines.Line2D(list_x,list_y, lw=5., color=t_color, alpha=0.4)
								#
								t_gca.add_line(line)
								#
							#
						#
					#
					'''


	def redraw(self, graph, ctt):
		#
		print(int(self.val_smp.get()),int(self.val_pnt.get()))
		#
		self.make_iter(int(self.val_smp.get()),int(self.val_pnt.get()),graph,ctt,self.plt)
		#
		self.plt.show(block = False)
		#