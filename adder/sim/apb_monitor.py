from pyuvm import *
from cocotb.triggers import RisingEdge
from dataclasses import dataclass
from typing import Dict, Set, List, Tuple

@dataclass
class APBCovData:
    PWRITE: bool = False
    PADDR: int = 0
    PWDATA: int = 0
    PRDATA: int = 0
    PSLVERR: bool = False

class APBMonitor(uvm_monitor):
    def build_phase(self):
        self.item_collected_port_mon = uvm_analysis_port("item_collected_port_mon", self)
        self.trans_collected = APBTransaction()
        
        # Get virtual interface
        if not uvm_config_db.get(self, "", "vif", self.vif):
            self.logger.error("Virtual interface not found!")
            raise Exception("Virtual interface not found")
        
        # Initialize coverage
        self.apb_cov = self.create_coverage()

    def create_coverage(self):
        """Create Python implementation of APB coverage"""
        class APBCoverage:
            def __init__(self):
                # Coverage bins storage
                self.coverage_bins = {
                    'PWRITE': {'read': set(), 'write': set()},
                    'PADDR': {
                        'addr0': range(0x00000000, 0x0000000D),
                        'addr1': range(0x00000100, 0x00000200),
                        'addr2': range(0x00000200, 0x00000300),
                        'other': set()
                    },
                    'PWDATA_frame': {
                        'frame_5': {0b101 << 5},
                        'frame_6': {0b110 << 5},
                        'frame_7': {0b111 << 5},
                        'frame_8': {0b000 << 5}
                    },
                    'PWDATA_parity': {
                        'none': {0},
                        'odd': {1},
                        'even': {2},
                        'unknown': {3}
                    },
                    'PWDATA_stop': {
                        'one_stop': {0},
                        'two_stop': {1 << 4}
                    },
                    'PWDATA_baud': {
                        'common': {4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 63, 0},
                        'reserved': {63, 0},
                        'misc': set()
                    },
                    'PRDATA': {
                        'zero': {0x00000000},
                        'ones': {0xFFFFFFFF},
                        'misc': set()
                    },
                    'PSLVERR': {
                        'ok': {False},
                        'error': {True}
                    }
                }
                
                # Track hits
                self.hits = {category: {bin_name: 0 for bin_name in bins} 
                            for category, bins in self.coverage_bins.items()}
                
            def sample(self, data: APBCovData):
                # PWRITE coverage
                if not data.PWRITE:
                    self.hits['PWRITE']['read'] = 1
                else:
                    self.hits['PWRITE']['write'] = 1
                
                # PADDR coverage
                if data.PADDR in self.coverage_bins['PADDR']['addr0']:
                    self.hits['PADDR']['addr0'] = 1
                elif data.PADDR in self.coverage_bins['PADDR']['addr1']:
                    self.hits['PADDR']['addr1'] = 1
                elif data.PADDR in self.coverage_bins['PADDR']['addr2']:
                    self.hits['PADDR']['addr2'] = 1
                else:
                    self.hits['PADDR']['other'] = 1
                
                # PWDATA frame coverage (bits 7:5)
                frame_bits = (data.PWDATA >> 5) & 0b111
                if frame_bits == 0b101:
                    self.hits['PWDATA_frame']['frame_5'] = 1
                elif frame_bits == 0b110:
                    self.hits['PWDATA_frame']['frame_6'] = 1
                elif frame_bits == 0b111:
                    self.hits['PWDATA_frame']['frame_7'] = 1
                elif frame_bits == 0b000:
                    self.hits['PWDATA_frame']['frame_8'] = 1
                
                # PWDATA parity coverage (bits 3:0)
                parity_bits = data.PWDATA & 0b1111
                if parity_bits == 0:
                    self.hits['PWDATA_parity']['none'] = 1
                elif parity_bits == 1:
                    self.hits['PWDATA_parity']['odd'] = 1
                elif parity_bits == 2:
                    self.hits['PWDATA_parity']['even'] = 1
                elif parity_bits == 3:
                    self.hits['PWDATA_parity']['unknown'] = 1
                
                # PWDATA stop bits coverage (bit 4)
                if (data.PWDATA & (1 << 4)) == 0:
                    self.hits['PWDATA_stop']['one_stop'] = 1
                else:
                    self.hits['PWDATA_stop']['two_stop'] = 1
                
                # PWDATA baud rate coverage
                if data.PWDATA in self.coverage_bins['PWDATA_baud']['common']:
                    self.hits['PWDATA_baud']['common'] = 1
                elif data.PWDATA in self.coverage_bins['PWDATA_baud']['reserved']:
                    self.hits['PWDATA_baud']['reserved'] = 1
                else:
                    self.hits['PWDATA_baud']['misc'] = 1
                
                # PRDATA coverage
                if data.PRDATA == 0x00000000:
                    self.hits['PRDATA']['zero'] = 1
                elif data.PRDATA == 0xFFFFFFFF:
                    self.hits['PRDATA']['ones'] = 1
                else:
                    self.hits['PRDATA']['misc'] = 1
                
                # PSLVERR coverage
                if data.PSLVERR:
                    self.hits['PSLVERR']['error'] = 1
                else:
                    self.hits['PSLVERR']['ok'] = 1
            
            def get_coverage(self) -> float:
                total_bins = sum(len(bins) for bins in self.coverage_bins.values())
                hit_bins = sum(sum(bin_hits.values()) for bin_hits in self.hits.values())
                return (hit_bins / total_bins) * 100 if total_bins > 0 else 0.0
            
            def report_coverage(self) -> Dict:
                return {
                    category: {
                        bin_name: "Hit" if self.hits[category][bin_name] else "Miss"
                        for bin_name in bins
                    }
                    for category, bins in self.coverage_bins.items()
                }
        
        return APBCoverage()

    async def run_phase(self):
        while True:
            # Wait for transaction start
            await RisingEdge(self.vif.PCLK)
            if not (self.vif.PSELx.value and self.vif.PENABLE.value):
                continue
            
            # Wait for completion (PREADY or PSLVERR)
            while not (self.vif.PREADY.value or self.vif.PSLVERR.value):
                await RisingEdge(self.vif.PCLK)
            
            # Capture transaction data
            self.trans_collected.PWRITE = bool(self.vif.PWRITE.value)
            self.trans_collected.PWDATA = self.vif.PWDATA.value.integer
            self.trans_collected.PADDR = self.vif.PADDR.value.integer
            self.trans_collected.PRDATA = self.vif.PRDATA.value.integer
            self.trans_collected.PREADY = bool(self.vif.PREADY.value)
            self.trans_collected.PSLVERR = bool(self.vif.PSLVERR.value)
            
            # Sample coverage
            cov_data = APBCovData(
                PWRITE=self.trans_collected.PWRITE,
                PADDR=self.trans_collected.PADDR,
                PWDATA=self.trans_collected.PWDATA,
                PRDATA=self.trans_collected.PRDATA,
                PSLVERR=self.trans_collected.PSLVERR
            )
            self.apb_cov.sample(cov_data)
            
            self.logger.debug(f"APB Monitor Collected Transaction:\n{self.trans_collected}")
            
            # Wait for transaction completion
            while self.vif.PREADY.value:
                await RisingEdge(self.vif.PCLK)
            
            # Send to scoreboard
            self.item_collected_port_mon.write(self.trans_collected)

    def print_coverage_APB_summary(self):
        coverage_percentage = self.apb_cov.get_coverage()
        self.logger.info(f"APB Covergroup coverage: {coverage_percentage:.2f}%")
        coverage_details = self.apb_cov.report_coverage()
        for category, bins in coverage_details.items():
            self.logger.debug(f"{category} coverage:")
            for bin_name, status in bins.items():
                self.logger.debug(f"  {bin_name}: {status}")