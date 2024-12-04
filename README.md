# Simple CDCL-based SAT Solver

This project was done as part of the COL876 (SAT Solvers and Automated Reasoning) course requirements.

A basic CDCL-based SAT solver has been implemented which utilises VSIDS for ordering
variables until one point and then switches to Random Choice Ordering after a
certain number of conflicts have been reached. Backjumping, which is crucial
to CDCL Solvers is implemented by finding the UIP nodes, learning the new
clause and then restarting again from level 0. This has been implemented to
be keep logic simple and also trying to prevent getting stuck in the same local
minima. The report contains more details and analysis regarding the SAT solver.

The following command is used for running the code for the CDCL Solver :

`python3 cdcl.py <test_file_name>`

For running solver with Random Choice Heuristic :

`python3 cdcl_random.py <test_file_name>`

For running solver with 2-Clause Heuristic :

`python3 cdcl_two_clause.py <test_file_name>`
