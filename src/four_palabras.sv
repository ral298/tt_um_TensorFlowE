module four_palabras (
    input  logic [7:0] dato,
    input  logic       rx_flat,
    input  logic       rst,
    input  logic       clk,

    output logic [15:0] data_comple,
    output logic        flat_comple
);
    parameter palabras_escale = 2;//cantidad de palabras de 8 bits
    parameter bits_escale = 2;
    logic [bits_escale:0]  con;
    logic [7:0]  mem; 
//    logic [palabras_escale*8-1:0] var_data_comple;

    // Inicialización
    initial begin
        con          <= 3'h0;
        data_comple  <= 16'h0;
        flat_comple  <= 1'b0;
        
        mem<= 8'h0;
        //var_data_comple=16'h0;
    end

    // Lógica secuencial con reset asíncrono
    always_ff @(posedge clk or negedge rst) begin
        if (!rst) begin
            con          <= 3'h0;
            data_comple  <= 16'h0;
            flat_comple  <= 1'b0;
            mem<= 8'h0;
            //var_data_comple=16'h0;
        end
        else begin
            if (rx_flat) begin
                if (con==3'h0)
                    mem <= dato;
                

                if (con == palabras_escale-1) begin
                    flat_comple<=1'b1;
                    //var_data_comple=({dato,8'h0});
                    //EL 4 ES POR (2**5)/8, DATA SERIA 5 DATA=5.
                    data_comple<=({dato,mem});
                    //data_comple<=var_data_comple;
                    
                    con             <= 3'h0;
                end
                else begin
                    flat_comple <= 1'b0;
                    con      <= con + 3'h1;
                end
            end
            else
                flat_comple <= 1'b0;
        end
   end

endmodule
/*
module four_palabras (
    input  logic [7:0] dato,
    input  logic       rx_flat,
    input  logic       rst,
    input  logic       clk,

    output logic [15:0] data_comple,
    output logic        flat_comple
);
    parameter palabras_escale = 2;//cantidad de palabras de 8 bits
    parameter bits_escale = 3;
    logic [bits_escale:0]  con;
    logic [7:0]  mem [palabras_escale-2:0]; 
    logic [palabras_escale*8-1:0] var_data_comple;

    // Inicialización
    initial begin
        con          <= 4'h0;
        data_comple  <= 16'h0;
        flat_comple  <= 1'b0;
        for (int j = 0; j < palabras_escale-2; j++) begin
            mem[j] <= 8'h0;
        end
        var_data_comple=16'h0;
    end

    // Lógica secuencial con reset asíncrono
    always_ff @(posedge clk or negedge rst) begin
        if (!rst) begin
            con          <= 4'h0;
            data_comple  <= 16'h0;
            flat_comple  <= 1'b0;
            for (int j = 0; j < palabras_escale-2; j++) begin
                mem[j] <= 8'h0;
            end
            var_data_comple=16'h0;
        end
        else begin
            if (rx_flat) begin
                mem[con[0]] <= dato;
                

                if (con == palabras_escale-1) begin
                    flat_comple<=1'b1;
                    var_data_comple=({8'h0,dato}<<(6'd8));
                    //EL 4 ES POR (2**5)/8, DATA SERIA 5 DATA=5.
                    for (int i = 0; i < palabras_escale-1; i = i + 1) begin
                        var_data_comple=var_data_comple+({8'h0,mem[i]}<<(i*4'd8));
                    end
                    data_comple<=var_data_comple;
                    
                    con             <= 4'h0;
                end
                else begin
                    flat_comple <= 1'b0;
                    con      <= con + 4'h1;
                end
            end
            else
                flat_comple <= 1'b0;
        end
   end

endmodule


*/