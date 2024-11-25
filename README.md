# Sturgeon

Sturgeon is a system for constraint-based level generation.



## Setup

* You will need Python 3.12 and pipenv on your system.  To install pipenv, if needed:
  ```
  pip3 install pipenv
  ```

* Pipenv is used to set up an environment.  This only needs to be done once (in any root folder for this project):

  * Either set up the environment with only the default PySAT-based solvers:
    ```
    pipenv install --categories solvers-minimal
    ```

  * Or, set up the environment with all solvers:
    ```
    pipenv install --categories solvers-all
    ```

* Any commands will need to be run in this environment.  Each time a shell is needed, start a shell in the environment with:
  ```
  pipenv shell
  ```



## Example Usage

For example usage (within pipenv), see:

* `examples_basic.sh` - basic use with tile-based levels
* `examples_custom.sh` - custom contraints, such as tile counts, level repair, and level extension
* `examples_junction.sh` - junctions for adding multiple reachable and unreachable paths
* `examples_blend.sh` - blending different games, using tiles and reachabiity from multiple games in one level
* `examples_mkiii.sh` - MKIII tile rewrite rules for generating playthroughs
* `examples_graph.sh` - graph generation
* `examples_mkiv.sh` - MKIV graph label rewrite rules for generating playthroughs
* `examples_explore.sh` - setup and use of level explorer application
* `examples_file.sh` - file conversion utilities
* `examples_external.sh` - use of external solver executables



## Programs

Tiles:
* `input2tile.py` - get tileset and tile levels from example levels, produce tile file
* `tile2scheme.py` - get patterns and counts from tile file, produce scheme file
* `scheme2output.py` - generate levels using a scheme file

Tile Utilities:
* `level2repath.py` - recompute path(s) through a level
* `tag2game.py` - produce a game id file based on tag file and scheme
* `name2json.py` - produce a json description of named infomration, such as reachability template
* `file2file.py` - convert between a few different formats, usually between pickle and json

Applications:
* `app_pathed.py` - path editor, draw paths and generate levels interactively, needs scheme file
* `app_explorer.py` - level explorer, explore a datast of levels, needs explorer file

Level Explorer:
* `levels2explore.py` - produce an explore file dataset from given levels
* `explore2summary.py` - display a summary of an explore file

Graphs:
* `graph2gdesc.py` - get graph description from graphs
* `gdesc2graph.py` - generate graphs based on graph description

Graph Utilities:
* `gdesc2summary.py` - display a summary of a graph description file
* `dot2graph.py` - convert dot file to graph file
* `graph2dot.py` - convert graph file to dot file
* `pdb2graph.py` - convert pdb to graph file
* `graph2pdb.py` - convert graph file to pdb
* `tile2graph.py` - convert tile file to graph file
* `mkiv2dot.py` - create dot file of MKIV rules
* `dot2pdf.py` - convert potentially multiple dot files to single pdf



## File Types

* `.lvl`, `.tag`, `.game` - text files containing text level, tags, or game ids, respectively; may contain metadata, sometimes used interchangeably
* `.tileset` - a tileset
* `.tile` - a tileset and levels
* `.scheme` - information needed to generate a level, such as tileset and patterns
* `.result` - a generated level and related metadata
* `.tlvl` - tile level in json
* `.explore` - dataset of levels for the level explorer app
* `.gr` - a graph
* `.gd` - graph description, such as patterns extracted from an example



## Related Publications

* Seth Cooper. 2022. "Sturgeon: tile-based procedural level generation via learned and designed constraints." Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment, 18(1), 26-36. https://doi.org/10.1609/aiide.v18i1.21944

* Seth Cooper. 2022. "Constraint-based 2D tile game blending in the Sturgeon system." Proceedings of the Experimental AI in Games Workshop. https://www.exag.org/papers/Constraint-Based%202D%20Tile%20Game%20Blending%20in%20the%20Sturgeon%20System.pdf

* Seth Cooper. 2023. "Sturgeon-GRAPH: constrained graph generation from examples." Proceedings of the 18th International Conference on the Foundations of Digital Games. https://doi.org/10.1145/3582437.3582465

* Seth Cooper. 2023. "Sturgeon-MKIII: simultaneous level and example playthrough generation via constraint satisfaction with tile rewrite rules." Proceedings of the 14th Workshop on Procedural Content Generation. https://doi.org/10.1145/3582437.3587205

* Hao Mao and Seth Cooper. 2023. "Segment-wise level generation using iterative constrained extension." Proceedings of the 2023 IEEE Conference on Games. https://doi.org/10.1109/CoG57401.2023.10333222

* Seth Cooper and Matthew Guzdial. 2023. "path2level: constraint-based level generation from paths." Proceedings of the 2023 IEEE Conference on Games. https://doi.org/10.1109/CoG57401.2023.10333205

* Seth Cooper and Eden Balema. 2023. "Learning constrained graph layout for content generation." Proceedings of the Experimental AI in Games Workshop. https://ceur-ws.org/Vol-3626/short4.pdf

* Seth Cooper, Faisal Abutarab, Emily Halina and Nathan Sturtevant. 2023. "Visual exploration of tile level datasets." Proceedings of the Experimental AI in Games Workshop. https://ceur-ws.org/Vol-3626/short3.pdf

* Seth Cooper and Mahsa Bazzaz. 2024. "Literally unplayable: on constraint-based generation of uncompletable levels." Proceedings of the 15th Workshop on Procedural Content Generation. https://doi.org/10.1145/3649921.3659844

* Seth Cooper and Mahsa Bazzaz. 2024. "Sturgeon-MKIV: Constraint-Based Level and Playthrough Generation with Graph Label Rewrite Rules." Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment, 20(1), 13-24. https://doi.org/10.1609/aiide.v20i1.31862
