`include "uvm_macros.svh"
import uvm_pkg::*;

class apbuart_config_test extends apbuart_base_test;
  `uvm_component_utils(apbuart_config_test)

  apbuart_config_seq apbuart_config_sq;

  function new(string name="apbuart_config_test", uvm_component parent=null);
    super.new(name, parent);
  endfunction

  virtual function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    apbuart_config_sq = apbuart_config_seq::type_id::create("apbuart_config_sq", this);
  endfunction

  virtual task run_phase(uvm_phase phase);
    repeat(cfg.loop_time) begin
      set_config_params(9600, 8, 3, 1, 1);
      cfg.print();
      set_apbconfig_params(2, 1);
      apb_cfg.print();
      phase.raise_objection(this);
      apbuart_config_sq.start(env_sq.v_sqr);
      phase.drop_objection(this);
    end
    phase.phase_done.set_drain_time(this, 20);
  endtask

endclass
