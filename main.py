""" Application to analyse Submissions of students
"""
import shutil
import sys
import os
from pathlib import Path
# from marko import Markdown
# import dload
import re

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QSortFilterProxyModel
# from PyQt6.QtCore import Qt, QSize

from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHeaderView,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSplitter,
    QTextEdit,
    QWidget
)

from PyQt6.QtGui import QAction, QIcon, QKeySequence #, QScreen

import pandas as pd
# file with table model
from listmodel import TableModel
from analyserWindow import AnalyserWindow
from projectObject import ProjectData

# global Vars
APPTITLE = 'Submissions Check - Analyse Student Projects'
"""
Unpack the ZIP-archive
to subdir outputDir
Dir-structure
subcheck1
subcheck1/data
subcheck1/data/<courseName>
subcheck1/data/<courseName>/outputDir
"""
dataDir = './data/'
outDir = 'outputDir' # in currWorkingDir
courseName = 'mit-ws-22-23' # e.g. mit-ws-22-23, input by textedit
currWorkingDir = '' # dataDir + courseName, dir made by Hand ?
srcFilesTypes = ["java", "ts", "js", "html", "css", "scss", "py"]
zipFileName = ''
processedFiles = []
# global report file
reportfile = None
reportfilename = ''
# FILES will be shown and processed!
FILES = True
stname = ''

# start with an empty frame
studentData = []
projData : ProjectData = ProjectData()
lstProjData = []
# global functions

# changed to pathlib
def listdir(path):
    dirs, files, links = [], [], []
    d = Path(path)
    for entry in d.iterdir():
        # path_name = os.path.join(path, name)
        if entry.is_dir():
            dirs.append(str(entry))
        elif entry.is_file():
            files.append(str(entry))
        elif entry.is_symlink():
            links.append(str(entry))
    return dirs, files, links

""" the ZIP file of a submission of Moodle contains subdirectories
with firstname lastname as beginning of the dir name
"""
def getStudentNameFromDirName(dn):
    print('Get Student\'s name from: ' + dn)
    # split the full dir name, get last part, Windows specific!?
    # lastdirpart = dn.split('\\')[-1]
    lastdirpart = dn.split(os.sep)[-1]
    # from filename with _ separators get first part, which is the name
    namepart = lastdirpart.split('_')[0]
    # get first and last name from namepart
    if namepart.find(' ') != -1:
        firstname, lastname = namepart.split(' ', 1) # process at most 2 parts of a name
        global stname
        stname = lastname + ", " + firstname
    print("stname: " + stname)

def getNameFromReadME(fn):    
    try:
        with open(fn, "r") as readme_file:
            first_line = readme_file.readline()
            print(first_line)
    except FileNotFoundError:
        print(f"File not found: {fn}")
    except PermissionError:
        print(f"Permission denied to read file: {fn}")
    return first_line

def enumerate2(sequence):
    length = len(sequence)
    for count, value in enumerate(sequence):
        yield count, count - length, value

