from pyuvm import *
from apbuart_coverage import ConfigCoverage, TxCoverage, RxCoverage
from cocotb.triggers import Timer
from uart_transaction import UARTTransaction
from apb_transaction import APBTransaction
from uart_config import uart_config

class APBUARTScoreboard(uvm_scoreboard):
    def __init__(self, name, parent):
        super().__init__(name, parent)

        # # Create vsc variables for coverage
        # self.vsc_baud = vsc.uint32_t(0)
        # self.vsc_frame = vsc.uint32_t(0)
        # self.vsc_parity = vsc.uint32_t(0)
        # self.vsc_stopbit = vsc.uint32_t(0)
        # self.vsc_apb_data = vsc.uint32_t(0)
        # self.vsc_uart_data = vsc.uint32_t(0)
        # self.vsc_rx_error = vsc.bit_t(0)
        
        # Create coverage components
        self.config_cg = ConfigCoverage()
        self.tx_cg = TxCoverage()
        self.rx_cg = RxCoverage()

        self.item_collected_export_monapb = uvm_analysis_export("item_collected_export_monapb", self)
        self.item_collected_export_monuart = uvm_analysis_export("item_collected_export_monuart", self)
        self.item_collected_export_drvuart = uvm_analysis_export("item_collected_export_drvuart", self)
       
        # Queues for storing transactions
        self.pkt_qu_monapb = []
        self.pkt_qu_monuart = []
        self.pkt_qu_drvuart = []

        # Hooks for config and registers
        self.cfg = None
        self.baud_rate_reg = 0
        self.frame_len_reg = 0
        self.parity_reg = 0
        self.stopbit_reg = 0

        self.config_sample_count = 0
        self.tx_sample_count=0
        self.rx_sample_count=0
        
    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(None, "", "cfg", uart_config())
        if not self.cfg:
            self.logger.fatal("No cfg",
                f"Configuration must be set for: {self.get_full_name()}.cfg")
            raise Exception("UART Config not found")

        # # Analysis ports (subscribers)
        # self.item_collected_export_monapb = uvm_analysis_imp("item_collected_export_monapb",self.write_monapb, self)
        # self.item_collected_export_monuart = uvm_analysis_imp("item_collected_export_monuart", self.write_monuart, self)
        # self.item_collected_export_drvuart = uvm_analysis_imp("item_collected_export_drvuart", self.write_drvuart, self)

    def write_monapb(self, pkt: "APBTransaction"):
        self.pkt_qu_monapb.append(pkt)

    def write_monuart(self, pkt: "UARTTransaction"):
        self.pkt_qu_monuart.append(pkt)

    def write_drvuart(self, pkt: "UARTTransaction"):
        self.pkt_qu_drvuart.append(pkt)

    async def run_phase(self):
        super().build_phase()
        while True:
            # Wait until APB monitor queue has data
            if self.pkt_qu_monapb:
                apb_pkt_mon = self.pkt_qu_monapb.pop(0)

            # Configuration writes
            if (apb_pkt_mon.PWRITE == 1 and 
                (apb_pkt_mon.PADDR == self.cfg.baud_config_addr or 
                 apb_pkt_mon.PADDR == self.cfg.frame_config_addr or 
                 apb_pkt_mon.PADDR == self.cfg.parity_config_addr or 
                 apb_pkt_mon.PADDR == self.cfg.stop_bits_config_addr)):
                
                addr = apb_pkt_mon.PADDR
                if addr == self.cfg.baud_config_addr:
                    self.baud_rate_reg = apb_pkt_mon.PWDATA
                elif addr == self.cfg.frame_config_addr:
                    self.frame_len_reg = apb_pkt_mon.PWDATA
                elif addr == self.cfg.parity_config_addr:
                    self.parity_reg = apb_pkt_mon.PWDATA
                elif addr == self.cfg.stop_bits_config_addr:
                    self.stopbit_reg = apb_pkt_mon.PWDATA
                else:
                    self.logger.error(f"Incorrect Config Address {addr:#x}")

            # Configuration reads
            elif (apb_pkt_mon.PWRITE == 0 and 
                    (apb_pkt_mon.PADDR == self.cfg.baud_config_addr or 
                    apb_pkt_mon.PADDR == self.cfg.frame_config_addr or 
                    apb_pkt_mon.PADDR == self.cfg.parity_config_addr or 
                    apb_pkt_mon.PADDR == self.cfg.stop_bits_config_addr)):
                    
                    self.compare_config(apb_pkt_mon)

            # Transmit data path
            elif apb_pkt_mon.PADDR == self.cfg.trans_data_addr:
                while len(self.pkt_qu_monuart) == 0:
                    await Timer(1, "NS")
                uart_pkt_mon = self.pkt_qu_monuart.popleft()
                self.compare_transmission(apb_pkt_mon, uart_pkt_mon)

            # Receive data path
            elif apb_pkt_mon.PADDR == self.cfg.receive_data_addr:
                while len(self.pkt_qu_drvuart) == 0:
                    await Timer(1, "NS")
                uart_pkt_drv = self.pkt_qu_drvuart.popleft()
                self.compare_receive(apb_pkt_mon, uart_pkt_drv)
            # Continue loop

    def compare_config(self, apb_pkt):

        # test = uvm_root().find("apbuart_base_test")  # Reference to your base test
        # Update vsc variables with current values
        self.cg_bRate.set_val(self.baud_rate_reg)
        self.cg_frame_len.set_val(self.frame_len_reg)
        self.cg_parity.set_val(self.parity_reg)
        self.cg_n_sb.set_val(self.stopbit_reg)

        if apb_pkt.PADDR == self.cfg.baud_config_addr:
            if apb_pkt.PRDATA == self.baud_rate_reg:
                self.logger.info("------ :: Baud Rate Match :: ------")
            else:
                self.logger.error(self.get_type_name(), "------ :: Baud Rate MisMatch :: ------")
                test.report_error("Baud Rate Mismatch detected in scoreboard!")
            self.logger.info(f"Expected Baud Rate: {self.baud_rate_reg} Actual Baud Rate: {apb_pkt.PRDATA}")
            
        if apb_pkt.PADDR == self.cfg.frame_config_addr:
            if apb_pkt.PRDATA == self.frame_len_reg:
                self.logger.info("------ :: Frame Rate Match :: ------")
            else:
                self.logger.error("------ :: Frame Rate MisMatch :: ------")
                test.report_error("Frame Length Mismatch detected in scoreboard!")
            self.logger.info(f"Expected Frame Rate: {hex(self.frame_len_reg)} Actual Frame Rate: {hex(apb_pkt.PRDATA)}")
            
        if apb_pkt.PADDR == self.cfg.parity_config_addr:
            if apb_pkt.PRDATA == self.parity_reg:
                self.logger.info("------ :: Parity Match :: ------")
            else:
                self.logger.error("------ :: Parity MisMatch :: ------")
                test.report_error("Parity Mismatch detected in scoreboard!")
            self.logger.info(f"Expected Parity Value: {hex(self.parity_reg)} Actual Parity Value: {hex(apb_pkt.PRDATA)}")
            
        if apb_pkt.PADDR == self.cfg.stop_bits_config_addr:
            if apb_pkt.PRDATA == self.stopbit_reg:
                self.logger.info("------ :: Stop Bit Match :: ------")
            else:
                self.logger.error("------ :: Stop Bit MisMatch :: ------")
                test.report_error("Stop Bit Mismatch detected in scoreboard!")
            self.logger.info(f"Expected Stop Bit Value: {hex(self.stopbit_reg)} Actual Stop Value: {hex(apb_pkt.PRDATA)}")
            
        # Sample coverage using dictionary of vsc variables
        self.config_cg.sample(
            bRate=self.cg_bRate.get_val(),
            frame_len=self.cg_frame_len.get_val(),
            parity=self.cg_parity.get_val(),
            n_sb=self.cg_n_sb.get_val()
        )
        self.config_sample_count += 1


    def compare_transmission(self, apb_pkt, uart_pkt):

        # test = uvm_root().find("apbuart_base_test")
        self.cg_apb_data.set_val(apb_pkt.PWDATA)
        self.cg_uart_data.set_val(uart_pkt.transmitter_reg)

        # Sample coverage
        
        if apb_pkt.PWDATA == uart_pkt.transmitter_reg:
            self.logger.info("Transmission Data Packet Match")
            self.tx_cg.sample(apb_data=self.cg_apb_data.get_val(), uart_data=self.cg_uart_data.get_val())
            self.tx_sample_count += 1
        else:
            self.logger.error("Transmission Data Packet Mismatch")
            test.report_error("Transmission Data Packet Mismatch detected in scoreboard!")
        self.logger.info(f"Expected: {apb_pkt.PWDATA:#x} Actual: {uart_pkt.transmitter_reg:#x}")

    def compare_receive(self, apb_pkt, uart_pkt):
        
        # test = uvm_root().find("apbuart_base_test")
        # Update vsc variables
        self.cg_apb_data.set_val(apb_pkt.PRDATA)
        self.cg_uart_data.set_val(uart_pkt.payload)
        self.cg_error.set_val(apb_pkt.PSLVERR)

              
        if apb_pkt.PRDATA == uart_pkt.payload:
            self.logger.info("------ :: Receiver Data Packet Match :: ------")
        else:
            self.logger.error("------ :: Receiver Data Packet MisMatch :: ------")
            test.report_error("Receiver Data Packet Mismatch detected in scoreboard!")
        self.logger.info(f"Expected Receiver Data Value: {uart_pkt.payload} Actual Receiver Data Value: {apb_pkt.PRDATA}")
        self.logger.info("------------------------------------")
        
        err_expected = 1
        if (uart_pkt.bad_parity and self.cfg.parity[1]) or (uart_pkt.sb_corr and (self.cfg.n_sb or uart_pkt.sb_corr_bit[0])):
            err_expected = 0
        
        err_actual = apb_pkt.PSLVERR
        
        if err_actual == err_expected:
            self.logger.info("------ :: Error Match :: ------")
        else:
            self.logger.error("------ :: Error MisMatch :: ------")
            test.report_error("Error Mismatch detected in scoreboard!")

            self.logger.info(f"Expected Error Value: {err_expected} Actual Error Value: {err_actual}")
            self.logger.info("------------------------------------")
        
         # Sample coverage
        self.rx_cg.sample(apb_data=self.cg_apb_data.get_val(),uart_data=self.cg_uart_data.get_val(),error=self.cg_error.get_val())
        self.rx_sample_count += 1 

    def report_phase(self):
        config_coverage = self.config_cg.get_coverage()
        tx_coverage = self.tx_cg.get_coverage()
        rx_coverage = self.rx_cg.get_coverage()
        
        self.logger.info("Coverage Report:")
        self.logger.info(f"Config Coverage: {config_coverage:.2f}%")
        self.logger.info(f"Tx Coverage: {tx_coverage:.2f}%")
        self.logger.info(f"Rx Coverage: {rx_coverage:.2f}%")