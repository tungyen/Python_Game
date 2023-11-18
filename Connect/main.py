from tkinter import *
from tkinter.messagebox import *
from threading import Timer
import random
import time


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def IsLink(p1, p2):
    if lineCheck(p1, p2):
        return True
    if OneCornerLink(p1, p2):
        return True
    if TwoCornerLink(p1, p2):
        return True
    return False


def IsSame(p1, p2):
    if map[p1.x][p1.y] == map[p2.x][p2.y]:
        return True
    return False


def callback(event):

    global Select_first, p1, p2, total, time_running, grade_text, grade, cur_time
    global firstSelectRectId, SecondSelectRectId, rightClick, hintSecond, hintFirst

    if time_running:
        return

    x = (event.x-border) // block_size
    y = (event.y-border) // block_size
    x1 = border+x*block_size
    y1 = border+y*block_size
    x2 = border+(x+1)*block_size
    y2 = border+(y+1) * block_size

    if map[x][y] == " ":
        showinfo(title="提示", message="這邊沒方塊")
    else:
        if not Select_first:
            p1 = Point(x, y)
            firstSelectRectId = cv.create_rectangle(x1, y1, x2, y2, width=2, outline="blue")
            Select_first = True
        else:
            p2 = Point(x, y)
            Select_first = False
            if (p1.x == p2.x) and (p1.y == p2.y):
                cv.delete(firstSelectRectId)
                return
            SecondSelectRectId = cv.create_rectangle(x1, y1, x2, y2, width=2, outline="yellow")
            cv.pack()

            # 判断是否连通
            if IsSame(p1, p2) and IsLink(p1, p2):
                drawLinkLine(p1, p2)
                time_running = True
                t = Timer(timer_interval, delayrun)
                t.start()
                total -= 2

                if time.time()-cur_time > 4:
                    grade += 1
                elif time.time()-cur_time > 3:
                    grade += 2
                elif time.time()-cur_time > 2:
                    grade += 3
                elif time.time()-cur_time > 1:
                    grade += 4
                else:
                    grade += 5

                cur_time = time.time()
                cv.delete(grade_text)
                grade_text = cv.create_text(5, 5, anchor="nw", text=f"Grade: {grade}", font=("Helvetica", 16), fill="white")
                if total == 0:
                    showinfo(title="提示", message="你好棒喔~過關了!")
                    root.quit()

            else:
                cv.delete(firstSelectRectId)
                cv.delete(SecondSelectRectId)

            # Cancel the hint block
            if rightClick:
                cv.delete(hintFirst)
                cv.delete(hintSecond)
                rightClick = False


def delayrun():
    global time_running
    clearTwoBlock()
    time_running = False


def clearTwoBlock():
    global rightClick, ConnectingLines, firstSelectRectId, SecondSelectRectId
    global hintFirst, hintSecond, map
    global p1, p2
    cv.delete(firstSelectRectId)
    cv.delete(SecondSelectRectId)
    if rightClick:
        cv.delete(hintFirst)
        cv.delete(hintSecond)
        rightClick = False
    # Clear connecting lines
    for line_id in ConnectingLines:
        cv.delete(line_id)
    ConnectingLines = []

    map[p1.x][p1.y] = " "
    cv.delete(image_map[p1.x][p1.y])
    map[p2.x][p2.y] = " "
    cv.delete(image_map[p2.x][p2.y])
    undrawConnectLine()


def print_map():
    c = block_size/2
    global image_map
    for x in range(0, Width):
        for y in range(0, Height):
            if map[x][y] != ' ':
                img1 = imgs[int(map[x][y])]
                id = cv.create_image((border+x*block_size+c, border+y*block_size+c), image=img1)
                image_map[x][y] = id
    cv.pack()


