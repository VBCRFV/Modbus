
class COM_485:
    '''
    Подключение через COM<->RS485 интерфейс
    протестировано на "WB-USB485"
    '''
    # WirenBoard -  baudrate=9600, bytesize=8, parity='N', stopbits=2
    # Меркурий -    baudrate=9600, bytesize=8, parity='N', stopbits=1
    # Милур -       baudrate=9600, bytesize=8, parity='N', stopbits=1
    def __init__(self,port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=2, timeout=1, userpass: list = None):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.userpass = userpass
        self.open()
    def open(self):
        import serial # pip3 install pyserial
        self.com = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits,self.timeout)
    def writeline(self,req):
        self.com.write(req)
    def readline(self):
        res = self.com.readline()
        return res
    def close(self):
        self.com.close()

class IP_485:
    '''
    Подключение через Ethernet<->RS485 интерфейс
    протестировано на "WB-MGE v2.10G "
    '''
    def __init__(self,ws_addr=None,timeout:int=1):
        self.ws_addr = ws_addr
        self.timeout = timeout
        self.open()
    def open(self):
        from websocket import create_connection # pip install websocket-client
        self.ws = create_connection(self.ws_addr,timeout=self.timeout)
    def writeline(self,binary):
        self.ws.send_binary(binary)
    def readline(self):
        Opcode, ret = self.ws.recv_data()
        #ret = self.ws.recv()
        return ret
    def close(self):
        self.ws.close()

