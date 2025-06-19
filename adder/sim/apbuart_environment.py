from pyuvm import *

class apbuart_env(uvm_env):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

        self.apb_agnt = None
        self.uart_agnt = None
        self.apbuart_scb = None
        self.v_sqr = None

    def build_phase(self, phase):
        super().build_phase(phase)
        self.apb_agnt = apb_agent.type_id.create("apb_agnt", self)
        self.uart_agnt = uart_agent.type_id.create("uart_agnt", self)
        self.apbuart_scb = apbuart_scoreboard.type_id.create("apbuart_scb", self)
        self.v_sqr = vsequencer.type_id.create("v_sqr", self)

    def connect_phase(self, phase):
        super().connect_phase(phase)

        self.apb_agnt.monitor.item_collected_port_mon.connect(self.apbuart_scb.item_collected_export_monapb)
        self.uart_agnt.driver.item_collected_port_drv.connect(self.apbuart_scb.item_collected_export_drvuart)
        self.uart_agnt.monitor.item_collected_port_mon.connect(self.apbuart_scb.item_collected_export_monuart)

        uvm_config_db.set(self, "*", "apb_sqr", self.apb_agnt.sequencer)
        uvm_config_db.set(self, "*", "uart_sqr", self.uart_agnt.sequencer)

    def final_phase(self, phase):
        super().final_phase(phase)
        # spawn print_all_coverages as a coroutine/task safely
        self._fork(self.print_all_coverages())

    async def print_all_coverages(self):
        if self.apb_agnt is not None and self.apb_agnt.monitor is not None:
            self.apb_agnt.monitor.print_coverage_APB_summary()
        else:
            self.uvm_warning("APB_MONITOR_NULL", "APB monitor instance is null. Cannot print coverage.")

        if self.uart_agnt is not None and self.uart_agnt.monitor is not None:
            self.uart_agnt.monitor.print_coverage_UART_summary()
        else:
            self.uvm_warning("UART_MONITOR_NULL", "UART monitor instance is null. Cannot print coverage.")
