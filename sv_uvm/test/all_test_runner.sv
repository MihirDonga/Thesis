// all_tests_runner.sv
import uvm_pkg::*;
`include "uvm_macros.svh"

class all_test_runner extends apbuart_base_test;
  `uvm_component_utils(all_test_runner)

  function new(string name = "all_test_runner", uvm_component parent = null);
    super.new(name, parent);
  endfunction

  task run_phase(uvm_phase phase);
    string test_names[] = {
      "apbuart_config_test",
      "apbuart_data_compare_test",
      "apbuart_parity_error_test",
      "apbuart_frame_error_test",
      "apbuart_free_error_test",
      "apbuart_rec_drv_test",
      "apbuart_rec_readreg_test"
    };

    foreach (test_names[i]) begin
      `uvm_info("ALL_TEST_RUNNER", $sformatf("Running test: %s", test_names[i]), UVM_LOW)

      // Run each test; run_test is a blocking call that runs and finishes the test
      uvm_root::run_test(test_names[i]);

      // Small delay to separate test runs (optional)
      #(100ns);
    end
  endtask

endclass
