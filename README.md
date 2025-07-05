# Thesis

coverage and .ucd fil egenrate  :  xrun -sv -coverage all -timescale 1ns/1ps +incdir+./rtl rtl/*.sv tb/apb_uart_tb.sv

simvision                       :  simvision /scratch/mihir/workarea/Thesis/Thesis/sv_uvm/cov_work/scope/test/icc_78f163a3_00000000.ucd  

rtl  compile                    :  xrun -sv -f filelist.f -access +rwc -compile

Test run : xrun -64bit -uvm -sv -f filelist.f +UVM_TESTNAME=apbuart_parity_error_test -top tbench_top -access +rwc -coverage functional -covoverwrite -covwork cov_work



SV_UVM:
    Config Coverage: 75.35% with 200 samples    50      simtime : 0.048 ms
    Config Coverage: 82.52% with 400 samples    100     simtime : 0.096 ms
    Config Coverage: 86.40% with 800 samples    200     simtime : 0.19 ms
    Config Coverage: 87.38% with 1600 samples   400     simtime : 0.38 ms
    Config Coverage: 87.50% with 3200 samples   800     simtime : 0.76 ms
    Config Coverage: 87.50% with 6400 samples   1600    simtime : 1.53 ms
    Config Coverage: 87.50% with 12800 samples  3200    simtime : 3.07 ms

cocotb_pyuvm:
    Config Coverage: 100.00% (7008 samples)  3200
                Simulation Time: 6,144,100 ns = ~6.1 ms
                Real Time:      161.69 seconds = ~2.7 minutes

    Config Coverage: 99.50% (3346 samples)  1600
                Simulation Time: 3,073,100 ns = ~3.07 ms
                Real Time:      80.71 seconds = ~1.34 minutes

    Config Coverage: 97.75% (1778 samples)  800
                Simulation Time: 1,536,100 ns = ~1.54 ms
                Real Time:      41.46 seconds = ~0.69 minutes
    
    Config Coverage: 93.38% (840 samples)  400
                Simulation Time: 786,100 ns = ~0.77 ms
                Real Time:      20.34 seconds = ~0.34 minutes

    Config Coverage: 88.25% (489 samples)  200
                Simulation Time: 384,100 ns = ~0.384 ms
                Real Time:      10.54 seconds = ~0.18 minutes
    
    Config Coverage: 84.38% (210 samples)  100
                Simulation Time: 192,100 ns = ~0.192 ms
                Real Time:      5.23 seconds = ~0.087 minutes
    
    Config Coverage: 82.62% (142 samples)  50
                Simulation Time: 96,100 ns = ~0.096 ms
                Real Time:      2.65 seconds = ~0.044 minutes

    