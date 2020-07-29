import mysql.connector
from _datetime import date
import datetime
import math

cnx = mysql.connector.connect('填你自己的')

dateFormat = '%Y-%m-%d %H:%M:%S'

Tablename = ['ToDoList', 'ReviewTime', 'Exam']
creatsql = [
    'CREATE TABLE IF NOT EXISTS `ToDoList` (`userId`  int(11) NOT NULL  ,`task` varchar(45) NOT NULL, `deadline` datetime NOT NULL ,PRIMARY KEY (`task`))ENGINE=InnoDB DEFAULT CHARACTER SET=utf8',
    'CREATE TABLE IF NOT EXISTS `ReviewTime` (`userId`  int(11) NOT NULL  ,`RecessDate` date NOT NULL, `ExamDate` date NOT NULL, `during`  int(11) NOT NULL,PRIMARY KEY (`userId`)  )ENGINE=InnoDB DEFAULT CHARACTER SET=utf8',
    'CREATE TABLE IF NOT EXISTS `Exam` (`Id`  int(11) NOT NULL AUTO_INCREMENT  ,`userId`  int(11) NOT NULL  ,`module` varchar(255) NOT NULL, `level` int(10) NOT NULL ,PRIMARY KEY (`Id`))ENGINE=InnoDB DEFAULT CHARACTER SET=utf8',
    ]


def creatTable():
    cursor = cnx.cursor()
    for i in range(len(Tablename)):
        try:
            cursor.execute(creatsql[i])
        except mysql.connector.Error as e:
            print('create {} orange fails!{}'.format(Tablename[i],e))


def getToDoList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s"
        args = (userId,)

        cursor.execute(statement, args)
        result = cursor.fetchall()
        # for debugging---------------------------
        # print(result)
        # for row in result:
        #    task = row[0];
        #    deadline = row[1];

        #    print("Task: " + task + ", Deadline: " + deadline.strftime('%d-%m-%Y %H:%M:%S'))
        # ----------------------------------------
        toDoList = "\"_Today is your opportunity to build the tomorrow you want.” \n- Ken Poirot_ \n"
        toDoList += "\nHere is the list of task you have, spend your day productively!✨ \n"
        i = 1
        for row in result:
            days_left = (row[1].date() - datetime.date.today()).days
            now = datetime.datetime.now()
            time_left = row[1] - now
            diff = countDown(time_left)
            toDoList += str(i) + ") \"" + row[0] + "\" _due in_ *" + str(diff.get('days')) + "* day *" + str(
                diff.get('hours')) + "* hr *" + str(diff.get('min')) + "* min\n"
            i += 1
            # print(toDoList)
        return toDoList
    finally:
        print()


# remember to chang
def countDown(timeLeft):
    d = {"days": timeLeft.days}
    d["hours"], rem = divmod(timeLeft.seconds, 3600)
    d["min"], d["seconds"] = divmod(rem, 60)
    return d


def getArrayList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()
        # for debugging----------
        for row in result:
            rawData = str(userId) + "|" + \
                str(row[0]) + "|" + row[1].strftime('%Y-%m-%d %H:%M:%S')
            print(rawData)
        # -----------------------
        return result
    finally:
        print('')


