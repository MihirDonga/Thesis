from pyuvm import *
import random

class HelloWorld(uvm_component):
    def build_phase(self):
        self.logger.info("Build phase: Hello World!")

    async def run_phase(self):
        self.raise_objection()
        self.logger.info("Run phase: Hello World!")
        self.drop_objection()

class HelloTest(uvm_test):
    def build_phase(self):
        self.hello = HelloWorld("hello", self)

    def end_of_elaboration_phase(self):
        self.print_topology()

@cocotb.test()
async def hello_uvm(dut):
    """Test pyuvm with Xcelium/Icarus"""
    await uvm_root().run_test("HelloTest")