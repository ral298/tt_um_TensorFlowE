module TensorFlowE (
    input logic [7:0]Datos_in,
    input logic Ena_write,rts,clk,Ena_read,clear,enable_accu,
    output logic [7:0] Datos_out,
    output logic Ena_out
    );


logic [63:0] dato_in_64_bits_A;
//logic [63:0] dato_in_32_bits_B;
logic [63:0] dato_in_64_bits;

logic [63:0] dato_in_64_bits_resultado;
logic [63:0] dato_in_64_bits_output;
logic flat_64_comple;

logic Ena_write_retradado,Ena_write_Ena;



four_palabras four_palabras_Unit(
    .dato(Datos_in),
    .rx_flat(Ena_write_Ena),
    .rst(rst),
    .clk(clk),

    .data_comple(dato_in_64_bits),
    .flat_comple(flat_64_comple)
);

logic conta_palabras;
logic Ena_accu_Ena;
logic Ena_accu_retradado;
logic Ena_read_Ena;
logic Ena_read_retradado;
assign Ena_write_Ena=(!Ena_write_retradado )&Ena_write;

assign Ena_accu_Ena=(!Ena_accu_retradado )&enable_accu;
assign Ena_read_Ena=(!Ena_read_retradado)&Ena_read;

initial
begin
    conta_palabras<=1'b0;
    ena_TPU<=1'b0;
    dato_in_64_bits_A<=64'h0;
    Ena_write_retradado<=1'h0;
    Ena_accu_retradado<=1'h0;
end

    always_ff @(posedge clk or negedge rst)
    begin
        if (!rst)
        begin
            conta_palabras<=1'b0;
            //ena_TPU<=1'b0;
            dato_in_64_bits_A<=64'h0;
            Ena_write_retradado<=1'h0;
            Ena_accu_retradado<=1'h0;
            Ena_read_retradado<=1'h0;
        end
        else
        begin

            Ena_write_retradado<=Ena_write;
            Ena_accu_retradado<=enable_accu;
            Ena_read_retradado<=Ena_read_retradado;
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
        end

    end





matrix_multiply_unit matrix_multiply_unit_u(
    
    .matrixA(dato_in_64_bits_A), //|<i
    .matrixB(dato_in_64_bits), //|<i
    .result(dato_in_64_bits_resultado)   //|>o
);


matrix_accumulate_unit matrix_accumulate_unit_u(

    .clock(clk),
    .reset(rst),
    .clear(clear),
    .enable(Ena_accu_Ena),//ena_TPU
    .result(dato_in_64_bits_resultado),
    .out(dato_in_64_bits_output)
); 


uart_tx_4in4 uart_tx_4in4_u(
.clk(clk),
.start,
.next_uart(Ena_read_Ena),
.rst(rst),
.input_dato(dato_in_64_bits_output),
.Output_dato(Datos_out),
.flat_out(Ena_out)


endmodule

