import minimalmodbus as mmb


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

    def set_modbus_address_switch(self):
        """Установка типа переключателя адреса на шине modbus.
            * 0 - старый переключатель.
            * +4 - новый переключатель.

            Возвращаемое значение:
                * retcode (int): статус ошибки:
                    * 0 - нет ошибок.
                    * 1 - ошибка.
        """
        retcode: int = 0
        sw_address: int = 0
        try:
            self.board.read_register(registeraddress=0xFFE7)
            print(f'Старый переключатель {self.board.address}')
        except Exception as e:
            sw_address = 4
            print(f'Не старый переключатель {self.board.address}')
            print(e)

        if sw_address == 4:
            self.board.address = self.slave_address + sw_address
            try:
                self.board.read_register(registeraddress=0xFFE7)
                print(f'Новый переключатель {self.board.address}')
            except Exception as e:
                print(f'Не новый переключатель {self.board.address}')
                self.board.address -= sw_address
                retcode = 1
                print(e)
                return retcode
        # если новый, записываем в регистр mb_address_switch значение 4
        try:
            if self.board.address == self.slave_address + 4:
                self.board.write_register(registeraddress=0xFFE7, value=4)
                self.board.address = self.slave_address  # возвращаем изначальный slave address платы объекту класса
        except Exception as e:
            retcode = 1
            print(f'Ошибка при установке смещения адреса: {e}\n')
        return retcode

    def read_general_registers(self):
        """Чтение общих регистров."""
        group_1 = 0  # sys_time(4 байта), mcusr, flash_crc, eeprom_crc, out_rst_timeout, modbus_remap, mb_address_switch
        group_2 = 0  # device_id, rx_buf_size, tx_bus_size, version, build_year, build_month_day, build_hour_minute
        group_3 = 0  # mcusr, modbus_diagnostic; D0-8: += errors, reads_counter, writes_counter
        general_registers: list = []
        try:
            group_1 = self.board.read_registers(registeraddress=0xFFE0, number_of_registers=8)
            group_2 = self.board.read_registers(registeraddress=0xFFF0, number_of_registers=7)
            group_3 = self.board.read_registers(registeraddress=0xFFC0, number_of_registers=2)
            general_registers.append(int.from_bytes(bytes(group_1[:2]), 'little'))
            general_registers.append(format(group_1[2], '016b'))
            general_registers.append(format(group_1[3], '016b'))
            general_registers.append(format(group_1[4], '016b'))
            general_registers += group_1[5:]
            general_registers += group_2[:3]
            general_registers.append(int((format(group_2[3], '016b')[:8]), 2))
            general_registers.append(int((format(group_2[3], '016b')[8:]), 2))
            general_registers.append(group_2[4])
            general_registers.append(int((format(group_2[5], '016b')[:8]), 2))
            general_registers.append(int((format(group_2[5], '016b')[8:]), 2))
            general_registers.append(int((format(group_2[6], '016b')[:8]), 2))
            general_registers.append(int((format(group_2[6], '016b')[8:]), 2))
            general_registers += group_3
        except Exception as e:
            self.error = 1
            print(e)
        return general_registers

    def read_r3_registers(self):
        """Чтение регистров модуля R3."""
        board_registers: list = []
        try:
            board_registers.append(format(self.board.read_register(registeraddress=0x0001), '016b')[13::-1])  # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0081), '016b')[13::-1])  # sli
        except Exception as e:
            self.error = 1
            print(e)
        return board_registers

    def read_mp4_registers(self):
        """Чтение регистров модуля MP4."""
        board_registers: list = []
        try:
            board_registers.append(format(self.board.read_register(registeraddress=0x0001), '016b')[::-1])  # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0002), '08b')[::-1])   # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0081), '016b')[::-1])  # sli
            board_registers.append(format(self.board.read_register(registeraddress=0x0082), '08b')[::-1])   # sli
        except Exception as e:
            self.error = 1
            print(e)
        return board_registers

    def read_mp2r1_registers(self):
        """Чтение регистров модуля MP2R1."""
        board_registers: list = []
        try:
            board_registers.append(format(self.board.read_register(registeraddress=0x0001), '016b')[::-1])  # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0002), '08b')[::-1])   # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0081), '016b')[::-1])  # sli
            board_registers.append(format(self.board.read_register(registeraddress=0x0082), '08b')[::-1])   # sli
        except Exception as e:
            self.error = 1
            print(e)
        return board_registers

    def read_d08_registers(self):
        """Чтение регистров модуля D0-8."""
        board_registers: list = []
        try:
            board_registers.append(format(self.board.read_register(registeraddress=0x0000), '08b')[::-1])  # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0010), '08b')[::-1])  # sl
            board_registers.append(format(self.board.read_register(registeraddress=0x0080), '08b')[::-1])  # sli
            board_registers.append(format(self.board.read_register(registeraddress=0x0090), '08b')[::-1])  # sli
        except Exception as e:
            self.error = 1
            print(e)
        return board_registers
