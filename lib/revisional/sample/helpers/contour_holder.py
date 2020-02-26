import xml.etree.ElementTree as ET
from copy import deepcopy
from fontParts.world import *
from fontTools.ufoLib.glifLib import GlifLibError, readGlyphFromString
from pnt import *


class ContourHolder(object):
	"""
	Get contours ordered and unidirectional from path string
	"""
	def __init__(self, path, debug):
		#
		root = ET.parse( path ).getroot()
		self.offset_y = 0
		self.offset_x = 0
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
			oncurvep = [item for item in contour.points if item.type != 'offcurve']
			#
			for bpoint in contour.bPoints:
				#
				psmooth = oncurvep[contour.bPoints.index(bpoint)].smooth
				#
				
			#
			for point in contour.points:
				#
				if _type == 'corner':
					#	
					if point.type != 'offcurve':
						#
						p_arr.append([round(float(point.x+self.offset_x),1), round(float(point.y-self.offset_y),1)])
						#
					#
				elif _type == 'get_type':
					#
					p_arr.append([round(float(point.x+self.offset_x),1), round(float(point.y-self.offset_y),1), point.type])
					#
				else:
					#
					p_arr.append([round(float(point.x+self.offset_x),1), round(float(point.y-self.offset_y),1)])
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
