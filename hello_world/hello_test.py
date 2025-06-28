from pyuvm import *
import cocotb
from cocotb.triggers import Timer
import random

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        self.unique_combinations = set()
        self.num_tests = 20  # Reduced for demo
    
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
            
            # Track unique combinations
            self.unique_combinations.add((a, b, cin))
        
        # Calculate and print ONLY overall coverage
        coverage_pct = len(self.unique_combinations) / 8 * 100
        self.logger.info(f"\nOVERALL FUNCTIONAL COVERAGE: {coverage_pct:.1f}%\n")
        
        self.drop_objection()

@cocotb.test()
async def run_test(dut):
    """Test entry point"""
    await uvm_root().run_test(FullAdderTest)