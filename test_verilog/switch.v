module switch (in_0, in_1, key, out_0, out_1);
  input in_0;
  input in_1;
  input key;

  output out_0;
  output out_1;

  wire out_0;
  wire out_1;
  wire k_b;
  wire n_3;
  wire n_1;
  wire n_2;
  wire n_0;

  assign out_0 = n_0 | n_1;
  assign out_1 = n_3 | n_2;
  assign k_b = ~key;
  assign n_3 = in_1 & k_b;
  assign n_1 = in_1 & key;
  assign n_2 = in_0 & key;
  assign n_0 = in_0 & k_b;
endmodule
