+sv
+incdir+./rtl
+access+rwc
-coverage all
-covdut apb_uart_tb
-covoverwrite
-covwork cov_work
+incdir+./tb
+incdir+./rtl

// RTL files (make sure to list all needed RTL files here)
rtl/Defines.sv
rtl/apb_slave.sv
rtl/apb_uart.sv
rtl/apb_uart_top.sv
rtl/tick_generator.sv
rtl/uart_rx_BB.sv
rtl/uart_transmitter.sv

tb/apbinterface.sv
tb/uartinterface.sv

// tb/apb_transaction.sv
// tb/uart_transaction.sv

// // UART agent files
// tb/uart_monitor.sv
// tb/uart_driver.sv
// tb/uart_sequencer.sv
// tb/uart_sequence.sv
// tb/uart_config.sv
// tb/uart_agent.sv

// // APB agent files
// tb/apb_monitor.sv
// tb/apb_driver.sv
// tb/apb_sequencer.sv
// tb/apb_sequence.sv
// tb/apb_config.sv
// tb/apb_agent.sv
// tb/apb_transaction.sv

// tb/apbuart_scoreboard.sv
// tb/apbuart_vsequencer.sv
// tb/apbuart_environment.sv

// // UVM sequencer and scoreboard files
// tb/apbuart_vseq_base.sv

// Testbench package and UVM components
tb/testbench_pkg.sv

// Test files
// tb/apbuart_base_test.sv
// tb/apbuart_rec_readreg_test.sv
// tb/apbuart_rec_drv_test.sv
// tb/apbuart_parity_error_test.sv
// tb/apbuart_free_error_test.sv
// tb/apbuart_frame_error_test.sv
// tb/apbuart_data_compare_test.sv
// tb/apbuart_config_test.sv

// Top level testbench
tb/testbench.sv


