# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge
from cocotb.binary import BinaryValue
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")
    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    
    
    
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()

    # # =====================================================================
    # # PRUEBA DE SEÑALES BÁSICAS
    # # =====================================================================
    # dut._log.info("=== Probando señales basicas ===")
    
    # # Probar clear
    # dut._log.info("Probando clear...")
    # dut.uio_in.value = 0b00000100  # clear = 1
    # await ClockCycles(dut.clk, 5)
    # dut.uio_in.value = 0b00000000
    # await ClockCycles(dut.clk, 10)
    # await debug_signals()

    # # Probar enable_accu
    # dut._log.info("Probando enable_accu...")
    # dut.uio_in.value = 0b00001000  # enable_accu = 1
    # await ClockCycles(dut.clk, 5)
    # dut.uio_in.value = 0b00000000
    # await ClockCycles(dut.clk, 10)
    # await debug_signals()

    # # Probar Ena_read
    # dut._log.info("Probando Ena_read...")
    # dut.uio_in.value = 0b00000010  # Ena_read = 1
    # await ClockCycles(dut.clk, 5)
    # dut.uio_in.value = 0b00000000
    # await ClockCycles(dut.clk, 10)
    # await debug_signals()

    # dut._log.info("=== Test de diagnostico completado ===")
    # dut._log.info("Test de diagnostico completado exitosamente")

@cocotb.test()
async def test_tensorflow_e2(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")

    # Matrices muy simples para debug
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    
    
    
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()

@cocotb.test()
async def test_tensorflow_e3(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")

    # Activar lectura
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_accu = 0
    await ClockCycles(dut.clk, 1)
    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()

@cocotb.test()
async def test_tensorflow_e4(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    
    dut._log.info("=== PRIMER CASO: Matrices simples ===")
    # Debug inicial
    await debug_signals(dut)
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_accu = 0
    await ClockCycles(dut.clk, 1)
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]
    
    
    # Activar lectura
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    
    # Activar lectura
    dut.uio_in.value = 0b00000100  # enable_clear = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_clear = 0
    await ClockCycles(dut.clk, 1)
    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 0],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    
    
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()
        

@cocotb.test()
async def test_tensorflow_e5(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")

    # Activar lectura
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_accu = 0
    await ClockCycles(dut.clk, 1)
    
    
    
    
    
    #Datos de entrada 1
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 2
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 3
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    
    
    #Datos de entrada 4
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)




    #Datos de entrada 5
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [2, 2],   # Identidad
        [2, 2],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)



    #Datos de entrada 6
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)









    # Intentar leer resultados
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()

@cocotb.test()
async def test_tensorflow_e6(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")

    # Activar lectura
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_accu = 0
    await ClockCycles(dut.clk, 1)
    
    
    
    
    
    #Datos de entrada 1
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 2
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 3
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    
    
    #Datos de entrada 4
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)




    #Datos de entrada 5
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [2, 2],   # Identidad
        [2, 2],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)



    #Datos de entrada 6
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)

    # Activar lectura
    dut.uio_in.value = 0b00000100  # enable_clear = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_clear = 0
    await ClockCycles(dut.clk, 1)
    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 0],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)

    







    # Intentar leer resultados
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()



