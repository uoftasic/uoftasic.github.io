---
title: "tinyCGRA"
slug: tinycgra
summary: "A configurable 2×2 coarse-grained reconfigurable array with serial configuration, implemented in SystemVerilog for Tiny Tapeout."
status: taped-out
date: 2026-05-18
featured: true
render: /assets/projects/tinycgra-die.png
hero: /assets/projects/tinycgra-hero.png
pdk: SKY130
image: /assets/projects/tinycgra-og.png
repo: https://github.com/uoftasic/ttsky-verilog-tinyCGRA
authors: "Rikuto Ide"
specs:
    Shuttle: TTSKY26b
    Die area: 1 × 1 tile
    Clock: 30 MHz
    Processing elements: 4
    Data width: 8 bit
    Configuration: 24 bit serial
    RTL: SystemVerilog
    Flow: OpenLane / LibreLane
    Verification: Cocotb + Python model
    Top module: tt_um_tinycgra
---

tinyCGRA is a small **coarse-grained reconfigurable array (CGRA)** designed for Tiny Tapeout. The taped-out design contains a 2 x 2 mesh of four 8-bit processing elements (PEs), with each PE configured through a serial 6-bit configuration word.

Each PE selects two operands from its **north, south, east, and west** connections, then applies one of three ALU operations: addition, subtraction, or multiplication. The resulting value is registered when the array is enabled, allowing computations to propagate through the mesh over successive clock cycles.

The Tiny Tapeout wrapper exposes the array through the standard 8-bit input and output buses together with the bidirectional pins used for configuration and control. An input byte is first latched and then broadcast to the north and west boundaries of the array, while the south and east boundaries are tied to zero. One PE can be selected for observation through `uo_out`, with an additional debug mode that XORs the outputs of all four PEs.

## Architecture

The core of tinyCGRA is a parameterized PE mesh. The `pe_array_mesh` module generates a configurable `ROWS × COLS` array and connects neighboring PEs directly. For the taped-out configuration this is a 2 × 2 mesh, giving four processing elements connected through the four cardinal directions.

Each PE contains a 6-bit configuration register. The configuration determines both operand routing and the ALU operation:

| Bits    | Function              |
| ------- | --------------------- |
| `[5:4]` | First operand source  |
| `[3:2]` | Second operand source |
| `[1:0]` | ALU operation         |

The operand selectors can independently choose north, south, east, or west. The ALU supports addition, subtraction, and multiplication.

Because the mesh is parameterized, the same PE and interconnect logic can also be synthesized as larger arrays. The repository includes 3 × 3 configurations used for area studies, including both north/south-only and full north/south/east/west connectivity.

## Configuration

The four-PE Tiny Tapeout design uses a **24-bit serial configuration stream**: six bits for each of the four PEs. Configuration is shifted through the array in the order

`PE00 → PE01 → PE10 → PE11`.

During configuration mode, `uio[0]` provides the serial configuration input and `uio[1]` provides the shift enable. The final configuration bit propagates to the `cfg_do` output, while `cfg_done` indicates that all 24 configuration bits have been shifted in.

The design separates configuration from execution using `config_mode`. Once configuration is complete, the same bidirectional pins are repurposed for execution controls and status signals. This allows the complete CGRA to fit within the limited Tiny Tapeout I/O budget.

## Pinout

| Pin       | Function                    |
| --------- | --------------------------- |
| `ui[7:0]` | 8-bit input data            |
| `uo[7:0]` | Selected PE output          |
| `uio[0]`  | `cfg_di` / `cfg_do`         |
| `uio[1]`  | `cfg_shift_en` / `cfg_done` |
| `uio[2]`  | Run enable                  |
| `uio[3]`  | PE output select bit 0      |
| `uio[4]`  | PE output select bit 1      |
| `uio[5]`  | Configuration mode          |
| `uio[6]`  | Input load                  |
| `uio[7]`  | XOR debug mode              |

The input byte on `ui[7:0]` is captured when `load_input` is asserted and subsequently drives both the north and west boundaries of the PE array. `uio[4:3]` selects which of the four PE outputs is presented on `uo_out`. In debug XOR mode, `uo_out` instead reports `PE00 ^ PE01 ^ PE10 ^ PE11`.

## Verification

The design was verified using **Cocotb** alongside a **Python reference model**. The Python model generates configuration bitstreams and calculates the expected cycle-by-cycle behavior of the PE mesh. The RTL testbench then loads the same configurations and compares the hardware outputs against the model.

The main regression covers serial configuration, configuration/run mode transitions, input loading, per-PE execution, PE output selection, and the XOR debug path. The test suite runs multiple mapping cases and boundary input values, checking the result after each execution cycle.

Separate area-study tops were also created to compare different CGRA organizations:

| Configuration | Array | Connectivity | Contexts |
| ------------- | ----: | ------------ | -------: |
| `pat0`        | 2 × 2 | NSWE         |        2 |
| `pat1`        | 3 × 3 | NS           |        2 |
| `pat2`        | 3 × 3 | NSWE         |        1 |

These variants use the same PE and mesh implementation, allowing the effect of array size, connectivity, and configuration contexts to be studied independently of the Tiny Tapeout wrapper.

## Area studies

In addition to the 2 × 2 taped-out design, the repository includes dedicated synthesis tops for evaluating larger and multi-context versions of the architecture. The 3 × 3 top contains nine PEs and can be instantiated with different interconnect and context configurations.

The area-study flow uses Yosys-based synthesis checks and separate Cocotb regressions for each configuration, making it possible to compare the cost of additional PEs, interconnect, and configuration storage before committing to a larger physical implementation.
