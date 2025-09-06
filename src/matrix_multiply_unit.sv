
module matrix_multiply_unit (
    input clk,rst,
    input  logic [63:0] matrixA, //|<i
    input  logic [63:0] matrixB, //|<i
    output logic [63:0] result   //|>o
);

 localparam VAR_WIDTH = 4;
 
 localparam M_SIZE = 4;
    //internal variables 
    logic [VAR_WIDTH-1:0] A1 [0:M_SIZE-1][0:M_SIZE-1];
    logic [VAR_WIDTH-1:0] B1 [0:M_SIZE-1][0:M_SIZE-1];
    logic [VAR_WIDTH-1:0] Res1 [0:M_SIZE-1][0:M_SIZE-1]; 
    initial
    begin
        {A1[0][0],A1[0][1],A1[1][0],A1[1][1],A1[1][2],A1[2][1],A1[2][0],A1[0][2],A1[2][3],A1[3][2],A1[3][0],A1[0][3],A1[3][1],A1[1][3],A1[2][2],A1[3][3]} <= 64'h0;
        {B1[0][0],B1[0][1],B1[1][0],B1[1][1],B1[1][2],B1[2][1],B1[2][0],B1[0][2],B1[2][3],B1[3][2],B1[3][0],B1[0][3],B1[3][1],B1[1][3],B1[2][2],B1[3][3]} <= 64'h0;
        {Res1[0][0],Res1[0][1],Res1[1][0],Res1[1][1],Res1[1][2],Res1[2][1],Res1[2][0],Res1[0][2],Res1[2][3],Res1[3][2],Res1[3][0],Res1[0][3],Res1[3][1],Res1[1][3],Res1[2][2],Res1[3][3]} <= 64'h0; //initialize to zeros.
        
    end

    always @ (posedge clk or negedge rst)
    begin
        if(!rst)
        begin
            {A1[0][0],A1[0][1],A1[1][0],A1[1][1],A1[1][2],A1[2][1],A1[2][0],A1[0][2],A1[2][3],A1[3][2],A1[3][0],A1[0][3],A1[3][1],A1[1][3],A1[2][2],A1[3][3]} <= 64'h0;
            {B1[0][0],B1[0][1],B1[1][0],B1[1][1],B1[1][2],B1[2][1],B1[2][0],B1[0][2],B1[2][3],B1[3][2],B1[3][0],B1[0][3],B1[3][1],B1[1][3],B1[2][2],B1[3][3]} <= 64'h0;
            {Res1[0][0],Res1[0][1],Res1[1][0],Res1[1][1],Res1[1][2],Res1[2][1],Res1[2][0],Res1[0][2],Res1[2][3],Res1[3][2],Res1[3][0],Res1[0][3],Res1[3][1],Res1[1][3],Res1[2][2],Res1[3][3]} <= 64'h0; //initialize to zeros.
            
        end
        else
        begin
            //Initialize the matrices-convert 1 D to 3D arrays
            {A1[0][0],A1[0][1],A1[1][0],A1[1][1],A1[1][2],A1[2][1],A1[2][0],A1[0][2],A1[2][3],A1[3][2],A1[3][0],A1[0][3],A1[3][1],A1[1][3],A1[2][2],A1[3][3]} <= matrixA;
            {B1[0][0],B1[0][1],B1[1][0],B1[1][1],B1[1][2],B1[2][1],B1[2][0],B1[0][2],B1[2][3],B1[3][2],B1[3][0],B1[0][3],B1[3][1],B1[1][3],B1[2][2],B1[3][3]} <= matrixB;
            //{Res1[0][0],Res1[0][1],Res1[1][0],Res1[1][1],Res1[1][2],Res1[2][1],Res1[2][0],Res1[0][2],Res1[2][3],Res1[3][2],Res1[3][0],Res1[0][3],Res1[3][1],Res1[1][3]} = 32'd0; //initialize to zeros.
            
            
            //Matrix multiplication
            for(int i=0;i < 4;i=i+1)
                for(int j=0;j < 4;j=j+1)
                    for(int k=0;k < 4;k=k+1)
                        Res1[i][j] <= Res1[i][j] + (A1[i][k] * B1[k][j]);
            //final output assignment - 3D array to 1D array conversion.
            result <= {Res1[0][0],Res1[0][1],Res1[1][0],Res1[1][1],Res1[1][2],Res1[2][1],Res1[2][0],Res1[0][2],Res1[2][3],Res1[3][2],Res1[3][0],Res1[0][3],Res1[3][1],Res1[1][3],Res1[2][2],Res1[3][3]};
        end
    end 
    
endmodule