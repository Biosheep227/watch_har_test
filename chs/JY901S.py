# coding:UTF-8
"""
    测试文件
    Test file
"""
import time
import datetime
import platform
import struct
import lib.device_model as deviceModel
from lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from lib.protocol_resolver.roles.wit_protocol_resolver import WitProtocolResolver

welcome = """
欢迎使用维特智能示例程序    Welcome to the Wit-Motoin sample program
"""
_writeF = None                  #写文件  Write file
_IsWriteF =False                #写文件标识    Write file identification


def setConfig(device):
    """
    设置配置信息示例    Example setting configuration information
    :param device: 设备模型 Device model
    :return:
    """
    device.writeReg(0x52)       # 设置Z轴角度归零
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x66)       # 设置安装方向:垂直
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x65)       # 设置安装方向:水平
    time.sleep(0.1)                # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x63)  # 设置波特率:115200  设置后，等待三秒，数据是不会回传回来的，需要去切换下面对应的波特率，重新运行程序
    time.sleep(0.1)  # 休眠100毫秒    Sleep 100ms
    device.writeReg(0x64)  # 设置波特率:9600    设置后，等待三秒，数据是不会回传回来的，需要去切换下面对应的波特率，重新运行程序
    time.sleep(0.1)  # 休眠100毫秒    Sleep 100ms

def AccelerationCalibration(device):
    """
    加计校准    Acceleration calibration
    :param device: 设备模型 Device model
    :return:
    """
    device.AccelerationCalibration()                 # Acceleration calibration
    print("加计校准结束")


def onUpdate(deviceModel):
    """
    数据更新事件  Data update event
    :param deviceModel: 设备模型    Device model
    :return:
    """
    print(
          # " temp:" + str(deviceModel.getDeviceData("temperature"))
          " acc：" + str(deviceModel.getDeviceData("accX")) +","+  str(deviceModel.getDeviceData("accY")) +","+ str(deviceModel.getDeviceData("accZ"))
         ,  " gyro:" + str(deviceModel.getDeviceData("gyroX")) +","+ str(deviceModel.getDeviceData("gyroY")) +","+ str(deviceModel.getDeviceData("gyroZ"))
         , " angle:" + str(deviceModel.getDeviceData("angleX")) +","+ str(deviceModel.getDeviceData("angleY")) +","+ str(deviceModel.getDeviceData("angleZ"))

          )
    if (_IsWriteF):    #记录数据    Record data
        Tempstr = " "
        Tempstr += "\t"+str(deviceModel.getDeviceData("accX")) + "\t"+str(deviceModel.getDeviceData("accY"))+"\t"+ str(deviceModel.getDeviceData("accZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("gyroX")) +"\t"+ str(deviceModel.getDeviceData("gyroY")) +"\t"+ str(deviceModel.getDeviceData("gyroZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("angleX")) +"\t" + str(deviceModel.getDeviceData("angleY")) +"\t"+ str(deviceModel.getDeviceData("angleZ"))
        Tempstr += "\t" + str(deviceModel.getDeviceData("temperature"))
        Tempstr += "\r\n"
        _writeF.write(Tempstr)

def startRecord():
    """
    开始记录数据  Start recording data
    :return:
    """
    global _writeF
    global _IsWriteF
    _writeF = open(str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ".txt", "w")    #新建一个文件
    _IsWriteF = True                                                                        #标记写入标识
    Tempstr = " "
    Tempstr +=  "\tax(g)\tay(g)\taz(g)"
    Tempstr += "\twx(deg/s)\twy(deg/s)\twz(deg/s)"
    Tempstr += "\tAngleX(deg)\tAngleY(deg)\tAngleZ(deg)"
    Tempstr += "\tT(°)"
    Tempstr += "\r\n"
    _writeF.write(Tempstr)
    print("开始记录数据")

def endRecord():
    """
    结束记录数据  End record data
    :return:
    """
    global _writeF
    global _IsWriteF
    _IsWriteF = False             # 标记不可写入标识    Tag cannot write the identity
    _writeF.close()               #关闭文件 Close file
    print("结束记录数据")

if __name__ == '__main__':

    print(welcome)
    """
    初始化一个设备模型   Initialize a device model
    """
    device = deviceModel.DeviceModel(
        "我的JY901",
        WitProtocolResolver(),
        JY901SDataProcessor(),
        "51_0"
    )

    if (platform.system().lower() == 'linux'):
        device.serialConfig.portName = "/dev/cu.usbserial-1140"   #设置串口   Set serial port
    else:
     device.serialConfig.portName = "/dev/cu.usbserial-1140"          #设置串口   Set serial port
    device.serialConfig.baud = 115200                    #设置波特率  Set baud rate
    device.openDevice()                                 #打开串口   Open serial port
   # device.AccelerationCalibration()  # Acceleration calibration
   # print("加计校准结束")
   # device.writeReg(0x52)     #设置z轴角度归零
   # device.writeReg(0x65)  # 设置安装方向:水平
   # device.writeReg(0x66)  # 设置安装方向:垂直
   # device.writeReg(0x63)  # 设置波特率:115200
   # device.writeReg(0x64)  # 设置波特率:9600
    device.dataProcessor.onVarChanged.append(onUpdate)  #数据更新事件 Data update event

'''
    startRecord()                                       # 开始记录数据    Start recording data
    input()
    device.closeDevice()
    endRecord()                                         #结束记录数据 End record data

'''