class Modbus:
    def __init__(self, session: object = None, SlaveID: int = None, modbus_reg: dict = None, debug: bool = True):
        self.ses = session
        self.SlaveID = SlaveID
        self.reg = modbus_reg
        self.debug = debug
    def request_response(self,description: str = None):
        self.data = self.reg[description]
        if description == 'Милур307, Modbus адрес':
            request = self.modbus_crc16(list(self.data['req']))
        else:
            request = self.modbus_crc16(list(self.SlaveID) + self.data['req'])
        self.data.update({'request':request})
        if debug:
            print('\n',description.upper(),sep='')
            print('=> HEX',[hex(el)[2:].rjust(2,'0').upper() for el in list(request)])
            print('=> INT',list(request),'\n')
        session.writeline(request)
        response = session.readline()
        if debug:
            print('<= HEX',[hex(el)[2:].rjust(2,'0').upper() for el in list(response)])
            print('<= INT',list(response))
            print('<= CHR',[chr(el) for el in list(response)])
        self.data.update({'response': response})
        ret = self.convert_response(self.data)
        if debug: print('return:',ret,'\n')
        return ret
    def close(self):
        if 'close' in self.reg:
            pass #todo ДОПИСАТЬ.
        self.ses.close()
    @staticmethod
    def convert_response(data):
        '''Конвертровать BYTE в человекочитаемую информацию'''
        if len(data['response']) == 0:
            return 'ERROR'
        elif data['res'][0] == 'byte_int':
            return data['response'][data['res'][1]]
        elif data['res'][0] == 'decode':
            ret = [el for el in data['response'][data['res'][1]:data['res'][2]] if el != 0]
            return bytearray(ret).decode()
        elif data['res'][0] == 'from_bytes':
            ret = data['response'][data['res'][1]:data['res'][2]]
            return int.from_bytes(ret)
        elif data['res'][0] == 'byte_revers_int':
            ret = data['response'][data['res'][1]:data['res'][2]][::-1]
            return int.from_bytes(ret) / data['res'][3]
        elif data['res'][0] == 'byte_revers_hex':
            ret = data['response'][data['res'][1]:data['res'][2]]
            data_hex_str = [hex(el)[2:].rjust(2, '0').upper() for el in list(ret)]
            return int(''.join(data_hex_str)[::-1]) / data['res'][3]
        elif data['res'][0] == 'Реактивная мощность':
            ret = int.from_bytes(data['response'][data['res'][1]:data['res'][2]][::-1])
            if ret == 0:
                return 0
            else:
                f8 = 4294967295
                difference = ret - f8
                return difference / data['res'][3]
        elif data['res'][0] == 'miluris_status':
            status = 'Ok' if data['response'][:3] == data['request'][:3] else 'Error'
            return status
        elif data['res'][0] == 'mecury_status':
            status = 'Ok' if (data['response'][0] == data['request'][0] and data['response'][1] == 0) else 'Error'
            return status
        elif data['res'][0] == 'mecury_sn_dom':
            sn = ''.join([str(i) for i in data['response'][1:5]])
            dom = f'{str(data['response'][5]).rjust(2, '0')}.{str(data['response'][6]).rjust(2, '0')}.20{data['response'][7]}'
            return [sn,dom]
        elif data['res'][0] == 'b2143_div4_to_int':
            arr = data['response'][data['res'][1]:data['res'][2]]
            b = 4
            divided = [arr[i:i + b] for i in range(0, len(arr), b)]
            ret = [int.from_bytes([b, a, d, c]) / data['res'][3] if [b, a, d, c] != [255, 255, 255, 255] else 0 for a, b, c, d in divided]
            return ret
        elif data['res'][0] == 'mecury_08_11':
            B1,B3,B2 = data['response'][data['res'][1]:data['res'][2]]
            multiplier = 1
            negative = data['res'][4]
            if B1 > 63:
                B1 = B1 - 64
                if negative:
                    multiplier = -1
            #P,Q,*_ = bin(B1)[2:]
            return (int.from_bytes([B1,B2,B3]) / data['res'][3]) * multiplier
    @staticmethod
    def byte_to_bits(byte):
        divisor = 128
        bits = []
        while len(bits) != 8:
            bits.append(byte // divisor)
            if bits[-1] == 1: byte = byte - divisor
            divisor = int(divisor / 2)
        return bits
    @staticmethod
    def modbus_crc16(data: b'', ret_type="bytes"): # Расчёт контройльной суммы(2 последних байта).
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

modbus_reg_Милур307 = {'Милур307, Modbus адрес':{'req':[255, 255, 255, 255, 15],'res':['byte_int',9]},
                       'Милур307, LoginUser': {'req': [8, 0, 255, 255, 255, 255, 255, 255], 'res': ['miluris_status']},
                       'Милур307, LoginAdmin': {'req': [8, 1, 255, 255, 255, 255, 255, 255], 'res': ['miluris_status']},
                       'Милур307, Модель счётчика Милур': {'req': [1, 32], 'res': ['decode', 4, -2]},
                       'Милур307, Серийный номер счетчика': {'req': [1, 68], 'res': ['decode', 4, -2]},
                       'Милур307, Напряжение, фаза A, В': {'req': [1, 100], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Напряжение, фаза B, В': {'req': [1, 101], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Напряжение, фаза C, В': {'req': [1, 102], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Ток, фаза A, А': {'req': [1, 103], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Ток, фаза B, А': {'req': [1, 104], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Ток, фаза C, А': {'req': [1, 105], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Активная мощность, фаза A, Вт': {'req': [1, 106], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Активная мощность, фаза B, Вт': {'req': [1, 107], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Активная мощность, фаза C, Вт': {'req': [1, 108], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Активная мощность, Сумма, Вт': {'req': [1, 109], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Реактивная мощность, фаза A, вар': {'req': [1, 110], 'res': ['Реактивная мощность', 4, -2, 100]},
                       'Милур307, Реактивная мощность, фаза B, вар': {'req': [1, 111], 'res':['Реактивная мощность', 4, -2, 100]},
                       'Милур307, Реактивная мощность, фаза C, вар': {'req': [1, 112], 'res': ['Реактивная мощность', 4, -2, 100]},
                       'Милур307, Реактивная мощность, Сумма, вар': {'req': [1, 113], 'res': ['Реактивная мощность', 4, -2, 100]},
                       'Милур307, Полная мощность, фаза A, ВА': {'req': [1, 114], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Полная мощность, фаза B, ВА': {'req': [1, 115], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Полная мощность, фаза C, ВА': {'req': [1, 116], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Полная мощность, Сумма, ВА': {'req': [1, 117], 'res': ['byte_revers_int', 4, -2, 100]},
                       'Милур307, Частота сети, Гц': {'req': [1, 9], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Напряжение батареи резервного питания, В': {'req': [1, 57], 'res': ['byte_revers_int', 4, -2, 1000]},
                       'Милур307, Энергия активная импортируемая суммарная, кВт*ч': {'req': [1, 118], 'res': ['byte_revers_hex', 4, -2, 1000]},
                       'Милур307, Энергия активная экспортируемая суммарная, кВт*ч': {'req': [1, 149], 'res': ['byte_revers_hex', 4, -2, 1000]},
                       'Милур307, Энергия реактивная импортируемая суммарная, квар*ч': {'req': [1, 127], 'res': ['byte_revers_hex', 4, -2, 1000]},
                       'Милур307, Энергия реактивная экспортируемая суммарная, квар*ч': {'req': [1, 158], 'res': ['byte_revers_hex', 4, -2, 1000]},
                       'Милур307, LogOut': {'req': [9, 1], 'res': ['miluris_status']},
                       }

modbus_reg_WirenBoard = {'WirenBoard, Модель устройства': {'req': [4, 0, 200, 0, 6], 'res': ['decode', 3, -2]},
                         'WirenBoard, Версия прошивки': {'req': [4, 0, 250, 0, 15], 'res': ['decode', 3, -2]},
                         'WirenBoard, Серийный номер': {'req': [4, 1, 14, 0, 2], 'res': ['from_bytes', 3, -2]},
                         }
bits = {'b2_0': '00',
        'b2_1': '01',
        'b2_2': '10',
        'b2_3': '11',
        'b4_0': '0000',
        'b4_1': '0001',
        'b4_2': '0010',
        'b4_3': '0011',
        'b4_4': '0100',
        'b4_5': '0101',
        'b4_6': '0110',
        'b4_7': '0111',
        'b4_8': '1000',
        'b4_9': '1001',
        'b4_A': '1010',
        'b4_B': '1011',
        'b4_C': '1100',
        'b4_D': '1101',
        'b4_E': '1110',
        'b4_F': '1111',
        }

modbus_reg_Меркурий236 = {'Меркурий236, Инициализация сеанса.': {'req': [0], 'res': ['mecury_status']},
                          'Меркурий236, [Серийный номер, дата изготовления]': {'req': [8, 0], 'res': ['mecury_sn_dom']},
                          'Меркурий236, LoginUser': {'req': [1,1,1,1,1,1,1,1], 'res': ['mecury_status']},
                          'Меркурий236, LoginAdmin': {'req': [1,2,2,2,2,2,2,2], 'res': ['mecury_status']},
                          'Меркурий236, Энергия [A+,A-,R+,R-]': {'req': [5, 0, 0], 'res': ['b2143_div4_to_int',1 ,-2 ,1000]},
                          'Меркурий236, Мощн.P Сумма (Вт)': {'req': [8, 17, int(bits['b4_0']+bits['b2_0']+bits['b2_0'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.P A (Вт)': {'req': [8, 17, int(bits['b4_0']+bits['b2_0']+bits['b2_1'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.P B (Вт)': {'req': [8, 17, int(bits['b4_0']+bits['b2_0']+bits['b2_2'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.P C (Вт)': {'req': [8, 17, int(bits['b4_0']+bits['b2_0']+bits['b2_3'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.Q Сумма (вар)': {'req': [8, 17, int(bits['b4_0']+bits['b2_1']+bits['b2_0'],2)], 'res': ['mecury_08_11',1,-2,100,True]},
                          'Меркурий236, Мощн.Q A (вар)': {'req': [8, 17, int(bits['b4_0']+bits['b2_1']+bits['b2_1'],2)], 'res': ['mecury_08_11',1,-2,100,True]},
                          'Меркурий236, Мощн.Q B (вар)': {'req': [8, 17, int(bits['b4_0']+bits['b2_1']+bits['b2_2'],2)], 'res': ['mecury_08_11',1,-2,100,True]},
                          'Меркурий236, Мощн.Q C (вар)': {'req': [8, 17, int(bits['b4_0']+bits['b2_1']+bits['b2_3'],2)], 'res': ['mecury_08_11',1,-2,100,True]},
                          'Меркурий236, Мощн.S Сумма (ВА)': {'req': [8, 17, int(bits['b4_0']+bits['b2_2']+bits['b2_0'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.S A (ВА)': {'req': [8, 17, int(bits['b4_0']+bits['b2_2']+bits['b2_1'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.S B (ВА)': {'req': [8, 17, int(bits['b4_0']+bits['b2_2']+bits['b2_2'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Мощн.S C (ВА)': {'req': [8, 17, int(bits['b4_0']+bits['b2_2']+bits['b2_3'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Напр.U A (В)': {'req': [8, 17, int(bits['b4_1']+bits['b4_1'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Напр.U B (В)': {'req': [8, 17, int(bits['b4_1']+bits['b4_2'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Напр.U C (В)': {'req': [8, 17, int(bits['b4_1']+bits['b4_3'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Ток.I A (А)': {'req': [8, 17, int(bits['b4_2']+bits['b4_1'],2)], 'res': ['mecury_08_11',1,-2,1000,False]},
                          'Меркурий236, Ток.I B (А)': {'req': [8, 17, int(bits['b4_2']+bits['b4_2'],2)], 'res': ['mecury_08_11',1,-2,1000,False]},
                          'Меркурий236, Ток.I C (А)': {'req': [8, 17, int(bits['b4_2']+bits['b4_3'],2)], 'res': ['mecury_08_11',1,-2,1000,False]},
                          'Меркурий236, Частота сети F (Гц)': {'req': [8, 17, int(bits['b4_4']+bits['b4_0'],2)], 'res': ['mecury_08_11',1,-2,100,False]},
                          'Меркурий236, Температура (°С)': {'req': [8, 17, int(bits['b4_7']+bits['b4_0'],2)], 'res': ['from_bytes',1,-2]},
                          'Меркурий236, Завершение сеанса.': {'req': [2], 'res': ['mecury_status']},
                          }

if __name__ == '__main__':
    debug = False
    modbus_reg = modbus_reg_Меркурий236
    SlaveID = [81] # Милур 255, Меркурий 81, WB-MR6LV 40, WB-MAP3E 32

    session = IP_485(ws_addr="ws://12.34.56.78:6432",timeout=1)
    #session = COM_485(port="COM3", baudrate=9600, bytesize=8, parity='N', stopbits=2, timeout=0.1)

    mb = Modbus(session=session,SlaveID=SlaveID,modbus_reg=modbus_reg,debug=debug)
    for description in [el for el in modbus_reg]:
        ret = mb.request_response(description=description)
        print(description,': ',ret,sep="")


