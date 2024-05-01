import struct
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

class AccutechRTU:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.client = ModbusTcpClient(host=ip_address, port=port, auto_open=True, auto_close=True)

    def test_connection(self, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            if self.client.connect():
                print(f"Conexión exitosa en el intento {attempt}")
                return True
            else:
                print(f"Intento {attempt} de conexión fallido")
                if attempt < max_attempts:
                    print("Reintentando...")
                    time.sleep(1)
        print("No se pudo establecer la conexión después de varios intentos")
        return False

    def read_specific_register(self, register):
        regs_l = self.client.read_holding_registers(register, 2)
        dec = BinaryPayloadDecoder.fromRegisters(regs_l, byteorder=Endian.Little, wordorder=Endian.Big)
        value = dec.decode_32bit_float()
        return value

    def read_values_fast(self, amount=30):
        data = []
        for i in range(1, amount + 1):
            modbus_register_address = 5 + (i * 10)
            data.append(self.read_specific_register(modbus_register_address))
        return data

    def read_values_by_rfid(self, amount=30):
        data = []
        for rfid in range(1, amount + 1):
            data.append(self.read_register_for_rfid(rfid))
        return data

    def read_values(self, amount=30, max_attempts=3):
        data = []
        for i in range(1, amount + 1):
            modbus_register_address = 5 + (i * 10)
            value = None
            attempts = 0
            while attempts < max_attempts:
                try:
                    value = self.read_specific_register(modbus_register_address)
                    break
                except Exception as e:
                    print(f"Intento {attempts + 1} de lectura fallido: {e}")
                    attempts += 1
                    time.sleep(1)
            if value is not None:
                data.append(value)
            else:
                print(f"No se pudo leer el valor del registro {modbus_register_address} después de {max_attempts} intentos.")
                data.append(None)
        return data

    def write_specific_register(self, register, value):
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder.add_32bit_float(value)
        payload = builder.build()
        self.client.write_registers(register - 2, payload, skip_encode=True)

    def write_register_for_rfid(self, rfid, value):
        modbus_register_address = 5 + (rfid * 10)
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder.add_32bit_float(value)
        regs_to_write = builder.to_registers()
        result = self.client.write_multiple_registers(modbus_register_address, regs_to_write)
        if result:
            print(f"Valor {value} escrito para RFID {rfid}")
        else:
            print(f"Error al escribir registros para RFID {rfid}")

    def read_register_for_rfid(self, rfid):
        modbus_register_address = 5 + (rfid * 10)
        regs_l = self.client.read_holding_registers(modbus_register_address, 2)
        if regs_l:
            dec = BinaryPayloadDecoder.fromRegisters(regs_l, byteorder=Endian.Little, wordorder=Endian.Big)
            value = dec.decode_32bit_float()
            return value
        else:
            return None
