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
def tc_get_simp_conf_b_coord(t_contour, simp_level, coordinate):
	#
	confine_from_coord = [d for d in t_contour["confines_simp"][simp_level] if d[1][1] == coordinate][0]
	confine_index = t_contour["confines_simp"][simp_level].index(confine_from_coord)
	#
	return confine_index, confine_from_coord
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
		#
	#
	'''
	def draw_cts(self, t_contour, smp, pnt):
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
			if simp_level == smp: # example one level 0 of simplification / removing will run whole simplification list
				#
				for z in y: # points
					#
					t_coord = geom.flipCoordPath([z],False,True)[0]
					#
					#graph_point_from_coord = tc_get_point_b_coord(t_contour,simp_level,t_coord)
					#
					conf_inx, conf_dat = tc_get_simp_conf_b_coord(t_contour,simp_level,t_coord)
					#
					if conf_inx == pnt:
						#
						pca_crd_c = tc_get_pca(t_contour,simp_level,conf_inx,"c")
						#
						list_x, list_y = get_perp(pca_crd_c, "virt")
						#
						line = lines.Line2D(list_x,list_y, lw=1., color=t_color, alpha=0.4)
						#
						t_gca.add_line(line)
						#
					#
	'''
	#
	def run(self):
		#
		root = Tk()
		#
		root.geometry("100x250+1800+0")
		#
		frame = Frame(root, borderwidth=1)
		frame.pack(side='top')
		label = Label(frame, text='Simplification')
		label.pack()
		self.val_smp = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_simplification_value_change)
		self.val_smp.delete(0,"end")
		self.val_smp.insert(0,0)
		self.val_smp.pack()
		#
		label_iter = Label(frame, text='Node Point')
		label_iter.pack()
		self.val_pnt = Spinbox(frame, width=8, from_=0, to=1000000, command=self.on_point_value_change)
		self.val_pnt.delete(0,"end")
		self.val_pnt.insert(0,0)
		self.val_pnt.pack()
		#
		label_instance = Label(frame, text='Instance')
		label_instance.pack()
		self.val_ins = Spinbox(frame, width=8, from_=0, to=10, command=self.on_instance_value_change)
		self.val_ins.delete(0,"end")
		self.val_ins.insert(0,0)
		self.val_ins.pack()
		#
		label_contour = Label(frame, text='Contour')
		label_contour.pack()
		self.val_cnt = Spinbox(frame, width=8, from_=0, to=10, command=self.on_contour_value_change)
		self.val_cnt.delete(0,"end")
		self.val_cnt.insert(0,0)
		self.val_cnt.pack()
		#
		label_instance_data = Label(frame, text='Instance Data')
		label_instance_data.pack()
		self.val_ins_dat = Spinbox(frame, width=8, from_=0, to=10, command=self.on_instance_value_change)
		self.val_ins_dat.delete(0,"end")
		self.val_ins_dat.insert(0,1)
		self.val_ins_dat.pack()
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
	def on_instance_value_change(self):
		#
		self.redraw(False, True)
		#
	#
	def on_contour_value_change(self):
		#
		self.redraw(False, True)
		#
	#
	def draw_ctt_tri(self,x,gca,_plt, _clr, _rad):
		#
		list_x, list_y = [
			x["lt_crd"][0], 
			x["pnt_dist_b"][1][0]
		],[
			x["lt_crd"][1], 
			x["pnt_dist_b"][1][1]
		]
		#
		line = lines.Line2D(list_x,list_y, lw=1, color=_clr, alpha=0.4)
		gca.add_line(line)
		#
		poly = _plt.Polygon(x["tri"], color=_clr,alpha=0.05, linewidth=0.2)
		gca.add_patch(poly)
		#
		draw.draw_circle_on_coord(x["lt"][1], gca, _rad, _clr, False, False)
		#
		#
	#
	def draw_pca_circles(self, crd, gca, _color, _pca_text):
		#
		draw.draw_circle_on_coord(crd, gca, 10, _color, False, False)
		draw.draw_label_pca(crd, gca,_color,_pca_text)
		#
	#
	def make_iter_current(self, _val_smp, _val_pnt, _val_ins, _val_cnt, _val_ins_dat, redraw_smp, redraw_pnt, _plt=False):
		#
		# For data that reffer to currently instansiating plot
		#
		for instance in self.instances:
			#
			#print("INSTANCE")
			#print(instance)
			#
			for letter in self.instances[instance]:
				#
				for contour in self.instances[instance][letter]:
					#
					t_contour = self.instances[instance][letter][contour] # this
					#
					points_lenwise = list(t_contour["graphs"][_val_smp].values())
					inst_inx = t_contour["inst"]
					cont_inx = t_contour["cont"]
					#
					t_plot = _plt.figure(t_contour["plot_num"])
					t_plot.clf() #remember clear figure ENABLE FOR MENU ACCESSIBILITY, DISABLE FOR DUMMY CODE
					t_gca = t_plot.gca()
					t_color = color[inst_inx]
					#
					# tight layout
					_plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
					#_plt.tight_layout(pad=0)
					#
				# STANDARD DRAW
					# Draw Graphs
					if _val_smp in t_contour["simplified"].keys():
						#
						# Show Graph according to simplified match index if _val_smp is changed shown by redraw_smp = True
						c_graph = t_contour["graphs_data"][_val_smp]#self.GC.make_instance_topo(t_contour, t_color,_val_smp)
						#
						draw.draw_instance_graphs_c(t_contour,c_graph)
						#
					#
					# Draw Start Point (After Graph because erase plot)
					contour_start_point = t_contour["coords"]["graph"][0]
					#
					# contour_start_point
					draw.draw_circle_on_coord(contour_start_point, t_gca, 20, t_color, False, False, '', ':')
					#
				# CURRENT INSTANCE SPECIFIC DRAW / CONTOUR SPECIFIC DRAW
					# Draw Center Transfer Tree Matches
					#
					_color_pre = 'brown'
					_color_cnt = 'purple'
					_color_ant = 'brown'
					#
					if instance == _val_ins and contour == _val_cnt:
						#
						try:
							#
							#
							coord_ct = [item[1] for item in t_contour["confines_simp"][_val_smp][_val_pnt]]
							#
							#
							draw.plot_region_line(t_gca, coord_ct, t_color, _plt)
							#
							#self.draw_cts(t_contour, _val_smp, _val_pnt)
							#
							added_circ = False
							added_pca_labels = [False,False,False]
							#
							#for x in t_contour["matching_best_area"][_val_smp]:
							for x in t_contour["matching_best_area"][_val_smp]:
								#
								#print(x)
								#
								if [_val_ins, _val_ins_dat] == x['instance_pair']:
									#
									if x["pnt_crd"] == coord_ct[0]: # Pre
										#pass
										self.draw_ctt_tri(x,t_gca,_plt, _color_pre, 1.5)
										#
										# drap Pre Point
										if added_pca_labels[0] == False:
											#
											self.draw_pca_circles(x["pnt_crd"], t_gca, _color_pre, 'P')
											#
											#
											added_pca_labels[0] = True
											#
										#
									#
									if x["pnt_crd"] == coord_ct[2]: # Ante
										#pass
										self.draw_ctt_tri(x,t_gca,_plt, _color_ant, 3)
										#
										if added_pca_labels[2] == False:
											#
											self.draw_pca_circles(x["pnt_crd"], t_gca, _color_ant, 'A')
											#
											#
											added_pca_labels[2] = True
											#
											#
										#
									#
									if x["pnt_crd"]  == coord_ct[1]: # Center #x["gpi"] == _val_pnt:
										#
										self.draw_ctt_tri(x,t_gca,_plt, _color_cnt, 4.5)
										#
										if added_pca_labels[1] == False: 
											#
											self.draw_pca_circles(x["pnt_crd"], t_gca, _color_cnt, 'C')
											#
											#
											added_pca_labels[1] = True
											#
										#
										#
										conf_inx, conf_dat = tc_get_simp_conf_b_coord(t_contour,_val_smp,x["pnt_crd"])
										#
										#
										if added_circ == False:
											#
											circl = _plt.Circle(x["pnt_crd"], x["max_radius"], color=t_color, fill=False, alpha=0.5, lw=0.5)
											circl.set_radius(x["max_radius"])
											circl.set_linestyle((0, (2,4)))
											t_gca.add_patch(circl)
											#
											# draw ctt perp line
											#
											pca_crd_p = tc_get_pca(t_contour,_val_smp,conf_inx,"p")
											pca_crd_c = tc_get_pca(t_contour,_val_smp,conf_inx,"c")
											pca_crd_a = tc_get_pca(t_contour,_val_smp,conf_inx,"a")
											#
											pca_crd = [pca_crd_p, pca_crd_c, pca_crd_a]
											#
											for y in pca_crd:
												#
												list_x, list_y = get_perp(y, "virt")
												#
												_clr = 'g'
												#
												if 0 == pca_crd.index(y):
													#
													_clr = _color_pre
													#
												#
												elif 1 == pca_crd.index(y):
													#
													_clr = _color_cnt
													#
												#
												elif 2 == pca_crd.index(y):
													#
													_clr = _color_ant
													#
												#
												line = lines.Line2D(list_x,list_y, lw=1., color=_clr, alpha=0.4)
												#
												t_gca.add_line(line)
												#
											#
											added_circ = True
											#
										#
										#
										# print("CTTS ++======")
										# print(coord_ct)
										#
										#if pca_checks[1] == 1:
										#
										#
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
					
	def make_iter_opposite(self, _val_smp, _val_pnt, _val_ins, _val_cnt, _val_ins_dat, redraw_smp, redraw_pnt, _plt=False):
		#
		# For data that reffer to opposite plots after plot instantiation
		#
		for instance in self.instances:
			#
			for letter in self.instances[instance]:
				#
				for contour in self.instances[instance][letter]:
					#
					t_contour = self.instances[instance][letter][contour] # this
					#
					for d,z in t_contour["ctt_match_lt"][_val_smp]["sequences"].items():
						#
						#print("---?")
						#print(d,z)
						#for z in j:
						#
						#
						#if len(z) > 0:
						#
						for x in z:
								
							#print([_val_ins, _val_ins_dat], x)
							#
							if [_val_ins, _val_ins_dat] == x['instance_pair']:
								#
								if _val_ins == x['inx_ins'] and _val_cnt == x['inx_cnt'] and _val_pnt == x['gpi']:
									#
									print("GOT SEQUENCE LINE")
									print(x["ctt_lt"])
									print("===========================?")
									print(x["lines"])
									#
									#
									#print(z["point_seq"])
									#
									t_color = color[x['inx_ins_opp']]
									t_plot_b = _plt.figure(x['plot_num_opp'])
									#
									t_gca_b = t_plot_b.gca()
									##
									#if len(x["lines"]):
									#
									#for y in x["lines"]:
									#
									#print("--------")
									#print(y)
									#
									draw.plot_region_line(t_gca_b, x["lines"], t_color, _plt)
									#
									#
									#
									#print("------")
									#pprint.pprint(y["matches"])
									#
									#draw.draw_circle_on_coord(y["matches"][i]["lt"][1], t_gca_b, 10, "r")
									#
									'''
									for h in y["matches"]:
										#
										#
										print("LT GPI")
										print(h['lt'])
										print(h['gpi'])
										print(h['point_graph_inx'])
										#for d in h['best_sorted']:
										#
										#if h['lt'][2] in z['seq_match']:
										#
										#draw.draw_circle_on_coord(h["lt_crd"], t_gca_b, 10, "r")
										draw.draw_circle_on_coord(h["lt"][1], t_gca_b, 20, "g")
										#
										#
									#
									'''
									#print("---------------------------")
							#
						#
					#except Exception as e:
						#
					#	print("DRAW ERROR")
					#	print(e)
					#	pass
						#
					'''
					for y in t_contour["confines_simp"][_val_smp]:
						#
						for z in y:
							
							#
							x = z[4]
							#print("-->>>")
							#print(x)
							#

							#
							
							#
							#j = 0
							#
							#for x in y: # each confine total 3 (p,c,a)
							#
							if _val_ins == x['inx_ins'] and _val_cnt == x['inx_cnt'] and _val_pnt == x['gpi']:
								#
								t_plot_b = _plt.figure(x['plot_num_opp'])
								#print("plot", x['plot_num'], x['inx_ins_opp'], t_plot_b)
								#
								t_gca_b = t_plot_b.gca()
								#
								print("================================")
								print(x['seq_match'])
								#
								for z in x['best_sorted']:
									#
									if z['lt'][2] in x['seq_match']:
										#
										draw.draw_circle_on_coord(z["lt"][1], t_gca_b, 10, "g")
										#
									#
								#
								#
								#j = j + 1
							#
								#
								i = i + 1
							#
					#
					'''
					

	def redraw(self, graph, ctt):
		#
		#self.make_iter_current(int(self.val_smp.get()),int(self.val_pnt.get()), int(self.val_ins.get()), int(self.val_cnt.get()),graph,ctt,self.plt)
		#self.make_iter_opposite(int(self.val_smp.get()),int(self.val_pnt.get()), int(self.val_ins.get()), int(self.val_cnt.get()),graph,ctt,self.plt)
		#
		self.make_iter_current(int(self.val_smp.get()),int(self.val_pnt.get()), int(self.val_ins.get()), int(self.val_cnt.get()), int(self.val_ins_dat.get()),graph,ctt,self.plt)
		self.make_iter_opposite(int(self.val_smp.get()),int(self.val_pnt.get()), int(self.val_ins.get()), int(self.val_cnt.get()), int(self.val_ins_dat.get()),graph,ctt,self.plt)
		#
		self.plt.show(block = False)

		#