package uart_cov_pkg;

  covergroup uart_cov_type_t with function sample(
    input logic [31:0] transmitter_reg,
    input logic        parity_en,
    input logic [6:0]  frame_len,
    input logic [3:0]  n_sb
  );

    option.per_instance = 1;

    cp_transmitter_reg : coverpoint transmitter_reg {
      bins all_zero     = {32'h0000_0000};
      bins all_ones     = {32'hFFFF_FFFF};
      bins alternating  = {32'hAAAAAAAA, 32'h55555555};
      bins misc         = default;
    }

    cp_parity_en : coverpoint parity_en {
      bins disabled = {0};
      bins enabled  = {1};
    }

    cp_frame_len : coverpoint frame_len {
      bins len5 = {5};
      bins len6 = {6};
      bins len7 = {7};
      bins len8 = {8};
      bins len9 = {9};
    }

    cp_n_sb : coverpoint n_sb {
      bins one_stop = {0};
      bins two_stop = {1};
    }

  endgroup

endpackage