def lineCheck(p1, p2):
    distance = 0
    count = 0
    # on the same row or column
    if p1.x == p2.x or p1.y == p2.y:

        # Same block
        if p1.x == p2.x and p1.y == p2.y:
            return True

        # on the same column
        elif p1.x == p2.x and p1.y != p2.y:
            distance = abs(p1.y - p2.y) - 1
            zf = -1 if p1.y - p2.y > 0 else 1
            for i in range(1, distance + 1):
                if map[p1.x][p1.y + i * zf] == " ":
                    count += 1
                else:
                    break

        # on the same row
        elif p1.y == p2.y and p1.x != p2.x:
            distance = abs(p1.x - p2.x) - 1
            zf = -1 if p1.x - p2.x > 0 else 1
            for i in range(1, distance + 1):
                if map[p1.x + i * zf][p1.y] == " ":
                    count += 1
                else:
                    break

        # There is no obstacle between p1 and p2
        if count == distance:
            return True
    else:
        return False


def OneCornerLink(p1, p2):

    p12 = Point(p1.x, p2.y)
    p21 = Point(p2.x, p1.y)

    if map[p12.x][p12.y] == " ":
        if lineCheck(p1, p12) and lineCheck(p12, p2):
            linePointStack.append(p12)
            return True

    if map[p21.x][p21.y] == " ":
        if lineCheck(p1, p21) and lineCheck(p21, p2):
            linePointStack.append(p21)
            return True

    return False


def TwoCornerLink(p1, p2):
    checkP = Point(p1.x, p1.y)
    for i in range(0, 4):
        checkP.x = p1.x
        checkP.y = p1.y
        if i == 3:
            checkP.y += 1
            while (checkP.y < Height) and map[checkP.x][checkP.y] == " ":
                linePointStack.append(checkP)
                if OneCornerLink(checkP, p2):
                    return True
                else:
                    linePointStack.pop()
                checkP.y += 1

            if checkP.y == Height:
                z = Point(p2.x, Height - 1)
                if lineCheck(z, p2):
                    linePointStack.append(Point(p1.x, Height))
                    linePointStack.append(Point(p2.x, Height))
                    return True
        elif i == 2:
            checkP.x += 1
            while (checkP.x < Width) and map[checkP.x][checkP.y] == " ":
                linePointStack.append(checkP)
                if OneCornerLink(checkP, p2):
                    return True
                else:
                    linePointStack.pop()
                checkP.x += 1

            if checkP.x == Width:
                z = Point(Width - 1, p2.y)
                if lineCheck(z, p2):
                    linePointStack.append(Point(Width, p1.y))
                    linePointStack.append(Point(Width, p2.y))
                    return True
        elif i == 1:
            checkP.x -= 1
            while (checkP.x >= 0) and map[checkP.x][checkP.y] == " ":
                linePointStack.append(checkP)
                if OneCornerLink(checkP, p2):
                    return True
                else:
                    linePointStack.pop()
                checkP.x -= 1

            if checkP.x == -1:
                z = Point(0, p2.y)
                if lineCheck(z, p2):
                    linePointStack.append(Point(-1, p1.y))
                    linePointStack.append(Point(-1, p2.y))
                    return True

        elif i == 0:
            checkP.y -= 1
            while (checkP.y >= 0) and map[checkP.x][checkP.y] == " ":
                linePointStack.append(checkP)
                if OneCornerLink(checkP, p2):
                    return True
                else:
                    linePointStack.pop()
                checkP.y -= 4
            if checkP.y == -1:
                z = Point(p2.x, 0)
                if lineCheck(z, p2):
                    linePointStack.append(Point(p1.x, -1))
                    linePointStack.append(Point(p2.x, -1))
                    return True
    return False


def drawLinkLine(p1, p2):
    global ConnectingLines, linePointStack
    new_lines = []

    if len(linePointStack) == 0:
        new_lines.append(drawLine(p1, p2))
    else:
        print(linePointStack, len(linePointStack))

    if len(linePointStack) == 1:
        z = linePointStack.pop()
        new_lines.append(drawLine(p1, z))
        new_lines.append(drawLine(p2, z))
    elif len(linePointStack) == 2:
        z1 = linePointStack.pop()
        new_lines.append(drawLine(p2, z1))
        z2 = linePointStack.pop()
        new_lines.append(drawLine(z1, z2))
        new_lines.append(drawLine(p1, z2))
    linePointStack = []
    print("Point left: ", len(linePointStack))
    ConnectingLines = new_lines


