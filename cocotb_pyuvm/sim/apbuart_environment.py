from pyuvm import *
from apb_agent import APBAgent
from uart_agent import UARTAgent
from apbuart_scoreboard import APBUARTScoreboard
from apbuart_vsequencer import VSequencer

class APBUARTEnv(uvm_env):
    
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.apb_agnt = None  # type: APBAgent
        self.uart_agnt = None  # type: UARTAgent
        self.apbuart_scb = None  # type: APBUARTScoreboard
        self.v_sqr = None  # type: VSequencer

    def build_phase(self):
        super().build_phase()
        # Create components
        self.apb_agnt = APBAgent("apb_agnt",self)
        self.uart_agnt = UARTAgent("uart_agnt",self)
        self.apbuart_scb = APBUARTScoreboard("apbuart_scb",self)
        self.v_sqr = VSequencer("v_sqr",self)

    def connect_phase(self):
        super().connect_phase()
        # Connect analysis ports
        self.apb_agnt.monitor.item_collected_port_mon.connect(
            self.apbuart_scb.item_collected_export_monapb)
        self.uart_agnt.driver.item_collected_port_drv.connect(
            self.apbuart_scb.item_collected_export_drvuart)
        self.uart_agnt.monitor.item_collected_port_mon.connect(
            self.apbuart_scb.item_collected_export_monuart)
        
        self.v_sqr.apb_sqr = self.apb_agnt.sequencer
        self.v_sqr.uart_sqr = self.uart_agnt.sequencer
        print(f"[APBUARTEnv] APB Sequencer connected: {self.v_sqr.apb_sqr is not None}")
        print(f"[APBUARTEnv] UART Sequencer connected: {self.v_sqr.uart_sqr is not None}")
        # Configure virtual sequencer
        ConfigDB().set(self, "*", "apb_sqr", self.apb_agnt.sequencer)
        ConfigDB().set(self, "*", "uart_sqr", self.uart_agnt.sequencer)
        
    # async def final_phase(self):
    #     super().final_phase(phase)
    #     # Start coverage printing as background task
    #     cocotb.start_soon(self.print_all_coverages())

    # async def print_all_coverages(self):
    #     super().print_all_coverages(phase)
    #     if self.apb_agnt and hasattr(self.apb_agnt.monitor, 'print_coverage_APB_summary'):
    #         self.apb_agnt.monitor.print_coverage_APB_summary()
    #     else:
    #         self.logger.warning("APB_MONITOR_NULL", 
    #                           "APB monitor instance is null or missing coverage method")
        
    #     if self.uart_agnt and hasattr(self.uart_agnt.monitor, 'print_coverage_UART_summary'):
    #         self.uart_agnt.monitor.print_coverage_UART_summary()
    #     else:
    #         self.logger.warning("UART_MONITOR_NULL", 
    #                           "UART monitor instance is null or missing coverage method")