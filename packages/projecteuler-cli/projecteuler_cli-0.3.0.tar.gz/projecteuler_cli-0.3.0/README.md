# Project Euler CLI



A command-line helper for Project Euler problems to:

* fetch any Project Euler problem and scaffold boiler-plate files
* pull the official RSS feed
* track which problems you have finished
* show quick progress stats

**Supports both Julia and Python!**

```
# install from PyPI
pip install projecteuler-cli

# create a folder "problem 944" with .md, .py, .ipynb
projecteuler 944 --lang py

# same but Julia template
projecteuler 944 --lang julia

# read RSS in your terminal
projecteuler rss

# also save RSS to a dated txt
projecteuler rss --txt

# mark problem 944 as done
projecteuler done 944

# show progress
projecteuler stats
projecteuler stats --txt
```