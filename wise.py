import csv
import sys
import copy
import pdb
import matplotlib.pyplot as plt
from datetime import datetime
import collections
import numpy as np
from scipy.interpolate import spline
import os
import gc

class School:
	def __init__(self, name, generate_graphs=True, students={}, homeworks={}, dates=[]):
		self.name=name
		self.students=students
		self.homeworks=homeworks
		self.dates=dates
		self.setSchoolData()
		if generate_graphs==True:
			self.generateGraphs() 

	def addStudent(self, student):
		self.students[student.code]=student

	def addHomework(self, code, homework):
		if code not in self.homeworks:
			self.homeworks[code]=[]
			self.homeworks[code].append(homework)
		else:
			self.homeworks[code].append(homework)

	def addHomeworkToStudent(self, code, homework):
		self.students[code].addHomework(homework)

	def setSchoolData(self, filename=False):
		if filename==False:
			filename=self.name+".csv"
		file=open(filename)
		reader=csv.reader(file)
		rownum=0
		for row in reader:
			if rownum==0:
				header=row
			else:
				code=int(row[1])
				if code not in self.students:
					gender=row[2].lower()
					student=Student(code, gender)
					self.addStudent(student)
				date=datetime.strptime(row[3], '%m/%d/%Y')
				self.dates.append(date)
				
				if row[7]!="":
					mathcomp=int(row[7])
				else:
					mathcomp=0

				if row[11]!="":
					engcomp=int(row[11])
				else:
					engcomp=0

				mathHomework=Homework("math", mathcomp, date)
				engHomework=Homework("eng", engcomp, date)
				self.addHomework(code, mathHomework)
				self.addHomework(code, engHomework)
			rownum+=1
		self.dates=list(set(self.dates))
		file.close()


	def getAverages(self, grade, subject, gender=False):
		averages={}
		sortedAverages={}
		for date in self.dates:
			compCount=0
			compTotal=0
			average=0
			for code in self.students:
				student=self.students[code]
				compAmt=0
				if gender != False:
					if student.gender==gender:
						compAmt=self.getCompFromStudent(code,grade,  subject, date)
				else:
					compAmt=self.getCompFromStudent(code, grade,  subject, date)
				if compAmt!=0:
					compCount+=1
					compTotal+=compAmt
			if compCount != 0:
				average=compTotal/compCount

			averages[date]=average
			self.removeEmptyAverages(averages)
			sortedAverages=self.sortAverages(averages)
		return sortedAverages

	def getCompFromStudent(self, code, grade, subject, date):
		if self.students[code].getGrade()==grade:
			for homework in self.homeworks[code]:
				if homework.date==date and homework.subject==subject:
					return homework.comprehension
		return 0

	def removeEmptyAverages(self, averages):
		
		for date in list(averages):
			if averages[date]==0:
				averages.pop(date, None)

	def sortAverages(self, averages):
		sortedAverages=collections.OrderedDict(sorted(averages.items()))
		return sortedAverages



	def plotGradeSubjectGraph(self, filename, grade, subject, gender=False):
		data=self.getAverages(grade, subject, gender)
		xdata=list(range(0, len(data)))
		ydata=list(data.values())
		miny=min(ydata)-0.5
		maxy=max(ydata)+0.5
		# USED FOR SMOOTH GRAPHS
		# x_sm=np.array(xdata)
		# y_sm=np.array(ydata)
		# x_smooth=np.linspace(x_sm.min(), x_sm.max(), 200)
		# y_smooth=spline(xdata, ydata, x_smooth)
		slope, intercept, vals=self.getLinearData(xdata,ydata)

		plt.plot(xdata, ydata, '--')
		plt.plot(xdata, vals, 'b')
		plt.text(len(data)+1, vals[-1], str(slope)[0:6])
		plt.xlabel('Days')
		plt.ylabel('Average Comprehension')
		subject="Math" if subject=="math" else "English"
		if gender==False:
			gender=""
		else:
			gender="Male" if gender=="m" else "Female" 
		title=self.name +" Grade " +str(grade)  +" " +subject +" " +gender 
		plt.title(title)
		plt.axis([0,len(data),miny,maxy])
		plt.savefig(self.name+"Graphs/"+filename+'.png')
		plt.clf()

	def getLinearData(self, xdata, ydata):
		slope=0
		intercept=0
		slope, intercept=np.polyfit(xdata, ydata,1)
		vals=[]
		for i in xdata:
			vals.append(slope*i+intercept)
		return slope, intercept, vals

	def generateGraphs(self):
		#Creates Directory for files
		if not os.path.exists(self.name+"Graphs"):
			os.makedirs(self.name+"Graphs")
		self.plotGradeSubjectGraph(self.name+"Grade2MathMale",2,'math','m')
		self.plotGradeSubjectGraph(self.name+"Grade2MathFemale",2,'math','f')
		self.plotGradeSubjectGraph(self.name+"Grade2Math",2,'math')
		self.plotGradeSubjectGraph(self.name+"Grade2EngMale",2,'eng','m')
		self.plotGradeSubjectGraph(self.name+"Grade2EngFemale",2,'eng','f')
		self.plotGradeSubjectGraph(self.name+"Grade2Eng",2,'eng')
		self.plotGradeSubjectGraph(self.name+"Grade4MathMale",4,'math','m')
		self.plotGradeSubjectGraph(self.name+"Grade4MathFemale",4,'math','f')
		self.plotGradeSubjectGraph(self.name+"Grade4Math",4,'math')
		self.plotGradeSubjectGraph(self.name+"Grade4EngMale",4,'eng','m')
		self.plotGradeSubjectGraph(self.name+"Grade4MathFemale",4,'math','f')
		self.plotGradeSubjectGraph(self.name+"Grade4Math",4,'math')

	def getTotalComprehensionAverages(self):
		
		# calculates the begin and end average for each subject and grade
		grade2MathBegin=grade2MathEnd=grade4MathBegin=grade4MathEnd=grade2EngBegin=grade2EngEnd=grade4EngBegin=grade4EngEnd=0
		grade2MathBegin, grade2MathEnd = self.getSubjectGradeComprehensionAverages(2,'math')
		grade4MathBegin, grade4MathEnd = self.getSubjectGradeComprehensionAverages(4,'math')
		grade2EngBegin, grade2EngEnd = self.getSubjectGradeComprehensionAverages(2, 'eng')
		grade4EngBegin, grade4EngEnd = self.getSubjectGradeComprehensionAverages(4, 'eng')
		
		# calculating total begin and end average for the school
		beginAvg=endAvg=0
		schoolbeginAvg=(grade2MathBegin+grade4MathBegin+grade2EngBegin+grade4EngBegin)/4
		schoolendAvg=(grade2MathEnd+grade4MathEnd+grade2EngEnd+grade4EngEnd)/4

		return schoolbeginAvg, schoolendAvg
	def getSubjectGradeComprehensionAverages(self, grade, subject):
		averages={}
		xdata=[]
		ydata=[]
		slope=0
		intercept=0
		vals=[]
		beginAvg=0
		endAvg=0
		averages=self.getAverages(grade, subject)
		xdata=list(range(0, len(averages)))
		ydata=list(averages.values())
		slope, intercept, vals=self.getLinearData(xdata, ydata)
		beginAvg=vals[0]
		endAvg=vals[-1]
		# print(grade)
		# print(subject)
		# print(beginAvg)
		# print(endAvg)
		return beginAvg, endAvg

