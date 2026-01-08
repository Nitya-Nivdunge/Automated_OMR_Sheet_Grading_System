import cv2
import numpy as np
import utlis
import pytesseract
import OCR
import os

### PARAMETERS ######
path = "Input Images/Stu_1.png"
width = 600
height = 700
img = cv2.imread(path)
img = cv2.resize(img,(width,height))
img_contours = img.copy()
img_largest_contours = img.copy()

questions = int(input("Enter no. of Questions : "))
choices = 4

# Define answer mappings
answer_map = {'A': 0, 'B': 1, 'C': 2, 'D':3, 'None': -1}  # Include "None" for unanswered
# A A B B C C D B C A B B C A D B C D C C A A B B C C D B C A D B C A D C A D C C

# Ask user for input in string format and map answers to integers
correct_ans = input(f"Enter the answers of {questions} questions: e.g., A B A D... (space-separated)\n")
correct_ans = [answer_map[ans] for ans in correct_ans.split() if ans in answer_map]

print("Mapped answers to integers:", correct_ans)   

### PREPROCESSING #####
img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
img_blur = cv2.GaussianBlur(img_gray,(5,5),1)
img_canny = cv2.Canny(img_blur,10,50)
# cv2.imshow("Edge Detection : ",img_canny)
# cv2.waitKey(0)

