# from pyuvm import *
# import random

# class HelloWorld(uvm_component):
#     def build_phase(self):
#         self.logger.info("Build phase: Hello World!")

#     async def run_phase(self):
#         self.raise_objection()
#         self.logger.info("Run phase: Hello World!")
#         self.drop_objection()

# class HelloTest(uvm_test):
#     def build_phase(self):
#         self.hello = HelloWorld("hello", self)

#     def end_of_elaboration_phase(self):
#         self.print_topology()

# @cocotb.test()
# async def hello_uvm(dut):
#     """Test pyuvm with Xcelium/Icarus"""
#     await uvm_root().run_test("HelloTest")
from pyuvm import *
import random
from cocotb.triggers import Timer

class FullAdderItem(uvm_sequence_item):
    def __init__(self, name="full_adder_item"):
        super().__init__(name)
        self.a = 0
        self.b = 0
        self.cin = 0
        self.sum = 0
        self.cout = 0

class FullAdderDriver(uvm_driver):
    def start_of_simulation_phase(self):
        self.dut = cocotb.top

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.get_next_item()
            self.raise_objection()
            await Timer(1, "NS")
            self.dut.a.value = item.a
            self.dut.b.value = item.b
            self.dut.cin.value = item.cin
            self.drop_objection()
            self.seq_item_port.item_done()

class FullAdderMonitor(uvm_monitor):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.dut = cocotb.top
        self.analysis_port = uvm_analysis_port("analysis_port", self)

    async def run_phase(self):
        while True:
            await Timer(1, "NS")
            tr = FullAdderItem()
            tr.a = int(self.dut.a.value)
            tr.b = int(self.dut.b.value)
            tr.cin = int(self.dut.cin.value)
            tr.sum = int(self.dut.sum.value)
            tr.cout = int(self.dut.cout.value)
            self.analysis_port.write(tr)

class FullAdderScoreboard(uvm_scoreboard):
    def build_phase(self):
        self.analysis_export = uvm_analysis_export("analysis_export", self)
        self.fifo = uvm_tlm_analysis_fifo("fifo", self)
        self.analysis_export.connect(self.fifo.analysis_export)

    def check_phase(self):
        while self.fifo.has_analysis():
            tr = self.fifo.get()
            expected_sum = tr.a ^ tr.b ^ tr.cin
            expected_cout = (tr.a & tr.b) | (tr.cin & (tr.a ^ tr.b))
            
            if tr.sum != expected_sum or tr.cout != expected_cout:
                self.logger.error(f"Mismatch! Inputs: a={tr.a}, b={tr.b}, cin={tr.cin}")
                self.logger.error(f"Expected: sum={expected_sum}, cout={expected_cout}")
                self.logger.error(f"Received: sum={tr.sum}, cout={tr.cout}")

class FullAdderEnv(uvm_env):
    def build_phase(self):
        self.driver = FullAdderDriver("driver", self)
        self.monitor = FullAdderMonitor("monitor", self)
        self.scoreboard = FullAdderScoreboard("scoreboard", self)

    def connect_phase(self):
        self.monitor.analysis_port.connect(self.scoreboard.analysis_export)

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.env = FullAdderEnv("env", self)

@cocotb.test()
async def run_test(dut):
    """Test full adder"""
    await uvm_root().run_test("FullAdderTest")