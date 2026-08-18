---
title: "SimProc: TinyTapeout"
excerpt: "Submitting an 8-bit processor to the TTSKY25b shuttle — what fit in four tiles, and what did not."
tags:
  - tapeout
  - tiny-tapeout
  - sky130
project: simproc
---

 This week, the ASIC Team submitted **SimProc (Simple Processor)** as a part of the TinyTapeout TTSKY25b shuttle on 10 November 2025. 
 
 TinyTapeout provides a multi-project wafer (MPW) platform where each design occupies a small tile within the final ASIC. 
 
 SimProc, along with an integrated UART-based communication interface, was implemented on a 2x2 tile (approximately 320×200 µm), with an on-chip memory size of 64 bytes (reduced from the original 256 bytes due to size limitations).

 The RTL for SimProc was written in **SystemVerilog** and first validated on a **DE10-Lite FPGA**. The tapeout flow was then handled by the **OpenLane/LibreLane** toolchain, which automated synthesis, floorplanning, and place-and-route. Aside from adjusting configuration parameters to ensure the design fit within a 2×2 tile and met timing, the end-to-end process from RTL to ASIC was almost entirely automated.

 The shuttle is now in fabrication, with chips expected to arrive in **May 2026**.

## ASIC Technical Details

After running the design through the OpenLane/LibreLane toolchain, the TinyTapeout GitHub workflow automatically executed synthesis, place-and-route, verification, and GDS generation. The resulting reports summarize resource usage, timing, and physical layout for the final SKY130 implementation of SimProc.


### Technical Specifications :
- **Recommended Clock Frequency:** 30 MHz  
- **Standard Cell Count:** 9199 cells  
- **Cell Area Usage:** 59.94% of 2×2 tile  
- **Total Wire Length:** 158,110 µm
- **Memory:** 64 bytes (implemented as flip-flops)  

- **Standard Cell Breakdown:**

  | Cell Type        | Count | Percentage |
  |------------------|-------|------------|
  | Combinational    | 1598     | 17.37% |
  | Flip Flops       | 706      | 7.69%  |
  | Buffers          | 443      | 4.81%  |
  | Inverters        | 42       | 0.46%  |
  | Fill             | 4068     | 44.22% |
  | Tap              | 1037     | 11.27% |
  | Misc             | 1305     | 14.18% |
  | **Total**        | 9199     | 100%   |


### I/O Signal Mapping (TinyTapeout Pinout)

SimProc uses TinyTapeout’s standard 8-pin I/O structure:  
- `ui[7:0]`: input
- `uo[7:0]`: output
- `uio[7:0]`: bidirectional (we use them as inputs)

The mapping for our design is:

| Pin # | Input          | Output     | Bidirectional     | 
|-------|----------------|------------|--------------------
| 0     | uart_rx        | uart_tx    | clk_per_bit[0]    |
| 1     | -              | halt       | clk_per_bit[1]    |
| 2     | -              | done       | clk_per_bit[2]    |
| 3     | -              | -          | clk_per_bit[3]    |
| 4     | -              | -          | clk_per_bit[4]    |
| 5     | -              | -          | clk_per_bit[5]    |
| 6     | -              | -          | clk_per_bit[6]    |
| 7     | -              | -          | clk_per_bit[7]    |

The UART baud rate can be configured using the 8-bit **clk_per_bit** input, given by the equation:

**BAUD = f_clk / (4 × clk_per_bit)**

### I/O Summary

- **UART:**  
  - RX on `ui[0]`  
  - TX on `uo[0]`  
  - Baud rate set using `uio[7:0]` (clk_per_bit)

- **Status Flags:**  
  - `halt` flag on `uo[1]`  
  - `done` flag on `uo[2]`  

## SimProc Design Overview

**SimProc** is a compact 8-bit CPU designed entirely from scratch in SystemVerilog.  
Its architecture was originally introduced in my **ECE243 (Computer Organization)** course, where our professor designed and explained the fundamentals of SimProc. Inspired by that, I implemented the full processor in SystemVerilog and adapted it for ASIC fabrication through TinyTapeout.  

The CPU features a minimalist instruction set of **11 atomic operations**, supported by a **64-byte unified memory** for both data and program storage.  

To make the processor more interactive and extensible, I integrated a **UART interface** for serial communication - enabling programming, monitoring, and debugging directly over a terminal connection.  
I’m also developing a **C library API** that provides a higher-level interface for communicating with the chip, making it easier to send instructions, read memory, and control execution from a host computer.






