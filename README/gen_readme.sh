#!/bin/bash
commit_message="$1"

python3 './README/gen_readme.py' -f 'pdf,html' -l "L1"
python3 './README/gen_readme.py' -f 'md' -l "L1"

# git add README 
# git add README.pdf
# git add README.md

# git commit -m "$commit_message"
# git push origin master