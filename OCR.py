import cv2
import pytesseract as pt
import numpy as np
import utlis
import os
import mysql.connector

output_folder = "Output Images"
os.makedirs(output_folder, exist_ok=True)

# Configure Tesseract path
pt.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
per = 15  # Lowered to ensure more good matches

# Dictionary to store extracted text for fields
form_data = {"Name": "", "Date": "", "Subject": "", "Rollno": ""}

# Function to extract text from a given image region
def extract_text_from_roi(img_path):
    roi = cv2.imread(img_path)

    if roi is None or roi.size == 0:
        print(f"Error reading image from {img_path}. Skipping...")
        return ""

    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi_thresh = cv2.adaptiveThreshold(roi_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    text = pt.image_to_string(roi_thresh)
    text = text.replace("|", "").replace("\n", "").strip()
    return text

def OCR_img(path):
    # Load the template image and form to process
    template_img = cv2.imread('template.png')
    h, w, c = template_img.shape
    template_img_resized = cv2.resize(template_img, (w // 3, h // 3))

    orb = cv2.ORB_create(7000)
    key_pt_1, descriptor_1 = orb.detectAndCompute(template_img_resized, None)

    # Folder to save contour images
    contour_folder = 'Contours'
    if not os.path.exists(contour_folder):
        os.makedirs(contour_folder)

    img = cv2.imread(path)
    img = cv2.resize(img, (w // 3, h // 3))

    key_pt_2, descriptor_2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = list(bf.match(descriptor_2, descriptor_1))
    matches.sort(key=lambda x: x.distance)
    good_match = matches[:int(len(matches) * (per / 100))]

    img_match = cv2.drawMatches(img, key_pt_2, template_img_resized, key_pt_1, good_match[:100], None, flags=2)
    cv2.imshow("Good Matches", img_match)
    cv2.waitKey(0)

    if len(good_match) >= 4:
        srcPoints = np.float32([key_pt_2[m.queryIdx].pt for m in good_match]).reshape(-1, 1, 2)
        destPoints = np.float32([key_pt_1[m.trainIdx].pt for m in good_match]).reshape(-1, 1, 2)
        M, _ = cv2.findHomography(srcPoints, destPoints, cv2.RANSAC, 5.0)
        imgScan = cv2.warpPerspective(img, M, (w // 3, h // 3))

        h, w, c = imgScan.shape
        new_img = imgScan[40:(h - 100), 0:(w // 2) - 60]
        img_contours = new_img.copy()
        warp_img = new_img.copy()
        cv2.imshow("Aligned and Cropped Form", new_img)

        img_gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray,(5,5),1)
        img_canny = cv2.Canny(img_blur,10,50)
        
        contours, _ = cv2.findContours(img_canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
        # Find rectangular contours
        rect_contours = utlis.rectContour(contours)

        # Calculate areas and get corner points
        contour_info = []
        for contour in rect_contours:
            area, corner_points = utlis.getCornerPoints(contour)
            contour_info.append({"area": area, "corner_points": corner_points})

        # Sort the contours by area
        contour_info.sort(key=lambda x: x["area"])

        # Remove the two largest contours
        if len(contour_info) > 2:
            contour_info = contour_info[:-2]  # Keep all but the last two (largest)

        # Print out the information for the remaining contours and save warped images
        for idx, contour in enumerate(contour_info):
            print(f"\nContour {idx + 1}:\nArea: {contour['area']}\nCorner Points: {contour['corner_points']}")
            cv2.drawContours(img_contours, [contour["corner_points"]], -1, (0, 255, 0), 3)
            contour["corner_points"] = utlis.reorder(contour["corner_points"])

            # Set the custom output sizes you want
            output_width, output_height = 350, 100

            # Convert corner points to float32 for perspective transform
            pt_mcq1_1 = np.float32(contour["corner_points"])

            # Define destination points for a full rectangle with custom size
            pt_dst = np.float32([[0, 0], [output_width, 0], [0, output_height], [output_width, output_height]])

            # Compute perspective transforms
            mcq_1_matrix = cv2.getPerspectiveTransform(pt_mcq1_1, pt_dst)

            # Apply warping with the desired output size
            imgWarpColored_1 = cv2.warpPerspective(warp_img, mcq_1_matrix, (output_width, output_height))

            # Save the warped image in the "Contours" folder
            warped_image_path = os.path.join(contour_folder, f"contour_{idx + 1}.png")
            cv2.imwrite(warped_image_path, imgWarpColored_1)
            cv2.imwrite(os.path.join(output_folder, f"ocr_contour_{idx + 1}.png"),imgWarpColored_1)

        # Draw remaining contours on the image
        cv2.imshow("Remaining Rectangular Contours", img_contours)
        cv2.waitKey(0)
        cv2.imwrite(os.path.join(output_folder, "Remaining Rectangular Contours.png"),img_contours)

        # Expected order of contour files for mapping to dictionary keys
        fields = list(form_data.keys())

        # Display, extract, and assign text to fields
        for idx, filename in enumerate(os.listdir(contour_folder)):
            if filename.endswith('.png') and idx < len(fields):
                img_path = os.path.join(contour_folder, filename)

                # Display the contour image
                img = cv2.imread(img_path)
                cv2.imshow(f"Contour: {filename}", img)
                cv2.imwrite(os.path.join(output_folder, f"Contour: {filename}"), img)
                cv2.waitKey(0)  # Wait for a key press

                # Extract text and save to dictionary
                extracted_text = extract_text_from_roi(img_path)
                form_data[fields[idx]] = extracted_text
                print(f"Extracted text for {fields[idx]}: {extracted_text}")

    # Display the populated dictionary
    print("\nExtracted Form Data:")
    print(form_data)
    # Clean up the display
    cv2.destroyAllWindows()

def calculate_grade(right_ans, total_questions=40):
    percentage = (right_ans / total_questions) * 100

    if percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 50:
        return 'C'
    elif percentage >= 40:
        return 'D'
    else:
        return 'F'


import mysql.connector

def db_connect(selected_ans_option, right_ans, wrong_ans, not_answered, score):
    # Calculate the grade based on the score
    grade = calculate_grade(right_ans)

    # Connect to MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",     
        password="", 
        database="MCQ_Test_data",
        port="3306"
    )

    # Insert data into the database
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO student_scores (Name, Rollno, Subject, Date, Score, Grade, Selected_Answers, Right_Ans, Wrong_Ans, Not_Answered)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convert selected_ans_option (assumed to be a list) to a string
        selected_answers_str = ', '.join(map(str, selected_ans_option))  # Convert each element to string and join
        
        # Prepare the data for insertion
        data = (
            form_data['Name'],              # Ensure this is a string
            form_data['Rollno'],            # Ensure this is a string
            form_data['Subject'],           # Ensure this is a string
            form_data['Date'],              # Ensure this is a string
            score,                          # Ensure this is an integer
            grade,                          # Grade calculated from the score
            selected_answers_str,           # String version of selected answers
            right_ans,                      # Ensure this is an integer
            wrong_ans,                      # Ensure this is an integer
            not_answered                    # Ensure this is an integer
        )
        
        cursor.execute(insert_query, data)
        connection.commit()
        print("Data inserted successfully.")
    except mysql.connector.Error as error:
        print(f"Failed to insert data: {error}")
    finally:
        cursor.close()
        connection.close()