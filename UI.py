# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5.QtCore import QThread
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import workerrftth
from popup import Ui_Dialog as Form

from cryptography.fernet import Fernet

def getID(filename):
    key = b'-GOWU3mr5SmwcI0jGmb9BzXKzyCCiW2UvUQIsvF0LPk='
    crypto = Fernet(key)

    f = open(filename)
    content = f.readlines()
    f.close()
    return [crypto.decrypt(x.strip().encode()).decode("utf-8") for x in content]


def setID(ID, mdp, filename):
    key = b'-GOWU3mr5SmwcI0jGmb9BzXKzyCCiW2UvUQIsvF0LPk='
    crypto = Fernet(key)

    IDcrypted = crypto.encrypt(ID.encode())
    mdpcrypted = crypto.encrypt(mdp.encode())

    f = open(filename, "w")
    f.writelines(IDcrypted.decode("utf-8")  + "\n")
    f.writelines(mdpcrypted.decode("utf-8")  + "\n")
    f.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(383, 532)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 2, 0, 1, 2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.Effacer = QtWidgets.QPushButton(self.centralwidget)
        self.Effacer.setObjectName("Effacer")
        self.verticalLayout.addWidget(self.Effacer)
        self.gridLayout.addLayout(self.verticalLayout, 6, 1, 5, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.ValidResolution = QtWidgets.QPushButton(self.centralwidget)
        self.ValidResolution.setObjectName("ValidResolution")
        self.gridLayout_3.addWidget(self.ValidResolution, 6, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 8, 0, 1, 1)
        self.Afficher = QtWidgets.QPushButton(self.centralwidget)
        self.Afficher.setObjectName("Afficher")
        self.gridLayout_3.addWidget(self.Afficher, 9, 0, 1, 1)
        self.NumeroCasResolution = QtWidgets.QLineEdit(self.centralwidget)
        self.NumeroCasResolution.setObjectName("NumeroCasResolution")
        self.gridLayout_3.addWidget(self.NumeroCasResolution, 5, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setObjectName("label_7")
        self.gridLayout_3.addWidget(self.label_7, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 7, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 6, 0, 5, 1)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_9.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_9.setScaledContents(True)
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 11, 0, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.InputID = QtWidgets.QLineEdit(self.centralwidget)
        self.InputID.setObjectName("InputID")
        self.verticalLayout_4.addWidget(self.InputID)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.InputMdP = QtWidgets.QLineEdit(self.centralwidget)
        self.InputMdP.setObjectName("InputMdP")
        self.verticalLayout_4.addWidget(self.InputMdP)
        self.InputMdP.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ValidTechnicien = QtWidgets.QPushButton(self.centralwidget)
        self.ValidTechnicien.setObjectName("ValidTechnicien")
        self.verticalLayout_4.addWidget(self.ValidTechnicien)
        self.gridLayout.addLayout(self.verticalLayout_4, 3, 0, 1, 2)
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap("half logo afd .png"))
        self.label_10.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 2)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 383, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setTabOrder(self.InputID, self.InputMdP)
        MainWindow.setTabOrder(self.InputMdP, self.ValidTechnicien)
        MainWindow.setTabOrder(self.ValidTechnicien, self.NumeroCasResolution)
        MainWindow.setTabOrder(self.NumeroCasResolution, self.ValidResolution)
        MainWindow.setTabOrder(self.ValidResolution, self.textBrowser)
        MainWindow.setTabOrder(self.textBrowser, self.Effacer)

        self.InputID.setText(getID(filename)[0])
        self.InputMdP.setText(getID(filename)[1])
        self.ModifierClick(MainWindow)
        #self.ValiderResolution(MainWindow)
        self.EffacerClick(MainWindow)
        self.Afficher.clicked.connect(self.open_dialog)
        self.ValidResolution.clicked.connect(self.ValiderResolution)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Resolution FTTH"))
        self.Effacer.setText(_translate("MainWindow", "Effacer"))
        self.ValidResolution.setText(_translate("MainWindow", "Valider"))
        self.label_8.setText(_translate("MainWindow", "Afficher le logigramme"))
        self.Afficher.setText(_translate("MainWindow", "Afficher"))
        self.label_7.setText(_translate("MainWindow", "Numero de cas "))
        self.label_9.setText(_translate("MainWindow", "AFD.INNOVATION - VALES Antoine"))
        self.label_5.setText(_translate("MainWindow", "Resolution - FTTH"))
        self.label.setText(_translate("MainWindow", "ID"))
        self.label_2.setText(_translate("MainWindow", "MdP"))
        self.ValidTechnicien.setText(_translate("MainWindow", "Modifier"))
        self.label_3.setText(_translate("MainWindow", "Technicien"))

    def ModifierClick(self, MainWindow):
        self.ValidTechnicien.clicked.connect(
            lambda: setID(self.InputID.text(), self.InputMdP.text(), filename)
        )

    def ValiderResolution(self, MainWindow):
        #print(self.ChoixResolution.currentText())
        #if self.ChoixResolution.currentText() == "Mobile Voix - Voix ":
        #    print('RM selected')
        #    self.setupWorkerResolutionMobile(MainWindow)
        #elif self.ChoixResolution.currentText() == "FTTH":
        #    print('FTTH selectionné')
        self.setupWorkerResolutionFTTH(MainWindow)
        #    print('FTTH apres')

    def EffacerClick(self, MainWindow):
        self.Effacer.clicked.connect(lambda: self.textBrowser.clear())

    def setupWorkerResolutionFTTH(self, MainWindow):
        print('setupWorkerResolutionFTTH selectionné')
        # Worker(Combobox, Ntelephone, IDs)
        self.wrkr = workerrftth.WorkerResolutionFTTH(
            getID(filename),
        )
        self.thread = QThread()

        self.wrkr.SendFTTH.connect(self.UiListen)
        self.wrkr.finished.connect(self.thread.quit)
        self.wrkr.moveToThread(self.thread)
        # self.thread.started.connect(self.wrkr.resolution)

        self.thread.started.connect(self.wrkr.main)
        self.thread.start()

     # lecteur de worker
    def UiListen(self, i):
        if i != "KILL":
            self.ValidResolution.setEnabled(False)
            #self.ValidScan.setEnabled(False)
            self.textBrowser.append("{}".format(i))
        else:
            self.ValidResolution.setEnabled(True)
            #self.ValidScan.setEnabled(True)

    def open_dialog(self, MainWindow):
        height, width, img = self.selectionLogigramme(MainWindow)
        dialog = QtWidgets.QDialog()
        dialog.ui = Form()
        dialog.ui.setupUi(dialog)
        dialog.ui.label.setText("")
        dialog.resize(width, height)
        dialog.ui.label.setPixmap(QtGui.QPixmap(img))

        dialog.exec_()
        dialog.show()

    def selectionLogigramme(self, MainWindow):
        #☻if self.ChoixResolution.currentText() == "Mobile Voix - Voix ":
        #    img = "LogigrammeMobileVoixVoix.png"
        #if self.ChoixResolution.currentText() == "FTTH":
        img = "LogigrammeFTTH.png"
        # if self.ChoixResolution.currentText() == "Mobile Voix - MV888":
        #    img = "LogigrammeMobileVoixMV888.png"

        imgnp = cv2.imread(img)
        height, width, _ = imgnp.shape
        return height, width, img

if __name__ == "__main__":
    filename = "code_interne/connexion.txt"

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())