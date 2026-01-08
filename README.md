Based on your repository, I've created a comprehensive README file below. It explains the project, its structure, and how to set it up.

# 📝 Automated OMR Sheet Grading System

An image processing and computer vision project designed to automatically grade scanned Optical Mark Recognition (OMR) sheets using contour detection and analysis.

## 📖 Overview

This system processes scanned OMR answer sheets to detect and evaluate marked responses automatically. By leveraging computer vision techniques, it eliminates manual grading efforts and provides accurate, efficient assessment of multiple-choice questionnaires.

## ✨ Key Features

- **Automated OMR Processing**: Detects and analyzes marked bubbles on answer sheets
- **Contour-based Detection**: Uses advanced contour analysis to identify answer regions
- **Template Matching**: Aligns scanned sheets with a reference template for accurate grading
- **Database Integration**: Includes SQL scripts for storing and managing results
- **Visual Output**: Generates processed images showing detected contours and marked answers

## 📁 Project Structure

```
Automated_OMR_Sheet_Grading_System/
│
├── Contours/                    # Contour detection and processing modules
├── Input Images/                # Folder for raw OMR sheet scans to process
├── Output Images/               # Processed results and visual outputs
│
├── OCR.py                       # Optical Character Recognition module
├── OMR_img.py                   # Main OMR processing and grading logic
├── utlis.py                     # Utility functions and helpers
├── template.png                 # Reference OMR sheet template
├── create_table.sql             # Database schema for storing results
├── .gitignore                   # Git exclusion rules
│
└── C171_C177_C195_C196_IVP_Research_Paper.pdf  # Related research paper
```

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- OpenCV (cv2)
- NumPy
- Other dependencies as required by the scripts

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nitya-Nivdunge/Automated_OMR_Sheet_Grading_System.git
   cd Automated_OMR_Sheet_Grading_System
   ```

2. **Install required packages**
   ```bash
   pip install opencv-python numpy
   ```

3. **Set up your database** (if using database features)
   ```bash
   # Run the SQL script to create necessary tables
   ```

### Usage

1. **Place your OMR sheet images** in the `Input Images/` folder

2. **Run the main OMR processing script**:
   ```bash
   python OMR_img.py
   ```

3. **Check the results** in the `Output Images/` folder and database

4. **For OCR functionality** (if needed):
   ```bash
   python OCR.py
   ```

## 🔧 How It Works

1. **Image Preprocessing**: The system loads and preprocesses the scanned OMR sheet
2. **Template Alignment**: Aligns the input sheet with the reference template
3. **Contour Detection**: Identifies all potential answer bubbles using contour analysis
4. **Bubble Analysis**: Determines which bubbles are filled/marked
5. **Grading Logic**: Compares detected answers with answer key
6. **Result Output**: Saves processed images and stores scores

## 📊 Expected Results

The system generates:
- Processed images with detected contours highlighted
- Grading results for each OMR sheet
- Structured data suitable for database storage
- Visual feedback on marked answers

## 📚 Technical Details

- **Primary Language**: Python
- **Core Libraries**: OpenCV for computer vision tasks
- **Processing Method**: Contour-based detection and analysis
- **Output Formats**: Processed images, database records

## 🔮 Future Enhancements

Consider expanding this project with:
- Web interface for easy upload and grading
- Support for different OMR sheet formats
- Export functionality (PDF reports, Excel sheets)
- Batch processing of multiple sheets
- Enhanced error handling for poor-quality scans

## 📄 License

This project is available for academic and educational purposes. For more details on usage rights, please refer to the included research paper.

## 👥 Contributors

- **Nitya Nivdunge** - Project developer

---

**Note**: For detailed understanding of the algorithms and methodologies, please refer to the included research paper `C171_C177_C195_C196_IVP_Research_Paper.pdf`.

I recommend copying this entire text into a file named `README.md` in your repository's root folder. The file will automatically display on your GitHub page.

Is there a specific section of the project you'd like me to explain in more detail, such as how the contour detection works or how to interpret the output?
