module count(input clk,output [7:0] LEDS);

reg [26:0] count;
assign LEDS = count[26:19];

always @(posedge clk) begin
    count <= count + 1;
end

endmodule