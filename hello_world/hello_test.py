from pyuvm import *
import cocotb
from cocotb.triggers import Timer
import random

class FullAdderCoverage(uvm_component):
    def build_phase(self):
        self.cvg = {
            'input_bins': {'a': set(), 'b': set(), 'cin': set()},
            'cross_bins': set(),
            'output_bins': {'sum': set(), 'cout': set()}
        }
    
    def sample(self, a, b, cin, sum_val, cout_val):
        # Input coverage
        self.cvg['input_bins']['a'].add(a)
        self.cvg['input_bins']['b'].add(b)
        self.cvg['input_bins']['cin'].add(cin)
        
        # Cross coverage
        self.cvg['cross_bins'].add((a, b, cin))
        
        # Output coverage
        self.cvg['output_bins']['sum'].add(sum_val)
        self.cvg['output_bins']['cout'].add(cout_val)
    
    def report_phase(self):
        # Calculate percentages
        input_cov = {k: len(v)/2*100 for k,v in self.cvg['input_bins'].items()}
        cross_cov = len(self.cvg['cross_bins'])/8*100
        output_cov = {
            'sum': len(self.cvg['output_bins']['sum'])/2*100,
            'cout': len(self.cvg['output_bins']['cout'])/2*100
        }
        
        # Overall functional coverage (weighted average)
        overall = (sum(input_cov.values()) + cross_cov + sum(output_cov.values())) / 5
        
        self.logger.info("\n=== FUNCTIONAL COVERAGE SUMMARY ===")
        self.logger.info(f"Input Coverage:")
        self.logger.info(f"  a:    {input_cov['a']:6.1f}%")
        self.logger.info(f"  b:    {input_cov['b']:6.1f}%")
        self.logger.info(f"  cin:  {input_cov['cin']:6.1f}%")
        self.logger.info(f"Cross Coverage: {cross_cov:6.1f}% (8 possible combinations)")
        self.logger.info(f"Output Coverage:")
        self.logger.info(f"  sum:  {output_cov['sum']:6.1f}%")
        self.logger.info(f"  cout: {output_cov['cout']:6.1f}%")
        self.logger.info(f"OVERALL FUNCTIONAL COVERAGE: {overall:6.1f}%")
        self.logger.info("=================================")

class FullAdderTest(uvm_test):
    def build_phase(self):
        self.dut = cocotb.top
        self.cov = FullAdderCoverage("cov", self)
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
            
            # Get outputs
            sum_val = int(self.dut.sum.value)
            cout_val = int(self.dut.cout.value)
            
            # Update coverage
            self.cov.sample(a, b, cin, sum_val, cout_val)
        
        self.drop_objection()

@cocotb.test()
async def run_test(dut):
    """Test entry point"""
    await uvm_root().run_test(FullAdderTest)