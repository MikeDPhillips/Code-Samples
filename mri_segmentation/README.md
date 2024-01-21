Here's a README.md for your Python script used in the digital imaging deep learning lab:

---

# MRI T1 Scan Segmentation and Dataset Creation Script
## Author
- **Author:** Mike Phillips, MASI Lab, Vanderbilt University

## Overview
This Python script is an integral tool in our digital imaging deep learning lab at Vanderbilt University. Developed by Mike Phillips from the MASI Lab, the script is designed to process MRI T1 scans using SLANT-generated segmentation results. The primary function is to overlay these segmentation results on the original T1 slices, label each slice with the segments it contains, and generate datasets in the Hugging Face format. This dataset serves as a foundation for fine-tuning a stable-diffusion 2 AI model, which is then used for dynamic brain segment image generation.


## Key Functionalities
- **Standard Orientation Reorientation:** Reorients raw MRI files to a standard orientation for uniform processing.
- **Segmentation Overlay:** Creates overlays of original T1 scans with their segmentations, providing detailed views of brain segments.
- **Slice Viewing and Labeling:** Views the mid-slice or all slices of each scan, with or without segmentation overlay, and labels each slice based on the contained segments.
- **Hugging Face Dataset Creation:** Generates a labeled dataset in the Hugging Face format, based on axial, sagittal, and coronal segmented views, for subsequent AI model training.


## Relevance to Data Science and Programming Roles

### Data Handling and Processing
- **Complex Data Manipulation:** This script demonstrates the ability to handle and manipulate complex medical imaging data, a skill highly applicable in data science roles requiring advanced data processing capabilities.
- **Data Cleaning and Standardization:** Reorienting raw MRI files to a standard orientation is akin to data cleaning and normalization, essential steps in any data science workflow.

### Innovation in Imaging and AI
- **Interdisciplinary Application:** The script's use in fine-tuning AI models for dynamic brain segment image generation highlights innovative applications of programming and data science in medical imaging and artificial intelligence research.

### Broader Impact
- The methodologies and skills demonstrated in this script have broad applications beyond medical imaging, including areas like automated image analysis, pattern recognition, and development of AI-driven diagnostic tools, making it highly relevant for a variety of data science and programming roles.


## Customization and Usage
- **Customizable Paths:** Users can customize `SOURCE_PATH`, `MATCH_STRING`, `T1_LABEL_FILE`, and `OUTPUT_DIR` for their specific environment and dataset.
- **Adaptable Functions:** Functions such as `show_slices()` and `save_t1_slices_and_labels()` are designed for easy modification to suit different research requirements.

## Target Users
This script is primarily used by a small team of AI researchers within our lab. It is crafted to function as a flexible, yet powerful tool for automated analysis without the need for a command-line interface. Documentation within the script guides users on how to alter results and functionalities to meet their specific research objectives.

## How to Run
Simply execute the `main()` function of the script. Ensure that all necessary files and directories as per the customization requirements are correctly set up.

__

Certainly! Here's an outline for the MRI T1 Scan Segmentation and Dataset Creation script, which can be included in the README:

---

## Script Outline

### Initialization and Imports
- **Encoding and Authorship Information:** Includes metadata about the script's encoding and authorship.
- **Import Statements:** Incorporates essential Python libraries and modules necessary for the script’s functionalities.

### Customization Parameters
- **Source Path and File Specifications:** Sets variables like `SOURCE_PATH`, `MATCH_STRING`, `T1_LABEL_FILE`, and `OUTPUT_DIR` for user customization.

### Main Function
- **Directory and File Retrieval:** Retrieves a list of scan directories and matching filenames within these directories.
- **Reorientation of Files:** Implements a function to reorient raw files to a standard orientation, ensuring uniform processing across scans.
- **Mid-slice and Full-scan Visualization:** Provides options to display either the mid-slice or all slices of each scan, with options for overlaying segmentation results.
- **Dataset Creation:** Generates a Hugging Face dataset in JSON format, based on segmented views from the MRI scans.

### Utility Functions
- **Image File Retrieval for Dataset:** Function to get all relevant T1 PNG files for dataset creation.
- **Hugging Face Dataset Creation:** Assembles a Hugging Face compatible dataset from the list of image files, demonstrating skills in data preparation for machine learning applications.
- **View-Specific Dataset Creation:** Offers the ability to create datasets for specific views (axial, sagittal, coronal) of MRI images.

### Data Processing Functions
- **Process All Scans:** Processes all MRI scans in the given directory list, saving T1 slices with segmentation labels.
- **Dictionary Creation from CSV:** Parses a CSV file to create a dictionary relating label indices to label names, used for labeling the dataset.
- **Save Slices and Labels:** Saves slices of MRI and corresponding segmentation labels as images, setting the foundation for dataset creation.

### Display Utilities
- **Show Slices:** A utility function to display a row of image slices, aiding in visualization and analysis.
- **Show Mid Slice from All:** Displays the middle slice from each MRI file, an essential step in preliminary data analysis and verification.

### Execution Block
- **Main Script Execution:** When run, the script executes the main function, processing MRI scans according to the specified parameters and user customizations.