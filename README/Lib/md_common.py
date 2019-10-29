import os
import glob
import re
import markdown2
from markdown2 import Markdown
from .generic_tools import *

def get_includes(dir_path, data):
	#
	dic = {}
	new_data = ''
	#
	def itter(_dat, new_data):
		#
		includes = re.findall('```{include=(.+?)}```', _dat)
		in_includes = []
		#
		for inc in includes:
			#
			if ',' in inc:
				#
				inc_split = inc.split(',')
				inc_level = inc_split[1]
				inc_path = '/'.join(inc_split[0].split('/')[:-1])+'/'+inc_level+'_'+inc_split[0].split('/')[-1]
				#
				in_p_dir = os.path.join(dir_path,inc_path)
				#
			else:
				#
				in_p_dir = os.path.join(dir_path,inc)
				#
			#
			in_p_f = open(in_p_dir,"r")
			#
			in_content = in_p_f.read()
			#
			in_includes = re.findall('```{include=(.+?)}```', in_content)
			#
			dic['```{include='+inc+'}```'] = in_content
			#
			if len(list(in_includes)):
				#
				new_data += itter(in_content, new_data)
				#
			#
		#
		new_data = replace_all(_dat,dic)
		#
		return new_data
		#
	#
	new_data += itter(data, new_data)
	#
	return new_data
	#
def collect_mds(dir_path, up_dir, name, levels):
	#
	outfile = open(os.path.join(up_dir, name), "w")
	#
	added = []
	#
	for file in sorted(glob.glob(os.path.join(dir_path,"*.md"))):
		#
		if name == 'README.md':
			#
			check_name = 'IGNORE'
			#
		else:
			#
			check_name = name
			#
		#
		#
		if "README.md" not in file and check_name not in file:
			#
			f_name_ = file.split('/')[-1]
			f_name = f_name_.split('_')[-1].split('.')[0]
			#
			#
			if f_name not in added:
				#
				added.append(f_name)
				#
				do_open = True
				#
				if "L0" in f_name_ or "L1" in f_name_: # prevent non matching levels from being included but allow levelless files normally.
					#
					if f_name_.split('_')[1] != levels[0]:
						#
						added.remove(f_name)
						#
						do_open = False
						#
					#
				#
				if do_open:
					#
					with open(file,"r") as infile:
						#
						data = infile.read()
						#
						new_data = get_includes(dir_path, data)
						#
						write_data = new_data
						#
						if name == 'README.md':
							#
							new_data_remove_html = re.sub('<[^<]+?>', '', new_data)
							new_data_add_dir_rep_data = new_data_remove_html.replace("assets/media", "README/assets/media")
							#
							write_data = new_data_add_dir_rep_data
							#
						#
						outfile.write(write_data)
						infile.close()
	#
	outfile.close()
	#
#
def md_to_html(dir_path):

	with open(os.path.join(dir_path,"README_collected.md"), 'r') as in_file: 
		col_html = markdown2.markdown(in_file.read(), extras=["fenced-code-blocks","markdown-in-html", "tables", "strike"])
		with open(os.path.join(dir_path,"md_temp.html"), 'w') as output_file: 
			output_file.write( col_html )
			output_file.close()
		in_file.close()


def _code_block_sub_b(self, match, is_fenced_code_block=False):
		lexer_name = None
		if is_fenced_code_block:
			lexer_name = match.group(1)
			if lexer_name:
				formatter_opts = self.extras['fenced-code-blocks'] or {}
			codeblock = match.group(2)
			codeblock = codeblock[:-1]  # drop one trailing newline
		else:
			codeblock = match.group(1)
			codeblock = self._outdent(codeblock)
			codeblock = self._detab(codeblock)
			codeblock = codeblock.lstrip('\n')  # trim leading newlines
			codeblock = codeblock.rstrip()      # trim trailing whitespace

			# Note: "code-color" extra is DEPRECATED.
			if "code-color" in self.extras and codeblock.startswith(":::"):
				lexer_name, rest = codeblock.split('\n', 1)
				lexer_name = lexer_name[3:].strip()
				codeblock = rest.lstrip("\n")   # Remove lexer declaration line.
				formatter_opts = self.extras['code-color'] or {}
		
		# Use pygments only if not using the highlightjs-lang extra
		if lexer_name and "highlightjs-lang" not in self.extras:
			def unhash_code(codeblock):
				for key, sanitized in list(self.html_spans.items()):
					codeblock = codeblock.replace(key, sanitized)
				replacements = [
					("&amp;", "&"),
					("&lt;", "<"),
					("&gt;", ">")
				]
				for old, new in replacements:
					codeblock = codeblock.replace(old, new)
				return codeblock
			#print(lexer_name)
			lexer = self._get_pygments_lexer(lexer_name)
		   
			if lexer:
				got_lexer = lexer
			else:
				got_lexer = self._get_pygments_lexer('text')
			#
			codeblock = unhash_code( codeblock )
			colored = self._color_with_pygments(codeblock, got_lexer, lexer_name,**formatter_opts)
			return "\n\n%s\n\n" % colored

		codeblock = self._encode_code(codeblock)
		pre_class_str = self._html_class_str_from_tag("pre")

		if "highlightjs-lang" in self.extras and lexer_name:
			code_class_str = ' class="%s"' % lexer_name
		else:
			code_class_str = self._html_class_str_from_tag("code")

		return "\n\n<pre%s><code%s>%s\n</code></pre>\n\n" % (
			pre_class_str, code_class_str, codeblock)

def _color_with_pygments_b(self, codeblock, lexer, lexer_name, **formatter_opts):
	import pygments
	import pygments.formatters

	class HtmlCodeFormatter(pygments.formatters.HtmlFormatter):
		def _wrap_code(self, inner):
			"""A function for use in a Pygments Formatter which
			wraps in <code> tags.
			"""
			yield 0, "<code class='codehilite "+lexer_name+"'>"
			for tup in inner:
				yield tup
			yield 0, "</code>"

		def wrap(self, source, outfile):
			"""Return the source with a code, pre, and div."""
			return self._wrap_pre(self._wrap_code(source))

	#formatter_opts.setdefault("cssclass", "codehilite "+lexer_name)
	formatter = HtmlCodeFormatter(**formatter_opts)
	return pygments.highlight(codeblock, lexer, formatter)


codeblock_sub_override = _code_block_sub_b
codeblock_color_override = _color_with_pygments_b
Markdown._code_block_sub = codeblock_sub_override
Markdown._color_with_pygments = codeblock_color_override