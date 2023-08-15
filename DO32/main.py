import sys
import pathlib

from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets

from DO32MainWindow import Ui_MainWindow
from modbus import Modbus_RTU
from functions import data_unpack, data_unpack_2, data_split


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("QtModBus App for DO32-NDC")
        self.setFixedSize(QSize(1210, 870))
        self.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px
            }
        """)

        self.device = None
        self.slave_address = 0x80
        self.ports_list: list = []
        self.requests_num: int = 1

        self.outputs_mode: list = [0, 0]
        self.outputs: list = [0, 0]
        self.pwm_outputs_invertion: list = [0, 0]
        self.period: list = [0] * 64
        self.duty: list = [0] * 64
        self.npulses: list = [0] * 64

# region: SIGNALS
        self.choice_port_find_button.clicked.connect(self.find_ports)
        self.choice_port_box.currentIndexChanged.connect(self.change_current_port)
        self.slave_address_edit.textChanged.connect(self.change_slave_address)
        self.data_read_button.clicked.connect(self.read_registers)
        self.data_write_button.clicked.connect(self.write_registers)

        self.outputs_mode_radio_1.stateChanged.connect(self.outputs_mode_groups_change_status)
        self.outputs_mode_radio_2.stateChanged.connect(self.outputs_mode_groups_change_status)
        self.outputs_mode_radio_3.stateChanged.connect(self.outputs_mode_groups_change_status)
        self.outputs_mode_radio_4.stateChanged.connect(self.outputs_mode_groups_change_status)

        self.outputs_radio_1.stateChanged.connect(self.outputs_groups_change_status)
        self.outputs_radio_2.stateChanged.connect(self.outputs_groups_change_status)
        self.outputs_radio_3.stateChanged.connect(self.outputs_groups_change_status)
        self.outputs_radio_4.stateChanged.connect(self.outputs_groups_change_status)

        self.pwm_outputs_invertion_radio_1.stateChanged.connect(self.pwm_outputs_invertion_groups_change_status)
        self.pwm_outputs_invertion_radio_2.stateChanged.connect(self.pwm_outputs_invertion_groups_change_status)
        self.pwm_outputs_invertion_radio_3.stateChanged.connect(self.pwm_outputs_invertion_groups_change_status)
        self.pwm_outputs_invertion_radio_4.stateChanged.connect(self.pwm_outputs_invertion_groups_change_status)

        self.period_reset_button.clicked.connect(self.clear_period_edits)
        self.duty_reset_button.clicked.connect(self.clear_duty_edits)
        self.npulses_reset_button.clicked.connect(self.clear_npulses_edits)
# endregion

    def write_registers(self):
        print('\nbutton "write_registers is clicked"')
        self.parse_data()
        self.device.write_multiple_registers(register_address=0x0000, data=self.outputs)
        self.device.write_multiple_registers(register_address=0x01C0, data=self.outputs_mode)
        self.device.write_multiple_registers(register_address=0x01C2, data=self.pwm_outputs_invertion)
        self.device.write_multiple_registers(register_address=0x0100, data=self.period)
        self.device.write_multiple_registers(register_address=0x0140, data=self.duty)
        self.device.write_multiple_registers(register_address=0x0180, data=self.npulses)

    def read_registers(self):
        try:
            print('\nbutton "read_registers is clicked"')
            self.requests_num = int(self.requests_number_edit.text())
            while self.requests_num >= 1:
                # ******************** mode ********************
                mode = self.device.read_multiple_registers(register_address=0x01C0, number=2)
                print(f'mode                    {mode}')
                # ******************** outputs ********************
                outputs = self.device.read_multiple_registers(register_address=0x0000, number=2)
                print(f'outputs                 {outputs}')
                # ******************** invertion ********************
                invertion = self.device.read_multiple_registers(register_address=0x01C2, number=2)
                print(f'invertion               {invertion}')
                # ******************** period ********************
                period = self.device.read_multiple_registers(register_address=0x0100, number=64)
                print(f'period                  {len(period), period}')
                period_unpuck = data_unpack(period)
                for i in range(self.period_layout_1.count()):
                    self.period_layout_1.itemAt(i).widget().setText(str(period_unpuck[i]))
                for i in range(self.period_layout_2.count()):
                    self.period_layout_2.itemAt(i).widget().setText(str(period_unpuck[i+16]))
                # ******************** duty ********************
                duty = self.device.read_multiple_registers(register_address=0x0140, number=64)
                print(f'duty                    {len(duty), duty}')
                duty_unpuck = data_unpack(duty)
                for i in range(self.duty_layout_1.count()):
                    self.duty_layout_1.itemAt(i).widget().setText(str(duty_unpuck[i]))
                for i in range(self.duty_layout_2.count()):
                    self.duty_layout_2.itemAt(i).widget().setText(str(duty_unpuck[i+16]))
                # ******************** npulses ********************
                npulses = self.device.read_multiple_registers(register_address=0x0180, number=64)
                print(f'npulses                 {len(npulses), npulses}')
                npulses_unpuck = data_unpack(npulses)
                for i in range(self.npulses_layout_1.count()):
                    self.npulses_layout_1.itemAt(i).widget().setText(str(npulses_unpuck[i]))
                for i in range(self.npulses_layout_2.count()):
                    self.npulses_layout_2.itemAt(i).widget().setText(str(npulses_unpuck[i+16]))
                # ******************** device_info ********************
                device_info = self.device.read_device_info()
                print(f'device_info             {device_info}')
                self.mb_rx_packets_edit.setText(str(device_info[0]))
                self.mb_tx_packets_edit.setText(str(device_info[1]))
                self.rs485_de_errors_edit.setText(str(device_info[2]))
                self.work_timer_edit.setText(str(device_info[3]))
                for i in range(6):
                    self.cpu_flags_layout.itemAt(i).widget().setText(str(device_info[4][i]))
                # ******************** device_static_info ********************
                static_info = self.device.read_static_info()
                print(f'static_info             {static_info}')
                # # ******************** cofe ********************
                cofe = self.device.read_single_register(register_address=0x0600)
                print(f'cofe                    {hex(cofe)}')
                self.requests_num -= 1
        except Exception as e:
            print(e)

    def change_current_port(self):
        if self.choice_port_box.currentText()[:11] == '/dev/ttyUSB':
            if self.device != None:
                self.device.board.serial.port = self.choice_port_box.currentText()
            else:  # create ModBus connect
                self.device = Modbus_RTU(self.choice_port_box.currentText()[5:], slave_address=self.slave_address)
                print('create Modbus connect')
            print(f'current mobbus port: {self.device.board.serial.port}')

    def change_slave_address(self):
        if self.device != None:
            self.get_slave_address()
            self.device.board.address = self.slave_address
            # print(self.device.board.address)
        else:
            print('ModBus not connected')

    def find_ports(self):
        current_directory = pathlib.Path('/dev')
        current_pattern = "ttyUSB*"
        self.ports_list = []
        for current_file in current_directory.glob(current_pattern):
            self.ports_list.append(str(current_file))
        self.ports_list.sort()
        self.choice_port_box.clear()
        self.choice_port_box.addItems(self.ports_list)

    def parse_data(self):
        outputs_mode = (
            [str(int(self.output_mode_checkbox_layout.itemAt(i).widget().isChecked())) for i in range(32)])
        outputs_mode = ''.join(outputs_mode)
        self.outputs_mode[0] = int(outputs_mode[:16][::-1], 2)
        self.outputs_mode[1] = int(outputs_mode[16:][::-1], 2)
        # *****************************************
        outputs = (
            [str(int(self.outputs_checkbox_layout.itemAt(i).widget().isChecked())) for i in range(32)])
        outputs = ''.join(outputs)
        self.outputs[0] = int(outputs[:16][::-1], 2)
        self.outputs[1] = int(outputs[16:][::-1], 2)
        # *****************************************
        pwm_outputs_invertion = (
            [str(int(self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().isChecked())) for i in range(32)])
        pwm_outputs_invertion = ''.join(pwm_outputs_invertion)
        self.pwm_outputs_invertion[0] = int(pwm_outputs_invertion[:16][::-1], 2)
        self.pwm_outputs_invertion[1] = int(pwm_outputs_invertion[16:][::-1], 2)
        # *****************************************
        period = ([int(self.period_layout_1.itemAt(i).widget().text()) for i in range(16)] +
                  [int(self.period_layout_2.itemAt(i).widget().text()) for i in range(16)])
        self.period = data_split(period)
        # *****************************************
        duty = ([int(self.duty_layout_1.itemAt(i).widget().text()) for i in range(16)] +
                [int(self.duty_layout_2.itemAt(i).widget().text()) for i in range(16)])
        self.duty = data_split(duty)
        # *****************************************
        npulses = ([int(self.npulses_layout_1.itemAt(i).widget().text()) for i in range(16)] +
                   [int(self.npulses_layout_2.itemAt(i).widget().text()) for i in range(16)])
        self.npulses = data_split(npulses)
        # *****************************************
        print(f'mode:                   {self.outputs_mode}')
        print(f'outputs:                {self.outputs}')
        print(f'invertion:              {self.pwm_outputs_invertion}')
        print(f'period:                 {len(self.period), self.period}')
        print(f'duty:                   {len(self.duty), self.duty}')
        print(f'npulses:                {len(self.duty), self.npulses}')

    def get_slave_address(self):
        slave_address = self.slave_address_edit.text()
        if slave_address[:2] == '0x' or slave_address[:2] == '0X':
            self.slave_address = 0 if len(slave_address) == 2 else int(slave_address, 16)
        elif slave_address[:2] == '0o' or slave_address[:2] == '0O':
            self.slave_address = 0 if len(slave_address) == 2 else int(slave_address, 8)
        elif slave_address[:2] == '0b' or slave_address[:2] == '0B':
            self.slave_address = 0 if len(slave_address) == 2 else int(slave_address, 2)
        else:
            self.slave_address = 0 if slave_address == '' else int(slave_address, 10)

    def outputs_mode_groups_change_status(self):
        if self.outputs_mode_radio_1.isChecked():
            for i in range(8):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_mode_radio_1.isChecked():
            for i in range(8):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_mode_radio_2.isChecked():
            for i in range(8, 16):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_mode_radio_2.isChecked():
            for i in range(8, 16):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_mode_radio_3.isChecked():
            for i in range(16, 24):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_mode_radio_3.isChecked():
            for i in range(16, 24):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_mode_radio_4.isChecked():
            for i in range(24, 32):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_mode_radio_4.isChecked():
            for i in range(24, 32):
                self.output_mode_checkbox_layout.itemAt(i).widget().setChecked(False)

    def outputs_groups_change_status(self):
        if self.outputs_radio_1.isChecked():
            for i in range(8):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_radio_1.isChecked():
            for i in range(8):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_radio_2.isChecked():
            for i in range(8, 16):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_radio_2.isChecked():
            for i in range(8, 16):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_radio_3.isChecked():
            for i in range(16, 24):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_radio_3.isChecked():
            for i in range(16, 24):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.outputs_radio_4.isChecked():
            for i in range(24, 32):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.outputs_radio_4.isChecked():
            for i in range(24, 32):
                self.outputs_checkbox_layout.itemAt(i).widget().setChecked(False)

    def pwm_outputs_invertion_groups_change_status(self):
        if self.pwm_outputs_invertion_radio_1.isChecked():
            for i in range(8):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.pwm_outputs_invertion_radio_1.isChecked():
            for i in range(8):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.pwm_outputs_invertion_radio_2.isChecked():
            for i in range(8, 16):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.pwm_outputs_invertion_radio_2.isChecked():
            for i in range(8, 16):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.pwm_outputs_invertion_radio_3.isChecked():
            for i in range(16, 24):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.pwm_outputs_invertion_radio_3.isChecked():
            for i in range(16, 24):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(False)
        #
        if self.pwm_outputs_invertion_radio_4.isChecked():
            for i in range(24, 32):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(True)
        elif not self.pwm_outputs_invertion_radio_4.isChecked():
            for i in range(24, 32):
                self.pwm_outputs_inversion_checkbox_layout.itemAt(i).widget().setChecked(False)

    def clear_period_edits(self):
        for i in range(self.period_layout_1.count()):
            self.period_layout_1.itemAt(i).widget().setText('0')
        for i in range(self.period_layout_2.count()):
            self.period_layout_2.itemAt(i).widget().setText('0')

    def clear_duty_edits(self):
        for i in range(self.duty_layout_1.count()):
            self.duty_layout_1.itemAt(i).widget().setText('0')
        for i in range(self.duty_layout_2.count()):
            self.duty_layout_2.itemAt(i).widget().setText('0')

    def clear_npulses_edits(self):
        for i in range(self.npulses_layout_1.count()):
            self.npulses_layout_1.itemAt(i).widget().setText('0')
        for i in range(self.npulses_layout_2.count()):
            self.npulses_layout_2.itemAt(i).widget().setText('0')


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
