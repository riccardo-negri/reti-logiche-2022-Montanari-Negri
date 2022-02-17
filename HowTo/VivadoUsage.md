# Vivado Usage
Prof Miele lecture about Vivado [link](https://politecnicomilano.webex.com/recordingservice/sites/politecnicomilano/recording/68ca392e3fc8103a9b2b0050568221e0/playback).

### Create a project
* RTL Project
* Select a board that starts with `xc7` (in the tutorial the professor selected the board `xc7vx485tffg1157-1`, if there is a problem with the license try with `xc7a200tffv1156-1`)
* To create or import .vhd file: select `Design Sources` folder, right click, click `add sources`, select `add or create design sources` and  make sure `copy sources into project` is checked

### Vivado UI
Useful tools:
* `Project Manager`
* `RTL Analysis` --> Elaborated Design --> Schematic
* `Synthesis` --> Synthetized Design --> Schematic
* `Implementation` --> Run Implementation
* `Simulation` --> Run Simulation

We don't use `IP Integrator`.

### Vivado Docs
Select `Language Templates` on the Flow Navigator sidebar.

### Testbench
To create or import .vhd file: select `sim_1` folder, right click, click `add sources`, select `add or create simulation sources` (it will not be include in the synthesis) and make sure `copy sources into project` is checked.