# see https://www.pythonguis.com/tutorials/pyqt6-qtableview-modelviews-numpy-pandas/

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        global studentData
            
        self.table = QtWidgets.QTableView()
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        """
        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # .Stretch to Maximu
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        """
        self.df = pd.DataFrame(studentData, columns = ['Name', 'Grades', 'File', 'Link1', 'Link2', 'Link3'])
            
        """
            [
          [1, 9, 2],
          [1, 0, -1],
          [3, 5, 2],
          [3, 3, 2],
          [5, 8, 9],
          ]
        """
        #, columns = ['Name', 'File', 'C']) # , index=['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5']
        self.model = TableModel(self.df)
        # for sorting
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.setModel(self.proxyModel)
        self.table.setColumnWidth(0, 20)
        self.table.setColumnWidth(1, 10)
        self.table.setColumnWidth(2, 20)
        self.table.setColumnWidth(3, 20)
        self.table.setColumnWidth(4, 20)
        self.table.setColumnWidth(5, 20)
        
        self.initUI()

    def initUI(self):
        
        global APPTITLE, courseName
        
        # 3 frames: 
        # One fixed for data like course name etc.
        # One flexible for the table with panda data
        # One flexible for file list and content
        
        # ?
        # frFixedData = QFrame(self)
        # frFixedData.setFrameShape(QFrame.Shape.StyledPanel)
        
        # TextEdit for coursename default courseName ?
        self.labCourseName = QLabel(self)
        self.labCourseName.setText("Course Name (used for output dir): ")
        
        self.leCourseName = QLineEdit(self)
        self.leCourseName.setText(courseName)

        self.courseNameLayout = QHBoxLayout(self)
        self.courseNameLayout.addWidget(self.labCourseName)
        self.courseNameLayout.addWidget(self.leCourseName)

        self.labToken = QLabel(self)
        self.labToken.setText("Gitlab Access Token: ")

        
        self.leToken = QLineEdit(self)
        self.leToken.setPlaceholderText("Enter Gitlab Token. (Necessary only if internet is available for project deregistration)")
        self.leToken.setEchoMode(QLineEdit.EchoMode.Password)

        self.tokenLayout = QHBoxLayout(self)
        self.tokenLayout.addWidget(self.labToken)
        self.tokenLayout.addWidget(self.leToken)
        
        # Label to display working directory
        self.labWorkingDir = QLabel(self)
        self.labWorkingDir.setText("Working Directory: " + dataDir)

        
        frTableData = QFrame(self)
        frTableData.setFrameShape(QFrame.Shape.StyledPanel)
        # Projects data table
        # layout.addWidget(self.table)
        
        ## add click signal to table
        self.table.clicked.connect(self.tabClicked)
        self.table.doubleClicked.connect(self.openAnalyserWindow)
        
        # Text Editor
        # frEditor = QFrame(self)
        # frEditor.setFrameShape(QFrame.Shape.StyledPanel)
        self.teProject = QTextEdit()
        
        # layout.addWidget(self.teProject)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(frTableData)
        splitter.addWidget(self.table) # so that table is visible!
        # splitter.addWidget(frEditor)
        splitter.addWidget(self.teProject)
        splitter.setStretchFactor(1, 1)
        # splitter.setSizes([125, 150])
        # VBoxLayout
        layout = QVBoxLayout()
        layout.addLayout(self.courseNameLayout)
        layout.addLayout(self.tokenLayout)
        layout.addWidget(self.labWorkingDir)
        layout.addWidget(splitter)
        
        # Menu
        # First action load iLearn ZIP
        # icons are in dir icons
        iconsDir = "icons/"
        button_load = QAction(QIcon(iconsDir + "notebook--plus.png"), "&Load iLearn ZIP", self)
        button_load.setStatusTip("Load ZIP with submission data")
        # You can enter keyboard shortcuts using key names (e.g. Ctrl+p)
        # Qt.namespace identifiers (e.g. Qt.CTRL + Qt.Key_P)
        # or system agnostic identifiers (e.g. QKeySequence.Print)
        button_load.setShortcut(QKeySequence("Ctrl+o"))
        button_load.triggered.connect(self.loadiLearnZIP)
        # Second action process
        """
        button_process = QAction(QIcon(iconsDir + "processor.png"), "&Process Projects", self)
        button_process.setStatusTip("Process Projects")
        button_process.setShortcut(QKeySequence("Ctrl+p"))
        button_process.triggered.connect(self.processProjects)
        button_process.setCheckable(True)
        """
        # Third action save
        button_save = QAction(QIcon(iconsDir + "store.png"), "&Save Overview Report", self)
        button_save.setStatusTip("Save Overview Report")
        button_save.setShortcut(QKeySequence("Ctrl+s"))
        button_save.triggered.connect(self.saveOverviewReport)
        button_save.setCheckable(True)
        
        # Forth action close
        button_close = QAction(QIcon(iconsDir + "external.png"), "&Close", self)
        button_close.setStatusTip("Close Application")
        button_close.setShortcut(QKeySequence("Ctrl+c"))
        button_close.triggered.connect(self.closeEvent)
        button_close.setCheckable(True)
        
        # Menubar
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_load)
        # file_menu.addAction(button_process)
        file_menu.addAction(button_save)
        file_menu.addAction(button_close)        
        
        # central Widget and layout
        cWidget = QWidget()
        cWidget.setLayout(layout)
        
        # width = self.table.sizeHint().width() * 2
        # width = self.maximumWidth() - 50
        # height = self.table.sizeHint().height() * 2
        # height = self.maximumHeight() - 50
        # print(width)
        
        # app = QtWidgets.QApplication.instance()
        # screen_resolution = QGuiApplication.primaryScreen().geometry()
        geometry = app.primaryScreen().geometry()
        # screen = QScreen
        # geometry = self.sizeHint()
        # self.setFixedSize(geometry.width(), geometry.height())
        self.resize(geometry.width() - 50, geometry.height() - 50)
        # self.showMaximized() # hides window bar
        # self.showFullScreen()
        
        
        self.setCentralWidget(cWidget)
        self.setWindowTitle(APPTITLE) # apptitle global var

    def tabClicked(self, item):
        global dataDir, currWorkingDir, outDir
        
        cd = item.data()
        print(cd) # cell data
        # self.teProject.setText("# %i" % item.row())
        # if cell content is a full path to a file that exists
        if (os.path.isfile(cd)):
            # open it
            with open( cd, 'r', encoding="utf-8") as f:
                print('Showing content of MD file:')
                # markdown = Markdown(extensions=['codehilite'])
                text = f.read()
                #markdown.parse(text)
                self.teProject.setText(text)
        else:
            if cd.startswith("https:"):
                print("Downloading " + cd)
                # dload.git_clone(str(cd))
                path  = currWorkingDir + os.sep + outDir
                # cwd = os.getcwd()
                # print("Current Working Dir: " + cwd)
                clone = "git clone " + cd # "git clone gitolite@<server_ip>:/your/project/name.git" 

                # os.system("sshpass -p your_password ssh user_name@your_localhost")
                # os.system("sshpass -p xxx ssh ugarmann@mygit.th-deg.de")
                os.chdir(path) # Specifying the path where the cloned project needs to be copied
                # to-do: check whether project was already downloaded
                os.system(clone) # Cloning

            else:
                # otherwise show cell content
                self.teProject.setText(str(cd))
                
    def loadiLearnZIP(self):
        global courseName, currWorkingDir, dataDir, outDir, zipFileName, studentData, projData
        
        zipFileName = QFileDialog.getOpenFileName(self, 'Open iLearn ZIP file', 
            './' + dataDir, "ZIP files (*.zip)")
        if len(zipFileName[0]) > 0:
            path = Path(zipFileName[0])
            parentpath = str(path.parent.absolute())
            print(path)
            print(parentpath)
            
            # courseName can be changed in TextEdit
            # so get current name now    
            courseName = self.leCourseName.text()
            
            currWorkingDir = str(parentpath) + os.sep + courseName
            
            # print(path.parent.absolute())
            # pathname = path.parent.name
            self.labWorkingDir.setText("Working Directory: " + currWorkingDir)
            
            # to-do: Overwrite if it exists?
            
            # unzip Moodle assignment ZIP
            shutil.unpack_archive(zipFileName[0], currWorkingDir + os.sep + outDir)
            fileName = zipFileName[0].split(os.sep)[-1]
            folderName = fileName.split('.')[0]
            projData.dirPath = currWorkingDir + os.sep + outDir + os.sep + folderName
            # creates subdirs in outDir of working dir
            # subdirs have student names as first chars
            # tree(currWorkingDir + os.sep + outDir)
            tree(projData.dirPath)
            self.df = pd.DataFrame(studentData, columns = ['Name', 'Grades', 'File', 'Link1', 'Link2', 'Link3'])
            self.model = TableModel(self.df)
            header = self.table.horizontalHeader()       
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            # for sorting
            self.proxyModel = QSortFilterProxyModel()
            self.proxyModel.setSourceModel(self.model)

            self.table.setSortingEnabled(True)

            self.table.setModel(self.proxyModel)
            self.table.update()
            
            return True
        return False
    
    def reloadTable(self):
        global studentData

        self.df = pd.DataFrame(studentData, columns = ['Name', 'Grades', 'File', 'Link1', 'Link2', 'Link3'])
        self.model = TableModel(self.df)
        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # .Stretch to Maximum
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        # for sorting
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.table.setSortingEnabled(True)

        self.table.setModel(self.proxyModel)
        self.table.update()
    
    # def processProjects(self):
    #    return True
        
    def saveOverviewReport(self):
        """DataFrame.to_csv(path_or_buf=None, sep=',', na_rep='', float_format=None, columns=None, header=True, index=True, index_label=None, mode='w', encoding=None, compression='infer', quoting=None, quotechar='"', lineterminator=None, chunksize=None, date_format=None, doublequote=True, escapechar=None, decimal='.', errors='strict', storage_options=None)"""
        global currWorkingDir, courseName
        
        if (os.path.exists(currWorkingDir)):
            filepath = Path(currWorkingDir + os.sep + courseName + "-report.csv")
            # create parent dir if it does not exist
            # filepath.parent.mkdir(parents=True, exist_ok=True)
            self.df.to_csv(filepath, ";")
            filepath = Path(currWorkingDir + os.sep + courseName + "-report.xlsx")
            self.df.to_excel(filepath, ";") # , engine using default openpyxl, engine='xlsxwriter'
            return True
        else:
            pass # continue
        
    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit? Any unsaved work will be lost.",
            # QMessageBox.StandardButton since PyQt6
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Cancel)

        if (reply == QMessageBox.StandardButton.Close)  : 
            print("Close Event reply close")
            sys.exit()        
        else:
            if (reply == QMessageBox.StandardButton.Save): 
                print("Save")
                self.saveOverviewReport()
                sys.exit()
            else:
                print("Cancel Closing")
                if not type(event) == bool:
                    event.ignore()
    
    def openAnalyserWindow(self, item):
        index = item.row()
        lstProjData[index].accessToken = self.leToken.text()
        self.analyserWindow = AnalyserWindow(lstProjData[index], index)
        self.analyserWindow.closed.connect(self.saveReport)
        self.analyserWindow.exec()
        return
    
    def saveReport(self,data : ProjectData, i):
        lstProjData[i] = data
        studentData[i][1] = data.grades.avgGrade
        self.df = pd.DataFrame(studentData, columns = ['Name', 'Grades', 'File', 'Link1', 'Link2', 'Link3'])
        self.model = TableModel(self.df)
        header = self.table.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # .Stretch to Maximum
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        # for sorting
        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)

        self.table.setSortingEnabled(True)

        self.table.setModel(self.proxyModel)
        self.table.update()
        return

