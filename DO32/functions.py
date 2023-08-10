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


def data_split(data_in: list):
    """Разбивка данных на два регистра"""
    split_data: list = []
    for item in data_in:
        split_data.append((item >> 16) & 0x0000FFFF)
        split_data.append(item & 0x0000FFFF)
    return split_data
