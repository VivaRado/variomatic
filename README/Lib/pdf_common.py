import os
import collections
from weasyprint import HTML
from .generic_tools import *
#
h_lists = []
h_book = []
global new_list
p_h_t_l = []
d = []
new_list = []
#
def generate_outline_str(bookmarks, indent=0):
	#
	outline_str = ""
	#
	for i, (label, [page, _, _], children) in enumerate(bookmarks, 1):
		#
		str_ = '<li>'+('%s <b>%d</b>' % ( label, (page-1)))+'</li>'
		#
		if label == "Cover" or label == "Contents":
			#
			str_ = ''
			#str_ = '<li>'+('%s' % ( label))+'</li>'
			#
		outline_str += str_
		outline_str += '<ul>'+generate_outline_str(children, indent + 2)+'</ul>'
		#
	
	return outline_str
#

def get_h_pos(self, t_label):
	#
	for page_number, page in enumerate(self.pages):
		#
		for level, label, (point_x, point_y) in page.bookmarks:
			#
			if t_label == label:
				
				subtree = (page_number, point_x, point_y)

				return subtree
			#
		#
	#
#

def get_pos_hie(self, lst):
	#
	for el in lst:
		#
		if isinstance(el, list):
			#
			chain = ' / '.join(list(flatten(el)))
			#
			subtree = get_h_pos(self,chain)
			#
			return subtree
			#
			
		#
	#
#



#
def combine(d, l):
	#
	if not l[0] in d:
		d[l[0]] = collections.OrderedDict()

	for v in l[1:]:
		if type(v) == list:
			combine(d[l[0]],v)
		else:
			d[l[0]] = v
#
def hierarchy_list(row, _l):
	#
	if(row is 0):
		return
	#
	return [ _l[len(_l)-row], hierarchy_list(row-1,_l)]
	#
	#
#
def make_list(ls):
	#
	z = []
	#
	if ls != None:
		#
		for y in ls:
			#
			z.append((y,[1,0,0],[]))
			#
		#
	#
	return z
	#
#
def deep_get(targ, obj):
	#
	def iterr (tg, ps):
		#
		got = ps.get(tg)
		#
		if got:
			#
			return [list(got),tg]	
			#
		else:
			for x,y in ps.items():
				#
				if len(list(y)) > 0:
					#
					got = y.get(tg)
					#
					if got:
						#
						return [list(got),x]
						#
					#
				#
				else:
					#
					iterr(targ,y)
					#	
				#
			#
		#
	#
	return iterr(targ, obj)
	#
#
def find_el_b(targ, lst, to_add):
	if not lst:
		return 0
	found = False
	for el in lst:
		#
		children = el[2]
		#
		if targ == el[0]:
			#
			found = True
			#
			v_add = [x[0] for x in to_add]
			v_is = [x[0] for x in children]
			#
			if v_add != v_is:
				#
				children.extend(to_add)
			#
			_f = True
			#
			break
			#
		else:
			#
			find_el_b(targ, children, to_add)
			#
#
remove_last = 0
#
def nested_dicts2lists(self, pairs):
	#
	def rec_for_sum(targ, lst, got_targ):
		#
		if got_targ != None:
			#
			if got_targ[0] != None:
				#
				el = list(got_targ[0])
				#
				if el != None:
					#
					to_add = make_list(el)
					#
					found_el = find_el_b(targ,lst, to_add)
					#
				#
			#
		#
	#
	current_chain = []
	#
	def iterr_b (self,ps, current_chain):
		#
		for x,y in ps.items():
			#
			if isinstance(y, dict):
				#
				current_chain.append(x)
				#
				got_targ = deep_get(x, ps)
				#
				rec_for_sum(x, new_list, got_targ)
				#
				iterr_b(self,y, current_chain)
				#
			#
		#
	#
	remove_last = 0
	#
	for x,y in pairs.items():
		#
		
		if x not in [item[0] for item in list(new_list)]:
			#
			#
			new_list.append((x,[1,0,0],[]))
			#
			remove_last = remove_last + 1
			#
		#
	#
	#
	iterr_b (self,pairs, current_chain)
	#
	return new_list
#
def add_position_tuple(self,h_lists, tup_list):
	#
	done = []
	#
	def iterr(f_list, _l, _t, c_c):
		#
		cur_chain = c_c
		
		for x in _t:
			#
			cur_chain = cur_chain + ' / ' + x[0]
			#
			if x[0] == f_list[-1]:
				#
				d = list(x)
				x[1][0] = y[1][0]+2
				x[1][1] = y[1][1] 
				x[1][2] = int(y[1][2])# + int(self.pages[0].height)
				b = tuple(d)
				x = b
				#
			#
			c_ch = cur_chain.split(' / ')[1:]
			#
			cur_chain = ' / '.join(c_ch)
			#
			iterr(f_list, _l, x[2], cur_chain)
			#
		#
	#
	for y in h_lists:
		#
		f_list = list(flatten(y[0]))
		#
		if f_list not in done:
			#
			iterr(f_list, y, tup_list, '')
			#
			done.append(f_list)
	#
	new_list = tup_list
	#
	return tup_list
