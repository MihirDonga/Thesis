`define MONAPB_IF vifapb.MONITOR.monitor_cb
import apb_cov_pkg::*;

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
`define MONUART_IF vifuart.MONITOR.monitor_cb

class uart_monitor extends uvm_monitor;
  `uvm_component_utils(uart_monitor)

  virtual uart_if vifuart;
  uvm_analysis_port #(uart_transaction) item_collected_port_mon;
  uart_config cfg;
  uart_transaction trans_collected;

  logic [6:0] count, count1;
  logic [31:0] receive_reg;
  logic [6:0] LT;
  logic parity_en;

  typedef struct {
    logic [31:0] transmitter_reg;
    logic parity_en;
    logic [6:0] frame_len;
    logic [3:0] n_sb;
  } uart_cov_data_t;

  // ✅ Covergroup defined inside the class
  covergroup uart_fcov with function sample(uart_cov_data_t data);
    option.per_instance = 1;

    TRANSMITTER_REG: coverpoint data.transmitter_reg {
      bins all_zero = {32'h0000_0000};
      bins all_ones = {32'hFFFF_FFFF};
      bins alternating = {32'hAAAAAAAA, 32'h55555555};
      bins misc = default;
    }

    PARITY_EN: coverpoint data.parity_en {
      bins disabled = {0};
      bins enabled  = {1};
    }

    FRAME_LEN: coverpoint data.frame_len {
      bins len5 = {5};
      bins len6 = {6};
      bins len7 = {7};
      bins len8 = {8};
      bins len9 = {9};
    }

    STOP_BITS: coverpoint data.n_sb {
      bins one_stop = {0};
      bins two_stop = {1};
    }

    PARITY_X_FRAME: cross PARITY_EN, FRAME_LEN;
  endgroup

  uart_fcov cov; // ✅ Now legal since covergroup is defined above

  function new(string name = "uart_monitor", uvm_component parent = null);
    super.new(name, parent);
    trans_collected = new();
    item_collected_port_mon = new("item_collected_port_mon", this);
    cov = new(); // ✅ Proper instantiation
  endfunction

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    if (!uvm_config_db#(uart_config)::get(this, "", "cfg", cfg))
      `uvm_fatal("NOCFG", "Configuration must be set");
    if (!uvm_config_db#(virtual uart_if)::get(this, "", "vifuart", vifuart))
      `uvm_fatal("NOVIF", "Virtual interface must be set");
  endfunction

  task run_phase(uvm_phase phase);
    super.run_phase(phase);
    forever begin
      @(posedge vifuart.PCLK);
      cfg_settings();
      monitor_and_send();
    end
  endtask

  function void cfg_settings();
    parity_en = cfg.parity[1];
    case(cfg.frame_len)
      5: LT = 7;
      6: LT = 6;
      7: LT = 5;
      8: LT = 4;
      9: LT = 4;
      default: `uvm_error(get_type_name(), "Incorrect frame length selected")
    endcase
  endfunction

  task monitor_and_send();
    uart_cov_data_t cov_data;
    count = 0;
    count1 = 1;

    for (int i = 0; i < LT; i++) begin
      wait(!vifuart.Tx);  // Wait for start bit
      cfg_settings();

      repeat(cfg.baud_rate/2) @(posedge vifuart.PCLK);
      repeat(cfg.frame_len) begin
        repeat(cfg.baud_rate) @(posedge vifuart.PCLK);
        receive_reg[count] = vifuart.Tx;
        count++;
      end

      if (parity_en)
        repeat(cfg.baud_rate) @(posedge vifuart.PCLK);

      repeat(cfg.n_sb + 1) begin
        repeat(cfg.baud_rate) @(posedge vifuart.PCLK);
      end

      trans_collected.transmitter_reg = receive_reg;

      cov_data.transmitter_reg = receive_reg;
      cov_data.parity_en       = parity_en;
      cov_data.frame_len       = cfg.frame_len;
      cov_data.n_sb            = cfg.n_sb;

      cov.sample(cov_data);
      item_collected_port_mon.write(trans_collected);
      receive_reg = 32'hx;
    end
  endtask

  function void print_coverage_UART_summary();
    real coverage = cov.get_inst_coverage();
    `uvm_info("COVERAGE", $sformatf("UART Coverage: %0.2f%%", coverage), UVM_MEDIUM)
  endfunction
endclass
