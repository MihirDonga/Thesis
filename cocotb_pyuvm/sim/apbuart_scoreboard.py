from pyuvm import *
from apbuart_coverage import ConfigCoverage, TxCoverage, RxCoverage
from cocotb.triggers import Timer
from uart_transaction import UARTTransaction
from apb_transaction import APBTransaction
from uart_config import uart_config
from apb_config import apb_config

class APBUARTScoreboard(uvm_scoreboard):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
       
        # Queues for storing transactions
        self.pkt_qu_monapb = []
        self.pkt_qu_monuart = []
        self.pkt_qu_drvuart = []

        # Configuration and registers
        self.cfg = None
        self.baud_rate_reg = 0
        self.frame_len_reg = 0
        self.parity_reg = 0
        self.stopbit_reg = 0
        print("Initializing coverage groups")
        # Initialize coverage groups
        self.config_cg = ConfigCoverage()
        self.tx_cg = TxCoverage()
        self.rx_cg = RxCoverage()
        print(f"Coverage groups initialized: {self.config_cg}, {self.tx_cg}, {self.rx_cg}")
        # Counters
        self.config_sample_count = 0
        self.tx_sample_count = 0
        self.rx_sample_count = 0

    def build_phase(self):
        super().build_phase()
        
         # Analysis exports
        self.item_collected_export_monapb = MyAPBExport("item_collected_export_monapb", self)
        self.item_collected_export_monuart = MyUARTExport("item_collected_export_monuart", self)
        self.item_collected_export_drvuart = MyDrvUARTExport("item_collected_export_drvuart", self)
        
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())
        if self.cfg is None:
            self.logger.fatal("No cfg",
                f"Configuration must be set for: {self.get_full_name()}.cfg")
            raise Exception("UART Config not found")
        self.apb_config=ConfigDB().get(None, "", "apb_cfg", apb_config())     
        if self.apb_config is None:
            self.logger.fatal("No cfg",
                f"Configuration must be set for: {self.get_full_name()}.cfg")
            raise Exception("APB Config not found")   

    def write_item_collected_export_monapb(self, pkt: APBTransaction):
        self.pkt_qu_monapb.append(pkt)

    def write_item_collected_export_monuart(self, pkt: UARTTransaction):
        self.pkt_qu_monuart.append(pkt)

    def write_item_collected_export_drvuart(self, pkt: UARTTransaction):
        self.pkt_qu_drvuart.append(pkt)

    async def run_phase(self):
        while True:
            if not self.pkt_qu_monapb:
                await Timer(1, "NS")
                continue
                
            apb_pkt_mon = self.pkt_qu_monapb.pop(0)

            # Handle configuration writes
            if apb_pkt_mon.PWRITE == 1:
                if apb_pkt_mon.PADDR == self.cfg.baud_config_addr:
                    self.baud_rate_reg = apb_pkt_mon.PWDATA
                    self.logger.info(f"Updated  baud_rate_reg={self.baud_rate_reg}")
                elif apb_pkt_mon.PADDR == self.cfg.frame_config_addr:
                    self.frame_len_reg = apb_pkt_mon.PWDATA
                    self.logger.info(f"Updated  frame_len_reg={self.frame_len_reg}")
                elif apb_pkt_mon.PADDR == self.cfg.parity_config_addr:
                    self.parity_reg = apb_pkt_mon.PWDATA
                    self.logger.info(f"Updated  parity_reg={self.parity_reg}")
                elif apb_pkt_mon.PADDR == self.cfg.stop_bits_config_addr:
                    self.stopbit_reg = apb_pkt_mon.PWDATA
                    self.logger.info(f"Updated  stopbit_reg={self.stopbit_reg}")

            # Handle configuration reads
            elif apb_pkt_mon.PWRITE == 0:
                if (apb_pkt_mon.PADDR in [
                    self.cfg.baud_config_addr,
                    self.cfg.frame_config_addr,
                    self.cfg.parity_config_addr,
                    self.cfg.stop_bits_config_addr
                ]):
                    self.compare_config(apb_pkt_mon)

            # Handle transmit data
            elif apb_pkt_mon.PADDR == self.cfg.trans_data_addr:
                while not self.pkt_qu_monuart:
                    await Timer(1, "NS")
                uart_pkt_mon = self.pkt_qu_monuart.pop(0)
                self.compare_transmission(apb_pkt_mon, uart_pkt_mon)

            # Handle receive data
            elif apb_pkt_mon.PADDR == self.cfg.receive_data_addr:
                while not self.pkt_qu_drvuart:
                    await Timer(1, "NS")
                uart_pkt_drv = self.pkt_qu_drvuart.pop(0)
                self.compare_receive(apb_pkt_mon, uart_pkt_drv)

    def compare_config(self, apb_pkt):
        test = None
        try:
            test = uvm_root().top
        except:
            pass
         # Sample coverage with direct values
        try:
            if hasattr(self, 'config_cg'):
                if self.cfg.parity in [0, 1, 2, 3]:
                    self.config_cg.sample(
                        self.baud_rate_reg,
                        self.frame_len_reg,
                        self.parity_reg,
                        self.stopbit_reg
                    )
                else:
                    self.logger.warning(f"Skipping coverage sample: invalid parity value {self.parity_reg}")
                self.config_sample_count += 1
                self.logger.info(f"Sampled coverage with: bRate={self.baud_rate_reg}, frame_len={self.frame_len_reg}, parity={self.parity_reg}, n_sb={self.stopbit_reg}")
        except Exception as e:
            self.logger.error(f"Failed to sample config coverage: {str(e)}")
            self.logger.error(f"Values: bRate={self.baud_rate_reg}, frame_len={self.frame_len_reg}, "
                            f"parity={self.parity_reg}, n_sb={self.stopbit_reg}")
        # Verification logic
        if apb_pkt.PADDR == self.cfg.baud_config_addr:
            if apb_pkt.PRDATA == self.baud_rate_reg:
                self.logger.info("Baud Rate Match")
            else:
                self.logger.error("Baud Rate Mismatch")
                test.report_error("Baud Rate Mismatch detected in scoreboard!")
            self.logger.info(f"Expected: {self.baud_rate_reg} Actual: {apb_pkt.PRDATA}")

        elif apb_pkt.PADDR == self.cfg.frame_config_addr:
            if apb_pkt.PRDATA == self.frame_len_reg:
                self.logger.info("Frame Length Match")
            else:
                self.logger.error("Frame Length Mismatch")
                test.report_error("Frame Length Mismatch detected in scoreboard!")
            self.logger.info(f"Expected: {self.frame_len_reg} Actual: {apb_pkt.PRDATA}")

        elif apb_pkt.PADDR == self.cfg.parity_config_addr:
            if apb_pkt.PRDATA == self.parity_reg:
                self.logger.info("Parity Match")
            else:
                self.logger.error("Parity Mismatch")
                test.report_error("Parity Mismatch detected in scoreboard!")
            self.logger.info(f"Expected: {self.parity_reg} Actual: {apb_pkt.PRDATA}")

        elif apb_pkt.PADDR == self.cfg.stop_bits_config_addr:
            if apb_pkt.PRDATA == self.stopbit_reg:
                self.logger.info("Stop Bits Match")
            else:
                self.logger.error("Stop Bits Mismatch")
                test.report_error("Stop Bits Mismatch detected in scoreboard!")
            self.logger.info(f"Expected: {self.stopbit_reg} Actual: {apb_pkt.PRDATA}")
      

    def compare_transmission(self, apb_pkt, uart_pkt):
        test = None
        try:
            test = uvm_root().top
        except:
            pass

        # Verification logic
        if apb_pkt.PWDATA == uart_pkt.transmitter_reg:
            # Sample coverage with direct values
            self.tx_cg.sample(
                apb_pkt.PWDATA,
                uart_pkt.transmitter_reg
            )
            self.tx_sample_count += 1
            self.logger.info("Transmission Data Match")
        else:
            self.logger.error("Transmission Data Mismatch")
            test.report_error("Transmission Data Mismatch detected in scoreboard!")
        self.logger.info(f"Expected: {apb_pkt.PWDATA:#x} Actual: {uart_pkt.transmitter_reg:#x}")

    def compare_receive(self, apb_pkt, uart_pkt):
        test = None
        try:
            test = uvm_root().top
        except:
            pass

        # Verification logic
        if apb_pkt.PRDATA == uart_pkt.payload:
            self.logger.info("Receiver Data Match")
        else:
            self.logger.error("Receiver Data Mismatch")
            test.report_error("Receiver Data Mismatch detected in scoreboard!")
        self.logger.info(f"Expected: {uart_pkt.payload:#x} Actual: {apb_pkt.PRDATA:#x}")

        # Error checking
        err_expected = 1 if ((uart_pkt.bad_parity and self.cfg.parity[1]) or 
                           (uart_pkt.sb_corr and (self.cfg.n_sb or uart_pkt.sb_corr_bit[0]))) else 0
        
        if apb_pkt.PSLVERR != err_expected:
            self.logger.error(f"Error Mismatch: Expected {err_expected}, Got {apb_pkt.PSLVERR}")
            test.report_error("Error Flag Mismatch")
        # Sample coverage with direct values
        self.rx_cg.sample(
            apb_pkt.PRDATA,
            uart_pkt.payload,
            apb_pkt.PSLVERR
        )
        self.rx_sample_count    += 1

    def report_phase(self):
        config_cov = self.config_cg.get_coverage()
        tx_cov = self.tx_cg.get_coverage()
        rx_cov = self.rx_cg.get_coverage()
        # self.logger.info(f"Parity_hit:{self.config_cg.parity_cp.get_coverage():.2f}%")
        self.logger.info("\nCoverage Report:")
        self.logger.info(f"Config Coverage: {config_cov:.2f}% ({self.config_sample_count} samples)")
        # self.logger.info(f"Tx Coverage: {tx_cov:.2f}% ({self.tx_sample_count} samples)")
     
        # self.logger.info(f"Rx Coverage: {rx_cov:.2f}% ({self.rx_sample_count} samples)")

class MyAPBExport(uvm_analysis_export):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def write(self, pkt):
        # Forward the packet to the scoreboard handler
        self.get_parent().write_item_collected_export_monapb(pkt)

class MyUARTExport(uvm_analysis_export):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def write(self, pkt):
        self.get_parent().write_item_collected_export_monuart(pkt)

class MyDrvUARTExport(uvm_analysis_export):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def write(self, pkt):
        self.get_parent().write_item_collected_export_drvuart(pkt)
