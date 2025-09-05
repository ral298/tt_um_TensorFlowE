module TensorFlowE (
    input logic [7:0]Datos_in,
    input logic Ena_write,rts,clk,Ena_read,clear,enable_accu,
    output logic [7:0] Datos_out
    );


logic [63:0] dato_in_64_bits_A;
//logic [63:0] dato_in_32_bits_B;
logic [63:0] dato_in_64_bits;

logic [63:0] dato_in_64_bits_resultado;
logic [63:0] dato_in_64_bits_output;
logic flat_64_comple;
four_palabras four_palabras_Unit(
    .dato(Datos_in),
    .rx_flat(Ena_write),
    .rst(rst),
    .clk(clk),

    .data_comple(dato_in_64_bits),
    .flat_comple(flat_64_comple)
);

logic conta_palabras;

logic ena_TPU;

logic 

    always_ff @(posedge clk or negedge rst)
    begin
        if (!rst)
        begin
            conta_palabras<=1'b0;
            //ena_TPU<=1'b0;
            dato_in_64_bits_A<=64'h0;
        end
        else
        begin
            if (!conta_palabras & flat_64_comple)
            begin
                dato_in_64_bits_A<= dato_in_64_bits;
                //ena_TPU<=1'b0;
            end
            /*
            else if (conta_palabras & flat_64_comple)
            begin
                
                ena_TPU<=1'b1;
            end
            */
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
    .enable(enable_accu),//ena_TPU
    .result(dato_in_64_bits_resultado),
    .out(dato_in_64_bits_output)
); 

endmodule

