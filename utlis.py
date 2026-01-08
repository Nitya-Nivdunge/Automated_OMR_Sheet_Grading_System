import cv2
import numpy as np

## TO STACK ALL THE IMAGES IN ONE WINDOW
def stackImages(imgArray,scale,lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        #print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    return ver

def reorder(points):
    points = points.reshape((4, 2)) # REMOVE EXTRA BRACKET
    print(points)
    pointsNew = np.zeros((4, 1, 2), np.int32) # NEW MATRIX WITH ARRANGED POINTS
    add = points.sum(1)
    print(add)
    
    print(np.argmax(add))
    pointsNew[0] = points[np.argmin(add)]  # [0,0] - Origin Least Sum
    pointsNew[3] = points[np.argmax(add)]  # [w,h] - Max Sum
    
    diff = np.diff(points, axis=1)
    pointsNew[1] = points[np.argmin(diff)]  # [w,0] - 
    pointsNew[2] = points[np.argmax(diff)] # [h,0] - 

    return pointsNew

""""
def rectContour(contours):

    rectCon = []
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if len(approx) == 4:
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea,reverse=True)
    #print(len(rectCon))
    return rectCon
"""

def rectContour(contours):
    rectContours = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:  # Filter based on minimum area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            if len(approx) == 4:  # Only keep rectangular contours
                rectContours.append([area, contour])

    # Sort contours by area in descending order
    rectContours = sorted(rectContours, key=lambda x: x[0], reverse=True)
    return rectContours


def getCornerPoints(contour_data):
    area, contour = contour_data
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)  # Get corner points
    return area, approx  # Return both area and corner points

## SPLIT THE MCQ IMG TO GET INDIVIDUAL ROWS AND COLUMNS ###
""""
def splitBoxes(img):
    rows = np.vsplit(img,5)
    boxes=[]
    for r in rows:
        cols= np.hsplit(r,20)
        for box in cols:
            boxes.append(box)
    return boxes"""

def splitCells(img):
    rows = np.vsplit(img, 20)  # SPLITS IMG INTO 20 EQUAL ROWS
    cells = []
    for i, r in enumerate(rows):
        cols = np.hsplit(r, 5)  # SPLITS EACH ROW INTO 5 COLUMNS
        options = cols[1:]  # Skip the first column (question numbers) and get only A, B, C, D columns
        for j, c in enumerate(options):
            cells.append(c)
            # cv2.imshow(f"Option cell {i}-{j+1}", c)  # Display each cell in the options columns
            # cv2.waitKey(50)  # Small delay to see each cell briefly (adjust as needed)
    return cells


def drawGrid(img,questions=5,choices=5):
    secW = int(img.shape[1]/questions)
    secH = int(img.shape[0]/choices)
    for i in range (0,9):
        pt1 = (0,secH*i)
        pt2 = (img.shape[1],secH*i)
        pt3 = (secW * i, 0)
        pt4 = (secW*i,img.shape[0])
        cv2.line(img, pt1, pt2, (255, 255, 0),2)
        cv2.line(img, pt3, pt4, (255, 255, 0),2)

    return img


def output_answers(img, selected_ans, score, correct_ans, questions, choices):
    secW = int(img.shape[1] / (choices + 1))  # Include the first column for calculations
    secH = int(img.shape[0] / questions)

    correct_ans_color = (0, 255, 0)
    wrong_ans_color = (0, 0, 255)

    for x in range(questions):
        my_ans = selected_ans[x]  # Keep the original variable name for selected answer
        cX = ((my_ans + 1) * secW) + secW // 2  # Shift by 1 column to skip the question numbers
        cY = (x * secH) + secH // 2
        
        if score[x] == 'R':
            # Shift by 1 column to ignore the first column
            startX = (my_ans + 1) * secW
            startY = x * secH
            endX = startX + secW
            endY = startY + secH
            # Draw a rectangle only around the selected answer with a border
            cv2.rectangle(img, (startX, startY), (endX, endY), correct_ans_color, 8)            
            cv2.circle(img, (cX, cY), 20, correct_ans_color, cv2.FILLED)
        elif score[x] == 'W':
            cv2.circle(img, (cX, cY), 20, wrong_ans_color, cv2.FILLED)
            # Draw correct answer if the answer was incorrect
            correct = correct_ans[x]  # This should be a list passed to the function
            cv2.circle(img, (((correct + 1) * secW) + secW // 2, cY), 20, correct_ans_color, cv2.FILLED)
        elif score[x] == 'N':   # Incase of no selected answers 'N' mark only correct answer
            correct = correct_ans[x]  # This should be a list passed to the function
            cv2.circle(img, (((correct + 1) * secW) + secW // 2, cY), 20, correct_ans_color, cv2.FILLED)

    return img