### FIND CONTOURS ####
contours,hierarchy = cv2.findContours(img_canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
cv2.drawContours(img_contours,contours,-1,(0,0,255),5)

### FIND 3 LARGEST RECTANGLE CONTOURS #####
# find their area and corner points
rect_contours = utlis.rectContour(contours)

mcq_1_box = {}  # For first largest contour
mcq_2_box = {}  # For second largest contour
score_box = {}  # For third largest contour

# Extract area and corner points, then store them in dictionaries
mcq_1_box["area"], mcq_1_box["corner_points"] = utlis.getCornerPoints(rect_contours[0])
mcq_2_box["area"], mcq_2_box["corner_points"] = utlis.getCornerPoints(rect_contours[1])
score_box["area"], score_box["corner_points"] = utlis.getCornerPoints(rect_contours[2])

# Print out the results
print(f"\n\nMCQ 1 BOX :\nArea: {mcq_1_box['area']}\nCorner Points: \n{mcq_1_box['corner_points']}")
print(f"\n\nMCQ 2 BOX :\nArea: {mcq_2_box['area']}\nCorner Points: \n{mcq_2_box['corner_points']}")
print(f"\n\nSCORE BOX :\nArea: {score_box['area']}\nCorner Points: \n{score_box['corner_points']}")

# HIGHLIGHT CORNER POINTS OF THE 3 LARGEST BOXES
if (mcq_1_box["area"]!=0 and mcq_2_box["area"]!=0 and score_box["area"]!=0):
        cv2.drawContours(img_largest_contours,mcq_1_box["corner_points"],-1,(0,0,255),15)   # red
        cv2.drawContours(img_largest_contours ,mcq_2_box["corner_points"],-1,(0,0,255),15)  # red
        cv2.drawContours(img_largest_contours,score_box["corner_points"],-1,(255,0,0),15)   # blue

        # Reorder corner points to avoid distortion
        mcq_1_box["corner_points"] = utlis.reorder(mcq_1_box["corner_points"])
        mcq_2_box["corner_points"] = utlis.reorder(mcq_2_box["corner_points"])
        score_box["corner_points"] = utlis.reorder(score_box["corner_points"])

        # Set the custom output sizes you want
        output_width, output_height = 350, 1400  # MCQ box dimensions
        score_width, score_height = 450, 200     # Score box dimensions

        # Convert corner points to float32 for perspective transform
        pt_mcq1_1 = np.float32(mcq_1_box["corner_points"])
        pt_mcq1_2 = np.float32(mcq_2_box["corner_points"])

        # Define destination points for a full rectangle with custom size
        pt_dst = np.float32([[0, 0], [output_width, 0], [0, output_height], [output_width, output_height]])

        # Compute perspective transforms
        mcq_1_matrix = cv2.getPerspectiveTransform(pt_mcq1_2, pt_dst)
        mcq_2_matrix = cv2.getPerspectiveTransform(pt_mcq1_1, pt_dst)

        # Apply warping with the desired output size
        imgWarpColored_1 = cv2.warpPerspective(img, mcq_1_matrix, (output_width, output_height))
        imgWarpColored_2 = cv2.warpPerspective(img, mcq_2_matrix, (output_width, output_height))

        # Handle the score box similarly
        pt_score_1 = np.float32(score_box["corner_points"])
        pt_score_2 = np.float32([[0, 0], [score_width, 0], [0, score_height], [score_width, score_height]])

        score_matrix = cv2.getPerspectiveTransform(pt_score_1, pt_score_2)
        score_display = cv2.warpPerspective(img, score_matrix, (score_width, score_height))

        # Convert warped images to grayscale and apply threshold
        imgGray_1 = cv2.cvtColor(imgWarpColored_1, cv2.COLOR_BGR2GRAY)
        imgGray_2 = cv2.cvtColor(imgWarpColored_2, cv2.COLOR_BGR2GRAY)

        imgThresh1 = cv2.threshold(imgGray_1, 170, 255, cv2.THRESH_BINARY_INV)[1]
        imgThresh2 = cv2.threshold(imgGray_2, 170, 255, cv2.THRESH_BINARY_INV)[1]

        # SPLITTING image into individual cells
        cell_set_1 = utlis.splitCells(imgThresh1)
        cell_set_2 = utlis.splitCells(imgThresh2)
        all_cells = cell_set_1 + cell_set_2

        # GETTING PIXEL VALUES TO COMPARE ANSWERS
        # PIXELS VALUES OF EACH OPTION OF EACH QUESTION
        cell_pixel_val = np.zeros((questions,choices)) 
        R_no = 0
        C_no = 0 
        for cell in all_cells:
                # Non-zero i.e non-black pixels : Threshold makes the colored option white with most non-zero pixels
                totPixels = cv2.countNonZero(cell)  
                cell_pixel_val[R_no, C_no] = totPixels

                # Move to the next choice
                C_no += 1
                if C_no == choices:  # When we've processed all choices for a question
                    R_no += 1       # Move to the next question
                    C_no = 0        # Reset choice counter
        print(cell_pixel_val)

        # Define the threshold for the minimum difference required to confidently select an option
        threshold = 800

        # Initialize lists to store answers and their indices
        selected_ans_option = []
        selected_ans_index = []  # List to store only the mapped index values

        # Loop through each question and determine the selected answer index
        print("\n\nCollected Answers and Indices:")
        for i in range(questions):
            rows = cell_pixel_val[i]  # Get the pixel values for each option in the question

            # Sort the pixel values in descending order and get the indices
            sorted_indices = np.argsort(rows)[::-1]  # Sorts in descending order
            max_index = sorted_indices[0]
            second_max_index = sorted_indices[1]

            # Check if the difference between the highest and second-highest values is significant
            if rows[max_index] - rows[second_max_index] < threshold:
                ans = "None"  # Assign "None"
            else:
                # Map the index back to the corresponding answer using `answer_map` keys
                ans = list(answer_map.keys())[max_index]

            # Append the answer to the list
            selected_ans_option.append(ans)
            selected_ans_index.append(answer_map.get(ans, -1))  # Append the mapped index for grading


        right_ans = 0
        wrong_ans = 0
        not_answered = 0

        ### CALCULATING GRADE ###
        score = []
        for i in range(questions):
                    if selected_ans_index[i] == -1:  # Check if no answer was selected
                        score.append("N")
                        not_answered += 1
                    elif selected_ans_index[i] == correct_ans[i]:  # Compare using selected_ans_indices for correct indexing
                        score.append("R")
                        right_ans += 1
                    else:
                        score.append("W")
                        wrong_ans += 1

        print("\nAns : \n",selected_ans_option,"\n\n(R/W/N) : ",score,"\n\nIndex : ",selected_ans_index)

        # Calculate grade based on the count of 'R' in score
        grade = (score.count("R") / questions) * 100
        print("\n\nFinal Percentage: ", grade)


        ### Show The answers and final Score ###
        # Slice the indices for warp_1 and warp_2
        set_1_ans_selected = selected_ans_index[:len(selected_ans_index) // 2]  # First half
        set_2_ans_selected = selected_ans_index[len(selected_ans_index) // 2:]  # Second half

        img_result_1 = imgWarpColored_1.copy()
        img_result_2 = imgWarpColored_2.copy()

        img_result_1 = utlis.output_answers(img_result_1,set_1_ans_selected,
            score[:((questions)//2)],correct_ans[:((questions)//2)],(questions//2),choices)

        img_result_2 = utlis.output_answers(img_result_2,set_2_ans_selected,
            score[((questions)//2):],correct_ans[((questions)//2):],(questions//2),choices)


        ### MAKING INVERSE PERSPECTIVE to display FINAL answers in score box ###
        img_raw_draw_1 = np.zeros_like(imgWarpColored_1)
        img_raw_draw_2 = np.zeros_like(imgWarpColored_2)        
        
        img_raw_draw_1 = utlis.output_answers(img_raw_draw_1,set_1_ans_selected,
            score[:((questions)//2)],correct_ans[:((questions)//2)],(questions//2),choices)   
        
        img_raw_draw_2 = utlis.output_answers(img_raw_draw_2,set_2_ans_selected,
            score[:((questions)//2)],correct_ans[:((questions)//2)],(questions//2),choices)
        

        # Compute INVERSE perspective transforms to blank image
        inv_mcq_1_matrix = cv2.getPerspectiveTransform(pt_dst,pt_mcq1_2)
        inv_mcq_2_matrix = cv2.getPerspectiveTransform(pt_dst,pt_mcq1_1)

        # Apply warping with the desired output size
        imgInvWarp_1 = cv2.warpPerspective(img_raw_draw_1, inv_mcq_1_matrix, (width, height))
        imgInvWarp_2 = cv2.warpPerspective(img_raw_draw_2, inv_mcq_2_matrix, (width, height))

        # Make a copy of the original image
        imgInvpers = img.copy()  

        # Create masks to isolate markings in each warped image
        mask_1 = cv2.threshold(cv2.cvtColor(imgInvWarp_1, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)[1]
        mask_2 = cv2.threshold(cv2.cvtColor(imgInvWarp_2, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)[1]

        # Use the masks to combine markings with the original image
        imgInvpers = cv2.bitwise_and(imgInvpers, imgInvpers, mask=cv2.bitwise_not(mask_1))  # Mask out where markings will go
        imgInvpers = cv2.add(imgInvpers, imgInvWarp_1)  # Add first markings layer

        imgInvpers = cv2.bitwise_and(imgInvpers, imgInvpers, mask=cv2.bitwise_not(mask_2))  # Mask out for second markings layer
        imgInvpers = cv2.add(imgInvpers, imgInvWarp_2)  # Add second markings layer


        ### Displaying grade using inverse prspective###
        img_raw_grade = np.zeros_like(score_display)
        cv2.putText(img_raw_grade,str(float(grade))+"%",(120,140),cv2.FONT_HERSHEY_COMPLEX,3,(255,0,0),5)

        inv_score_matrix = cv2.getPerspectiveTransform(pt_score_2,pt_score_1)
        inv_score_display = cv2.warpPerspective(img_raw_grade, inv_score_matrix, (width,height))

        # Step 1: Create a mask for the grade display
        mask_grade = cv2.threshold(cv2.cvtColor(inv_score_display, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)[1]

        # Step 2: Mask out the area in imgInvpers where the grade display will go
        imgInvpers = cv2.bitwise_and(imgInvpers, imgInvpers, mask=cv2.bitwise_not(mask_grade))

        # Step 3: Overlay the grade display onto imgInvpers
        imgInvpers = cv2.add(imgInvpers, inv_score_display)

# Prepare image stacks for display
img_blank = np.zeros_like(img)
img_inp = ([img, img_gray, img_blur], [img_canny, img_contours, img_largest_contours])
img_pro = ([imgWarpColored_1,imgThresh1,img_result_1,imgWarpColored_2,imgThresh2,img_result_2])
img_inv_pro = ([imgInvWarp_1,imgInvWarp_2,imgInvpers])
img_final_otp = ([img,imgInvpers])

# Stack images for display
inp_img_stack = utlis.stackImages(img_inp, 0.5)
pro_img_stack = utlis.stackImages(img_pro, 0.5)
inv_pro_img_stack = utlis.stackImages(img_inv_pro, 0.7)
final_img_stack = utlis.stackImages(img_final_otp, 0.7)

# Display the results
cv2.imshow("Input", inp_img_stack)
cv2.imshow("Processing & Output", pro_img_stack)
cv2.imshow("Inverse Processing", inv_pro_img_stack)
cv2.imshow("Final Score", final_img_stack)

# Save all the images
output_folder = "Output Images"
os.makedirs(output_folder, exist_ok=True)

# Save each image to the output folder
cv2.imwrite(os.path.join(output_folder, "PreProcessing_Contours.jpg"), inp_img_stack)
cv2.imwrite(os.path.join(output_folder, "Processing_Output.jpg"), pro_img_stack)
cv2.imwrite(os.path.join(output_folder, "Inverse_Processing.jpg"), inv_pro_img_stack)
cv2.imwrite(os.path.join(output_folder, "Final_Score.jpg"), final_img_stack)

OCR.OCR_img(path)
OCR.db_connect(selected_ans_option,right_ans,wrong_ans,not_answered,grade)
cv2.waitKey(0)
cv2.destroyAllWindows()