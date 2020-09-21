
from pydm.widgets.timeplot import PyDMTimePlot
from pydm import Display
import sys, time
import json
import random
import pyqtgraph as pg
from epics import PV
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread

class Window(Display):
    def __init__(self):
        super(Window, self).__init__(ui_filename='UI-HLS.ui')
        self.associatePvs()

        self.btn_initRack.clicked.connect(self.initRack_func)
        self.btn_startAcq.clicked.connect(self.startAcq_func)
        self.btn_stopAcq.clicked.connect(self.stopAcq_func)
        self.acq_spin.valueChanged.connect(self.set_t_aq)

        self.tableThread = TableThread (self)
        self.tableThread.signal.connect(self.updateTable)
        self.tableThread.start()

        self.checkPlots = [[self.check_R1S1L, self.check_R1S2L, self.check_R1S3L, self.check_R1S4L, self.check_R1S5L],
                           [self.check_R1S1T, self.check_R1S2T, self.check_R1S3T, self.check_R1S4T, self.check_R1S5T],
                           [self.check_R2S1L, self.check_R2S2L, self.check_R2S3L, self.check_R2S4L, self.check_R2S5L],
                           [self.check_R2S1T, self.check_R2S2T, self.check_R2S3T, self.check_R2S4T, self.check_R2S5T],
                           [self.check_R3S1L, self.check_R3S2L, self.check_R3S3L, self.check_R3S4L, self.check_R3S5L],
                           [self.check_R3S1T, self.check_R3S2T, self.check_R3S3T, self.check_R3S4T, self.check_R3S5T],
                           [self.check_R4S1L, self.check_R4S2L, self.check_R4S3L, self.check_R4S4L, self.check_R4S5L],
                           [self.check_R4S1T, self.check_R4S2T, self.check_R4S3T, self.check_R4S4T, self.check_R4S5T]]

        for check_outer in self.checkPlots:
            for check_inner in check_outer:
                check_inner.stateChanged.connect(self.updatePlot)
        
        #self.plot.setLabels(left='axis')
        
        self.p1 = self.plot.plotItem
        self.p1.setLabels(left='Level [mm]')

        self.p2 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.p1)
        self.p1.getAxis('right').setLabel('Temperature [C]') 

        self.updateViews()
        self.p1.vb.sigResized.connect(self.updateViews)

    def updateViews(self):
        ## view has resized; update auxiliary views to match
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        
        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis) 

    def isCurveAtPlot (self, name):
        i = 0
        for plotItem in self.plot.getCurves():
            data = json.loads(plotItem)
            if (name == data['name']):
                return [True, i]
            i+=1
        return [False, -1]
    

    def updatePlot (self):
        for i in range (8):
            for j in range (5):
                if (i % 2 == 0):
                    channel = self.data_levelPV[int(i/2)][j]
                    name = "R"+str(int((i+1)/2))+"-S"+str(int(j+1))+"-Level"
                    rightYAxis = False
                else:
                    channel = self.data_tempPV[int(i/2)][j]
                    name = "R"+str(int((i+1)/2))+"-S"+str(int(j+1))+"-Temp"
                    rightYAxis = True
                
                curveCheck = self.isCurveAtPlot(name)                
                
                if (self.checkPlots[i][j].isChecked() and not curveCheck[0]):
                    curve = self.plot.addYChannel(y_channel="ca://"+channel.pvname, name=name, color=QColor(random.uniform (0,255), random.uniform (0,255), random.uniform (0,255)))
                    self.plot.setTimeSpan(15)
                    self.plot.setUpdatesAsynchronously(True)
                    if (rightYAxis):                       
                        self.p2.addItem(curve)
                    print(self.plot.listDataItems())
                    #print(self.p2.listDataItems())
                elif (not self.checkPlots[i][j].isChecked() and curveCheck[0]):
                    self.plot.removeYChannelAtIndex(curveCheck[1])

        self.plot.setShowLegend(True)

        


    def updateTable (self):
        self.data_level = [[self.data_levelPV[0][0].get(), self.data_levelPV[0][1].get(), self.data_levelPV[0][2].get(), self.data_levelPV[0][3].get(), self.data_levelPV[0][4].get()],
                           [self.data_levelPV[1][0].get(), self.data_levelPV[1][1].get(), self.data_levelPV[1][2].get(), self.data_levelPV[1][3].get(), self.data_levelPV[1][4].get()],
                           [self.data_levelPV[2][0].get(), self.data_levelPV[2][1].get(), self.data_levelPV[2][2].get(), self.data_levelPV[2][3].get(), self.data_levelPV[2][4].get()],
                           [self.data_levelPV[3][0].get(), self.data_levelPV[3][1].get(), self.data_levelPV[3][2].get(), self.data_levelPV[3][3].get(), self.data_levelPV[3][4].get()]]

        self.data_temp = [[self.data_tempPV[0][0].get(), self.data_tempPV[0][1].get(), self.data_tempPV[0][2].get(), self.data_tempPV[0][3].get(), self.data_tempPV[0][4].get()],
                          [self.data_tempPV[1][0].get(), self.data_tempPV[1][1].get(), self.data_tempPV[1][2].get(), self.data_tempPV[1][3].get(), self.data_tempPV[1][4].get()],
                          [self.data_tempPV[2][0].get(), self.data_tempPV[2][1].get(), self.data_tempPV[2][2].get(), self.data_tempPV[2][3].get(), self.data_tempPV[2][4].get()],
                          [self.data_tempPV[3][0].get(), self.data_tempPV[3][1].get(), self.data_tempPV[3][2].get(), self.data_tempPV[3][3].get(), self.data_tempPV[3][4].get()]]

        for i in range (4):
            for j in range (5):
                item1 = QtWidgets.QTableWidgetItem(str('%.3f' % self.data_level[i][j]))
                item1.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                item2 = QtWidgets.QTableWidgetItem(str('%.3f' % self.data_temp[i][j]))
                item2.setFlags(Qt.ItemIsDragEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled)
                self.data_table.setItem(i*2, j, item1)
                self.data_table.setItem(i*2+1, j, item2)

    
    def associatePvs (self):
        self.cmdPV = PV('cmd')
        self.acqPV = PV('acq_time')
        self.rack_state = [PV('state_rack1'), PV('state_rack2'), PV('state_rack3'), PV('state_rack4')]
        self.data_levelPV = [[PV('HLS:R1_S1_L'), PV('HLS:R1_S2_L'), PV('HLS:R1_S3_L'), PV('HLS:R1_S4_L'), PV('HLS:R1_S5_L')],
                           [PV('HLS:R2_S1_L'), PV('HLS:R2_S2_L'), PV('HLS:R2_S3_L'), PV('HLS:R2_S4_L'), PV('HLS:R2_S5_L')],
                           [PV('HLS:R3_S1_L'), PV('HLS:R3_S2_L'), PV('HLS:R3_S3_L'), PV('HLS:R3_S4_L'), PV('HLS:R3_S5_L')],
                           [PV('HLS:R4_S1_L'), PV('HLS:R4_S2_L'), PV('HLS:R4_S3_L'), PV('HLS:R4_S4_L'), PV('HLS:R4_S5_L')]]
        self.data_tempPV = [[PV('HLS:R1_S1_T'), PV('HLS:R1_S2_T'), PV('HLS:R1_S3_T'), PV('HLS:R1_S4_T'), PV('HLS:R1_S5_T')],
                          [PV('HLS:R2_S1_T'), PV('HLS:R2_S2_T'), PV('HLS:R2_S3_T'), PV('HLS:R2_S4_T'), PV('HLS:R2_S5_T')],
                          [PV('HLS:R3_S1_T'), PV('HLS:R3_S2_T'), PV('HLS:R3_S3_T'), PV('HLS:R3_S4_T'), PV('HLS:R3_S5_T')],
                          [PV('HLS:R4_S1_T'), PV('HLS:R4_S2_T'), PV('HLS:R4_S3_T'), PV('HLS:R4_S4_T'), PV('HLS:R4_S5_T')]]
    
    def verifyRackState (self):
        current_state = [self.rack_state[0].get(), self.rack_state[1].get(), self.rack_state[2].get(), self.rack_state[3].get()]

        if (self.en_rack1.isChecked()):
            if(current_state[0] == -1):
                self.led_rack1.brush.setColor (Qt.yellow)
                self.led_rack1.update()
            elif (current_state[0] == -2):
                self.led_rack1.brush.setColor (Qt.red)
                self.led_rack1.update()
            else:
                self.led_rack1.brush.setColor (Qt.green)
                self.led_rack1.update()
        if (self.en_rack2.isChecked()):
            if(current_state[1] == -1):
                self.led_rack2.brush.setColor (Qt.yellow)
                self.led_rack2.update()
            elif (current_state[1] == -2):
                self.led_rack2.brush.setColor (Qt.red)
                self.led_rack2.update()
            else:
                self.led_rack2.brush.setColor (Qt.green)
                self.led_rack2.update()
        if (self.en_rack3.isChecked()):
            if(current_state[2] == -1):
                self.led_rack3.brush.setColor (Qt.yellow)
                self.led_rack3.update()
            elif (current_state[2] == -2):
                self.led_rack3.brush.setColor (Qt.red)
                self.led_rack3.update()
            else:
                self.led_rack3.brush.setColor (Qt.green)
                self.led_rack3.update()
        if (self.en_rack4.isChecked()):
            if(current_state[3] == -1):
                self.led_rack4.brush.setColor (Qt.yellow)
                self.led_rack4.update()
            elif (current_state[3] == -2):
                self.led_rack4.brush.setColor (Qt.red)
                self.led_rack4.update()
            else:
                self.led_rack1.brush.setColor (Qt.green)
                self.led_rack1.update()
 

    def initRack_func (self):
        current_cmd = self.cmdPV.get()
        if(current_cmd == -1):
             self.cmdPV.put(1)
        self.verifyRackState()


    def startAcq_func (self):
        current_cmd = self.cmdPV.get()
        if(current_cmd == -1):
             self.cmdPV.put(2)

    def stopAcq_func (self):
        current_cmd = self.cmdPV.get()
        self.cmdPV.put(3)

    def set_t_aq (self):
        t_aq = self.acq_spin.value()
        self.acqPV.put(int(t_aq))



class TableThread(QThread):
    signal = pyqtSignal()
    def __init__(self, parent):
        QObject.__init__(self)
        QThread.__init__(self, parent)

    def callback(self):
        self._stop()

    def run(self):
        while(1):
            self.signal.emit()
            time.sleep(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
