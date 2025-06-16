// `define MONAPB_IF vifapb.MONITOR.monitor_cb
// import apb_cov_pkg::*;

// class apb_monitor extends uvm_monitor;
  
//   `uvm_component_utils(apb_monitor)
  
//   // Define a struct to hold transaction data for the covergroup
//   typedef struct {
//     bit        PWRITE;
//     bit [31:0] PADDR;
//     bit [31:0] PWDATA;
//     bit [31:0] PRDATA;
//     bit        PSLVERR;
//   } apb_cov_data_t;


//   // Covergroup definition (now samples a struct)
//   covergroup apb_cov_type_t with function sample(
//       input bit        PWRITE,
//       input bit [31:0] PADDR,
//       input bit [31:0] PWDATA,
//       input bit [31:0] PRDATA,
//       input bit        PSLVERR
//     );

//     option.per_instance = 1; 
    
//     cp_pwrite: coverpoint data.PWRITE {
//       bins read  = {0};
//       bins write = {1};
//     }

//     cp_paddr : coverpoint data.PADDR {
//       bins addr[4]   = {[32'h0000_0000 : 32'h0000_000C]};
//       bins ranges[4] = {[32'h0000_0100 : 32'h0000_01FF], [32'h0000_0200 : 32'h0000_02FF]};
//       bins other     = default;
//     }

//     // Decode frame_len from PWDATA[7:5]
//     cp_pdata_7_5 : coverpoint data.PWDATA[7:5] {
//       bins frame_5 = {3'b101};
//       bins frame_6 = {3'b110};
//       bins frame_7 = {3'b111};
//       bins frame_8 = {3'b000}; // Assuming wrap-around
//     }

//     // Decode parity from PWDATA[3:0]
//     cp_data_3_0 : coverpoint data.PWDATA[3:0] {
//       bins none    = {0};
//       bins odd     = {1};
//       bins even    = {2};
//       bins unknown = {3};
//     }

//     // Decode n_sb from PWDATA[4]
//     cp_data_4 : coverpoint data.PWDATA[4] {
//       bins one_stop = {0};
//       bins two_stop = {1};
//     }

//     // Baud rate in PWDATA[31:8]
//     cp_pwada : coverpoint data.PWDATA {
//       bins common_baud = {4800,9600,14400,19200,38400,57600,115200,128000,63,0};
//       bins reserved     = {63, 0}; // Any special codes
//       bins misc         = default;
//     }

//     cp_prdata : coverpoint data.PRDATA {
//       bins zero = {32'h0000_0000};
//       bins ones = {32'hFFFF_FFFF};
//       bins misc = default;
//     }

//     cp_pslverr : coverpoint data.PSLVERR {
//       bins ok    = {0};
//       bins error = {1};
      
//     }
//   // Example meaningful cross coverage
//       // cross cp_pwrite, cp_paddr {
//       //   ignore_bins read_only  = binsof(cp_paddr.special_ranges) && binsof(cp_pwrite.write);
//       // }
  
    
//   endgroup


//   // Covergroup instance
//   apb_cov_type_t apb_cov;

//   // Virtual Interface
//   virtual apb_if vifapb;

//   // Analysis port to send transactions to the scoreboard
//   uvm_analysis_port #(apb_transaction) item_collected_port_mon;
  
//   // Transaction being captured
//   apb_transaction trans_collected; 

//   // Constructor
//   function new (string name, uvm_component parent);
//     super.new(name, parent);
//     trans_collected = new();
//     item_collected_port_mon = new("item_collected_port_mon", this);
//     apb_cov = new(); // Instantiate the covergroup (no constructor args)
//   endfunction : new


//       // Build phase: Get the virtual interface
//   function void build_phase(uvm_phase phase);
//     super.build_phase(phase); 
//     if(!uvm_config_db#(virtual apb_if)::get(this, "", "vifapb", vifapb))
//       `uvm_fatal("NOVIF",{"virtual interface must be set for: ",get_full_name(),".vifapb"})
//   endfunction: build_phase
  
//   // Run phase: Monitor transactions and sample coverage
//   task run_phase(uvm_phase phase);
//     apb_cov_data_t cov_data; // Struct to hold sampled data
//     forever begin
//       // Wait for a transaction
//       wait(`MONAPB_IF.PSELx && `MONAPB_IF.PENABLE);
//       wait(`MONAPB_IF.PREADY || `MONAPB_IF.PSLVERR);
      
//       @(posedge vifapb.PCLK);
//         trans_collected.PSLVERR = `MONAPB_IF.PSLVERR;
      
//       trans_collected.PWRITE = `MONAPB_IF.PWRITE;
//       trans_collected.PWDATA = `MONAPB_IF.PWDATA;
//       trans_collected.PADDR  = `MONAPB_IF.PADDR;
//       trans_collected.PRDATA = `MONAPB_IF.PRDATA;
//       trans_collected.PREADY = `MONAPB_IF.PREADY;

//       // Pack transaction data into the struct
//       cov_data.PWRITE  = trans_collected.PWRITE;
//       cov_data.PADDR   = trans_collected.PADDR;
//       cov_data.PWDATA  = trans_collected.PWDATA;
//       cov_data.PRDATA  = trans_collected.PRDATA;
//       cov_data.PSLVERR = trans_collected.PSLVERR;

//       // Sample the covergroup with the struct
//       apb_cov.sample(
//               cov_data.PWRITE,
//               cov_data.PADDR,
//               cov_data.PWDATA,
//               cov_data.PRDATA,
//               cov_data.PSLVERR
//             );
//       // Log the transaction
//       `uvm_info(get_type_name(), {"APB Monitor :: Transaction Collected:\n", trans_collected.sprint()}, UVM_HIGH);
      
