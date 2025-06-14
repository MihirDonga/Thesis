// tb/apb_uart_tb.sv
module apb_uart_tb;

  logic PCLK;
  logic PRESETn;
  logic PSELx;
  logic PENABLE;
  logic PWRITE;
  logic [31:0] PWDATA;
  logic [31:0] PADDR;
  logic RX;
  logic [32:0] PRDATA;
  logic PREADY;
  logic PSLVERR;
  logic Tx;

  // Instantiate DUT
  apb_uart_top dut (
    .PCLK(PCLK), .PRESETn(PRESETn), .PSELx(PSELx), .PENABLE(PENABLE),
    .PWRITE(PWRITE), .PWDATA(PWDATA), .PADDR(PADDR), .RX(RX),
    .PRDATA(PRDATA), .PREADY(PREADY), .PSLVERR(PSLVERR), .Tx(Tx)
  );

  // Clock generation
  initial PCLK = 0;
  always #5 PCLK = ~PCLK;

  // Stimulus
  initial begin
    PRESETn = 0; RX = 1; PSELx = 0; PENABLE = 0; PWRITE = 0;
    PWDATA = 8'h00; PADDR = 4'h0;
    #20 PRESETn = 1;

    // APB write example
    apb_write(4'h1, 8'hA5);
    apb_read(4'h1);

    #100 $finish;
  end

  // APB read/write tasks
  task apb_write(input logic [3:0] addr, input logic [7:0] data);
    @(posedge PCLK);
    PSELx = 1; PWRITE = 1; PADDR = addr; PWDATA = data;
    PENABLE = 0;
    @(posedge PCLK);
    PENABLE = 1;
    @(posedge PCLK);
    PSELx = 0; PENABLE = 0; PWRITE = 0;
  endtask

  task apb_read(input logic [3:0] addr);
    @(posedge PCLK);
    PSELx = 1; PWRITE = 0; PADDR = addr;
    PENABLE = 0;
    @(posedge PCLK);
    PENABLE = 1;
    @(posedge PCLK);
    $display("Read from %h: %h", addr, PRDATA);
    PSELx = 0; PENABLE = 0;
  endtask

endmodule

