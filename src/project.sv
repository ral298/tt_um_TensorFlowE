/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  logic [7:0] ui_in,    // Dedicated inputs
    output logic [7:0] uo_out,   // Dedicated outputs
    input  logic [7:0] uio_in,   // IOs: Input path
    output logic [7:0] uio_out,  // IOs: Output path
    output logic [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  logic       ena,      // always 1 when the design is powered, so you can ignore it
    input  logic       clk,      // clock
    input  logic       rst_n     // reset_n - low to reset
);
  assign uio_oe  = 8'b0001_0000;
  
  // List all unused inputs to prevent warnings
logic _unused = &{ena, uio_in[7:5],uio_out[7:5],uio_out[3:0], 1'b0, };
  
TensorFlowE core(
    .Datos_in(ui_in),
    .Ena_write(uio_in[0]),
    .rts(rst_n),
    .clk(clk),
    .Ena_read(uio_in[1]),
    .clear(uio_in[2]),
    .enable_accu(uio_in[3]),
    .Datos_out(uo_out),
    .Ena_out(uio_in[4])

);


endmodule