def getDoneList(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT task, deadline FROM ToDoList WHERE userId = %s"
        args = (userId,)
        cursor.execute(statement, args)
        result = cursor.fetchall()

        DoneList = "Done list: \n"
        for row in result:
            DoneList += row[0] + "\n"
        return DoneList
    finally:
        print("DoneList done")


def addTask(userId, task, deadline):
    # print("Server manager add task executed")

    try:
        cursor = cnx.cursor()
        statement = "INSERT INTO ToDoList(task, deadline, userId) VALUES (%s, %s, %s)"
        args = (task, deadline, userId)
        cursor.execute(statement, args)
    finally:
        cnx.commit()


def removeTask(userId, task, deadline):
    # print("remove task")

    try:
        cursor = cnx.cursor()
        statement = "DELETE FROM ToDoList WHERE userId = %s AND task = %s AND deadline = %s "
        args = (userId, task, deadline)
        cursor.execute(statement, args)
    finally:
        cnx.commit()


def alluserId():
    try:
        cursor = cnx.cursor()
        statement = "SELECT userId FROM ToDoList "
        cursor.execute(statement)
        result = cursor.fetchall()
        # print(result) #测试用
        return result
    finally:
        cnx.commit()


def addreviewtime(userId, starting, ending):
    startingarray = starting.split('/')
    endingarray = ending.split('/')
    a = datetime.date(int(startingarray[2]), int(
        startingarray[1]), int(startingarray[0]))
    b = datetime.date(int(endingarray[2]), int(
        endingarray[1]), int(endingarray[0]))
    during = b.__sub__(a).days
    print(startingarray,endingarray)
    startingarray.reverse()
    start = '-'.join(startingarray)
    endingarray.reverse()
    end = '-'.join(endingarray)
    try:
        cursor = cnx.cursor()
        statement = "INSERT INTO ReviewTime(userId, RecessDate, ExamDate, during) VALUES (%s, %s, %s, %s)"
        args = (userId, start, end, during)
        cursor.execute(statement, args)
    finally:
        cnx.commit()


def addexam(userId, module, level):
    try:
        cursor = cnx.cursor()
        for i in range(len(module)):
            statement = "INSERT INTO Exam(userId, module, level) VALUES (%s, %s, %s)"
            args = (userId, module[i], level[i])
            cursor.execute(statement, args)
    finally:
        cnx.commit()


def getreviewtime(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT during FROM ReviewTime WHERE userId = %s"
        args = (userId,)

        cursor.execute(statement, args)
        result = cursor.fetchone()
        return result
    finally:
        cnx.commit()


def examinformation(userId):
    try:
        cursor = cnx.cursor()
        statement = "SELECT module, level FROM Exam WHERE userId = %s"
        args = (userId,)

        cursor.execute(statement, args)
        result = cursor.fetchall()
        # classification用来考试权重分类，0,1,2分别对应权重1，2，3
        classification = [[], [], []]
        for row in result:
            if row[1] == 1:
                classification[0].append(row[0])
            elif row[1] == 2:
                classification[1].append(row[0])
            else:
                classification[2].append(row[0])
        return classification  # 此函数返回是一个列表
    finally:
        cnx.commit()


def setnumber(number):
    if math.modf(number)[0] >= 0.5:
        return math.floor(number)+0.5
    else:
        return math.floor(number)


def odd(number):
    if number % 2 == 0:
        return False
    else:
        return True


def arrange(userId): #安排课表的算法
    exam = examinformation(userId)
    x, y, z = len(exam[0]), len(exam[1]), len(exam[2])  # x,y,z分别对应权重1，2，3的考试数目
    days = getreviewtime(userId)[0]
    state = days*4
    basetime = state/(1.25*x+y+0.75*z)
    first, second, third = setnumber(
        basetime*1.25), setnumber(basetime*1), setnumber(basetime*0.75)
    firstlarge = 0
    secondlarge = 0
    thirdlarge = 0
    if first > math.floor(first):
        firstlarge = 1
        first = math.floor(first)
    if second > math.floor(second):
        secondlarge = 1
        second = math.floor(second)
    if third > math.floor(third):
        thirdlarge = 1
        third = math.floor(third)
    arrangearray = [[0 for i in range(days)] for j in range(4)]
    index = 0
    start = 0
    for i in range(state):
        flag = i+1
        if i < x*first:
            arrangearray[index][i % days] = exam[0][start]
            if flag % first == 0:
                start += 1
            if flag % days == 0:
                index += 1
            if flag == x*first:
                start = 0
        elif i < x*first+y*second:
            arrangearray[index][i % days] = exam[1][start]
            if (flag-x*first) % second == 0:
                start += 1
            if flag % days == 0:
                index += 1
            if flag == x*first+y*second:
                start = 0
        elif i < x*first+y*second+z*third:
            arrangearray[index][i % days] = exam[2][start]
            if (flag-x*first+y*second) % third == 0:
                start += 1
            if flag % days == 0:
                index += 1
            if flag == x*first+y*second+z*third:
                start = 0
        else:
            halfarray = []
            if firstlarge == 1:
                halfarray.extend(exam[0])
            if secondlarge == 1:
                halfarray.extend(exam[1])
            if thirdlarge == 1:
                halfarray.extend(exam[2])
            if odd(len(halfarray)):
                halfarray.append(0)
            arrangearray[index][i % days] = [
                halfarray[start], halfarray[start+1]]
            if flag % days == 0:
                index += 1
            start += 2
    return arrangearray
