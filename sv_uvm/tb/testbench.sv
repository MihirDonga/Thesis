`include "uvm_macros.svh"
`include "uartinterface.sv" 
`include "apbinterface.sv"
`include "apbuart_property.sv"
`include "testbench_pkg.sv"

module tbench_top;
  
  import uvm_pkg::*;
  import testbench_pkg::*;
  
  bit PCLK;
  bit PRESETn;

//   clk_rst_interface vifclk(PRESETn, PCLK);
  apb_if            vifapb  (PCLK,PRESETn);
  uart_if           vifuart (PCLK,PRESETn);

  apb_uart_top  DUT (
                 	  .PCLK(PCLK),
                 	  .PRESETn(PRESETn),
	             	  .PSELx(vifapb.PSELx),
	             	  .PENABLE(vifapb.PENABLE),
	             	  .PWRITE(vifapb.PWRITE),
	             	  .Tx(vifuart.Tx),
	             	  .RX(vifuart.RX),
	             	  .PREADY(vifapb.PREADY),
	             	  .PSLVERR(vifapb.PSLVERR),
	             	  .PWDATA(vifapb.PWDATA),
	             	  .PADDR(vifapb.PADDR),
	             	  .PRDATA(vifapb.PRDATA)
                    );
	
  apbuart_property assertions (
                              	.PCLK(PCLK),
                 	        	.PRESETn(PRESETn),
	             	            .PSELx(vifapb.PSELx),
	             	            .PENABLE(vifapb.PENABLE),
	             	            .PWRITE(vifapb.PWRITE),
	             	            .PREADY(vifapb.PREADY),
	             	            .PSLVERR(vifapb.PSLVERR),
	             	            .PWDATA(vifapb.PWDATA),
	             	            .PADDR(vifapb.PADDR),
	             	            .PRDATA(vifapb.PRDATA)            
                              );
  
   // Clock Generation: 50 MHz => 20 ns period
  initial begin
    PCLK = 0;
    forever #10 PCLK = ~PCLK;  // 10 ns high, 10 ns low = 20 ns period = 50 MHz
  end

  // Reset Generation
  initial begin
    PRESETn = 0;
    #10;          // Hold reset low for 100 ns
    PRESETn = 1;   // Release reset
  end
  
  initial 
  begin 
    uvm_config_db # (virtual apb_if)::set(uvm_root::get(),"*","vifapb",vifapb);
    uvm_config_db # (virtual uart_if)::set(uvm_root::get(),"*","vifuart",vifuart);
    $dumpfile("dump.vcd"); 
    $dumpvars(0, tbench_top);
  end
  

  initial
    run_test(); // built in func...you can give test name as argument
endmodule


// "[ Virtual Sequence ]
//         |
//         v
// [ UART Driver ] -----> RX ---> [ DUT ] ---> RXDATA ---> [ APB Driver ]
//         |                              |                  |
// [ UART Monitor ]             [ UART Logic ]         [ APB Monitor ]
//         \                            |                  /
//          \__________________________v__________________/
//                                [ Scoreboard ]
// "