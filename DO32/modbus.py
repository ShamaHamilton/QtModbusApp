import minimalmodbus as mmb

from functions import data_unpack


class Modbus_RTU():
    """Modbus RTU."""

    def __init__(self, port: str, slave_address: int = 0, debug: bool = False):
        port: str = f'/dev/{port}'
        baudrate: int = 115_200
        self.slave_address: int = slave_address

        # Инициализация Modbus
        self.board = mmb.Instrument(port=port, slaveaddress=self.slave_address, debug=debug)
        self.board.serial.baudrate = baudrate

    def read_single_register(self, register_address: int, signed: bool = False):
        """Читает и возвращает значение ОДНОГО указанного регистра.

            Параметры:
                * register_address (int): адрес регистра из которого нужно
                прочитать данные.
                * signed (bool): формат интерпретации данных:
                    * True - знаковый формат (int_16: от -32 768 до 32 767)
                    * False - беззнаковый формат (uint_16: от 0 до 65 535)

            Возвращаемое значение:
                * data (int | float): данные из регистра.
        """
        data: int | float = 0
        try:
            data = self.board.read_register(
                registeraddress=register_address,
                signed=signed
            )
        except Exception as e:
            print(e)
            self.error = 1
        return data

    def read_multiple_registers(self, register_address: int, number: int):
        """Читает и возвращает значения указанных регистров.

            Параметры:
                * register_address (int): начальный адрес регистроров, данные из которых требуется получить.
                * number (int): количество регистров, данные из которых необходимо получить.

            Возвращаемое значение:
                * data (list): данные из указанных регистров.
        """
        data: list = []
        try:
            data = self.board.read_registers(registeraddress=register_address, number_of_registers=number)
        except Exception as e:
            print(e)
            self.error = 1
        return data

    def write_single_register(self, register_address: int, data: int | float):
        """Записывает переданное значение в указанный регистр.

            Параметры:
                * register_address (int): адрес регистра куда будет записано переданное значение.
                * data (int | float): значение для записи в указанный регистр.

            Возвращаемое значение:
                * retcode (int): статус ошибки:
                    * 0 - нет ошибок.
                    * 1 - ошибка.
        """
        retcode: int = 0
        try:
            self.board.write_register(registeraddress=register_address, value=data)
        except Exception as e:
            print(e)
            retcode = 1
        return retcode

    def write_multiple_registers(self, register_address: int, data: list):
        """Записывает список переданных значений в регистры начиная с указанного регистра.

            Параметры:
                * register_address (int): начальный адрес регистра куда будут записаны переданные значения.
                * data (list): список значений для записи в регистры.

            Возвращаемое значение:
                * retcode (int): статус ошибки:
                    * 0 - нет ошибок.
                    * 1 - ошибка.
        """
        retcode: int = 0
        try:
            self.board.write_registers(registeraddress=register_address, values=data)
        except Exception as e:
            print(e)
            retcode = 1
        return retcode

    def read_device_info(self):
        """Чтение общих регистров."""
        group = 0
        device_info_registers: list = []
        try:
            group = self.board.read_registers(registeraddress=0x3000, number_of_registers=10)
            device_info_registers.append(data_unpack(group[:2])[0])
            device_info_registers.append(data_unpack(group[2:4])[0])
            device_info_registers.append(group[4])
            device_info_registers.append(data_unpack(group[7:9])[0])
            device_info_registers.append(list(format(group[9], '08b'))[::-1])
        except Exception as e:
            self.error = 1
            print(e)
        return device_info_registers

    def read_static_info(self):
        """Чтение общих регистров."""
        group = 0  # version, build_year, build_month_day, build_hour_minute
        static_info_registers: list = []
        try:
            group = self.board.read_registers(registeraddress=0x4000, number_of_registers=4)
            static_info_registers.append(int((format(group[0], '016b')[:8]), 2))
            static_info_registers.append(int((format(group[0], '016b')[8:]), 2))
            static_info_registers.append(group[1])
            static_info_registers.append(int((format(group[2], '016b')[:8]), 2))
            static_info_registers.append(int((format(group[2], '016b')[8:]), 2))
            static_info_registers.append(int((format(group[3], '016b')[:8]), 2))
            static_info_registers.append(int((format(group[3], '016b')[8:]), 2))
        except Exception as e:
            self.error = 1
            print(e)
        return static_info_registers
