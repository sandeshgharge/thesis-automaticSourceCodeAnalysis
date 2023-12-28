class ProjectData :
    def __init__(self):
        self.studentName : str
        self.files = []
        self.srcFiles = []
        self.remark = ""
        self.dirPath = ""
        self.grades : GradingFields = GradingFields()
        self.accessToken = "" ## glpat-wJ_VrJJxeF_wJ9zHdH1V
        return
    
class GradingFields :
    def __init__(self):

        self.comments : int = 0
        self.code : int = 0
        self.documentation : int = 0
        self.graded : bool = False
        self.avgGrade : int = 0
        return
    
    def saveGrades(self, comntGrade : int, codeGrade : int, docGrade : int, remarks : str):
        self.comments = comntGrade
        self.code = codeGrade
        self.documentation = docGrade
        self.remark = remarks
        self.graded = True
        return

    def calAvgGrade(self):
        totalGrades = 0
        count = 0
        self.avgGrade = 0
        if self.comments > 0:
            count += 1
            totalGrades += self.comments
        
        if self.code > 0:
            count += 1
            totalGrades += self.code

        if self.documentation > 0:
            count += 1
            totalGrades += self.documentation
        if count == 0:
            self.avgGrade = 0
        else:
            self.avgGrade = totalGrades / count