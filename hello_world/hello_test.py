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
import random

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        # VCS-style coverage bins
        self.input_coverage = {
            'a': set(),
            'b': set(),
            'cin': set()
        }
        self.transaction_coverage = set()
        self.num_tests = 20  # Reduced for demo

    def update_coverage(self, a, b, cin):
        """VCS-style coverage sampling"""
        self.input_coverage['a'].add(a)
        self.input_coverage['b'].add(b)
        self.input_coverage['cin'].add(cin)
        self.transaction_coverage.add((a, b, cin))

    def print_coverage(self):
        """Prints coverage directly to log (VCS-style)"""
        self.logger.info("=== COVERAGE SUMMARY ===")
        self.logger.info(f"Input a:    {len(self.input_coverage['a'])}/2 bins hit")
        self.logger.info(f"Input b:    {len(self.input_coverage['b'])}/2 bins hit")
        self.logger.info(f"Input cin:  {len(self.input_coverage['cin'])}/2 bins hit")
        self.logger.info(f"Transactions: {len(self.transaction_coverage)}/8 combinations")
        self.logger.info("=======================")

    async def run_phase(self):
        self.raise_objection()
        
        for _ in range(self.num_tests):
            a = random.randint(0, 1)
            b = random.randint(0, 1)
            cin = random.randint(0, 1)
            
            # Drive inputs
            self.dut.a.value = a
            self.dut.b.value = b
            self.dut.cin.value = cin
            await Timer(1, "NS")
            
            # Verify outputs
            sum_val = self.dut.sum.value
            cout_val = self.dut.cout.value
            expected_sum = a ^ b ^ cin
            expected_cout = (a & b) | (cin & (a ^ b))
            
            if sum_val != expected_sum or cout_val != expected_cout:
                self.logger.error(f"Error: Inputs: a={a}, b={b}, cin={cin}")
            
            # Update coverage
            self.update_coverage(a, b, cin)
        
        # Print final coverage to log
        self.print_coverage()
        self.drop_objection()

@cocotb.test()
async def run_test(dut):
    """Test with VCS-style coverage logging"""
    await uvm_root().run_test("FullAdderTest")