class apbuart_env extends uvm_env;
  
	`uvm_component_utils(apbuart_env)

    // ---------------------------------------
    //  agent and scoreboard instance
    // ---------------------------------------
    apb_agent           apb_agnt;
    uart_agent          uart_agnt;
//     clk_rst_agent       clk_agnt;
    apbuart_scoreboard  apbuart_scb;
    vsequencer          v_sqr;
    
    // --------------------------------------- 
    //  Calling the constructor
    // ---------------------------------------
    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction : new

    extern virtual function void build_phase(uvm_phase phase);
    extern virtual function void connect_phase(uvm_phase phase);
    extern virtual function void final_phase(uvm_phase phase);
    extern task print_all_coverages();
endclass : apbuart_env

// --------------------------------------------------------------
//  build_phase - create the components of scorebaord and agent
// --------------------------------------------------------------
function void apbuart_env::build_phase(uvm_phase phase);
  	super.build_phase(phase);
    apb_agnt        = apb_agent::type_id::create("apb_agnt", this);
    uart_agnt       = uart_agent::type_id::create("uart_agnt", this);
//     clk_agnt        = clk_rst_agent::type_id::create("clk_agnt", this);  
  	apbuart_scb     = apbuart_scoreboard::type_id::create("apbuart_scb", this);
    v_sqr           = vsequencer::type_id::create("v_sqr",this);
endfunction : build_phase


// ------------------------------------------------------------
//  connect_phase - connecting monitor and scoreboard port
// ------------------------------------------------------------
function void apbuart_env::connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    apb_agnt.monitor.item_collected_port_mon.connect(apbuart_scb.item_collected_export_monapb);
   	uart_agnt.driver.item_collected_port_drv.connect(apbuart_scb.item_collected_export_drvuart);
    uart_agnt.monitor.item_collected_port_mon.connect(apbuart_scb.item_collected_export_monuart); 
     
    uvm_config_db#(apb_sequencer)::set(this,"*","apb_sqr",apb_agnt.sequencer);
    uvm_config_db#(uart_sequencer)::set(this,"*","uart_sqr",uart_agnt.sequencer);
endfunction : connect_phase

function void apbuart_env::final_phase(uvm_phase phase);
  super.final_phase(phase);
  fork
    print_all_coverages(); // spawn a task safely
  join_none
endfunction
       
task apbuart_env::print_all_coverages();
  if (apb_agnt != null && apb_agnt.monitor != null)
    apb_agnt.monitor.print_coverage_APB_summary();
  else
    `uvm_warning("APB_MONITOR_NULL", "APB monitor instance is null. Cannot print coverage.")

  if (uart_agnt != null && uart_agnt.monitor != null)
    uart_agnt.monitor.print_coverage_UART_summary();
  else
    `uvm_warning("UART_MONITOR_NULL", "UART monitor instance is null. Cannot print coverage.")
endtask


      

