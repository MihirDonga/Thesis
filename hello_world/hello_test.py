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
import cocotb
from cocotb.triggers import Timer

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top  # Get access to the DUT

    async def run_phase(self):
        self.raise_objection()
        
        # Test all 8 possible input combinations
        for a in [0, 1]:
            for b in [0, 1]:
                for cin in [0, 1]:
                    # Drive inputs
                    self.dut.a.value = a
                    self.dut.b.value = b
                    self.dut.cin.value = cin
                    await Timer(1, "NS")
                    
                    # Check outputs
                    sum = self.dut.sum.value
                    cout = self.dut.cout.value
                    
                    # Calculate expected values
                    expected_sum = a ^ b ^ cin
                    expected_cout = (a & b) | (cin & (a ^ b))
                    
                    # Verify
                    if sum != expected_sum or cout != expected_cout:
                        self.logger.error(f"FAIL: a={a}, b={b}, cin={cin}")
                        self.logger.error(f"Got sum={sum}, cout={cout}")
                        self.logger.error(f"Expected sum={expected_sum}, cout={expected_cout}")
                    else:
                        self.logger.info(f"PASS: a={a}, b={b}, cin={cin}")
        
        self.drop_objection()

@cocotb.test()
async def run_test(dut):
    """Simple full adder test"""
    await uvm_root().run_test("FullAdderTest")