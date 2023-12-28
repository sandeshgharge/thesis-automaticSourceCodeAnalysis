import sys
import subprocess, os, shlex, json


from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from projectObject import ProjectData
from listmodel import TableModel
import pandas as pd
import pyjslint as jslint
import requests

GIT_LAB_URL = "https://mygit.th-deg.de/api/v4"

class AnalyserWindow(QDialog):
    closed = pyqtSignal(ProjectData, int)
    def __init__(self, data, index):

        super(AnalyserWindow, self).__init__()
        self.setWindowTitle("Analysis and Report")
        self.stuObj : ProjectData
        self.stuObj = data
        self.i = index
        self.resize(600,600)
        self.initUI()
        return
    
    def initUI(self):

        ## Display name of the student        
        self.projectName = QLabel(self)
        self.projectName.setText(self.stuObj.studentName)
        ## Display name of the student end

        ## Highlighting Name of the student
        lblStyle = QFont()
        lblStyle.setBold(True)
        lblStyle.setItalic(True)
        self.projectName.setFont(lblStyle)
        ## Highlighting Name of the student end

        # Analysed window design

        ## self.checkJSFiles()

        analysedData = json.loads(subprocess.run(shlex.split('pygount --format=json ' + self.stuObj.dirPath), capture_output=True).stdout.decode("utf-8"))
        dispData = []
        for lang in analysedData['languages']:
            dispData.append(
                [
                    lang['language'],
                    lang['fileCount'],
                    lang['sourceCount'],
                    lang['documentationCount']
                ]
            )
        self.df = pd.DataFrame(dispData,
            columns= ['Type of Language', 'No of Files', 'No of Lines', 'No of Comments']
        )

        self.tbl = TableModel(self.df)
        self.dispData = QTableView()
        self.dispData.verticalHeader().hide()
        self.dispData.setColumnWidth(0, 500)
        self.dispData.resize(200, 400)

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.tbl)
        self.dispData.setSortingEnabled(True)
        self.dispData.setModel(self.proxyModel)

        self.remarks = QTextEdit(self)
        self.remarks.setPlaceholderText("Remarks")
        self.remarks.setText(self.stuObj.remark)

        self.analysedLayout = QVBoxLayout(self)
        self.analysedLayout.addWidget(self.dispData)
        # Analysed window design end

        # Grading Window Design for different category
        self.cat1 = QLabel()
        self.cat1.setText("Code")

        self.cat2 = QLabel()
        self.cat2.setText("Comments")

        self.cat3 = QLabel()
        self.cat3.setText("Documentation")

        self.cbcat1 = QComboBox()
        self.cbcat1.addItems(["Select","1","2","3","4","5"])
        self.cbcat1.setCurrentIndex(self.stuObj.grades.code)

        self.cbcat2 = QComboBox()
        self.cbcat2.addItems(["Select","1","2","3","4","5"])
        self.cbcat2.setCurrentIndex(self.stuObj.grades.comments)


        self.cbcat3 = QComboBox()
        self.cbcat3.addItems(["Select","1","2","3","4","5"])
        self.cbcat3.setCurrentIndex(self.stuObj.grades.documentation)

        self.catLayout = QGridLayout(self)
        self.catLayout.addWidget(self.cat1, 0, 0)
        self.catLayout.addWidget(self.cat2, 1, 0)
        self.catLayout.addWidget(self.cat3, 2, 0)

        self.catLayout.addWidget(self.cbcat1, 0, 1)
        self.catLayout.addWidget(self.cbcat2, 1, 1)
        self.catLayout.addWidget(self.cbcat3, 2, 1)
        # Grading Window Design for different category end

        # De Register Window

        self.deRegL = QVBoxLayout()

        self.userId = QLineEdit(self)
        self.userId.setPlaceholderText("Enter User ID")

        self.projId = QLineEdit(self)
        self.projId.setPlaceholderText("Enter Proj ID")
        
        self.deReg = QPushButton(self)
        self.deReg.setText("Click here to De Register from this project")
        self.deReg.clicked.connect(self.deRegister)
        self.deRegWarning = QLabel()
        self.deRegWarning.setText("Once De registered, you will loose all the access to project. This step cannot be reverted")
        
        self.deRegL.addWidget(self.userId)
        self.deRegL.addWidget(self.projId)
        self.deRegL.addWidget(self.deReg)
        self.deRegL.addWidget(self.deRegWarning)

        # De Register Window end

        # Lint Analysis tab

        self.la = QTextEdit(self)
        self.la.setPlaceholderText("Analysis")
        self.analyseFiles()
        self.la.setText(self.lintData)

        self.lalayout = QHBoxLayout()
        self.lalayout.addWidget(self.la)

        # Line Analysis tab end

        ## Tab Widget initialisation
        self.tab = QTabWidget()
        self.analysedData = QWidget()
        self.grades = QWidget()
        self.dReg = QWidget()
        self.lintAnalysis = QWidget()
        ## Tab Widget initialisation end

        ## Tab widget add layout

        self.analysedData.setLayout(self.analysedLayout)
        self.grades.setLayout(self.catLayout)
        self.dReg.setLayout(self.deRegL)
        self.lintAnalysis.setLayout(self.lalayout)
        
        self.tab.addTab(self.analysedData, "Analysed Data")
        self.tab.addTab(self.lintAnalysis, "Lint Analysis")
        self.tab.addTab(self.grades, "Grading")
        self.tab.addTab(self.dReg, "De Register")

        ## Tab widget add layout end

        # Action button layout

        self.save = QPushButton("Save",self)
        self.save.clicked.connect(self.saveData)
        self.closeBtn = QPushButton("Close", self)
        self.closeBtn.clicked.connect(self.closeAndEmitData)

        self.actionLayout = QHBoxLayout()
        self.actionLayout.addWidget(self.save)
        self.actionLayout.addWidget(self.closeBtn)

        # Action button end

        # Designing final Layout

        self.ml = QVBoxLayout()
        self.ml.addWidget(self.projectName)
        self.ml.addWidget(self.tab)
        self.ml.addWidget(self.remarks)
        self.ml.addLayout(self.actionLayout)

        # Designing final Layout end

        self.setLayout(self.ml)

        
        return
    
    def checkJSFiles(self):
        for file in self.stuObj.srcFiles:
            if file.split('.')[-1].lower() == 'js':
                with open(file, 'r') as file:
                    js_code = file.read()
                    print(jslint.check_JSLint(js_code))
            
        return
    
    def analyseFiles(self):
        self.lintData = ""
        for file in self.stuObj.srcFiles:
            ext = file.split('.')[-1].lower()
            print(file)
            if ext == 'js' and False:
                with open(file, 'r') as f:
                    js_code = f.read()
                    print(jslint.check_JSLint(js_code))
            elif ext == 'py':
                d = subprocess.run(shlex.split('pylint '+ file), capture_output=True).stdout.decode("utf-8")
                self.lintData = self.lintData + ' \n ' + d
        return
    
    def closeAndEmitData(self):
        self.closed.emit(self.stuObj, self.i)
        super().accept()
        return
    
    def saveData(self):
        self.stuObj.grades.code = self.cbcat1.currentIndex()
        self.stuObj.grades.comments = self.cbcat2.currentIndex()
        self.stuObj.grades.documentation = self.cbcat3.currentIndex()
        self.stuObj.grades.calAvgGrade()

        print(self.stuObj.grades.avgGrade)

        self.stuObj.remark = self.remarks.toPlainText()
        return
    
    def deRegister(self):

        if self.stuObj.accessToken == "":
            QMessageBox.information(self, "Token Unavailable", "Please Enter the token on main window and re open this window")
            return

        uId = self.userId.text()
        pId = self.projId.text()
        deReg_Url = GIT_LAB_URL+"/projects/"+ pId +"/members/" + uId
        print(deReg_Url)

        headers = {
            "PRIVATE-TOKEN": self.stuObj.accessToken,
            "Content-Type": "application/json"  # You can adjust this header based on your API requirements
        }

        response = requests.delete(deReg_Url, headers=headers)
        print(response.status_code)

        if response.status_code == 204:
            QMessageBox.information(self, "De Registration Status", "The project has been successfully de registered.")
            
        elif response.status_code == 404:
           resData = json.loads(response.text)
           QMessageBox.critical(self, "De Registration Status", resData["message"])

        return

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlgMain = AnalyserWindow()
    dlgMain.show()
    sys.exit(app.exec())