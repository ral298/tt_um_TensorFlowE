# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
import random

@cocotb.test()
async def test_tensorflow_e(dut):
    dut._log.info("Iniciando Test de TensorFlowE")
    
    # Configurar período de reloj a 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())

    # Inicializar señales
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Secuencia de reset
    dut._log.info("Aplicando Reset")
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        lista_bytes = []
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in range(0, 4, 2):
                valor_byte = (fila[i] << 4) | fila[i+1]
                lista_bytes.append(valor_byte)
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz):
        dut._log.info(f"Enviando {nombre_matriz}")
        for valor_byte in bytes_matriz:
            await ClockCycles(dut.clk, 1)
            dut.ui_in.value = valor_byte
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 2)
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 2)
        await ClockCycles(dut.clk, 10)

    # Función para leer resultados
    async def leer_resultados():
        dut._log.info("Leyendo resultados")
        resultados = []
        for i in range(4):  # Esperando 4 bytes de salida (resultado de 16 bits)
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 2)
            resultados.append(dut.uo_out.value.integer)
            dut._log.info(f"Byte leído {i}: {hex(resultados[-1])}")
            dut.uio_in.value = 0b00000000
            await ClockCycles(dut.clk, 3)
        
        # Reconstruir resultado de 16 bits desde los bytes
        valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado final: {hex(valor_resultado)}")
        return valor_resultado

    # =====================================================================
    # PRIMER CASO: Matrices predefinidas (A × Identidad = A)
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices predefinidas ===")

    # Matriz A predefinida
    matriz_A = [
        [1, 2, 3, 4],   # Fila 0
        [5, 6, 7, 8],   # Fila 1
        [9, 10, 11, 12],# Fila 2
        [13, 14, 15, 0] # Fila 3
    ]

    # Matriz B (matriz identidad)
    matriz_B = [
        [1, 0, 0, 0],   # Fila 0
        [0, 1, 0, 0],   # Fila 1
        [0, 0, 1, 0],   # Fila 2
        [0, 0, 0, 1]    # Fila 3
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A)
    matriz_B_bytes = matriz_a_bytes(matriz_B)

    dut._log.info(f"Bytes de Matriz A: {[hex(x) for x in matriz_A_bytes]}")
    dut._log.info(f"Bytes de Matriz B: {[hex(x) for x in matriz_B_bytes]}")

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A")
    await enviar_matriz(matriz_B_bytes, "Matriz B (Identidad)")

    # Esperar cálculo
    dut._log.info("Esperando finalización del cálculo...")
    await ClockCycles(dut.clk, 200)

    # Habilitar acumulación y leer resultados
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 5)

    resultado_1 = await leer_resultados()
    assert resultado_1 != 0, "El resultado no debería ser cero"

    # Limpiar para siguiente prueba
    dut.uio_in.value = 0b00000100  # clear = 1
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 20)

    # =====================================================================
    # SEGUNDO CASO: Matrices aleatorias
    # =====================================================================
    dut._log.info("=== SEGUNDO CASO: Matrices aleatorias ===")

    # Generar matrices aleatorias 4x4 con valores de 0 a 15 (4 bits)
    random.seed(42)  # Semilla para reproducibilidad

    def generar_matriz_aleatoria():
        return [[random.randint(0, 15) for _ in range(4)] for _ in range(4)]

    matriz_A_rand = generar_matriz_aleatoria()
    matriz_B_rand = generar_matriz_aleatoria()

    dut._log.info(f"Matriz A aleatoria: {matriz_A_rand}")
    dut._log.info(f"Matriz B aleatoria: {matriz_B_rand}")

    matriz_A_rand_bytes = matriz_a_bytes(matriz_A_rand)
    matriz_B_rand_bytes = matriz_a_bytes(matriz_B_rand)

    dut._log.info(f"Bytes de Matriz A aleatoria: {[hex(x) for x in matriz_A_rand_bytes]}")
    dut._log.info(f"Bytes de Matriz B aleatoria: {[hex(x) for x in matriz_B_rand_bytes]}")

    # Enviar matrices aleatorias
    await enviar_matriz(matriz_A_rand_bytes, "Matriz A aleatoria")
    await enviar_matriz(matriz_B_rand_bytes, "Matriz B aleatoria")

    # Esperar cálculo
    dut._log.info("Esperando finalización del cálculo con matrices aleatorias...")
    await ClockCycles(dut.clk, 200)

    # Habilitar acumulación y leer resultados
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 5)

    resultado_2 = await leer_resultados()
    assert resultado_2 != 0, "El resultado con matrices aleatorias no debería ser cero"

    # Verificar que los resultados son diferentes (debido a matrices diferentes)
    assert resultado_1 != resultado_2, "Los resultados deberían ser diferentes con matrices diferentes"

    dut._log.info(f"Resultado caso 1: {hex(resultado_1)}")
    dut._log.info(f"Resultado caso 2: {hex(resultado_2)}")

    # =====================================================================
    # TERCER CASO: Matriz cero (caso límite)
    # =====================================================================
    dut._log.info("=== TERCER CASO: Matriz cero (caso límite) ===")

    # Matriz cero
    matriz_cero = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    matriz_cero_bytes = matriz_a_bytes(matriz_cero)

    # Limpiar acumulador
    dut.uio_in.value = 0b00000100  # clear = 1
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 20)

    # Enviar matriz cero y matriz identidad (A × B = 0 × I = 0)
    await enviar_matriz(matriz_cero_bytes, "Matriz Cero")
    await enviar_matriz(matriz_B_bytes, "Matriz Identidad")

    # Esperar cálculo
    await ClockCycles(dut.clk, 200)

    # Leer resultados (debería ser cero o muy cercano a cero)
    resultado_3 = await leer_resultados()
    dut._log.info(f"Resultado con matriz cero: {hex(resultado_3)}")

    # =====================================================================
    # PRUEBA DE CLEAR
    # =====================================================================
    dut._log.info("=== Probando funcionalidad de clear ===")
    
    dut.uio_in.value = 0b00000100  # clear = 1
    await ClockCycles(dut.clk, 2)
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 10)

    # Leer después de clear
    dut.uio_in.value = 0b00000010  # Ena_read = 1
    await ClockCycles(dut.clk, 2)
    valor_limpiado = dut.uo_out.value.integer
    dut.uio_in.value = 0b00000000
    await ClockCycles(dut.clk, 3)

    dut._log.info(f"Valor después de clear: {hex(valor_limpiado)}")

    dut._log.info("=== Todos los tests completados exitosamente ===")
    dut._log.info(f"Resumen:")
    dut._log.info(f"  - Caso 1 (A×I): {hex(resultado_1)}")
    dut._log.info(f"  - Caso 2 (Aleatorio): {hex(resultado_2)}")
    dut._log.info(f"  - Caso 3 (Cero×I): {hex(resultado_3)}")
    dut._log.info(f"  - Después de clear: {hex(valor_limpiado)}")