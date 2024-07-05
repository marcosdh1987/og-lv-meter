import logging
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException

class WenlenPLC:
    def __init__(self, ip_address, port, retries=2):
        self.retries = retries
        self.logger = logging.getLogger("WenlenPLC")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

    def read_boolean_registers(self, start_reg=10001, count=32):
        first_values = []
        for i in range(count):
            discrete_input = self.read_discrete_inputs(start_reg=i, count=8)
            if discrete_input is not None:
                first_values.append(discrete_input[0])
            else:
                first_values.append(None)
        return first_values
    
    def combine_registers_to_floats(self, registers):
        floats = []
        for i in range(0, len(registers), 2):
            if registers[i] is not None and registers[i+1] is not None:
                combined_value = float(f"{registers[i]}.{registers[i+1]:02d}")
                floats.append(combined_value)
            else:
                floats.append(None)
        return floats

    def read_holding_registers_values(self):
        holding_values = []
        for i in range(8):
            holding_register = self.read_holding_registers(start_reg=i, length=1)
            if holding_register is not None:
                holding_values.append(holding_register[0])
            else:
                holding_values.append(None)
        return holding_values
    
    def read_float_registers(self, start_reg=40001, count=4):
        holding_registers = self.read_holding_registers_values()
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