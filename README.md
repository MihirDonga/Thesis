# Thesis

coverage and .ucd fil egenrate  :  xrun -sv -coverage all -timescale 1ns/1ps +incdir+./rtl rtl/*.sv tb/apb_uart_tb.sv

simvision                       :  simvision /scratch/mihir/workarea/Thesis/Thesis/sv_uvm/cov_work/scope/test/icc_78f163a3_00000000.ucd  

rtl  compile                    :  xrun -sv -f filelist.f -access +rwc -compile

Test run : xrun -64bit -uvm -sv -f filelist.f +UVM_TESTNAME=apbuart_parity_error_test -top tbench_top -access +rwc -coverage functional -covoverwrite -covwork cov_work



SV_UVM:
    Config Coverage: 75.35% with 200 samples
    Config Coverage: 82.52% with 400 samples
    
