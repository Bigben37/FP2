##Fortgeschrittenenpraktikum (Teil 2)

####Useful links

- [information (2015)](http://portal.uni-freiburg.de/jakobs/Lehre/ws-14-15/fp2015-1)
- [information (general)](http://portal.uni-freiburg.de/jakobs/Fortgeschrittenen-Praktikum)
- [instructions](http://hacol13.physik.uni-freiburg.de/fp/)
- [list of tutors](http://hacol13.physik.uni-freiburg.de/fp/fp2015-1/Assistenten.pdf)

####Setup
We use the latest [Eclipse](https://www.eclipse.org/) version as IDE with following plugins:
- [TeXlipse](http://texlipse.sourceforge.net/) for LaTeX
- [PyDev](http://pydev.org/) for Python

#####Running LaTeX scripts
You can import the existing project with Eclipse. You can check our configuration in the `.texlipse` file.

#####Running Python scripts
Unfortunatley we cant sync our `.pydevproject` configuration file, because PyDev saves absolute paths. You need to add the `lib` folder by yourself to the `PYTHONPATH` (for example add it to the `external libraries` list of the project).

####directory structure
Every experiment has its own directory. In this directory you may find following subdirectories:
- `bin`: binary file of protocol (not final version), excluded from commits
- `calc`: raw data for further calculation
- `data`: measured data from experiment, sometimes includes quick evaluation with Mathematica
- `fit` : results of fits
- `img`: pictures made in the experiment, rendered graphs from ROOT and self-made svg-graphics
- `src`: source directory for Python and LaTeX code
- `stuff`: mostly mathematica files for on-the-fly evaluation, error calculation and other math stuff
