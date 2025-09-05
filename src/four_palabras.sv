module four_palabras (
    input  logic [7:0] dato,
    input  logic       rx_flat,
    input  logic       rst,
    input  logic       clk,

    output logic [63:0] data_comple,
    output logic        flat_comple
);
    parameter palabras_escale = 8;
    parameter bits_escale = 3;
    logic [bits_escale-1:0]  con;
    logic [7:0]  mem [palabras_escale-2:0]; 
    logic [palabras_escale*8-1:0] var_data_comple;

    // Inicialización
    initial begin
        con          <= bits_escale'h0;
        data_comple  <= 64'h0;
        flat_comple  <= 1'b0;
        for (int j = 0; j < palabras_escale-1; j++) begin
            mem[j] <= 8'h0;
        end
    end

    // Lógica secuencial con reset asíncrono
    always_ff @(posedge clk or negedge rst) begin
        if (!rst) begin
            con          <= bits_escale'h0;
            data_comple  <= 64'h0;
            flat_comple  <= 1'b0;
            for (int j = 0; j < palabras_escale-1; j++) begin
                mem[j] <= 8'h0;
            end
        end
        else begin
            if (rx_flat) begin
                mem[con] <= dato;
                

                if (con == palabras_escale-1) begin
                    flat_comple<=1'b1;
                    var_data_comple=(dato<<(6'd56));
                    //EL 4 ES POR (2**5)/8, DATA SERIA 5 DATA=5.
                    for (int i = 0; i < palabras_escale-1; i = i + 1) begin
                        var_data_comple=var_data_comple+(mem[i]<<(i*4'd8));
                    end
                    data_comple<=var_data_comple;
                    
                    con             <= bits_escale'h0;
                end
                else begin
                    flat_comple <= 1'b0;
                    con      <= con + bits_escale'h1;
                end
            end
        end
    end

endmodule
