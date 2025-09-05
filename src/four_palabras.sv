module four_palabras (
    input  logic [7:0] dato,
    input  logic       rx_flat,
    input  logic       rst,
    input  logic       clk,

    output logic [31:0] data_comple,
    output logic        flat_comple
);

    logic [1:0]  con;
    logic [7:0]  mem [0:3]; 
    logic [31:0] var_data_comple;

    // Inicialización
    initial begin
        con          = 2'h0;
        data_comple  = 32'h0;
        flat_comple  = 1'b0;
        for (int j = 0; j < 4; j++) begin
            mem[j] = 8'h0;
        end
    end

    // Lógica secuencial con reset asíncrono
    always_ff @(posedge clk or negedge rst) begin
        if (!rst) begin
            con         <= 2'h0;
            data_comple <= 32'h0;
            flat_comple <= 1'b0;
            for (int j = 0; j < 4; j++) begin
                mem[j] <= 8'h0;
            end
        end
        else begin
            if (rx_flat) begin
                mem[con] <= dato;
                con      <= con + 1;

                if (con == 2'h3) begin
                    var_data_comple = {dato, mem[2], mem[1], mem[0]};
                    data_comple     <= var_data_comple;
                    flat_comple     <= 1'b1;
                    con             <= 2'h0;
                end
                else begin
                    flat_comple <= 1'b0;
                end
            end
        end
    end

endmodule
