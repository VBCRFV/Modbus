import serial

modbus_307 = {'Modbus адрес':{'req':[255, 255, 255, 255, 15],'res':['byte_int',9]},
              'Модель счётчика Милур': {'req': [1, 32], 'res': ['decode', 4, -2]},
              'Серийный номер счетчика': {'req': [1, 68], 'res': ['decode', 4, -2]},
              'Напряжение, фаза A, В': {'req': [1, 100], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Напряжение, фаза B, В': {'req': [1, 101], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Напряжение, фаза C, В': {'req': [1, 102], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Ток, фаза A, А': {'req': [1, 103], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Ток, фаза B, А': {'req': [1, 104], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Ток, фаза C, А': {'req': [1, 105], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Активная мощность, фаза A, Вт': {'req': [1, 106], 'res': ['byte_revers_int', 4, -2, 100]},
              'Активная мощность, фаза B, Вт': {'req': [1, 107], 'res': ['byte_revers_int', 4, -2, 100]},
              'Активная мощность, фаза C, Вт': {'req': [1, 108], 'res': ['byte_revers_int', 4, -2, 100]},
              'Активная мощность, Сумма, Вт': {'req': [1, 109], 'res': ['byte_revers_int', 4, -2, 100]},
              'Реактивная мощность, фаза A, вар': {'req': [1, 110], 'res': ['Реактивная мощность', 4, -2, 100]},
              'Реактивная мощность, фаза B, вар': {'req': [1, 111], 'res':['Реактивная мощность', 4, -2, 100]},
              'Реактивная мощность, фаза C, вар': {'req': [1, 112], 'res': ['Реактивная мощность', 4, -2, 100]},
              'Реактивная мощность, Сумма, вар': {'req': [1, 113], 'res': ['Реактивная мощность', 4, -2, 100]},
              'Полная мощность, фаза A, ВА': {'req': [1, 114], 'res': ['byte_revers_int', 4, -2, 100]},
              'Полная мощность, фаза B, ВА': {'req': [1, 115], 'res': ['byte_revers_int', 4, -2, 100]},
              'Полная мощность, фаза C, ВА': {'req': [1, 116], 'res': ['byte_revers_int', 4, -2, 100]},
              'Полная мощность, Сумма, ВА': {'req': [1, 117], 'res': ['byte_revers_int', 4, -2, 100]},
              'Частота сети, Гц': {'req': [1, 9], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Напряжение батареи резервного питания, В': {'req': [1, 57], 'res': ['byte_revers_int', 4, -2, 1000]},
              'Энергия активная импортируемая суммарная, кВт*ч': {'req': [1, 118], 'res': ['byte_revers_hex', 4, -2, 1000]},
              'Энергия активная экспортируемая суммарная, кВт*ч': {'req': [1, 149], 'res': ['byte_revers_hex', 4, -2, 1000]},
              'Энергия реактивная импортируемая суммарная, квар*ч': {'req': [1, 127], 'res': ['byte_revers_hex', 4, -2, 1000]},
              'Энергия реактивная экспортируемая суммарная, квар*ч': {'req': [1, 158], 'res': ['byte_revers_hex', 4, -2, 1000]},
              }
class miluris:
    def __init__(self,port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=2, timeout=1, modbus: dict = {}, SlaveID: list = [255], userpass: list = [0,255,255,255,255,255,255], debug = False):
        self.debug = debug
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.SlaveID = SlaveID
        self.userpass = userpass
        self.data = None
        self.connect()
        self.modbus = modbus
    def connect(self):
        # Ошибка подключения и так пишется в явном виде, обработка не требуется.
        self.con = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,self.timeout)
    def write(self,data_list):
        self.request = data_list
        data_byte = self.modbus_crc16(data_list)
        if self.debug:
            print('=> HEX',[hex(el)[2:].rjust(2,'0').upper() for el in list(data_byte)])
            print('=> INT',list(data_byte))
        self.con.write(data_byte)
        res = self.con.readline()
        if self.debug:
            print('<= HEX', [hex(el)[2:].rjust(2,'0').upper() for el in list(res)])
            print('<= INT',list(res))
        return res
    def close(self):
        self.con.close()
    def miluris_login(self, SlaveID: list = None, userpass: list = None):
        print('Аутентификация.')
        # userpass - User  [0,255,255,255,255,255,255]
        # userpass - Admin [1,255,255,255,255,255,255]
        if userpass is not None: self.userpass = userpass
        if SlaveID is not None: self.SlaveID = SlaveID
        req = self.SlaveID + [8] + self.userpass
        res = self.write(req)
        status = 'Ok' if req[:3] == list(res)[:3] else 'Error'
        print('\tStatus:',status,'\n')
        return status
    def miluris_logout(self, SlaveID: list = None):
        print('\nЗакрыть сеанс')
        if SlaveID is not None: self.SlaveID = SlaveID
        req = self.SlaveID + [9, 1]
        res = self.write(req)
        status = 'Ok' if req[:3] == list(res)[:3] else 'Error'
        print('\tStatus:',status)
        return status
    def miluris_request(self,SlaveID:int = None, description=None, session=False):
        if SlaveID is not None: self.SlaveID = SlaveID
        if session: self.miluris_login()
        self.data = self.modbus[description]
        if description == 'Modbus адрес':
            req = self.data['req']
        else:
            req = self.SlaveID + self.data['req']
        res = self.write(req)
        self.data.update({'response':res})
        data = self.get_data()
        print(f'{description}:',data)
        if session: self.miluris_logout()
        return data
    def get_data(self):
        if  self.data['res'][0] == 'byte_int':
            return self.data['response'][self.data['res'][1]]
        elif self.data['res'][0] == 'decode':
            data = [el for el in self.data['response'][self.data['res'][1]:self.data['res'][2]] if el != 0]
            return bytearray(data).decode()
        elif self.data['res'][0] == 'byte_revers_int':
            data = self.data['response'][self.data['res'][1]:self.data['res'][2]][::-1]
            return int.from_bytes(data)/self.data['res'][3]
        elif self.data['res'][0] == 'byte_revers_hex':
            data = self.data['response'][self.data['res'][1]:self.data['res'][2]]
            data_hex_str = [hex(el)[2:].rjust(2,'0').upper() for el in list(data)]
            return int(''.join(data_hex_str)[::-1])/self.data['res'][3]
        elif self.data['res'][0] == 'Реактивная мощность':
            data = int.from_bytes(self.data['response'][self.data['res'][1]:self.data['res'][2]][::-1])
            if data == 0:
                return 0
            else:
                f8 = 4294967295
                difference = data - f8
                return difference/self.data['res'][3]
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
    print('ТЕСТ ПОДКЛЮЧЕНИЯ\n')
    m = miluris(port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.1, modbus=modbus_307)
    m.miluris_request(description='Modbus адрес')
    m.close()
    print('\n'*3)

if __name__ == '__main__0':
    print('ЗАПРОС ДАННЫХ\n')
    user = [0] # [0]-User, [1]-Admin
    passwd = [255,255,255,255,255,255] #UserPass - [255,255,255,255,255,255], AdminPass - [255,255,255,255,255,255]
    userpass = user + passwd
    m = miluris(port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=0.1, modbus=modbus_307, debug=False)
    m.miluris_login(userpass=userpass)
    m.miluris_request(description='Modbus адрес')
    m.miluris_request(description='Серийный номер счетчика')
    m.miluris_request(description='Модель счётчика Милур')
    m.miluris_request(description='Напряжение, фаза A, В')
    m.miluris_request(description='Напряжение, фаза B, В')
    m.miluris_request(description='Напряжение, фаза C, В')
    m.miluris_request(description='Ток, фаза A, А')
    m.miluris_request(description='Ток, фаза B, А')
    m.miluris_request(description='Ток, фаза C, А')
    m.miluris_request(description='Активная мощность, фаза A, Вт')
    m.miluris_request(description='Активная мощность, фаза B, Вт')
    m.miluris_request(description='Активная мощность, фаза C, Вт')
    m.miluris_request(description='Активная мощность, Сумма, Вт')
    m.miluris_request(description='Реактивная мощность, фаза A, вар')
    m.miluris_request(description='Реактивная мощность, фаза B, вар')
    m.miluris_request(description='Реактивная мощность, фаза C, вар')
    m.miluris_request(description='Реактивная мощность, Сумма, вар')
    m.miluris_request(description='Полная мощность, фаза A, ВА')
    m.miluris_request(description='Полная мощность, фаза B, ВА')
    m.miluris_request(description='Полная мощность, фаза C, ВА')
    m.miluris_request(description='Полная мощность, Сумма, ВА')
    m.miluris_request(description='Частота сети, Гц')
    m.miluris_request(description='Напряжение батареи резервного питания, В')
    m.miluris_request(description='Энергия активная импортируемая суммарная, кВт*ч')
    m.miluris_request(description='Энергия активная экспортируемая суммарная, кВт*ч')
    m.miluris_request(description='Энергия реактивная импортируемая суммарная, квар*ч')
    m.miluris_request(description='Энергия реактивная экспортируемая суммарная, квар*ч')
    m.miluris_logout()
    m.close()



