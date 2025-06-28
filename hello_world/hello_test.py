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

# VCS-style coverage class
class FullAdderCoverage:
    def __init__(self):
        self.input_cov = self.InputCoverage()
        self.trans_cov = self.TransactionCoverage()
        
    class InputCoverage:
        def __init__(self):
            self.a = set()
            self.b = set()
            self.cin = set()
            
        def sample(self, a, b, cin):
            self.a.add(a)
            self.b.add(b)
            self.cin.add(cin)
            
        def get_coverage(self):
            return {
                'a': len(self.a)/2 * 100,
                'b': len(self.b)/2 * 100,
                'cin': len(self.cin)/2 * 100
            }
    
    class TransactionCoverage:
        def __init__(self):
            self.combinations = set()
            
        def sample(self, a, b, cin):
            self.combinations.add((a, b, cin))
            
        def get_coverage(self):
            return len(self.combinations)/8 * 100
            
    def sample(self, a, b, cin):
        self.input_cov.sample(a, b, cin)
        self.trans_cov.sample(a, b, cin)
        
    def report(self):
        input_cov = self.input_cov.get_coverage()
        trans_cov = self.trans_cov.get_coverage()
        print("\n=== VCS-STYLE COVERAGE REPORT ===")
        print(f"Input coverage: a={input_cov['a']:.1f}%, b={input_cov['b']:.1f}%, cin={input_cov['cin']:.1f}%")
        print(f"Transaction coverage: {trans_cov:.1f}%")
        print("===============================\n")

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        self.coverage = FullAdderCoverage()
        self.num_tests = 50
        
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
            
            # Check outputs
            sum_val = self.dut.sum.value
            cout_val = self.dut.cout.value
            expected_sum = a ^ b ^ cin
            expected_cout = (a & b) | (cin & (a ^ b))
            
            if sum_val != expected_sum or cout_val != expected_cout:
                self.logger.error(f"Error: a={a}, b={b}, cin={cin}")
                self.logger.error(f"Expected: sum={expected_sum}, cout={expected_cout}")
                self.logger.error(f"Received: sum={sum_val}, cout={cout_val}")
            
            # Sample coverage
            self.coverage.sample(a, b, cin)
        
        self.coverage.report()
        self.drop_objection()

@cocotb.test()
async def run_test(dut):
    """Full adder test with VCS-style coverage"""
    await uvm_root().run_test("FullAdderTest")