@cocotb.test()
async def test_tensorflow_e7(dut):
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
    await ClockCycles(dut.clk, 10)

    # Función para convertir matrices a formato de datos serial
    def matriz_a_bytes(matriz):
        """Convertir matriz 4x4 con elementos de 4 bits a 8 bytes"""
        
        lista_bytes=""
        for fila in matriz:
            # Empaquetar dos elementos de 4 bits en cada byte
            for i in fila:
                lista_bytes+=f'{i:04b}'
        return lista_bytes

    # Función para enviar una matriz al DUT
    async def enviar_matriz(bytes_matriz, nombre_matriz,dut):
        dut._log.info(f"Enviando {nombre_matriz}")
        for index in range(2):
            await ClockCycles(dut.clk, 1)
            
            datos_a=(bytes_matriz[index*8:index*8+8])
            dut.ui_in.value = int(datos_a[4:8]+datos_a[0:4],2)
            
            
            dut.uio_in.value = 0b00000001  # Ena_write = 1
            await ClockCycles(dut.clk, 3)  # Más tiempo para estabilizar
            dut.uio_in.value = 0b00000000  # Ena_write = 0
            await ClockCycles(dut.clk, 3)
        # await ClockCycles(dut.clk, 20)  # Más tiempo entre matrices

    # Función para leer resultados de forma segura
    async def leer_resultados(dut):
        
        resultados = []
        await debug_signals(dut,tiempo=15)# tiempo necesario para obtener los datos, 15 es el tiempo minimo propuesto,
        # para ello se hicieron las mediciones usandl mkwave
        
        dut._log.info("Leyendo resultados")
        for i in range(2):  # Esperando 4 bytes de salida
            # Esperar a que la salida sea estable
            await ClockCycles(dut.clk, 5)
            
            
            
            # Activar lectura
            dut.uio_in.value = 0b00000010  # Ena_read = 1
            await ClockCycles(dut.clk, 5)
            dut.uio_in.value = 0b00000000 # Ena_read = 0
            await ClockCycles(dut.clk, 1)
            
            # Leer valor de forma segura manejando 'x'
            valor_actual = dut.uo_out.value
            
            valor_acticacion = (dut.uio_out.value).integer
            
            if valor_actual.is_resolvable:
                valor_int = valor_actual.integer
                dato_out8b=f'{valor_int:08b}'
                
                
                
                resultados.append([int(dato_out8b[4:8],2),int(dato_out8b[0:4],2)])
                dut._log.info(f"Byte leído {i}: {resultados[i]}")
                dut._log.info(f"Byte leido : {valor_acticacion:08b}")
            else:
                valor_int = 0  # Default si hay 'x'
                dut._log.warning(f"Byte leído {i}: Valor indeterminado (x), usando 0")
            
            
        # Reconstruir resultado
        # valor_resultado = (resultados[3] << 24) | (resultados[2] << 16) | (resultados[1] << 8) | resultados[0]
        dut._log.info(f"Resultado reconstruido: {resultados}")
        return resultados

    # Función para debuggear señales internas
    async def debug_signals(dut,tiempo=2):
        dut._log.info("=== DEBUG SEÑALES ===")
        dut._log.info(f"uo_out: {dut.uo_out.value}")
        dut._log.info(f"uio_out: {dut.uio_out.value}")
        dut._log.info(f"uio_oe: {dut.uio_oe.value}")
        await ClockCycles(dut.clk, tiempo)

    # =====================================================================
    # PRIMER CASO: Matrices pequeñas simples
    # =====================================================================
    dut._log.info("=== PRIMER CASO: Matrices simples ===")

    # Activar lectura
    dut.uio_in.value = 0b00001000  # enable_accu = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_accu = 0
    await ClockCycles(dut.clk, 1)
    
    
    
    
    
    #Datos de entrada 1
    # Matrices muy simples para debug
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 2
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    #Datos de entrada 3
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)
    
    
    
    
    
    #Datos de entrada 4
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 2],
    ]

    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)




    #Datos de entrada 5
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [2, 2],   # Identidad
        [2, 2],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    await debug_signals(dut,tiempo=20)
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)



    #Datos de entrada 6
    matriz_A_simple = [
        [1, 0],   # Identidad
        [0, 1],
    ]
    
    matriz_B_simple = [
        [1, 1],   # Identidad
        [1, 1],
    ]
    
    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)
    
    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")
    
    
    # Debug inicial
    await debug_signals(dut)
    
    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)

    # Activar lectura
    dut.uio_in.value = 0b00000100  # enable_clear = 1
    await ClockCycles(dut.clk, 5)
    dut.uio_in.value = 0b00000000 # enable_clear = 0
    await ClockCycles(dut.clk, 1)
    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [2, 0],   # Identidad
        [0, 0],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    await debug_signals(dut,tiempo=20)

    

    
    # Matrices muy simples para debug
    matriz_A_simple = [
        [0, 0],   # Identidad
        [0, 1],
    ]

    matriz_B_simple = [
        [4, 1],   # Identidad
        [2, 5],
    ]

    matriz_A_bytes = matriz_a_bytes(matriz_A_simple)
    matriz_B_bytes = matriz_a_bytes(matriz_B_simple)

    dut._log.info(f"Matriz A simple: {matriz_A_simple}")
    dut._log.info(f"Matriz B simple: {matriz_B_simple}")
    dut._log.info(f"Bytes Matriz A: {matriz_A_bytes}")
    dut._log.info(f"Bytes Matriz B: {matriz_B_bytes}")

    # Debug inicial
    await debug_signals(dut)

    # Enviar matrices
    await enviar_matriz(matriz_A_bytes, "Matriz A simple",dut)
    await debug_signals(dut)
    
    await enviar_matriz(matriz_B_bytes, "Matriz B simple",dut)
    





    # Intentar leer resultados
    # # Esperar cálculo con más tiempo
    # dut._log.info("Esperando cálculo...")
    # for i in range(50):
    #     await ClockCycles(dut.clk, 10)
    #     if i % 10 == 0:
    #         dut._log.info(f"Esperando... ciclo {i}")
    #         await debug_signals()

    # Intentar leer resultados
    # await leer_resultados(dut)
    try:
        resultado = await leer_resultados(dut)
        dut._log.info(f"Resultado obtenido: {resultado}")
        await debug_signals(dut,tiempo=10)
        # # Verificación básica
        # if resultado != 0:
        #     dut._log.info(" Test pasado - Resultado no cero")
        # else:
        #     dut._log.warning(" ️  Resultado cero - puede ser válido para este caso")
            
    except Exception as e:
        dut._log.error(f"Error leyendo resultados: {e}")
        await debug_signals()

