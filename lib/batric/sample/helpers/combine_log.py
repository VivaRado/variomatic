import os
from distutils.dir_util import copy_tree

def combine_log(output):

	print("COMBINING LOG")

	_str = '''
<!DOCTYPE html>
<html>
	<head>
		<title></title>
		<link rel="stylesheet" type="text/css" href="./log_public/log_css.css">
		<script type="text/javascript" src="./log_public/jquery.min.js"></script>
		<script type="text/javascript" src="./log_public/pprint.js"></script>
		<script type="text/javascript" src="./log_public/js.js"></script>
	</head>
	<body>
		{}
	</body>
</html>
	'''

	svg_data = ""

	for file in os.listdir(output):
		if file.endswith(".svg"):
			#
			fi = open(os.path.join(output, file), "r")
			svg_image = fi.read()
			glyph_name = file.split(".svg")[0]
			#
			json_fi = open(os.path.join(output, glyph_name+'.json'), "r")
			glyph_info = json_fi.read()
			#
			svg_data = svg_data + "<div class='glyph' data-glyph='"+glyph_name+"'>"+svg_image+"<div class='glyph_info'><div class='glyph_name'>"+glyph_name+"</div><div class='init_info'>"+glyph_info+"</div></div></div>"
			#
	f = open(os.path.join(output,'index.html'), "w")
	f.write(_str.format(svg_data))
	f.close()

	dir_path = os.path.dirname(os.path.realpath(__file__))

	copy_tree(os.path.join(dir_path,"log_public"), os.path.join(output,"log_public"))