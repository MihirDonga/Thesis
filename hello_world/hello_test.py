from pyuvm import *
import cocotb
from cocotb.triggers import Timer
import random

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        # VCS-style coverage bins
        self.coverage = {
            'a': set(),       # Track 'a' input values (0,1)
            'b': set(),        # Track 'b' input values (0,1) 
            'cin': set(),      # Track 'cin' input values (0,1)
            'transactions': set()  # Track unique (a,b,cin) combinations
        }
        self.num_tests = 20

    def update_coverage(self, a, b, cin):
        """Record coverage in VCS style"""
        self.coverage['a'].add(a)
        self.coverage['b'].add(b)
        self.coverage['cin'].add(cin)
        self.coverage['transactions'].add((a, b, cin))

    def print_coverage(self):
        """Print percentage coverage to log (VCS-style)"""
        cov_pct = {
            'a': len(self.coverage['a']) / 2 * 100,
            'b': len(self.coverage['b']) / 2 * 100,
            'cin': len(self.coverage['cin']) / 2 * 100,
            'transactions': len(self.coverage['transactions']) / 8 * 100
        }
        
        self.logger.info("=== COVERAGE PERCENTAGE ===")
        self.logger.info(f"Input a:    {cov_pct['a']:6.1f}%")
        self.logger.info(f"Input b:    {cov_pct['b']:6.1f}%") 
        self.logger.info(f"Input cin:  {cov_pct['cin']:6.1f}%")
        self.logger.info(f"Transactions: {cov_pct['transactions']:6.1f}%")
        self.logger.info("==========================")

    async def run_phase(self):
        self.raise_objection()
        
        for _ in range(self.num_tests):
            a = random.randint(0, 1)
            b = random.randint(0, 1)
            cin = random.randint(0, 1)
            
            # Drive and verify (same as before)
            self.dut.a.value = a
            self.dut.b.value = b
            self.dut.cin.value = cin
            await Timer(1, "NS")
            
            # Update coverage
            self.update_coverage(a, b, cin)
        
        self.print_coverage()
        self.drop_objection()