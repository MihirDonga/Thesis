// import uvm_pkg::*;
// `include "uvm_macros.svh"
class apbuart_all_seq extends vseq_base;
  `uvm_object_utils(apbuart_all_seq)
  
  
  function new(string name = "apbuart_all_seq");
    super.new(name);
  endfunction
  
 class apbuart_all_seq extends vseq_base;
  `uvm_object_utils(apbuart_all_seq)

  function new(string name = "apbuart_all_seq");
    super.new(name);
  endfunction

      task body();


        apbuart_config_seq        seq1;
        apbuart_singlebeat_seq    seq2;
        apbuart_NoError_seq       seq3;
        apbuart_parityError_seq   seq4;
        apbuart_frameError_seq    seq5;
        apbuart_recdrv_seq        seq6;
        apbuart_recreadreg_seq    seq7;

        super.body();  // initialize apb_sqr and uart_sqr

        seq1 = apbuart_config_seq::type_id::create("seq1");
        seq2 = apbuart_singlebeat_seq::type_id::create("seq2");
        seq3 = apbuart_NoError_seq::type_id::create("seq3");
        seq4 = apbuart_parityError_seq::type_id::create("seq4");
        seq5 = apbuart_frameError_seq::type_id::create("seq5");
        seq6 = apbuart_recdrv_seq::type_id::create("seq6");
        seq7 = apbuart_recreadreg_seq::type_id::create("seq7");

        `uvm_info("ALL_SEQ", "Running apbuart_config_seq", UVM_MEDIUM)
        seq1.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_singlebeat_seq", UVM_MEDIUM)
        seq2.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_NoError_seq", UVM_MEDIUM)
        seq3.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_parityError_seq", UVM_MEDIUM)
        seq4.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_frameError_seq", UVM_MEDIUM)
        seq5.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_recdrv_seq", UVM_MEDIUM)
        seq6.start(p_sequencer);

        `uvm_info("ALL_SEQ", "Running apbuart_recreadreg_seq", UVM_MEDIUM)
        seq7.start(p_sequencer);
      endtask
	endclass
endclass