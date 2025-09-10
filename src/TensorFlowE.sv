module TensorFlowE (
    input logic [7:0]Datos_in,
    input logic Ena_write,rst,clk,Ena_read,clear,enable_accu,
    output logic [7:0] Datos_out,
    output logic Ena_out
    );

logic ena_TPU;
logic [15:0] dato_in_64_bits_A;
//logic [63:0] dato_in_32_bits_B;
logic [15:0] dato_in_64_bits;

logic [15:0] dato_in_64_bits_resultado;
logic [15:0] dato_in_64_bits_output;
logic flat_64_comple;

logic Ena_write_retradado;
logic Ena_write_retradado_re;
logic Ena_write_Ena;

logic conta_palabras;
logic Ena_accu_Ena;
logic Ena_accu_retradado;
logic Ena_accu_retradado_re;
logic Ena_read_Ena;
logic Ena_read_retradado;
logic Ena_read_retradado_re;



logic Ena_clear_Ena;
logic Ena_clear_retradado;
logic Ena_clear_retradado_re;

logic flat_out_tx;
logic dato_disponible;
logic listo;
logic flat_Ena_accu_Ena;
//  logic flat_listo;
assign Ena_write_Ena=(!Ena_write_retradado_re )&Ena_write_retradado;

assign Ena_accu_Ena=(!Ena_accu_retradado_re )&Ena_accu_retradado;
assign Ena_read_Ena=(!Ena_read_retradado_re)&Ena_read_retradado;

assign Ena_clear_Ena=(!Ena_clear_retradado_re)&Ena_clear_retradado;

initial
begin
            dato_disponible<=1'b0;
            conta_palabras<=1'b0;
            ena_TPU<=1'b0;
            dato_in_64_bits_A<=16'h0;
            Ena_write_retradado<=1'h0;
            Ena_accu_retradado<=1'h0;
            Ena_read_retradado<=1'h0;
            Ena_write_retradado_re<=1'h0;
            Ena_accu_retradado_re<=1'h0;
            Ena_read_retradado_re<=1'h0;
            Ena_clear_retradado<=1'h0;
            Ena_clear_retradado_re<=1'h0;
            flat_Ena_accu_Ena<=1'h0;
            //flat_listo<=1'h0;
end

    always_ff @(posedge clk or negedge rst)
    begin
        if (!rst)
        begin
            dato_disponible<=1'b0;
            conta_palabras<=1'b0;
            ena_TPU<=1'b0;
            dato_in_64_bits_A<=16'h0;
            Ena_write_retradado<=1'h0;
            Ena_accu_retradado<=1'h0;
            Ena_read_retradado<=1'h0;
            Ena_write_retradado_re<=1'h0;
            Ena_accu_retradado_re<=1'h0;
            Ena_read_retradado_re<=1'h0;
            Ena_clear_retradado<=1'h0;
            Ena_clear_retradado_re<=1'h0;
            flat_Ena_accu_Ena<=1'h0;
            //flat_listo<=1'h0;

        end
        else
        begin
            if (listo)
                dato_disponible<=1'b1;

            if (dato_disponible & Ena_read_Ena)
                dato_disponible<=1'b0;
            Ena_write_retradado<=Ena_write;
            Ena_write_retradado_re<=Ena_write_retradado;
            Ena_accu_retradado<=enable_accu;
            Ena_accu_retradado_re<=Ena_accu_retradado;
            Ena_read_retradado<=Ena_read;
            Ena_read_retradado_re<=Ena_read_retradado;

            Ena_clear_retradado<=clear;
            Ena_clear_retradado_re<=Ena_clear_retradado;
	    
            if (Ena_accu_Ena & (!listo))
                flat_Ena_accu_Ena<=1'h1;
            else if ((!Ena_accu_Ena )& Ena_clear_Ena)
                flat_Ena_accu_Ena<=1'h0;

            /*
            if (listo)
                flat_listo<=1'h1;
            else if (Ena_clear_Ena)
                flat_listo<=1'h0;
            */
            if (!conta_palabras & flat_64_comple)
            begin
                dato_in_64_bits_A<= dato_in_64_bits;
                ena_TPU<=1'b0;
                conta_palabras<=1'b1;
            end

            else if (conta_palabras & flat_64_comple)
            begin
                conta_palabras<=1'b0;
                ena_TPU<=1'b1;
            end
            else if(!conta_palabras)
                ena_TPU<=1'b0;
        end

    end

matrix_multiply_unit multiply_unit_u ( //#(.DATA_WIDTH(64), .VAR_WIDTH (8), .M_SIZE(4)) 
    .clk(clk),.rst(rst),
    .enable(ena_TPU),
    .matrixA(dato_in_64_bits_A), //|<i
    .matrixB(dato_in_64_bits), //|<i
    .result(dato_in_64_bits_resultado),   //|>o
    .listo(listo)
);



matrix_accumulate_unit  accumulate_unit_u (

    .clock(clk),
    .reset(rst),
    .clear(Ena_clear_Ena),
    .listo(listo),
    .enable(flat_Ena_accu_Ena),//ena_TPU////&flat_listo
    .result(dato_in_64_bits_resultado),
    .out(dato_in_64_bits_output)
); 




four_palabras four_palabras_Unit(
    .dato(Datos_in),
    .rx_flat(Ena_write_Ena),
    .rst(rst),
    .clk(clk),

    .data_comple(dato_in_64_bits),
    .flat_comple(flat_64_comple)
);
uart_tx_4in4 uart_tx_u(
    .clk(clk),
    .start(dato_disponible & Ena_read_Ena),
    .next_uart(Ena_read_Ena),
    .rst(rst),
    .input_dato(dato_in_64_bits_output),
    .Output_dato(Datos_out),
    .flat_out(flat_out_tx)
);


reg [2:0] estado_actual;

    // Lógica para la transición de estados (Contador Síncrono)
    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            estado_actual <= 3'b000; // Reset a 0
            Ena_out<=1'b0;
        end else if (estado_actual == 3'b000) begin
            if (flat_out_tx)begin
                estado_actual <= 3'b001; // Reinicia a 0 después del estado 5
                Ena_out<=1'b1;
            end
        end else if (estado_actual == 3'b101) begin
            
                estado_actual <= 3'b000; // Reinicia a 0 después del estado 5
                Ena_out<=1'b0;
            
        end else begin
            estado_actual <= estado_actual + 3'h1; // Incrementa el contador
        end
    end




endmodule