//       // Wait for transaction completion and send to scoreboard
//       wait(!`MONAPB_IF.PREADY); 
//       item_collected_port_mon.write(trans_collected);
//     end
//   endtask : run_phase

//   // Utility task to print coverage summary
//   task print_coverage_APB_summary();
//     real coverage_percentage;
//     coverage_percentage = $get_coverage();
//     `uvm_info("APB_MONITOR", $sformatf("APB Covergroup coverage: %0.2f%%", coverage_percentage), UVM_LOW)
//   endtask
// endclass
`define MONAPB_IF vifapb.MONITOR.monitor_cb

class apb_monitor extends uvm_monitor;
  `uvm_component_utils(apb_monitor)
  
  // Virtual Interface
  virtual apb_if vifapb;

  // Analysis port
  uvm_analysis_port #(apb_transaction) item_collected_port_mon;
  
  // Transaction objects
  apb_transaction trans_collected;
  apb_transaction cov_data;  // For coverage sampling
  
  // Covergroup definition
  covergroup apb_fcov;
    option.per_instance = 1;
    
    // PWRITE coverage
    PWRITE_CP: coverpoint cov_data.PWRITE {
      bins read  = {0};
      bins write = {1};
    }
    
    // PADDR coverage
    PADDR_CP: coverpoint cov_data.PADDR {
      bins addr_ranges[4] = {[32'h0000_0000 : 32'h0000_000C]};
      bins special_ranges = {[32'h0000_0100 : 32'h0000_01FF], 
                            [32'h0000_0200 : 32'h0000_02FF]};
      bins other = default;
    }
    
    // PWDATA coverage - frame_len bits [7:5]
    FRAME_LEN_CP: coverpoint cov_data.PWDATA[7:5] {
      bins frame_5 = {3'b101};
      bins frame_6 = {3'b110};
      bins frame_7 = {3'b111};
      bins frame_8 = {3'b000};
    }
    
    // PWDATA coverage - parity bits [3:0]
    PARITY_CP: coverpoint cov_data.PWDATA[3:0] {
      bins none    = {0};
      bins odd     = {1};
      bins even    = {2};
      bins unknown = {[3:15]};
    }
    
    // PWDATA coverage - stop bit [4]
    STOP_BIT_CP: coverpoint cov_data.PWDATA[4] {
      bins one_stop = {0};
      bins two_stop = {1};
    }
    
    // PWDATA coverage - baud rate [31:8]
    BAUD_RATE_CP: coverpoint cov_data.PWDATA {
      bins common_baud = {4800,9600,14400,19200,38400,57600,115200,128000};
      bins special_codes = {0,63};
      bins misc = default;
    }
    
    // PRDATA coverage
    PRDATA_CP: coverpoint cov_data.PRDATA {
      bins zero = {32'h0000_0000};
      bins ones = {32'hFFFF_FFFF};
      bins misc = default;
    }
    
    // PSLVERR coverage
    PSLVERR_CP: coverpoint cov_data.PSLVERR {
      bins ok    = {0};
      bins error = {1};
    }
    
    // Cross coverage examples
    WRITE_X_ADDR: cross PWRITE_CP, PADDR_CP {
      ignore_bins read_only = binsof(PWRITE_CP.read) && binsof(PADDR_CP.special_ranges);
    }
    
    FRAME_X_PARITY: cross FRAME_LEN_CP, PARITY_CP;
  endgroup
  
  // Constructor
  function new(string name, uvm_component parent);
    super.new(name, parent);
    trans_collected = new();
    item_collected_port_mon = new("item_collected_port_mon", this);
    apb_fcov = new();  // Initialize covergroup
  endfunction
  
  // Build phase
  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if(!uvm_config_db#(virtual apb_if)::get(this, "", "vifapb", vifapb))
      `uvm_fatal("NOVIF", "Virtual interface must be set");
  endfunction
  
  // Run phase
  task run_phase(uvm_phase phase);
    super.run_phase(phase);
    forever begin
      // Wait for a transaction
      wait(`MONAPB_IF.PSELx && `MONAPB_IF.PENABLE);
      wait(`MONAPB_IF.PREADY || `MONAPB_IF.PSLVERR);
      
      @(posedge vifapb.PCLK);
      
      // Capture transaction data
      trans_collected.PSLVERR = `MONAPB_IF.PSLVERR;
      trans_collected.PWRITE = `MONAPB_IF.PWRITE;
      trans_collected.PWDATA = `MONAPB_IF.PWDATA;
      trans_collected.PADDR = `MONAPB_IF.PADDR;
      trans_collected.PRDATA = `MONAPB_IF.PRDATA;
      trans_collected.PREADY = `MONAPB_IF.PREADY;
      
      // Prepare coverage data
      cov_data = trans_collected;
      
      // Sample coverage
      apb_fcov.sample();
      
      // Log and send transaction
      `uvm_info(get_type_name(), $sformatf("APB Transaction:\n%s", trans_collected.sprint()), UVM_HIGH);
      item_collected_port_mon.write(trans_collected);
      
      // Wait for transaction completion
      wait(!`MONAPB_IF.PREADY);
    end
  endtask
  
  // Coverage report
  task print_coverage_APB_summary();
    real coverage = apb_fcov.get_inst_coverage();
    `uvm_info("APB_COVERAGE", $sformatf("APB Coverage: %0.2f%%", coverage), UVM_MEDIUM)
  endtask
endclass