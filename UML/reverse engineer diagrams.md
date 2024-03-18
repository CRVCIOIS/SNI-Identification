The class diagram and package diagram were created with the help of `pyreverse`, 
but some steps were necessary to make it work correctly with our package structure:
1. Install `pylint` with pip (not included in `requirements.txt` as it's not used in the actual project).
2. Install [Graphviz](https://graphviz.org/) (**not with pip!**) on your system.
3. Create an `__init__.py` in the project's root folder.
4. Rename all import calls to `NLP.` (i.e. `from adapters.scb import SCBAdapter` becomes `from NLP.adapters.scb import SCBAdapter`).
5. Run `pyreverse -my -A -o <output_type> -p <project_name> <path/to/NLP_root_folder>`