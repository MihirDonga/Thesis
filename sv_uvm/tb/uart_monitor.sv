`define MONUART_IF vifuart.MONITOR.monitor_cb

class uart_monitor extends uvm_monitor;
  
	`uvm_component_utils(uart_monitor)

	// ✅ Coverage struct
	typedef struct {
	logic [31:0] transmitter_reg;
	logic        parity_en;
	logic [6:0]  frame_len;
	logic [3:0]  n_sb;
	} uart_cov_data_t;

	 // ✅ Coverage instance
  	uart_cov_type_t uart_cov;
	
	// ✅ Covergroup definition
	covergroup uart_cov_type_t with function sample(uart_cov_data_t data);

	option.per_instance = 1;
	
	cp_transmitter_reg : coverpoint data.transmitter_reg {
		bins all_zero = {32'h0000_0000};
		bins all_ones = {32'hFFFF_FFFF};
		bins alternating = {32'hAAAAAAAA, 32'h55555555};
		bins misc = default;
	}

	cp_parity_en : coverpoint data.parity_en {
		bins disabled = {0};
		bins enabled = {1};
	}

	cp_frame_len : coverpoint data.frame_len {
		bins len5 = {5};
		bins len6 = {6};
		bins len7 = {7};
		bins len8 = {8};
		bins len9 = {9};
	}

	cp_n_sb : coverpoint data.n_sb {
		bins one_stop = {0};
		bins two_stop = {1};
	}


	endgroup

  	// ---------------------------------------
  	//  Virtual Interface
  	// ---------------------------------------
  	virtual uart_if vifuart;

	// Handle to  a cfg class
  	uart_config cfg; 
  	// ---------------------------------------
  	// analysis port, to send the transaction
  	// to scoreboard
  	// ---------------------------------------
  	uvm_analysis_port #(uart_transaction) item_collected_port_mon;
   
  
  	// ------------------------------------------------------------------------
  	// The following property holds the transaction information currently
  	// begin captured by monitor run phase and make it one transaction.
  	// ------------------------------------------------------------------------
  	uart_transaction trans_collected; 

	logic [6:0] 	count,count1;
	logic [31:0] 	receive_reg;
	logic [6:0] 	LT; 
	logic 			parity_en;  

  	// ---------------------------------------
  	//  new - constructor
  	// ---------------------------------------
  	function new (string name, uvm_component parent);
  	  	super.new(name, parent);
  	  	trans_collected = new();
  	  	item_collected_port_mon = new("item_collected_port_mon", this);
      	uart_cov = new(); // ✅ instantiate coverage
  	endfunction : new

	extern virtual function void build_phase(uvm_phase phase);
	extern virtual function void cfg_settings();
	extern virtual task monitor_and_send();
	extern virtual task run_phase(uvm_phase phase);
    extern virtual task print_coverage_UART_summary();

endclass
	
// -----------------------------------------------
//  build_phase - getting the interface handle
// -----------------------------------------------
function void uart_monitor::build_phase(uvm_phase phase);
	super.build_phase(phase);
	if(!uvm_config_db#(uart_config)::get(this, "", "cfg", cfg))
		`uvm_fatal("No cfg",{"Configuration must be set for: ",get_full_name(),".cfg"});    
  	if(!uvm_config_db#(virtual uart_if)::get(this, "", "vifuart", vifuart))
    	`uvm_fatal("NOVIF",{"virtual interface must be set for: ",get_full_name(),".vifuart"});
endfunction: build_phase
	
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%	
// ------------------------------------------------------------------------------------
// run_phase - convert the signal level activity to transaction level.
// i.e, sample the values on interface signal ans assigns to transaction class fields
// ------------------------------------------------------------------------------------
task uart_monitor::run_phase(uvm_phase phase);
	super.run_phase(phase);
	forever 
	begin
		@(posedge vifuart.PCLK);
		cfg_settings(); // extracting parity enable (parity_en) and loop time (LT).
		monitor_and_send();
	end								
endtask : run_phase
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%	
	
	
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function void uart_monitor::cfg_settings();
	parity_en=cfg.parity[1];
	case(cfg.frame_len)
		5:		LT =7;
		6:		LT =6;
		7:		LT =5;
		8:		LT =4;
		9:		LT =4;
		default:	 `uvm_error(get_type_name(),$sformatf("------ :: Incorrect frame length selected :: ------"))
	endcase
endfunction
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
task uart_monitor::monitor_and_send ();
    uart_cov_data_t cov_data;
	count = 0;
	count1 = 1;

	for(int i=0;i<LT;i++) 
	begin
    	wait(!`MONUART_IF.Tx);  // waiting for start bit
		cfg_settings();
		repeat(cfg.baud_rate/2)@(posedge vifuart.PCLK);
		repeat(cfg.frame_len) 
		begin
			repeat(cfg.baud_rate)@(posedge vifuart.PCLK);
			receive_reg[count]  = `MONUART_IF.Tx;
			count=count+1;
		end		
		if(parity_en)  // if parity is enabled
		begin
			repeat(cfg.baud_rate)@(posedge vifuart.PCLK); // wait for parity bit
		end
		repeat(cfg.n_sb+1)
		begin
			repeat(cfg.baud_rate)@(posedge vifuart.PCLK); // wait for parity bit
		end
      trans_collected.transmitter_reg=receive_reg;
       // ✅ Sample coverage
     
      cov_data.transmitter_reg = trans_collected.transmitter_reg;
      cov_data.parity_en = parity_en;
      cov_data.frame_len = cfg.frame_len;
      cov_data.n_sb = cfg.n_sb;
      uart_cov.sample(cov_data);
	end
	item_collected_port_mon.write(trans_collected); // It sends the transaction non-blocking and it sends to all connected export 
	receive_reg = 32'hx;
endtask
      
 // Utility task to print coverage summary
  task uart_monitor::print_coverage_UART_summary();
    real coverage_percentage;
    coverage_percentage = $get_coverage();
    `uvm_info("UART_MONITOR", $sformatf("UART Covergroup coverage: %0.2f%%", coverage_percentage), UVM_LOW)
    
  endtask
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
