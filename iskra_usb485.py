import serial # pip3 install pyserial
from time import sleep
class COM_RS485:
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
    def __init__(self,port="COM3", baudrate=9600, bytesize=7, parity=PARITY_EVEN, stopbits=1, timeout=0.1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.connect()
    def connect(self):
        self.con = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,self.timeout)
    def write(self,data_list,crc16 = True,timeout=None):
        if crc16:
            data_byte = self.modbus_crc16(data_list)
        else:
            data_byte = bytes(data_list)
        if timeout is not None:
            self.con.timeout = timeout
        print('=>',data_byte)
        self.con.write(data_byte)
        ret = self.con.readline()
        print('<=',ret)
        return ret
    def close(self):
        self.con.close()
    @staticmethod
    def modbus_crc16(data: b'', ret_type="bytes"):
        HIBYTE = b'\x00\xC0\xC1\x01\xC3\x03\x02\xC2\xC6\x06\x07\xC7\x05\xC5\xC4\x04\xCC\x0C\x0D\xCD\x0F\xCF\xCE\x0E\x0A\xCA\xCB\x0B\xC9\x09\x08\xC8\xD8\x18\x19\xD9\x1B\xDB\xDA\x1A\x1E\xDE\xDF\x1F\xDD\x1D\x1C\xDC\x14\xD4\xD5\x15\xD7\x17\x16\xD6\xD2\x12\x13\xD3\x11\xD1\xD0\x10\xF0\x30\x31\xF1\x33\xF3\xF2\x32\x36\xF6\xF7\x37\xF5\x35\x34\xF4\x3C\xFC\xFD\x3D\xFF\x3F\x3E\xFE\xFA\x3A\x3B\xFB\x39\xF9\xF8\x38\x28\xE8\xE9\x29\xEB\x2B\x2A\xEA\xEE\x2E\x2F\xEF\x2D\xED\xEC\x2C\xE4\x24\x25\xE5\x27\xE7\xE6\x26\x22\xE2\xE3\x23\xE1\x21\x20\xE0\xA0\x60\x61\xA1\x63\xA3\xA2\x62\x66\xA6\xA7\x67\xA5\x65\x64\xA4\x6C\xAC\xAD\x6D\xAF\x6F\x6E\xAE\xAA\x6A\x6B\xAB\x69\xA9\xA8\x68\x78\xB8\xB9\x79\xBB\x7B\x7A\xBA\xBE\x7E\x7F\xBF\x7D\xBD\xBC\x7C\xB4\x74\x75\xB5\x77\xB7\xB6\x76\x72\xB2\xB3\x73\xB1\x71\x70\xB0\x50\x90\x91\x51\x93\x53\x52\x92\x96\x56\x57\x97\x55\x95\x94\x54\x9C\x5C\x5D\x9D\x5F\x9F\x9E\x5E\x5A\x9A\x9B\x5B\x99\x59\x58\x98\x88\x48\x49\x89\x4B\x8B\x8A\x4A\x4E\x8E\x8F\x4F\x8D\x4D\x4C\x8C\x44\x84\x85\x45\x87\x47\x46\x86\x82\x42\x43\x83\x41\x81\x80\x40'
        LOBYTE = b'\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40\x00\xC1\x81\x40\x01\xC0\x80\x41\x00\xC1\x81\x40\x01\xC0\x80\x41\x01\xC0\x80\x41\x00\xC1\x81\x40'
        crchi = 0xFF
        crclo = 0xFF
        for byte in data:
            index = crchi ^ int(byte)
            crchi = crclo ^ LOBYTE[index]
            crclo = HIBYTE[index]
        if ret_type == "bytes":
            return bytes(data + [crchi, crclo])
        else:
            return data + [crchi, crclo]
    @staticmethod
    def print_bytes(b):
        i = []
        for el in b:
            i.append(el)
        print(i)
        return i
def read_bytes(com_rs,next=False,debug=False):
    if debug: print('read_bytes:.')
    ret_byte = com_rs.con.read()
    if ret_byte == b'\x15':
        ret_byte = b''
    if ret_byte == b'':
        while_i = 0
        while ret_byte == b'' and while_i < 3:
            sleep(0.5)
            if debug: print('\tread_byte_while:', ret_byte)
            ret_byte = com_rs.con.read()
            while_i += 1
    while_i, res = 0, b''
    while ret_byte != b'' and while_i < 5:
        if debug: print('\tread_byte:',ret_byte)
        res = res + ret_byte
        ret_byte = com_rs.con.read()
        next = True
    return res, next
def res_clr(text):
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
def iskra_to_json(data_bytes:bytes="", get_data:dict={}, debug = False):
    data_text = res_clr(data_bytes.decode())
    j = {}
    for code_value in data_text.split('\r\n'):
        if (True if code_value.find('(') != -1 else False) and (True if code_value.find(')') != -1 else False):
            fr = code_value.find('(')
            to = code_value.find(')')
            code = code_value[:fr]
            data = code_value[fr+1:to]
            if get_data.get(code) is not None:
                i, t = '', ''
                _float = False
                for s in data:
                    o = ord(s)
                    #print('o:',o)
                    if o == 46: _float = True
                    if o >= 46 and o <= 57:
                        i = i + s
                    else:
                        t = t + s
                value = float(i) if _float else int(i)
                if debug: print('code: ',code,'\n','data: ',data,'\n',' value: ',value,'\n',' ediz: ',t,'\n',sep='')
                get_data[code].update({'value': value,'ediz':t})
    return get_data

