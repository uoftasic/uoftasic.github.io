---
title: "SimProc"
slug: simproc
summary: "An 8-bit processor programmable over UART, taped out on the Tiny Tapeout TTSKY25b shuttle."
status: taped-out
date: 2025-11-10
featured: true
render: /assets/projects/simproc-die.png     # card + spec rail
hero: /assets/projects/simproc-hero.png      # full-bleed home hero
caption: "GDS layout, TTSKY25b"
image: /assets/projects/simproc-og.png
repo: https://github.com/uoftasic/simproc
authors: "Saptarshi Talukdar"
specs:
  Process: SKY130
  Shuttle: TTSKY25b
  Die area: 2 × 2 tiles
  Clock: 30 MHz
  Standard cells: "9,199"
  Core utilisation: 59.94 %
  Wire length: 158,110 µm
  On-chip memory: 64 B
  RTL: SystemVerilog
  Flow: OpenLane / LibreLane
  Top module: tt_um_ieeeuoftasic_simproc
---

SimProc is a simple 8-bit processor. Send it three-byte packets over UART and you can
program it, then read memory contents and processor state back out over the same link.
The RTL was written in **SystemVerilog** and validated on a **DE10-Lite FPGA** before
being handed to the hardening flow.

Tiny Tapeout provides a multi-project wafer platform where each design occupies a small
tile within a larger ASIC. SimProc and its UART interface were implemented on a 2 × 2
tile, with on-chip memory reduced from the original 256 bytes to 64 to fit the area
budget.

## Pinout

| Pin | Function |
|---|---|
| `ui[0]` | UART RX |
| `uo[0]` | UART TX |
| `uo[1]` | Halt flag |
| `uo[2]` | Done flag |
| `uio[7:0]` | Clocks per bit — sets the internal UART baud rate |

## Hardening

The OpenLane / LibreLane toolchain automated synthesis, floorplanning and
place-and-route. Aside from adjusting configuration parameters so the design fit within
four tiles and met timing, the path from RTL to GDS was almost entirely automated.

## Where the area went

Nearly half the cell count is fill, which is worth stating plainly — a reader arriving
from FPGA work will see *9,199 cells* and reasonably expect nine thousand cells of logic.

| Cell type | Count | Share |
|---|---:|---:|
| Fill | 4,068 | 44.22 % |
| Combinational | 1,598 | 17.37 % |
| Miscellaneous | 1,305 | 14.18 % |
| Tap | 1,037 | 11.27 % |
| Flip-flops | 706 | 7.69 % |
| Buffers | 443 | 4.81 % |
| Inverters | 42 | 0.46 % |

The shuttle went to fabrication after submission, with chips expected back in May 2026.
