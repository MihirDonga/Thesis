from pyuvm import *
import cocotb
from cocotb.triggers import Timer
import random

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        self.coverage = {
            'a': set(), 
            'b': set(),
            'cin': set(),
            'transactions': set()
        }

    def update_coverage(self, a, b, cin):
        self.coverage['a'].add(a)
        self.coverage['b'].add(b)
        self.coverage['cin'].add(cin)
        self.coverage['transactions'].add((a, b, cin))

    def print_coverage(self):
        self.logger.info("=== COVERAGE ===")
        self.logger.info(f"a: {len(self.coverage['a'])/2*100:.1f}%")
        self.logger.info(f"b: {len(self.coverage['b'])/2*100:.1f}%")
        self.logger.info(f"cin: {len(self.coverage['cin'])/2*100:.1f}%")
        self.logger.info(f"trans: {len(self.coverage['transactions'])/8*100:.1f}%")

    async def run_phase(self):
        self.raise_objection()
        
        for _ in range(20):
            a = random.randint(0, 1)
            b = random.randint(0, 1)
            cin = random.randint(0, 1)
            
            self.dut.a.value = a
            self.dut.b.value = b
            self.dut.cin.value = cin
            await Timer(1, "NS")
            
            self.update_coverage(a, b, cin)
        
        self.print_coverage()
        self.drop_objection()

# MUST use @cocotb.test() decorator
@cocotb.test()
async def test_full_adder(dut):
    """Main test entry point"""
    await uvm_root().run_test(FullAdderTest)  # Pass class reference, not string