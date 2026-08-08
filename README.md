# 📝 Automated OMR Sheet Grading System

An automated system for grading Optical Mark Recognition (OMR) sheets using computer vision techniques. This project processes scanned answer sheets, detects marked responses, compares them against correct answers, and generates graded results with visual feedback.

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Output](#output)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Automated Answer Detection**: Uses contour analysis to identify and extract OMR bubbles
- **Perspective Correction**: Handles skewed/scanned images with perspective transformation
- **Smart Thresholding**: Adaptive detection of marked vs. unmarked bubbles
- **Answer Validation**: Compares student answers against provided answer key
- **Visual Feedback**: Generates color-coded results (Green=Correct, Red=Wrong, Blue=Unanswered)
- **OCR Integration**: Optional text recognition for additional processing
- **Database Storage**: Saves results to database for record-keeping
- **Multi-format Output**: Saves processed images at each pipeline stage

## 🏗️ System Architecture

### Processing Pipeline
1. **Image Preprocessing** → Grayscale conversion, Gaussian blur, Canny edge detection
2. **Contour Detection** → Finds all contours, identifies three largest rectangular regions
3. **Perspective Warping** → Corrects image perspective for consistent analysis
4. **Bubble Segmentation** → Splits OMR sheet into individual question cells
5. **Pixel Analysis** → Calculates marked bubbles using non-zero pixel counts
6. **Grading Logic** → Compares against answer key with confidence thresholding
7. **Visualization** → Overlays results on original image with score display

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for text recognition features)

### Step 1: Install Dependencies
```bash
pip install opencv-python numpy pytesseract
```

### Step 2: Install Tesseract OCR
- **Windows**: Download from [GitHub Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

### Step 3: Clone Repository
```bash
git clone https://github.com/Nitya-Nivdunge/Automated_OMR_Sheet_Grading_System.git
cd Automated_OMR_Sheet_Grading_System
```

## 🚀 Usage

### Basic Execution
1. Place your OMR sheet image in the `Input Images/` folder
2. Run the main script:
```bash
python OMR_img.py
```

### Interactive Input
When prompted:
1. Enter the number of questions on the sheet
2. Enter the correct answers (space-separated, e.g., `A B C D A B C D`)

### Example
```bash
$ python OMR_img.py
Enter no. of Questions: 20
Enter the answers of 20 questions: e.g., A B A D... (space-separated)
A A B B C C D B C A B B C A D B C D C C
```

### Processing Multiple Sheets
Modify the `path` variable in `OMR_img.py`:
```python
# Change this line to process different images
path = "Input Images/Stu_1.png"  # Change filename as needed
```

## 📁 Project Structure

```
Automated_OMR_Sheet_Grading_System/
├── OMR_img.py              # Main processing script (core functionality)
├── OCR.py                  # OCR and database integration module
├── utlis.py                # Utility functions for image processing
├── create_table.sql        # Database schema for storing results
├── template.png            # Reference template for OMR sheet
├── .gitignore              # Git exclusion rules
│
├── Input Images/           # Directory for input OMR sheets
│   └── Stu_1.png          # Example input image
│
├── Output Images/          # Processed results (auto-generated)
│   ├── PreProcessing_Contours.jpg
│   ├── Processing_Output.jpg
│   ├── Inverse_Processing.jpg
│   └── Final_Score.jpg
│
├── Contours/               # Contour processing modules
└── C171_C177_C195_C196_IVP_Research_Paper.pdf  # Research documentation
```

## ⚙️ Configuration

### Key Parameters in OMR_img.py
```python
# Image Settings
width = 600        # Resize width
height = 700       # Resize height

# Processing Parameters
threshold = 800    # Minimum pixel difference for confident answer detection
choices = 4        # Number of choices per question (A/B/C/D)

# Output Settings
output_width, output_height = 350, 1400  # Warped MCQ box dimensions
score_width, score_height = 450, 200     # Score box dimensions
```

### Customization Options
1. **Adjust Threshold Sensitivity**: Modify `threshold` variable for different lighting conditions
2. **Change Answer Mapping**: Update `answer_map` dictionary for different labeling schemes
3. **Modify Output Size**: Adjust warping dimensions for different OMR sheet formats

## 📊 Output

### Generated Files
1. **PreProcessing_Contours.jpg** - Edge detection and contour identification
2. **Processing_Output.jpg** - Warped images, thresholding, and answer marking
3. **Inverse_Processing.jpg** - Perspective-corrected visualizations
4. **Final_Score.jpg** - Original image with overlaid results and final score

### Console Output
```
Mapped answers to integers: [0, 0, 1, 1, 2, 2, 3, 1, 2, 0, ...]

MCQ 1 BOX:
Area: 12345
Corner Points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

Ans: ['A', 'A', 'B', 'None', ...]
(R/W/N): ['R', 'R', 'W', 'N', ...]
Index: [0, 0, 1, -1, ...]

Final Percentage: 85.0%
```

### Visual Indicators
- **Green Circle**: Correct answer
- **Red Circle**: Wrong answer  
- **Blue Circle**: Unanswered question
- **Red Box**: MCQ answer regions
- **Blue Box**: Score display region

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "No contours found" | Check image quality, adjust Canny edge thresholds |
| Incorrect answer detection | Modify `threshold` value in pixel analysis section |
| Perspective warp distortion | Ensure OMR sheet is properly aligned in image |
| Database connection errors | Verify database credentials in `OCR.py` |
| Tesseract OCR errors | Ensure Tesseract is installed and in system PATH |

### Debug Mode
For debugging, uncomment these lines in `OMR_img.py`:
```python
# cv2.imshow("Edge Detection : ",img_canny)
# cv2.waitKey(0)
```

## 📈 Performance Optimization

1. **Image Resolution**: For faster processing, reduce `width` and `height` values
2. **Batch Processing**: Modify script to loop through multiple images in `Input Images/` folder
3. **Parallel Processing**: Implement multi-threading for processing multiple sheets simultaneously

## 🔗 Dependencies

- **OpenCV 4.x**: Computer vision operations
- **NumPy 1.19+**: Numerical computations and array operations
- **PyTesseract**: OCR functionality (optional)
- **SQL Database**: MySQL/PostgreSQL for result storage

## 📝 License

Academic and educational use. See included research paper for detailed methodology.

## 👥 Contributors

- **Nitya Nivdunge** - Project Developer & Maintainer



### Quick Start Checklist
- [ ] Install Python dependencies
- [ ] Install Tesseract OCR (if using OCR features)
- [ ] Place OMR sheet in `Input Images/` folder
- [ ] Update `path` variable in `OMR_img.py` if needed
- [ ] Run `python OMR_img.py`
- [ ] Enter number of questions and answer key when prompted
- [ ] Check `Output Images/` folder for results

For detailed algorithm explanation, refer to `C171_C177_C195_C196_IVP_Research_Paper.pdf`.
