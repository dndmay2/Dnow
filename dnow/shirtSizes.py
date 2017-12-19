from dnow.models import *
from collections import defaultdict

class Tshirts():
    def __init__(self, hostHome):
        self.tshirtCounts = defaultdict(lambda: 0)
        self.hostHome = hostHome

    def countShirts(self):
        self.getHostHomeShirts()
        self.getLeaderShirts()
        self.getStudentShirts()
        print(self.hostHome, self.tshirtCounts)

    def getHostHomeShirts(self):
        sizeString = self.hostHome.tshirtSize.replace(' ', '')
        sizes = sizeString.split(',')
        for size in sizes:
            self.tshirtCounts[size] += 1

    def getLeaderShirts(self):
        for leader in self.hostHome.leader_set.all():
            self.tshirtCounts[leader.tshirtSize] += 1

    def getStudentShirts(self):
        for student in self.hostHome.student_set.all():
            self.tshirtCounts[student.tshirtSize] += 1

    def createTshirtHtml(self):
        html = '<h2>T Shirts</h2>'
        html += '<table sumary="Tshirt Table">'
        html += '<tr>'
        for size in SHIRT_SIZES:
            print('size', size[1])
            html += '<th>%s</th>' % size[1]
        html += '<th>Total</th>'
        html += '</tr>'
        html += '<tr>'
        count = 0
        for size in SHIRT_SIZES:
            num = self.tshirtCounts[size[1]]
            count += num
            html += '<td>%d</td>' % num
        html += '<td>%d</td>' % count
        html += '</tr>'
        html += '</table>'
        return html