def undrawConnectLine():
    while len(Line_id) > 0:
        idpop = Line_id.pop()
        cv.delete(idpop)


def drawLine(p1, p2):
    c = block_size/2
    print("drawLine p1,p2", p1.x, p1.y, p2.x, p2.y)
    x1 = p1.x*block_size+c + border
    y1 = p1.y*block_size+c + border
    x2 = p2.x*block_size+c + border
    y2 = p2.y*block_size+c + border
    id = cv.create_line(x1, y1, x2, y2, width=5, fill='red')
    return id


def create_map():
    global map
    tmpMap = []
    m = Width * Height // category
    for x in range(0, m):
        for i in range(0, category):
            tmpMap.append(x)
    random.shuffle(tmpMap)
    for x in range(0, Width):
        for y in range(0, Height):
            map[x][y] = tmpMap[x * Height + y]


def find2Block(event):
    global hintSecond, hintFirst, rightClick, ConnectingLines, linePointStack
    global time_running, grade_text, grade
    if time_running:
        return
    rightClick = True
    m_nRoW = Height
    m_nCol = Width
    bFound = False
    for i in range(0, m_nRoW * m_nCol):
        if bFound:
            break
        x1 = i % m_nCol
        y1 = i // m_nCol
        p1 = Point(x1, y1)
        if map[x1][y1] == ' ':
            continue
        for j in range(i + 1, m_nRoW * m_nCol):

            x2 = j % m_nCol
            y2 = j // m_nCol
            p2 = Point(x2, y2)
            if map[x2][y2] != ' ' and IsSame(p1, p2):
                if IsLink(p1, p2):
                    ConnectingLines = []
                    linePointStack = []
                    bFound = True
                    break
    if bFound:
        hintFirst = cv.create_rectangle(border+x1*block_size, border+y1*block_size, border+(x1+1)*block_size, border+(y1+1)*block_size, width=2, outline="red")
        hintSecond = cv.create_rectangle(border+x2*block_size, border+y2*block_size, border+(x2+1)*block_size, border+(y2+1)*block_size, width=2, outline="red")
        grade -= 1
        cv.delete(grade_text)
        grade_text = cv.create_text(5, 5, anchor="nw", text=f"Grade: {grade}", font=("Helvetica", 16), fill="white")

    return bFound


if __name__ == '__main__':

    # Initialize Tkinter
    root = Tk()
    root.title("Python連連看")

    # Initial game hyperparameter
    category = 20
    block_size = 40
    fac = 5
    border = block_size
    timer_interval = 0.3
    grade = 0

    # Initial parameters
    total = category**2
    ConnectingLines = []
    imgs = [PhotoImage(file='pic/' + str(i) + '.png').subsample(x=fac, y=fac) for i in range(1, category+1)]
    Select_first = False
    time_running = False
    firstSelectRectId = -1
    SecondSelectRectId = -1
    hintFirst = -1
    hintSecond = -1
    clearFlag = False
    rightClick = False
    linePointStack = []
    Line_id = []

    # Constructing the map
    Height = category
    Width = category
    map = [[" " for y in range(Height)] for x in range(Width)]
    image_map = [[" " for y in range(Height)] for x in range(Width)]

    # Set up the canvas
    cv = Canvas(root, bg='green', width=2*border+block_size*category, height=2*border+block_size*category)
    grade_text = cv.create_text(5, 5, anchor="nw", text=f"Grade: {grade}", font=("Helvetica", 16), fill="white")
    cv.bind("<Button-1>", callback)
    cv.bind("<Button-3>", find2Block)
    cv.pack()
    create_map()
    print_map()
    cur_time = time.time()
    root.mainloop()
