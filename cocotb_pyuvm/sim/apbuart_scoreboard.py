from pyuvm import *
import cocotb

@uvm_component_utils
class APBUARTScoreboard(uvm_scoreboard):
    def __init__(self, name, parent):
        super().__init__(name, parent)
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
        success, self.cfg = ConfigDB().get(self, "", "cfg")
        if not success or self.cfg is None:
            self.logger.fatal("No cfg",
                f"Configuration must be set for: {self.get_full_name()}.cfg")
            raise Exception("UART Config not found")

        # Analysis ports (subscribers)
        self.item_collected_export_monapb = uvm_analysis_imp(self.write_monapb, "item_collected_export_monapb", self)
        self.item_collected_export_monuart = uvm_analysis_imp(self.write_monuart, "item_collected_export_monuart", self)
        self.item_collected_export_drvuart = uvm_analysis_imp(self.write_drvuart, "item_collected_export_drvuart", self)

    def write_monapb(self, pkt: 'APBTransaction'):
        self.pkt_qu_monapb.append(pkt)

    def write_monuart(self, pkt: 'UARTTransaction'):
        self.pkt_qu_monuart.append(pkt)

    def write_drvuart(self, pkt: 'UARTTransaction'):
        self.pkt_qu_drvuart.append(pkt)

    async def run_phase(self, phase):
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
        if apb_pkt.PADDR == self.cfg.baud_config_addr:
            if apb_pkt.PRDATA == self.baud_rate_reg:
                self.uvm_info(self.get_type_name(), "------ :: Baud Rate Match :: ------", UVM_LOW)
            else:
                self.uvm_error(self.get_type_name(), "------ :: Baud Rate MisMatch :: ------")
            self.uvm_info(self.get_type_name(), 
                         f"Expected Baud Rate: {self.baud_rate_reg} Actual Baud Rate: {apb_pkt.PRDATA}", 
                         UVM_LOW)
            
        if apb_pkt.PADDR == self.cfg.frame_config_addr:
            if apb_pkt.PRDATA == self.frame_len_reg:
                self.uvm_info(self.get_type_name(), "------ :: Frame Rate Match :: ------", UVM_LOW)
            else:
                self.uvm_error(self.get_type_name(), "------ :: Frame Rate MisMatch :: ------")
            self.uvm_info(self.get_type_name(), 
                         f"Expected Frame Rate: {hex(self.frame_len_reg)} Actual Frame Rate: {hex(apb_pkt.PRDATA)}", 
                         UVM_LOW)
            
        if apb_pkt.PADDR == self.cfg.parity_config_addr:
            if apb_pkt.PRDATA == self.parity_reg:
                self.uvm_info(self.get_type_name(), "------ :: Parity Match :: ------", UVM_LOW)
            else:
                self.uvm_error(self.get_type_name(), "------ :: Parity MisMatch :: ------")
            self.uvm_info(self.get_type_name(), 
                         f"Expected Parity Value: {hex(self.parity_reg)} Actual Parity Value: {hex(apb_pkt.PRDATA)}", 
                         UVM_LOW)
            
        if apb_pkt.PADDR == self.cfg.stop_bits_config_addr:
            if apb_pkt.PRDATA == self.stopbit_reg:
                self.uvm_info(self.get_type_name(), "------ :: Stop Bit Match :: ------", UVM_LOW)
            else:
                self.uvm_error(self.get_type_name(), "------ :: Stop Bit MisMatch :: ------")
            self.uvm_info(self.get_type_name(), 
                         f"Expected Stop Bit Value: {hex(self.stopbit_reg)} Actual Stop Value: {hex(apb_pkt.PRDATA)}", 
                         UVM_LOW)
            
            self.uart_config_cg.sample()        
            self.config_sample_count += 1

    def compare_transmission(self, apb_pkt, uart_pkt):
        if apb_pkt.PWDATA == uart_pkt.transmitter_reg:
            self.logger.info("Transmission Data Packet Match")
        else:
            self.logger.error("Transmission Data Packet Mismatch")
        self.logger.info(f"Expected: {apb_pkt.PWDATA:#x} Actual: {uart_pkt.transmitter_reg:#x}")
        self.tx_cg.sample(apb_pkt.PWDATA, uart_pkt.transmitter_reg)
        self.tx_sample_count += 1

    def compare_receive(self, apb_pkt, uart_pkt):
        if apb_pkt.PRDATA == uart_pkt.payload:
            self.logger.info("Receiver Data Packet Match")
        else:
            self.logger.error("Receiver Data Packet Mismatch")
        self.logger.info(f"Expected: {uart_pkt.payload:#x} Actual: {apb_pkt.PRDATA:#x}")

        error = uart_pkt.bad_parity and self.cfg.parity \
                or uart_pkt.sb_corr and self.cfg.n_sb
        expected = 1 if error else 0
        if apb_pkt.PSLVERR == expected:
            self.logger.info("Error Status Match")
        else:
            self.logger.error("Error Status Mismatch")
        self.logger.info(f"Expected PSLVERR: {expected} Actual: {apb_pkt.PSLVERR}")
        
        self.rx_cg.sample(apb_pkt.PRDATA, uart_pkt.payload, err_actual)
        self.rx_sample_count += 1

