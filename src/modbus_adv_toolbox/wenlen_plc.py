import logging
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException

class WenlenPLC:
    def __init__(self, ip_address, port, retries=2, simulation=False):
        self.retries = retries
        self.logger = logging.getLogger("WenlenPLC")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.simulation = simulation

        self.client = ModbusTcpClient(ip_address, port=port)

    def update_ip_and_port(self, new_ip_address, new_port):
        self.client = ModbusTcpClient(
                host=new_ip_address, port=new_port, auto_open=True, auto_close=True
            )

    def connect(self):
        try:
            if self.client.connect():
                self.logger.info("Connection successful")
                return True
            else:
                self.logger.error("Failed to connect")
                return False
        except ConnectionException as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def close_connection(self):
        self.client.close()
        self.logger.info("Connection closed")

    def read_coils(self, start_reg, count=1, unit=1):
        try:
            self.logger.debug(f"Attempting to read {count} coils starting at {start_reg} with unit {unit}")
            result = self.client.read_coils(start_reg, count, unit=unit)
            if not result.isError():
                return result.bits
            else:
                self.logger.error(f"Failed to read coils: {result}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read coils: {e}")
            return None

    def read_holding_registers(self, start_reg, length=1, unit=1):
        try:
            self.logger.debug(f"Attempting to read {length} holding registers starting at {start_reg} with unit {unit}")
            regs = self.client.read_holding_registers(start_reg, length, unit=unit)
            if not regs.isError():
                return regs.registers
            else:
                self.logger.error(f"Failed to read holding registers: {regs}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read holding registers: {e}")
            return None

    def read_input_registers(self, start_reg, length=1, unit=1):
        try:
            self.logger.debug(f"Attempting to read {length} input registers starting at {start_reg} with unit {unit}")
            regs = self.client.read_input_registers(start_reg, length, unit=unit)
            if not regs.isError():
                return regs.registers
            else:
                self.logger.error(f"Failed to read input registers: {regs}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read input registers: {e}")
            return None

    def read_discrete_inputs(self, start_reg, count=1, unit=1):
        try:
            self.logger.debug(f"Attempting to read {count} discrete inputs starting at {start_reg} with unit {unit}")
            result = self.client.read_discrete_inputs(start_reg, count, unit=unit)
            if not result.isError():
                return result.bits
            else:
                self.logger.error(f"Failed to read discrete inputs: {result}")
                return None
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to read discrete inputs: {e}")
            return None

    def read_boolean_registers(self, start_reg=0, count=32):
        """Read boolean values from discrete inputs (10001-19999)"""
        #check if simulation is enabled
        if self.simulation:
            self.logger.info("Simulation enabled, reading discrete inputs instead of coils")
            discrete_input = self.read_coils(start_reg=0, count=count)
        else:
            discrete_input = self.read_discrete_inputs(start_reg=0, count=count)
        return discrete_input
    
    def combine_registers_to_floats(self, registers):
        floats = []
        for i in range(0, len(registers), 2):
            if registers[i] is not None and registers[i+1] is not None:
                combined_value = float(f"{registers[i]}.{registers[i+1]:02d}")
                floats.append(combined_value)
            else:
                floats.append(0)
        return floats

    def read_holding_registers_values(self, count=8):
        holding_values = []
        for i in range(count*2):
            holding_register = self.read_holding_registers(start_reg=i, length=1)
            if holding_register is not None:
                holding_values.append(holding_register[0])
            else:
                holding_values.append(None)
        return holding_values
    
    def read_float_registers(self, start_reg=40001, count=8):
        holding_registers = self.read_holding_registers_values(count=count)
        float_registers = self.combine_registers_to_floats(holding_registers)
        return float_registers
    
    def write_coils(self, start_reg, values, unit=1):
        try:
            self.logger.debug(f"Attempting to write coils starting at {start_reg} with unit {unit}")
            result = self.client.write_coils(start_reg, values, unit=unit)
            if not result.isError():
                self.logger.info("Write coils successful")
                return True
            else:
                self.logger.error(f"Failed to write coils: {result}")
                return False
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to write coils: {e}")
            return False

    def write_register(self, start_reg, value, unit=1):
        try:
            self.logger.debug(f"Attempting to write register at {start_reg} with unit {unit}")
            result = self.client.write_register(start_reg, value, unit=unit)
            if not result.isError():
                self.logger.info("Write register successful")
                return True
            else:
                self.logger.error(f"Failed to write register: {result}")
                return False
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to write register: {e}")
            return False
        
    def write_discrete_inputs(self, start_reg, values, unit=1):
        try:
            self.logger.debug(f"Attempting to write discrete inputs starting at {start_reg} with unit {unit}")
            result = self.client.write_coils(start_reg, values, unit=unit)  # Reuse write_coils for discrete inputs
            if not result.isError():
                self.logger.info(f"Successfully wrote discrete inputs: {values}")
                return True
            else:
                self.logger.error(f"Failed to write discrete inputs: {result}")
                return False
        except ModbusIOException as e:
            self.logger.error(f"Modbus IO Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to write discrete inputs: {e}")
            return False

    def write_boolean_registers(self, start_reg, values, unit=1):
        """Write boolean values to coils (1-9999) that map to discrete inputs (10001-19999)"""
        try:
            # Map start_reg from discrete input (10001-19999) to coil (1-9999) address
            coil_start = start_reg - 10001 + 1  # Convert from discrete input to coil address
            
            self.logger.debug(f"Writing {len(values)} boolean values to coils starting at {coil_start}")
            result = self.client.write_coils(coil_start, values, unit=unit)
            
            if not result.isError():
                self.logger.info(f"Successfully wrote boolean values to coils starting at {coil_start}")
                return True
                
            self.logger.error(f"Failed to write boolean values: {result}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to write boolean values: {e}")
            return False

    def write_single_boolean(self, reg, value, unit=1):
        """Write single boolean value to coil (0-9998)"""
        try:
            # Use direct coil addressing (0-based)
            coil_addr = 0  # Write to first coil
            self.logger.debug(f"Writing single boolean value {value} to coil {coil_addr}")
            result = self.client.write_coil(coil_addr, value, unit=unit)
            if not result.isError():
                self.logger.info(f"Successfully wrote {value} to coil {coil_addr}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to write boolean: {e}")
            return False

    def read_single_boolean(self, reg, unit=1):
        """Read single boolean value from discrete input (10001-19999)"""
        try:
            # Use same address as write
            addr = 0  # Read from first discrete input
            self.logger.debug(f"Reading discrete input at {addr}")
            result = self.client.read_discrete_inputs(addr, 1, unit=unit)
            if not result.isError():
                value = result.bits[0]
                self.logger.info(f"Read value {value} from discrete input {addr}")
                return value
            return None
        except Exception as e:
            self.logger.error(f"Failed to read boolean: {e}")
            return None