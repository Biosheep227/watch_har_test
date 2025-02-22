# coding:UTF-8
import time
from lib.protocol_resolver.interface.i_protocol_resolver import IProtocolResolver

"""
    维特协议解析器
"""

class WitProtocolResolver(IProtocolResolver):
    TempBytes=[]         # 临时数据列表
    PackSize = 11        # 一包数据大小
    gyroRange = 2000.0   # 角速度量程
    accRange = 16.0      # 加速度量程
    angleRange = 180.0   # 角度量程
    TempFindValues=[]    # 读取指定寄存器返回的数据

    def setConfig(self, deviceModel):
        pass

    def sendData(self, sendData, deviceModel):
        success_bytes = deviceModel.serialPort.write(sendData)
    def passiveReceiveData(self, data, deviceModel):
        """
        接收数据处理
        :param data: 串口数据
        :param deviceModel: 设备模型
        :return:
        """
        global TempBytes
        for val in data:
            self.TempBytes.append(val)
            if (self.TempBytes[0]!=0x55):                   #非标识符0x55开头的
                del self.TempBytes[0]                       #去除第一个字节
                continue
            if (len(self.TempBytes)>1):
                if (((self.TempBytes[1] - 0x51 >=0 and self.TempBytes[1] - 0x51 <=11) or self.TempBytes[1]==0x53)==False):   #第二个字节数值不在0x51~0x53范围或者不等于0x5f
                    del self.TempBytes[0]                   #去除第一个字节
                    continue
            if (len(self.TempBytes) == self.PackSize):      #表示一个包的数据大小
                CheckSum = 0                                #求和校验位
                for i in range(0,self.PackSize-1):
                    CheckSum+=self.TempBytes[i]
                if (CheckSum&0xff==self.TempBytes[self.PackSize-1]):  #校验和通过
                    if (self.TempBytes[1]==0x51):                    #加速度包
                        self.get_acc(self.TempBytes,deviceModel)       #结算加速度数据
                    elif(self.TempBytes[1]==0x52):                    #角速度包
                        self.get_gyro(self.TempBytes,deviceModel)     #结算角速度数据
                    elif(self.TempBytes[1]==0x53):                    #角度包
                        self.get_angle(self.TempBytes,deviceModel)    #结算角度数据
                        deviceModel.dataProcessor.onUpdate(deviceModel) #触发数据更新事件
                    self.TempBytes=[]                        #清除数据
                else:                                        #校验和未通过
                    del self.TempBytes[0]                    # 去除第一个字节

    def get_readbytes(self,regAddr):
        """
        获取读取的指令
        :param regAddr: 寄存器地址
        :return:
        """
        return [0xff, 0xaa,0x27, regAddr & 0xff, regAddr >> 8]

    def get_writebytes(self,regAddr):
        """
        获取写入的指令
        :param regAddr: 寄存器地址
        :param sValue: 写入的值
        :return:
        """
        return [0xff, 0xaa, regAddr,regAddr  & 0xff, regAddr >> 8]

    def get_acc(self,datahex, deviceModel):
        """
        加速度、温度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        axl = datahex[2]
        axh = datahex[3]
        ayl = datahex[4]
        ayh = datahex[5]
        azl = datahex[6]
        azh = datahex[7]

        tempVal = (datahex[9] << 8 | datahex[8])
        acc_x = (axh << 8 | axl) / 32768.0 * self.accRange
        acc_y = (ayh << 8 | ayl) / 32768.0 * self.accRange
        acc_z = (azh << 8 | azl) / 32768.0 * self.accRange
        if acc_x >= self.accRange:
            acc_x -= 2 * self.accRange
        if acc_y >= self.accRange:
            acc_y -= 2 * self.accRange
        if acc_z >= self.accRange:
            acc_z -= 2 * self.accRange

        deviceModel.setDeviceData("accX", round(acc_x, 4))     # 设备模型加速度X赋值
        deviceModel.setDeviceData("accY", round(acc_y, 4))     # 设备模型加速度Y赋值
        deviceModel.setDeviceData("accZ", round(acc_z, 4))     # 设备模型加速度Z赋值
        temperature = round(tempVal / 32768 * 96.38 + 36.53, 2)                                           # 温度结算,并保留两位小数
        deviceModel.setDeviceData("temperature", temperature)                             # 设备模型温度赋值

    def get_gyro(self,datahex, deviceModel):
        """
        角速度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        wxl = datahex[2]
        wxh = datahex[3]
        wyl = datahex[4]
        wyh = datahex[5]
        wzl = datahex[6]
        wzh = datahex[7]

        gyro_x = (wxh << 8 | wxl) / 32768.0 * self.gyroRange
        gyro_y = (wyh << 8 | wyl) / 32768.0 * self.gyroRange
        gyro_z = (wzh << 8 | wzl) / 32768.0 * self.gyroRange
        if gyro_x >= self.gyroRange:
            gyro_x -= 2 * self.gyroRange
        if gyro_y >= self.gyroRange:
            gyro_y -= 2 * self.gyroRange
        if gyro_z >= self.gyroRange:
            gyro_z -= 2 * self.gyroRange

        deviceModel.setDeviceData("gyroX", round(gyro_x, 4))  # 设备模型角速度X赋值
        deviceModel.setDeviceData("gyroY", round(gyro_y, 4))  # 设备模型角速度Y赋值
        deviceModel.setDeviceData("gyroZ", round(gyro_z, 4))  # 设备模型角速度Z赋值

    def get_angle(self,datahex, deviceModel):
        """
        角度结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        rxl = datahex[2]
        rxh = datahex[3]
        ryl = datahex[4]
        ryh = datahex[5]
        rzl = datahex[6]
        rzh = datahex[7]

        angle_x = (rxh << 8 | rxl) / 32768.0 * self.angleRange
        angle_y = (ryh << 8 | ryl) / 32768.0 * self.angleRange
        angle_z = (rzh << 8 | rzl) / 32768.0 * self.angleRange
        if angle_x >= self.angleRange:
            angle_x -= 2 * self.angleRange
        if angle_y >= self.angleRange:
            angle_y -= 2 * self.angleRange
        if angle_z >= self.angleRange:
            angle_z -= 2 * self.angleRange

        deviceModel.setDeviceData("angleX", round(angle_x, 3))  # 设备模型角度X赋值
        deviceModel.setDeviceData("angleY", round(angle_y, 3))  # 设备模型角度Y赋值
        deviceModel.setDeviceData("angleZ", round(angle_z, 3))  # 设备模型角度Z赋值



    def readReg(self, regAddr,regCount, deviceModel):
        """
        读取寄存器
        :param regAddr: 寄存器地址
        :param regCount: 寄存器个数
        :param deviceModel: 设备模型
        :return:
        """
        tempResults = []                      #返返数据
        readCount = int(regCount/4)           #根据寄存器个数获取读取次数
        if (regCount % 4>0):
            readCount+=1
        for n in range(0,readCount):
            self.TempFindValues = []  # 清除数据
            tempBytes = self.get_readbytes(regAddr + n * 4)             # 获取读取的指令
            success_bytes = deviceModel.serialPort.write(tempBytes)     #写入数据
            for i in range(0,20): #设置超时1秒
                time.sleep(0.05)  # 休眠50毫秒
                # time.sleep(1)  # 休眠1000毫秒
                if (len(self.TempFindValues)>0):    #已返回所找查的寄存器的值
                    for j in range(0,len(self.TempFindValues)):
                        if (len(tempResults) < regCount):
                            tempResults.append(self.TempFindValues[j])
                        else:
                            break
                    break
        return tempResults

    def writeReg(self, regAddr, deviceModel):
        """
        写入寄存器
        :param regAddr: 寄存器地址
        :param sValue: 写入值
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(regAddr)                  #获取写入指令
        success_bytes = deviceModel.serialPort.write(tempBytes)          #写入寄存器
        time.sleep(3)
    def unlock(self, deviceModel):
        """
        解锁
        :return:
        """
        tempBytes = self.get_writebytes(0x69, 0xb588)                    #获取写入指令
        success_bytes = deviceModel.serialPort.write(tempBytes)          #写入寄存器

    def save(self, deviceModel):
        """
        保存
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(0x00, 0x00)                      #获取写入指令
        success_bytes = deviceModel.serialPort.write(tempBytes)          #写入寄存器

    def AccelerationCalibration(self,deviceModel):
        """
        加计校准
        :param deviceModel: 设备模型
        :return:
        """
        tempBytes = self.get_writebytes(0x67)                      # 获取写入指令
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器
        time.sleep(5.5)                                                  # 休眠5500毫秒

    def BeginFiledCalibration(self,deviceModel):
        """
        开始磁场校准
        :param deviceModel: 设备模型
        :return:
        """
        self.unlock(deviceModel)                                         # 解锁
        time.sleep(0.1)                                                  # 休眠100毫秒
        tempBytes = self.get_writebytes(0x01, 0x07)                      # 获取写入指令 磁场校准
        success_bytes = deviceModel.serialPort.write(tempBytes)          # 写入寄存器


    def EndFiledCalibration(self,deviceModel):
        """
        结束磁场校准
        :param deviceModel: 设备模型
        :return:
        """
        self.unlock(deviceModel)                                         # 解锁
        time.sleep(0.1)                                                  # 休眠100毫秒
        self.save(deviceModel)                                           #保存

    def get_find(self,datahex, deviceModel):
        """
        读取指定寄存器结算
        :param datahex: 原始始数据包
        :param deviceModel: 设备模型
        :return:
        """
        t0l = datahex[2]
        t0h = datahex[3]
        t1l = datahex[4]
        t1h = datahex[5]
        t2l = datahex[6]
        t2h = datahex[7]
        t3l = datahex[8]
        t3h = datahex[9]

        val0 = (t0h << 8 | t0l)
        val1 = (t1h << 8 | t1l)
        val2 = (t2h << 8 | t2l)
        val3 = (t3h << 8 | t3l)
        self.TempFindValues.extend([val0,val1,val2,val3])