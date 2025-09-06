# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 0
    
    
    
    A_1=145
    A_2=221
    A_3=101
    A_4=8
    A_5=251
    A_6=123
    A_7=54
    A_8=23
    datoA=f'{A_1:08b}'+f'{A_2:08b}'+f'{A_3:08b}'+f'{A_4:08b}'+f'{A_5:08b}'+f'{A_6:08b}'+f'{A_7:08b}'+f'{A_8:08b}'
    
    datoA=datoA[::-1]
    
    B_1=132
    B_2=102
    B_3=251
    B_4=34
    B_5=29
    B_6=121
    B_7=10
    B_8=104
    datoB=f'{B_1:08b}'+f'{B_2:08b}'+f'{B_3:08b}'+f'{B_4:08b}'+f'{B_5:08b}'+f'{B_6:08b}'+f'{B_7:08b}'+f'{B_8:08b}'
    datoB=datoB[::-1]
    
    
    
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    for indix_a in range(8):
        await ClockCycles(dut.clk, 1)
        datos_a=(datoA[indix_a*8:indix_a*8+8])[::-1]
        dut.ui_in.value = int(datos_a,2)
        dut.uio_in.value = int("00000001",2)
        await ClockCycles(dut.clk, 3)
        dut.uio_in.value = int("00000000",2)
        await ClockCycles(dut.clk, 4)
    
    await ClockCycles(dut.clk, 10)
    for indix_b in range(8):
        await ClockCycles(dut.clk, 1)
        datos_b=(datoB[indix_b*8:indix_b*8+8])[::-1]
        dut.ui_in.value = int(datos_b,2)
        dut.uio_in.value = int("00000001",2)
        await ClockCycles(dut.clk, 3)
        dut.uio_in.value = int("00000000",2)
        await ClockCycles(dut.clk, 4)
    await ClockCycles(dut.clk, 1000)

    