"""
dn directory name
fn full file name (incl directory)
"""
def handleFileType(dn, fn):
    # check file suffix for extension
    ext = ""
    # check for . in filename, so it has an extension, take last extension
    if '.' in fn:
        ext = fn.split('.')[-1].lower()
    """
    ZIP files are unpacked with shutil
    ZIPs in ZIPs are not handled recursively
    """
    if ext == 'zip':
        try:
            # unzip_recursively(dn + fn)
            # extractDir = os.path.abspath('.')
            
            # dfn = dn + os.sep + fn
            shutil.unpack_archive(fn, dn) # , 'zip'
            # name of unpacked dirs unknown here
            # tree(dn) 
            # process the dir again
            try:
                dirs, files = listdir(dn)[:2]
            except:
                pass
            else:
                walk(dn, dirs, files, '+---') # good visual prefix? Must not be ''
        except:
            print('Error while trying to unzip file: ' + fn)
    if ext == 'md':
        handleMarkdown(dn, fn)
    if ext == 'pdf':
        handlePDF(dn, fn)
    if not ext:
        print('Processed file has no or unknown extension: ' + fn)
    if ext in srcFilesTypes :
        projData.srcFiles.append(fn)
    else:
        projData.files.append(fn)

"""
Markdown are handled 
- Content is printed
"""
def handleMarkdown(dn, fn):
    global reportfile, reportfilename, stname, studentData, projData
    hfn = fn # handled file name, which contains the path , dn + "/" + 
    print("Markdown file: " + hfn)
    if reportfile:
        reportfile.write(stname + "\n")
        reportfile.write(hfn + "\n")
        with open(hfn, 'r') as mdf:
            # see 
            patt = re.compile(r'https:\/\/[0-9a-zA-Z./-]*', re.MULTILINE | re.DOTALL) # .git not at end of every link!
            allLinks = patt.findall(mdf.read())
            #print(type(allLinks[0]))
            #print(type(allLinks))
            if  re.search("readme.md", fn, re.IGNORECASE):
                stname = getNameFromReadME(fn)
                newList = [stname, 'Not Graded', hfn, '','','']
                if (len(allLinks) == 0):
                    newList = [stname, 'Not Graded', hfn, '','',''] # .append(allLinks)
                if (len(allLinks) == 1):
                    newList = [stname, 'Not Graded', hfn, allLinks[0], '', ''] # .append(allLinks)
                    com = 'git clone ' + allLinks[0]
                    print("Executing: " + com)
                    # subprocess.run(com)
                if (len(allLinks) == 2):
                    newList = [stname, 'Not Graded', hfn, allLinks[0], allLinks[1], ''] # .append(allLinks)
                
                
                print('allLinks: ' + str(allLinks))
                
                print('newList: ' + str(newList))
                # several code blocks
                # for l in allLinks:
                # Update table data
                studentData.append(newList)
                projData.studentName = stname
                projData.files.append(fn)
    return True

