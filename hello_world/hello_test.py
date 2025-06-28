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

class FullAdderItem(uvm_sequence_item):
    def __init__(self, name="full_adder_item"):
        super().__init__(name)
        self.a = 0
        self.b = 0
        self.cin = 0

class FullAdderDriver(uvm_driver):
    async def run_phase(self):
        while True:
            item = await self.seq_item_port.get_next_item()
            self.raise_objection()
            await Timer(1, "NS")
            dut.a.value = item.a
            dut.b.value = item.b
            dut.cin.value = item.cin
            self.drop_objection()
            self.seq_item_port.item_done()

class FullAdderMonitor(uvm_monitor):
    def __init__(self, name, parent, dut):
        super().__init__(name, parent)
        self.dut = dut

    async def run_phase(self):
        while True:
            await Timer(1, "NS")
            tr = FullAdderItem()
            tr.sum = int(self.dut.sum.value)
            tr.cout = int(self.dut.cout.value)
            self.analysis_port.write(tr)

class FullAdderScoreboard(uvm_scoreboard):
    def build_phase(self):
        self.analysis_imp = uvm_analysis_imp("analysis_imp", self)

    def write(self, tr):
        expected_sum = tr.a ^ tr.b ^ tr.cin
        expected_cout = (tr.a & tr.b) | (tr.cin & (tr.a ^ tr.b))
        
        if tr.sum != expected_sum or tr.cout != expected_cout:
            self.logger.error(f"Mismatch! a={tr.a}, b={tr.b}, cin={tr.cin}")
            self.logger.error(f"Got sum={tr.sum}, cout={tr.cout}")
            self.logger.error(f"Expected sum={expected_sum}, cout={expected_cout}")

class FullAdderEnv(uvm_env):
    def build_phase(self):
        self.driver = FullAdderDriver("driver", self)
        self.monitor = FullAdderMonitor("monitor", self, cocotb.top)
        self.scoreboard = FullAdderScoreboard("scoreboard", self)

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.env = FullAdderEnv("env", self)

@cocotb.test()
async def run_test(dut):
    """Test full adder"""
    await uvm_root().run_test("FullAdderTest")