def Получить_дату_и_время(sn,passwd='PARAM'):
    error, response = True, 'Ошибка входа в коммуникационную сессию!'
    debug = True
    debug = False
    com_rs = COM_RS485(timeout=0.1)
    # Инициализация сессии (Видимо что бы все слушали).
    data = [0,0,0,0,0,0,0,0]
    print('=>',data)
    ret = com_rs.con.write(data)
    if debug: print("write:",ret)
    #print(com_rs.con.readable())
    print('<=',com_rs.con.readlines(),'\n')
    sleep(0.1)

    # Отправляем серийник (Видимо в надежде на то, что нужный услышит и ответит)
    data = f'/?{sn}!\r\n'.encode()
    print('=>', data)
    ret = com_rs.con.write(data)
    if debug: print("write:",ret)
    #print(com_rs.con.readable())
    res, next = read_bytes(com_rs,debug=debug)
    print('<=',res,'\n')

    if next:
        # Отправляем 051 (Видимо запрос на авторизацию пользователя)
        data = '051\r\n'.encode()
        print('=>', data)
        ret = com_rs.con.write(data)
        if debug: print("write:",ret)
        #print(com_rs.con.readable())
        res, next = read_bytes(com_rs,debug=debug)
        print('<=',res,'\n')

    if next:
        # Ввод пароля, по умолчанию, PARAM.
        data = f'P1({passwd}).'.encode()
        print('=>', data)
        ret = com_rs.con.write(data)
        if debug: print("write:",ret)
        #print(com_rs.con.readable())
        res, next = read_bytes(com_rs,debug=debug)
        print('<=',res,'\n')

    if next:
        # Запрос даты и время.
        data = 'R10.9.4()^'.encode()
        print('=>', data)
        ret = com_rs.con.write(data)
        if debug: print("write:",ret)
        #print(com_rs.con.readable())
        res, next = read_bytes(com_rs,debug=debug)
        print('<=',res,'\n')
        res_clear = res_clr(res.decode())
        print('res_clear:',res_clear)
        YY = res_clear[1:3]
        MM = res_clear[3:5]
        DD = res_clear[5:7]
        hh = res_clear[7:9]
        mm = res_clear[9:11]
        ss = res_clear[11:13]
        response = f'{DD}.{MM}.20{YY} {hh}:{mm}:{ss}'
        error = False
    data_quit = 'B0q'.encode()
    ret = com_rs.con.write(data_quit)
    com_rs.con.close()
    if debug: print("write:", ret)
    return error,response

def Регистры_опрос(sn,info=False,debug = False):
    error, response = True, 'Ошибка входа в коммуникационную сессию!'
    if debug: info = True
    com_rs = COM_RS485(timeout=0.1)
    # Инициализация сессии (Видимо что бы все слушали).
    data = [0,0,0,0,0,0,0,0]
    if info: print('=>',data)
    ret = com_rs.con.write(data)
    if debug: print("write:",ret)
    if info: print('<=',com_rs.con.readlines(),'\n')
    sleep(0.1)
    # Отправляем серийник (Видимо в надежде на то, что нужный услышал и ответит)
    #sn = '35620873'
    data = f'/?{sn}!\r\n'.encode()
    if info: print('=>', data)
    ret = com_rs.con.write(data)
    if debug: print("write:",ret)
    res, next = read_bytes(com_rs,debug=debug)
    if info: print('<=',res,'\n')

    if next:
        # Запрос регистров.
        data = '050\r\n'.encode()
        if info: print('=>', data)
        ret = com_rs.con.write(data)
        if debug: print("write:",ret)
        #print(com_rs.con.readable())
        res, next = read_bytes(com_rs,debug=debug)
        if info: print('<=',res,'\n')
        response = res
        error = False

    # Закрыть сессии(485 и serial).
    data_quit = 'B0q'.encode()
    ret = com_rs.con.write(data_quit)
    com_rs.con.close()
    if debug: print("write:", ret)
    return error,response

# Проверено на ISKRA MT831. (если данные не приходят, поменяй таймаут: COM_RS485(timeout=0.1))
if __name__ == '__main__':
    fun = Регистры_опрос
    sn = '35620873'
    err, res = fun(sn)
    i =  0
    # Так как прочитать с первого раза, не получается и родной прогой, добавляем цикл.
    while err and i < 3:
        err, res = fun(sn)
        sleep(5)
        i += 1
    # Что мы хотим отфильтровать из общего списка {res}.
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
    # В словарь get_data дописываем значения регистров.
    j = iskra_to_json(data_bytes=res, get_data=get_data)
    print(j)
