
### **Introduction / Organisational Documents**

The documentation for this project and the project modules has been split to partial MD files for easier editing and alterations. Three options are provided (HTML,PDF,MD) Contents of generated files are stored in the ``` /README ``` folder as numbered main files and includes in the ``` /README/partials ``` as partial MD files.

Documentation Types and generating them:

*  HTML - Responsive preview in HTML format - At README directory:

	```python3 README/gen_readme.py -f 'html' -l "L1"```

*  Standard Repository README - At the root of the repository:
	
	```python3 README/gen_readme.py -f 'md' -l "L1"```

*  PDF - At the root of the repository:
	
	```python3 README/gen_readme.py -f 'pdf' -l "L1"```

You can pass multiple formats:

```python3 README/gen_readme.py -f 'html,pdf,md' -l "L1"```

You can pass documentation Level:

Requirements:

*  Markdown2 module for python3
	
	*  Linux: ```pip3 install markdown2```
	*  Windows: ```py -m pip install markdown2```

*  pygments

	*  Linux: ```pip3 install pygments```
	*  Windows: ```py -m pip install pygments```

*  weasyprint

	*  Linux: ```pip3 install weasyprint==45```
	*  Windows: ```py -m pip install weasyprint==45```


Features:

*  Responsive Interface
*  Synchronized Sidebar
*  Hashtag Navigation
*  PDF with TOC and Cover

Drawbacks:

*  Graphs and Diagrams will not work in github and bitbucket preview, but are still readable.
*  Graphs and Diagrams will not work in PDF will be assessed.

Details:

*  For the PDF Contents. As we generate URL style blocks:
	*  We override the weasyprint Document.make_bookmark_tree

*  For the HTML and the Diagrams. As we load them into Codeblocks:
	*  We override the markdown2 ```Markdown._code_block_sub```
	*  We override the markdown2 ```Markdown._color_with_pygments```
