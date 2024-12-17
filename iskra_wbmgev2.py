import time
from websocket import create_connection # pip install websocket-client

class iskra_wbmgev2:
    def __init__(self,ws_addr=None,timeout:int=1):
        self.ws_addr = ws_addr
        self.timeout = timeout
    def connect(self,sn:str=''):
        self.ws = create_connection(self.ws_addr, timeout=self.timeout)
        data = [0, 0, 0, 0, 0, 0, 0, 0]
        self.ws.send_binary(data)
        time.sleep(0.1)
        data = f'/?{sn}!\r\n'.encode()
        self.ws.send_binary(data)
        Opcode, ret = self.ws.recv_data()
        return ret
    def recv_all_data(self):
        data = b''
        ret = self.ws.recv()
        while len(ret) == 1460:
            data = data + ret
            ret = self.ws.recv()
        data = data + ret
        return data
    def send_binary(self,binary=b'',timeout=None):
        if timeout is not None: self.ws.settimeout(timeout)
        data = binary.encode()
        self.ws.send_binary(data)
        ret = self.recv_all_data()
        #Opcode, ret = self.ws.recv()
        if timeout is not None: self.ws.settimeout(self.timeout)
        return ret
    def close(self):
        data = 'B0q'.encode()
        self.ws.send_binary(data)
        self.ws.close()
    @staticmethod
    def clear_data(text):
        ascii_x = {'00': ' ',
                   '01': '',
                   '02': '',
                   '03': '',
                   '04': '',
                   '05': '',
                   '06': '',
                   '07': '',
                   '0b': '',
                   '0e': '',
                   '0f': '',
                   }
        for k in ascii_x:
            text = text.replace(ascii_x[k], '')
        return text
    @staticmethod
    def data_filter(data_text:str="", fltr:dict={}, debug = False):
        ret = {}
        for code_value in data_text.split('\r\n'):
            if (True if code_value.find('(') != -1 else False) and (True if code_value.find(')') != -1 else False):
                fr = code_value.find('(')
                to = code_value.find(')')
                code = code_value[:fr]
                data = code_value[fr + 1:to]
                if fltr.get(code) is not None:
                    i, t = '', ''
                    _float = False
                    for s in data:
                        o = ord(s)
                        # print('o:',o)
                        if o == 46: _float = True
                        if o >= 46 and o <= 57:
                            i = i + s
                        else:
                            t = t + s
                    value = float(i) if _float else int(i)
                    if debug: print('code: ', code, '\n', 'data: ', data, '\n', ' value: ', value, '\n', ' ediz: ', t,
                                    '\n', sep='')
                    ret.update({code:fltr[code]})
                    ret[code].update({'value': value, 'ediz': t})
        return ret

if __name__ == '__main__':
    debug = False
    if debug: start_time = time.time()
    # Адрес:порт WB-MGEv2 (любой K3 подобный)
    # естествено через веб выставляем параметы счётчика, для MT831: baudrate=9600(в документации 300, на моём стоял 9600), bytesize=7, parity=PARITY_EVEN, stopbits=1
    ws_addr='ws://10.10.10.10:6432'
    # Серийный номер искры (тестировался на ISKRA MT831)
    sn = '12345678'
    ws = iskra_wbmgev2(ws_addr=ws_addr)
    # Договариваемся пообщатся с конкретным счётчиком.
    ret = ws.connect(sn)
    if debug: print('ws.connect():',ret)
    # Запрос данных анологичных: MeterView4: [Счётчик] => [Чтение] => [Регистры (опрос)]
    ret = ws.send_binary(binary='050\r\n', timeout=10)
    if debug: print('ws.send_binary():',ret)
    # Закрываем соеденение.
    ws.close()
    # Убираем служебные символы (открытия, закрытия полседовательности)
    data = ws.clear_data(ret.decode())
    if debug: print('-=ws.clear_data()=-\n',data)
    # Что мы хотим отфильтровать из общего списка {data}.
    # Описания кодов можно получть в программе MeterView4: [Счётчик] => [Чтение] => [Регистры (опрос)]
    get_data = {'15.7.0': {'dis': 'Суммарная активная мощность'},
         '1.8.0': {'dis': 'L123 Текущее накопительное значение активной энергии+'},
         '2.8.0': {'dis': 'L123 Текущее накопительное значение активной энергии-'},
         '3.8.0': {'dis': 'L123 Текущее накопительное значение реактивной энергии+'},
         '4.8.0': {'dis': 'L123 Текущее накопительное значение реактивной энергии-'},
         '9.8.0': {'dis': 'L123 Текущее накопительное значение полной энергии+'},
         '10.8.0': {'dis': 'L123 Текущее накопительное значение полной энергии-'},
         '31.7.0': {'dis': 'L1 Ток'},
         '51.7.0': {'dis': 'L2 Ток'},
         '71.7.0': {'dis': 'L3 Ток'},
         '32.7.0': {'dis': 'L1 Напряжение'},
         '52.7.0': {'dis': 'L2 Напряжение'},
         '72.7.0': {'dis': 'L3 Напряжение'},
         '33.7.0': {'dis': 'L1 Коэффициент мощности'},
         '53.7.0': {'dis': 'L2 Коэффициент мощности'},
         '73.7.0': {'dis': 'L3 Коэффициент мощности'},
         '81.7.40': {'dis': 'L1 Фазный угол'},
         '81.7.51': {'dis': 'L2 Фазный угол'},
         '81.7.62': {'dis': 'L3 Фазный угол'},
         '11.7.0': {'dis': 'L123 Ток'},
         '12.7.0': {'dis': 'L123 Напряжение'},
         '13.7.0': {'dis': 'L123 Коэффициент мощности'},
         }
    # Фильтруем данные пришедшие с счётчика и возвращаем только то что нужно(то что в {get_data})
    # Если нужны даты срезов или всё в json, правим data_filter под себя.
    data = ws.data_filter(data_text=data, fltr=get_data,debug=debug)
    print('data:',data)
    if debug:
        print('Всё ли пришло:', len(get_data) == len(data))
        print('Время выполнения:',time.time()-start_time)
    # Если передавать в zabbix: data = json.dumps(data)
    # Если кирилица идёт лесом, енкодим-декодим из своей в нужную кодировку.
