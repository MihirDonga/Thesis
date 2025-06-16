package apb_cov_pkg;

  covergroup apb_cov_type_t with function sample(
    input bit        PWRITE,
    input bit [31:0] PADDR,
    input bit [31:0] PWDATA,
    input bit [31:0] PRDATA,
    input bit        PSLVERR
  );

    option.per_instance = 1;

    cp_pwrite: coverpoint PWRITE {
      bins read  = {0};
      bins write = {1};
    }

    cp_paddr: coverpoint PADDR {
      bins addr[4]   = {[32'h0000_0000 : 32'h0000_000C]};
      bins ranges[4] = {[32'h0000_0100 : 32'h0000_01FF], [32'h0000_0200 : 32'h0000_02FF]};
      bins other     = default;
    }

    cp_pdata_7_5: coverpoint PWDATA[7:5] {
      bins frame_5 = {3'b101};
      bins frame_6 = {3'b110};
      bins frame_7 = {3'b111};
      bins frame_8 = {3'b000};
    }

    cp_data_3_0: coverpoint PWDATA[3:0] {
      bins none    = {0};
      bins odd     = {1};
      bins even    = {2};
      bins unknown = {3};
    }

    cp_data_4: coverpoint PWDATA[4] {
      bins one_stop = {0};
      bins two_stop = {1};
    }

    cp_pwada: coverpoint PWDATA {
      bins common_baud = {4800,9600,14400,19200,38400,57600,115200,128000,63,0};
      bins reserved    = {63, 0};
      bins misc        = default;
    }

    cp_prdata: coverpoint PRDATA {
      bins zero = {32'h0000_0000};
      bins ones = {32'hFFFF_FFFF};
      bins misc = default;
    }

    cp_pslverr: coverpoint PSLVERR {
      bins ok    = {0};
      bins error = {1};
    }

  endgroup

endpackage
