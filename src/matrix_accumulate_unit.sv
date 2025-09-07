
module matrix_accumulate_unit #( localparam DATA_WIDTH = 64//, //data width of the module
  
// localparam VAR_WIDTH = 8,  //data width of internal variables
 
 //localparam M_SIZE = 4 //matrix size
 )(

    input logic clock,                           //|<i
    input logic reset,                           //|<i
    input logic clear,                           //|<i
    input logic enable,                          //|<i
    input  logic [DATA_WIDTH-1:0] result,  //|<i
    output logic [DATA_WIDTH-1:0] out      //|>o    
); 

//internal register
logic [DATA_WIDTH-1:0] accumulator;

    always_ff @(posedge clock or negedge reset) begin
        if (!reset) begin
          accumulator <= 64'h0;
        end
        else if (clear) begin
          accumulator <= 64'h0;
        end
        else begin
          accumulator <= result;
        end

    end

//final assignment
assign out = enable ? result + accumulator : accumulator;

endmodule 