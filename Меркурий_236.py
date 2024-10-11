# Doc: https://www.teleuchet.ru/docs/pdf/protokol.pdf
'''
Таймауты: ReadInterval=25, ReadTotalTimeoutMultiplier=4, ReadTotalTimeoutConstant=200, WriteTotalTimeoutMultiplier=1, WriteTotalTimeoutConstant=100
Скорость передачи 9600
RTS выключен
DTR выключен
Биты данных=8, Стоповые биты=1, Четность=None
Служ. символы: Eof=0x00, Error=0x00, Break=0x00, Event=0x00, Xon=0x00, Xoff=0x00
Контроль передачи: ControlHandShake=(), Замена=(), Лимит Xon=0, Лимит Xoff=0
DTR включен
RTS включен
Очистка порта: RXCLEAR, TXCLEAR
'''

import serial

class Меркурий_236:
    def __init__(self,port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=2, timeout=1, userpass:list = [1,1,1,1,1,1,1]):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.userpass = userpass
        self.connect()
    def connect(self):
        # Ошибка подключения и так пишется в явном виде, обработка не требуется.
        self.con = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,self.timeout)
    def write(self,data_list):
        self.request = data_list
        data_byte = self.modbus_crc16(data_list)
        #print('=>',list(data_byte))
        self.con.write(data_byte)
        res = self.con.readline()
        #print('<=',list(res))
        return res
    def close(self):
        self.con.close()
    def status(self,response):
        if response != b'':
            if self.request[0] == response[0]:
                if response[1] == 0:
                    return 'Ok'
        return 'Error'
    def test(self,SlaveID:int = 0):
        self.SlaveID = SlaveID
        print('Инициализация сеанса.')
        res = self.write([self.SlaveID,0])
        status = self.status(res)
        print('\tОтвет:',status)
        if status == "Error": return None
        print()
        res = self.write([self.SlaveID,8,0])
        sn = ''.join([str(i) for i in res[1:5]])
        dom = f'{str(res[5]).rjust(2,'0')}.{str(res[6]).rjust(2,'0')}.20{res[7]}'
        print('Серийный номер:',sn)
        print('Дата изготовления:',dom)
        print()
        print('Завершение сеанса.')
        res = self.write([self.SlaveID,2])
        print('\tОтвет:',self.status(res))
    def энергия(self,SlaveID:int = 0,divisor:int = 1000):
        self.SlaveID = SlaveID
        print('Инициализация сеанса.')
        res = self.write([self.SlaveID,0])
        status = self.status(res)
        print('\tОтвет:',status)
        if status == "Error": return None
        print()
        print('Аутентификация.')
        res = self.write([self.SlaveID,1]+self.userpass)
        status = self.status(res)
        print('\tОтвет:',status)
        print()
        data = self.write([self.SlaveID, 5, 0, 0])
        ret = self.b2143_to_int(data[1:-2])
        print("Энергия A+:", ret[0], "кВт*ч")
        print("Энергия A-:", ret[1], "кВт*ч")
        print("Энергия R+:", ret[2], "кВАр*ч")
        print("Энергия R-:", ret[3], "кВАр*ч")
        print()
        print('Завершение сеанса.')
        res = self.write([self.SlaveID,2])
        print('\tОтвет:',self.status(res))
        return ret
    @staticmethod
    def b2143_to_int(arr,divisor:int = 1000):
        b = 4
        divided = [arr[i:i + b] for i in range(0, len(arr), b)]
        ret = [int.from_bytes([b, a, d, c]) / divisor if [b, a, d, c] != [255, 255, 255, 255] else 0 for a, b, c, d in divided]
        return ret
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

if __name__ == '__main__':
    print('ТЕСТ ПОДКЛЮЧЕНИЯ')
    m = Меркурий_236(port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.1)
    m.test()
    m.close()
    print('\n'*3)

if __name__ == '__main__':
    print('ЗАПРОС ЗНАЧЕНИЙ')
    user = [1] # [1]-User, [2]-Admin
    passwd = [1,1,1,1,1,1] #UserPass - [1,1,1,1,1,1], AdminPass - [2,2,2,2,2,2]
    userpass = user + passwd
    m = Меркурий_236(port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.1, userpass=userpass)
    энергия = m.энергия()
    m.close()
    print('\nЭнергия:',энергия)