def handlePDF(dn, fn):
    hfn = dn + "/" + fn # handled file name
    print("PDF file: " + hfn)
    if reportfile:
        reportfile.write(stname + "\n")
        reportfile.write(hfn + "\n")
    return True
    
def processFile(dirname, name):
    # import
    print('Processing file ' + name)
#    getStudentNameFromDirName(dirname)
    # handle files, if not already processed
    fullname = dirname + os.sep + name
    if fullname not in processedFiles:
        processedFiles.append(fullname)
        handleFileType(dirname, name)


# Walk through the dir tree
def tree(path):
    # path = str(Path(path))
    dirs, files = listdir(path)[:2]
    # print(path)
    
    global zipFileName, reportfile, reportfilename, processedFiles, studentData, lstProjData, projData
    # create report files? Global report and student's reports!
    try:
        filename = Path(path).parent.name
        print(filename)
        reportfilename = path + os.sep + filename + ".md"
        print(reportfilename)
        with open(reportfilename, 'w') as reportfile:
            processedFiles.append(reportfilename)
            walk(path, dirs, files)
            # save processed files in reportfile
            print('Processed Files: \n')
            for name in processedFiles:
                print(name + '\n')
        
    except:
        print('Error while walking through dir tree path: ' + path)
        # reportfile.close()
    print(processedFiles)
    print(studentData)
    lstProjData.append(projData)
    projData = ProjectData()
    
    
