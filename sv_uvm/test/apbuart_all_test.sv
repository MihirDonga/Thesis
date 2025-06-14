class apbuart_all_test extends apbuart_base_test;
  `uvm_component_utils(apbuart_all_test)

  function new(string name = "apbuart_all_test", uvm_component parent = null);
    super.new(name, parent);
  endfunction

  virtual task run_phase(uvm_phase phase);
    apbuart_all_seq all_seq;
    phase.raise_objection(.obj(this));

    all_seq = apbuart_all_seq::type_id::create("all_seq");
    all_seq.start(env_sq.v_sqr);

    phase.drop_objection(.obj(this));
    phase.phase_done.set_drain_time(this, 20);
  endtask
 
endclass
