`define MONAPB_IF vifapb.MONITOR.monitor_cb

class apb_monitor extends uvm_monitor;
  
  `uvm_component_utils(apb_monitor)
  
// Define a struct to hold transaction data for the covergroup
typedef struct {
  bit        PWRITE;
  bit [31:0] PADDR;
  bit [31:0] PWDATA;
  bit [31:0] PRDATA;
  bit        PSLVERR;
} apb_cov_data_t;

// Covergroup definition (now samples a struct)
covergroup apb_cov_type_t with function sample(apb_cov_data_t data);

  option.per_instance = 1; 
  
  cp_pwrite: coverpoint data.PWRITE {
    bins read  = {0};
    bins write = {1};
  }

  cp_paddr : coverpoint data.PADDR {
    bins addr[4]   = {[32'h0000_0000 : 32'h0000_000C]};
    bins ranges[4] = {[32'h0000_0100 : 32'h0000_01FF], [32'h0000_0200 : 32'h0000_02FF]};
    bins other     = default;
  }

  // Decode frame_len from PWDATA[7:5]
  cp_pdata_7_5 : coverpoint data.PWDATA[7:5] {
    bins frame_5 = {3'b101};
    bins frame_6 = {3'b110};
    bins frame_7 = {3'b111};
    bins frame_8 = {3'b000}; // Assuming wrap-around
  }

  // Decode parity from PWDATA[3:0]
  cp_data_3_0 : coverpoint data.PWDATA[3:0] {
    bins none    = {0};
    bins odd     = {1};
    bins even    = {2};
    bins unknown = {3};
  }

  // Decode n_sb from PWDATA[4]
  cp_data_4 : coverpoint data.PWDATA[4] {
    bins one_stop = {0};
    bins two_stop = {1};
  }

  // Baud rate in PWDATA[31:8]
   cp_pwada : coverpoint data.PWDATA {
    bins common_baud = {4800,9600,14400,19200,38400,57600,115200,128000,63,0};
    bins reserved     = {63, 0}; // Any special codes
    bins misc         = default;
  }

  cp_prdata : coverpoint data.PRDATA {
    bins zero = {32'h0000_0000};
    bins ones = {32'hFFFF_FFFF};
    bins misc = default;
  }

  cp_pslverr : coverpoint data.PSLVERR {
    bins ok    = {0};
    bins error = {1};
    
  }
// Example meaningful cross coverage
    // cross cp_pwrite, cp_paddr {
    //   ignore_bins read_only  = binsof(cp_paddr.special_ranges) && binsof(cp_pwrite.write);
    // }
 
  
endgroup


  // Virtual Interface
  virtual apb_if vifapb;

  // Analysis port to send transactions to the scoreboard
  uvm_analysis_port #(apb_transaction) item_collected_port_mon;
  
  // Transaction being captured
  apb_transaction trans_collected; 

  // Covergroup instance
  apb_cov_type_t apb_cov;

  // Constructor
  function new (string name, uvm_component parent);
    super.new(name, parent);
    trans_collected = new();
    item_collected_port_mon = new("item_collected_port_mon", this);
    apb_cov = new(); // Instantiate the covergroup (no constructor args)
  endfunction : new


      // Build phase: Get the virtual interface
  function void build_phase(uvm_phase phase);
    super.build_phase(phase); 
    if(!uvm_config_db#(virtual apb_if)::get(this, "", "vifapb", vifapb))
      `uvm_fatal("NOVIF",{"virtual interface must be set for: ",get_full_name(),".vifapb"})
  endfunction: build_phase
  
  // Run phase: Monitor transactions and sample coverage
  task run_phase(uvm_phase phase);
    apb_cov_data_t cov_data; // Struct to hold sampled data
    forever begin
      // Wait for a transaction
      wait(`MONAPB_IF.PSELx && `MONAPB_IF.PENABLE);
      wait(`MONAPB_IF.PREADY || `MONAPB_IF.PSLVERR);
      
      @(posedge vifapb.PCLK);
        trans_collected.PSLVERR = `MONAPB_IF.PSLVERR;
      
      trans_collected.PWRITE = `MONAPB_IF.PWRITE;
      trans_collected.PWDATA = `MONAPB_IF.PWDATA;
      trans_collected.PADDR  = `MONAPB_IF.PADDR;
      trans_collected.PRDATA = `MONAPB_IF.PRDATA;
      trans_collected.PREADY = `MONAPB_IF.PREADY;

      // Pack transaction data into the struct
      cov_data.PWRITE  = trans_collected.PWRITE;
      cov_data.PADDR   = trans_collected.PADDR;
      cov_data.PWDATA  = trans_collected.PWDATA;
      cov_data.PRDATA  = trans_collected.PRDATA;
      cov_data.PSLVERR = trans_collected.PSLVERR;

      // Sample the covergroup with the struct
      apb_cov.sample(cov_data);

      // Log the transaction
      `uvm_info(get_type_name(), {"APB Monitor :: Transaction Collected:\n", trans_collected.sprint()}, UVM_HIGH);
      
      // Wait for transaction completion and send to scoreboard
      wait(!`MONAPB_IF.PREADY); 
      item_collected_port_mon.write(trans_collected);
    end
  endtask : run_phase

  // Utility task to print coverage summary
  task print_coverage_APB_summary();
    real coverage_percentage;
    coverage_percentage = $get_coverage();
    `uvm_info("APB_MONITOR", $sformatf("APB Covergroup coverage: %0.2f%%", coverage_percentage), UVM_LOW)
  endtask
endclass