def walk(root, dirs, files, prefix=''):
    global reportfile, reportfilename, processedFiles, stname
    # create a report file
    # currentReportFileName = root  + '-report-' + stname + '.md'
    # currentReportFile = open(currentReportFileName, "w") # + os.sep
    currentReportFile = reportfile
    print('Walking through root: ' + root, currentReportFile)
    # process files
    if FILES and files:
        file_prefix = prefix + ('|' if dirs else ' ') + '   '
        # process files in root dir
        for name in files:
            print(file_prefix + name + ' -> processing', currentReportFile)
            # read the file and process content
            # use the data directory
            processFile(root, name) # + dataDir + 'outputDir/'
        print(file_prefix)
    # currentReportFile.close()
    # process dirs
    dir_prefix, walk_prefix = prefix + '+---', prefix + '|   '
    for pos, neg, name in enumerate2(dirs):
        if neg == -1:
            dir_prefix, walk_prefix = prefix + '\\---', prefix + '    '
        print(dir_prefix + name)
        path = os.path.join(root, name)
        # print(name)
        # students names only from dirs on top level in Moodle ZIP
        if prefix == "":
            getStudentNameFromDirName(name)
            print(stname)
        try:
            dirs, files = listdir(path)[:2]
        except:
            pass
        else:
            walk(path, dirs, files, walk_prefix)


app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec()