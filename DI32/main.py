import sys
import pathlib
import asyncio
from struct import pack, unpack

from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets

from modbus import Modbus_RTU


from MainWindow import Ui_MainWindow


def data_unpack(data_in: list):
    """Преобразование данных из регистров в ток/напряжение/проценты.

        Параметры:
            * data_in (list): список входных данных из регистров.

        Возвращаемое значение:
            * data_list (list): список преобразованных данных.
    """
    data_list: list = []
    for i in range(0, len(data_in), 2):
        r0 = data_in[i]
        r1 = data_in[i + 1] << 16
        data = r0 | r1
        data_list.append(data)
    return data_list


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("ModBus App for DI32")
        self.setFixedSize(QSize(770, 810))

        self.device = None
        self.ports_list: list = []
        self.requests_num: int = 1

        self.choice_port_box.currentIndexChanged.connect(self.change_current_port)
        self.data_read_button.clicked.connect(self.read_registers)
        self.choice_port_find_button.clicked.connect(self.find_ports)

    def read_registers(self):
        self.requests_num = int(self.requests_number_edit.text())

        while self.requests_num >= 1:
            inputs = self.device.read_multiple_registers(register_address=0x0000, number=2)
            inputs = list(format(inputs[0], '016b')[::-1] + format(inputs[1], '016b')[::-1])
            for i in range(32):
                self.inputs_edit_layout.itemAt(i).widget().setText(inputs[i])

            counter = data_unpack(self.device.read_multiple_registers(register_address=0x0100, number=64))
            for i in range(16):
                self.counter_layout_1.itemAt(i).widget().setText(f'{counter[i]}')
            for i in range(16):
                self.counter_layout_2.itemAt(i).widget().setText(f'{counter[i+16]}')

            counterF = data_unpack(self.device.read_multiple_registers(register_address=0x0200, number=64))
            for i in range(16):
                self.counterF_layout_1.itemAt(i).widget().setText(f'{counterF[i]}')
            for i in range(16):
                self.counterF_layout_2.itemAt(i).widget().setText(f'{counterF[i+16]}')

            # device_info
            device_info = self.device.read_multiple_registers(register_address=0x0300, number=10)
            print(device_info)
            self.mb_rx_packets_edit.setText(f'{data_unpack(device_info[:2])[0]}')
            self.mb_tx_packets_edit.setText(f'{data_unpack(device_info[2:4])[0]}')
            self.rs485_de_errors_edit.setText(f'{device_info[4]}')
            self.work_timer_edit.setText(f'{data_unpack(device_info[7:9])[0]}')
            # cpu_flags
            cpu_flags = list(format(device_info[9], '08b'))[::-1]
            for i in range(6):
                self.cpu_flags_layout.itemAt(i).widget().setText(cpu_flags[i])

            self.requests_num -= 1
            # self.requests_number_edit.setText(str(self.requests_num))

    def change_current_port(self):
        if self.choice_port_box.currentText()[:11] == '/dev/ttyUSB':
            if self.device != None:
                self.device.board.serial.port = self.choice_port_box.currentText()
            else:  # create ModBus connect
                self.device = Modbus_RTU(self.choice_port_box.currentText()[5:], slave_address=0x30)
                print('create Modbus connect')
            print(f'current mobbus port: {self.device.board.serial.port}')

    def find_ports(self):
        current_directory = pathlib.Path('/dev')
        current_pattern = "ttyUSB*"
        self.ports_list = []
        for current_file in current_directory.glob(current_pattern):
            self.ports_list.append(str(current_file))
        self.ports_list.sort()
        self.choice_port_box.clear()
        self.choice_port_box.addItems(self.ports_list)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