def generateComprehensionGraph(schools=False):
	if schools==False:
		schools=[ "Freeman"]
	i=1
	xtotaldata=[]
	ytotaldata=[]
	schoolList=[]
	for s in schools:
		school=School(s, False)
		schoolList.append(school)
		beginAvg=0
		endAvg=0
		beginAvg, endAvg = school.getTotalComprehensionAverages()
		ytotaldata.append(beginAvg)
		ytotaldata.append(endAvg)
		ydata=[beginAvg, endAvg]
		print(school.name)
		print(beginAvg)
		print(endAvg)
		xdata=[i,i]
		xtotaldata.append(i)
		xtotaldata.append(i)
		if endAvg > beginAvg:
			plt.plot(xdata, ydata, 'g-', linewidth=10.0)
			plt.text(i,endAvg+0.05, school.name, horizontalalignment='center')
		else:
			plt.plot(xdata,ydata, 'r-', linewidth=10.0)
			plt.text(i,beginAvg+0.05, school.name, horizontalalignment='center')
		i+=1
		gc.collect()

	plt.title("Comprehension Comparison Grade")
	plt.ylabel("Average Comprehension")
	plt.xlabel("Schools")
	plt.axis([0,len(schools)+1, min(ytotaldata)-0.2, max(ytotaldata)+0.2])
	plt.savefig('ComprehensionComparisonFreeman.png')
	plt.clf()

	
class Student:
	# GRADE 2 CODES
	FREEMANGRADE2CODES=list(range(1,13))
	OLDROADGRADE2CODES=list(range(31,43))
	PARESGRADE2CODES=list(range(58,70))
	CEDARGRADE2CODES=list(range(82,104))
	SROLIVIAGRADE2CODES=list(range(129,149))
	VILLAGRADE2CODES=list(range(168,194))
	GRADE2CODES=FREEMANGRADE2CODES+OLDROADGRADE2CODES+PARESGRADE2CODES+CEDARGRADE2CODES+SROLIVIAGRADE2CODES+VILLAGRADE2CODES
	
	# GRADE 4 CODES
	FREEMANGRADE4CODES=list(range(13,31))
	OLDROADGRADE4CODES=list(range(43,58))
	PARESGRADE4CODES=list(range(70,82))
	CEDARGRADE4CODES=list(range(104,129))
	SROLIVIAGRADE4CODES=list(range(149,168))
	VILLAGRADE4CODES=list(range(194,215))
	GRADE4CODES=FREEMANGRADE4CODES+OLDROADGRADE4CODES+PARESGRADE4CODES+CEDARGRADE4CODES+SROLIVIAGRADE4CODES+VILLAGRADE4CODES
	def __init__(self, code, gender):
		self.code=code
		self.gender=gender

	def getGrade(self):
		if self.code in self.GRADE2CODES:
			return 2
		if self.code in self.GRADE4CODES:
			return 4
		else:
			return False

class Homework:
	def __init__(self, subject, comprehension, date):
		self.subject=subject
		self.comprehension=comprehension
		self.date=date


