module uart_tx_4in4(
input logic clk,start,next_uart,rst,
input logic [63:0] input_dato,
output logic [7:0] Output_dato,
output logic flat_out
);

	logic Flat,First;
	logic [63:0] Dato;
	logic [3:0]Con;
	initial
	begin
		Flat<=1'b0;
			Con<=4'h0;
			First<=1'b0;
			flat_out<=1'b0;
			Output_dato<=8'h0;
			Dato<=64'h0;
	end

	always @(posedge clk,negedge rst)
	begin
		if(!rst)
		begin
			Flat<=1'b0;
			Con<=4'h0;
			First<=1'b0;
			flat_out<=1'b0;
			Output_dato<=8'h0;
			Dato<=64'h0;
		end
		else
		begin
			if (start)
			begin
				Flat<=1'b1;
				flat_out<=1'b1;
				Dato<=input_dato;
				//Output_dato<=input_dato[7:0];
				First<=1'b1;
				Con<=4'h0;
			end
			/*
			if(First)
			begin
				flat_out<=0;
				First<=0;
			end
			*/
			
			if (Flat&(First|next_uart))
			begin
				
				
				First<=1'b0;
				
				if (Con<4'd8)
				begin
					
					Dato<=Dato>>4'd8;
					Con<=Con+4'b01;

					flat_out<=1'b1;
					Output_dato<=Dato[7:0];
					//flat_out<=1;
				end
				else
				begin
					Flat<=1'b0;
					Con<=4'h0;
					flat_out<=1'b0;

					//flat_out<=0;
					//Flat_next_dato_conv<=1;
				end
			end
			
			else
			begin
				
				flat_out<=1'b0;

				
				//Flat_next_dato_conv<=0;
			end
			
		end

	end
endmodule 

