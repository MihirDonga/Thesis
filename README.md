# Thesis

coverage and .ucd fil egenrate  :  xrun -sv -coverage all -timescale 1ns/1ps +incdir+./rtl rtl/*.sv tb/apb_uart_tb.sv

simvision                       :  simvision /scratch/mihir/workarea/Thesis/Thesis/sv_uvm/cov_work/scope/test/icc_78f163a3_00000000.ucd  

rtl  compile                    :  xrun -sv -f filelist.f -access +rwc -compile

Test run : xrun -64bit -uvm -sv -f filelist.f +UVM_TESTNAME=apbuart_parity_error_test -top tbench_top -access +rwc -coverage functional -covoverwrite -covwork cov_work



SV_UVM:
    Config Coverage: 75.35% with 200 samples    50
    Config Coverage: 82.52% with 400 samples    100
    Config Coverage: 86.40% with 800 samples    200
    Config Coverage: 87.38% with 1600 samples   400
    Config Coverage: 87.50% with 3200 samples   800
    Config Coverage: 87.50% with 6400 samples   1600
    Config Coverage: 87.50% with 12800 samples  3200

cocotb_pyuvm:
    Config Coverage: 100.00% (7008 samples)  3200
                Simulation Time: 6,144,100 ns = ~6.1 ms
                Real Time:      161.69 seconds = ~2.7 minutes
                
    Config Coverage: 99.31% (3532 samples)  1600

