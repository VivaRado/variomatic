#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import os
import glob
import re
import time
#from bs4 import BeautifulSoup
from shutil import copyfile
from weasyprint import HTML
from weasyprint.document import Document, Page  # noqa

import pprint
import datetime
import operator
import collections
from collections import Iterable
from Lib.pdf_common import make_bookmark_tree_b
from Lib.pdf_common import *
from Lib.md_common import *
from Lib.generic_tools import *
#
from argparse import ArgumentParser
#
dir_path = os.path.dirname(os.path.realpath(__file__))
up_dir = os.path.abspath(os.path.join(dir_path, '..'))
#
css_file = os.path.join(dir_path, 'assets/css/'+'pdf'+'.css')
css_file_cover = os.path.join(dir_path, 'assets/css/'+'pdf_cover'+'.css')
css_file_contents = os.path.join(dir_path, 'assets/css/'+'pdf_contents'+'.css')
#
project_name = up_dir.rsplit('/', 1)[1]
gen_date = datetime.datetime.today().strftime('%Y/%m/%d')
version = open(os.path.join(dir_path,'version'),'r').read()
#

#
bookmark_override = make_bookmark_tree_b
Document.make_bookmark_tree = bookmark_override
make_bookmark_tree = bookmark_override

#
dir_path = os.path.dirname(os.path.realpath(__file__))
#
#
parser = ArgumentParser()
parser.add_argument("-f", "--format", dest="format",
                    help="Export Format: comma separated")
parser.add_argument("-l", "--level", dest="level",
                    help="Export Level: L0 or L1")
#
args = parser.parse_args()
#
def formats(_f, _err):
	#
	gen_formats = []
	#
	supported_f = ["pdf","md","html"]
	#
	if ',' in _f:
		#
		gen_formats = _f.split(',')
		#
	else:
		#
		gen_formats = [_f]
		#
	#
	for x in gen_formats:
		#
		if x not in supported_f:
			#
			_err = True
			#
			print('=\n=> Please Provide Supported Formats: '+x+' is not Supported. Supported Formats: '+','.join(supported_f)+'\n=')	
			#
		#
	#
	return [gen_formats, _err]
	#
#
def levels(_f, _err):
	#
	gen_levels = []
	#
	supported_l = ["L0","L1"]
	#
	if ',' in _f:
		#
		_err = True
		#
		print('=\n=> Please Provide Supported Levels: '+x+' is not Supported. Supported Levels: '+','.join(supported_l)+'\n=')	
		#
	else:
		#
		if _f not in supported_l:
			#
			_err = True
			#
			print('=\n=> Please Provide Supported Levels: '+_f+' is not Supported. Supported Levels: '+','.join(supported_l)+'\n=')	
			#
		else:
			#
			gen_levels = [_f]
			#
		#
	#
	#
	return [gen_levels, _err]
	#
#

faults = False
#
if  args.format is None:
	#
	faults = True
	#
	print('=\n=> Please Provide Export Format: -f "pdf,md,html"\n=')	
	#
#
if  args.level is None:
	#
	faults = True
	#
	print('=\n=> Please Provide Export Level: -l "L0" or "LA"\n=')	
	#
#
if faults == False:
	#
	check_formats = formats(args.format, faults)
	check_levels = levels(args.level, faults)
	#
	gen_formats = check_formats[0]
	format_faults = check_formats[1]
	gen_levels = check_levels[0]
	level_faults = check_levels[1]
	#
	if format_faults:
		#
		print('=\n=> Please Provide Valid Export Format: -f "pdf,md,html"\n=')	
		#
	elif level_faults:
		#
		print('=\n=> Please Provide Valid Export Level: -l "L0" or "L1"\n=')	
		#
	else:
		#
		for x in gen_formats:
			#
			if x == 'pdf' or x == 'html':
				#
				md_name = "README_collected.md"
				md_path = dir_path
				md_path_b = dir_path
				#
			elif x == 'md':
				#
				md_name = "README.md"
				md_path = dir_path
				md_path_b = up_dir
				#
			#
			collect_mds(md_path, md_path_b, md_name, gen_levels)
			#
			if x == 'pdf' or x == 'html':
				#
				md_to_html(dir_path)
				#
				book_path = os.path.join(dir_path,"md_temp.html")
				book_path_new = os.path.join(dir_path,"README.html")
				#
				temp_html = open(book_path, "r")
				html_data = temp_html.read()
				temp_html.close()
				#
				title_full = "VRD | "+project_name+' | '+version+' | '+gen_date
				#
				if x == 'pdf':
					#
					title = "VRD | "+project_name
					#
				elif x == 'html':
					#
					title = title_full#"VRD | "+project_name+' | '+version+' | '+gen_date
					#
				#
				new_data = combine_header(html_data, title_full)
				newfile = open(book_path_new, "w")
				newfile.write(new_data)
				newfile.close()
				#
				os.remove(book_path)
				os.remove(os.path.join(dir_path, "README_collected.md"))
				#
				if x == 'pdf':
					#
					make_pdf(new_data, new_list, css_file, css_file_contents, css_file_cover, version, up_dir, title, gen_date)
					#
				#
			#
		#
	#
#
