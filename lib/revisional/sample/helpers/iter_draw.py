#
import draw
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
		self._simp = 0
		self._iter = 0
		#
		# if self.run_sp != "":
		# 	#
		# 	self.spinbox.delete(0,"end")
		# 	self.spinbox.insert(0,0)
		# 	self.rad_search_box.delete(0,"end")
		# 	self.rad_search_box.insert(0,0)
			#
		self.redraw(True, True)
		#
	#
	def on_matching_value_change(self):
		#
		self.redraw(True, True)
		#
	#
	def make_iter(self, val_simplification, val_iteration, draw_graph, draw_ctt, _plt=False):
		#
		# if _plt:
		# 	#
		# 	if self.run_sp != "":
		# 		#
		# 		print ('\n'+tcolor.WARNING + "MANUAL MATCH REVIEW:" + "\n\tSIMPLIFICATION: " + str(self.spinbox.get())+ "\n\tPOINT: " + str(self.rad_search_box.get()) + tcolor.ENDC)
		# 		#
		# 	else:
		# 		#
		# 		print ('\n'+tcolor.WARNING + "MATCH REVIEW:" + "\n\tSIMPLIFICATION: " + str(self._simp)+ "\n\tPOINT: " + str(self._iter) + tcolor.ENDC)
		# 		#
		# #
			
		if val_simplification == False and val_iteration == False:
			#
			#if self.run_sp != "":
				#
			val_simplification = self.spinbox.get()
			val_iteration = self.rad_search_box.get()
				#
			#
			#else:
				#
			#	val_simplification = self._simp
			#	val_iteration = self._iter
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
					if int(val_simplification) in self.instances[x][y][z]["simplified"].keys():
						#
						if draw_graph:
							#
							self.instances[x][y][z]["graph"] = None
							self.instances[x][y][z] = self.GC.make_instance_topo(self.instances[x][y][z], color[inst_inx],int(val_simplification))
							#
						#
						draw.draw_instance_graphs_c(self.instances[x][y][z])
						#

	def redraw(self, graph, ctt):
		#
		self.make_iter(0,0,graph,ctt,self.plt)
		#
		self.plt.show(block = False)
		#