#


def make_nested_b(self, lst):
	#
	# ----------------------------------------------------------------------
	#
	# URL Style list to Nested Hierarchy lists
	# [a,b,c] -> [a,[b,[c]]]
	#
	for x in lst:
		#
		hier_list = remove_none(hierarchy_list(len(x[0]),x[0]))
		#
		t_chain = ' / '.join(x[0])
		#
		h_lists.append([hier_list,x[1]])
		#
	#
	#print('_____A')
	#pprint.pprint(h_lists)
	#
	# ----------------------------------------------------------------------
	#
	# Nested Hierarchy lists to similar hierarchy Ordered Dictionary
	# [a,[b,[c]]],[a,[b,[d]]] - > {a,{b,{{c},{d}}}}
	#
	h_dict = collections.OrderedDict()
	#
	for y in h_lists:
		#
		if len(list(flatten(y[0]))) > 0:
			#
			combine(h_dict, y[0])	
			#
		#
	#
	#print('_____B')
	#pprint.pprint(h_dict)
	#
	# ----------------------------------------------------------------------
	#
	# similar hierarchy Ordered Dictionary to List and Tuple hierarchy
	# {a,{b,{{c},{d}}}} - > [(a,[(b,[(c,[]),(d,[])])])]
	#
	n_l = nested_dicts2lists(self, h_dict)
	new_list = add_position_tuple(self,h_lists, n_l)
	# ----------------------------------------------------------------------
	#
	# List and Tuple hierarchy add position tuple
	# adding a position as a tuple or as a list makes no difference: (p,x,y) || [p,x,y]
	# [(a,[(b,[(c,[]),(d,[])])])] - > [(a,(p,x,y)[(b,(p,x,y)[(c,(p,x,y)[]),(d,(p,x,y)[])])])]
	#
	#
	#print('_____C')
	#pprint.pprint(new_list)
	#
	#self.new_list = new_list
	#
	return new_list
	#
#


def gather_labels(self):
	labels = []
	#
	for page_number, page in enumerate(self.pages):
		#
		for level, label, (point_x, point_y) in page.bookmarks:
			#
			h_level = level#x[0]
			#
			if h_level == 2 or h_level == 3: # only h2 and h3 are considered labels
				#
				labels.append([label.split(' / '),(page_number, point_x, point_y)])
				#
			#
		#
	#
	return labels
	#
#
def make_bookmark_tree_b(self, call=False):
	#
	root = []
	#
	labels = gather_labels(self)
	nested_labels = make_nested_b(self, labels)
	#
	return nested_labels
	#

def add_intro(doc, new_data, new_list, css_file, css_file_contents, css_file_cover, version, up_dir, title, gen_date):
	#
	if 'Contents' not in [item[0] for item in list(new_list)]:
		new_list.insert(0,('Contents',[-1,0,0],[]))

	if 'Cover' not in [item[0] for item in list(new_list)]:

		new_list.insert(0,('Cover',[-1,0,0],[]))
		#
	#
	table_of_contents_string = generate_outline_str(new_list,0)
	#
	TOC_str = '''<div class="toc_"><h3>Contents</h3><div class="toc_lists">'''+table_of_contents_string+'''</div></div>'''
	#
	#
	table_of_contents_document = HTML(string=TOC_str).render(stylesheets=[css_file_contents])
		#table_of_contents_document = HTML(string=table_of_contents_string).render()
	table_of_contents_page = table_of_contents_document.pages[0]
	#
	doc.pages.insert(0, table_of_contents_page)
	cover_string = '<div class="cover_"><h1>'+title+'</h1><br><span class="version">∞'+version+'</span>, <span class="date">'+gen_date+'</span></div>'
	doc.pages.insert(0, HTML(string=cover_string).render(stylesheets=[css_file_cover]).pages[0])
	#
#
def make_pdf(new_data, new_list, css_file, css_file_contents, css_file_cover, version, up_dir, title, gen_date):
	#
	write_data = new_data.replace("assets/media", "README/assets/media")
	#
	doc = HTML(string=write_data, base_url=os.path.join(up_dir)).render(stylesheets=[css_file])
	doc.make_bookmark_tree('convert')
	#
	data = make_bookmark_tree_b(doc,'last')
	#
	output = os.path.join(up_dir, "README.pdf")
	#
	add_intro(doc, new_data, new_list, css_file, css_file_contents, css_file_cover, version, up_dir, title, gen_date)
	#
	doc.write_pdf(output)
#