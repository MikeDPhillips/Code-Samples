# -*- coding: utf-8 -*-
""" 
This script performs various operations on MRI T1 scans and their segmentations.
It includes functions to:
- Reorient the raw files to standard orientation
- Create an overlay of the original T1 scans and the segmentations
- View the mid-slice of each scan, with or without overlay of the segmentation
- View all slices of each scan, with or without overlay of the segmentation
- Create a Hugging Face dataset (JSON) based on the axial, sagittal, and coronal segmented views

The script requires the following customization:
- SOURCE_PATH: Location of the scan and segmentation files
- MATCH_STRING: String to find the nii.gz files recursively
- T1_LABEL_FILE: File containing the label volumes for the T1 scans
- OUTPUT_DIR: Directory to save the processed files

To use the script, simply run the main() function.

Note: Edit the show_slices() function to customize the display of the slices for simple viewing.
      Edit save_t1_slices_and_labels() to customize options for saving the slices in the dataset.

@author: Mike Phillips, MASI Lab, Vanderbilt University
"""
import os
import csv
import glob
import json
import shutil
from fsl.wrappers.misc import fslreorient2std
import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib

# Customize the following to your environment:
SOURCE_PATH = "CIBS_BRAIN2/Resources"  # Location of the scan and segmentation files
MATCH_STRING = "**/NIFTI/*.nii.gz"  # string to find the nii.gz files recursively
T1_LABEL_FILE = "T1_label_volumes.txt"
OUTPUT_DIR = "slice_data"
OUTPUT_SIZE = (256, 256)
IMG_DPI = 96


def main():
    """
    Main function that performs the MRI T1 segmentation overlay process.

    This function performs the following steps:
    1. Retrieves a list of scan directories.
    2. Retrieves a list of matching filenames within the scan directories.
    3. Reorients the raw files to standard orientation (if necessary).
    4. Optionally shows the mid-slice of each scan.
    5. Creates an overlay of the original T1 scans and the segmentations.
    6. Saves
    7. Creates a Hugging Face dataset based on the segmented views.

    Args:
        None

    Returns:
        None
    """
    dirs = get_list_of_scan_dirs(SOURCE_PATH)
    filenames = get_matching_filenames(dirs, MATCH_STRING, True)

    # Note raw files need to be reoriented to standard orientation
    # If already processed comment out the next line
    reorient_files(filenames, True)

    # If you wish to view the mid-slice of each scan, uncomment the next line
    # show_mid_slice_from_all(filenames, Save=False)

    # Create the overlay of the original T1 scans and the segmentations
    csv_file = os.path.join(SOURCE_PATH, T1_LABEL_FILE)
    result_dict = create_dict_from_csv(csv_file)
    result_dir = os.path.join(SOURCE_PATH, OUTPUT_DIR)
    process_all(dirs, result_dict, result_dir)

    # Create the Hugging Face dataset (JSON) based on the axial, sagittal,
    # and coronal segmented views
    # For more info see https://huggingface.co/docs/datasets/loading_datasets
    # create a dataset for all views (axial, sagittal, coronal)
    create_hf_dataset(result_dir, os.path.join(result_dir, "hf"), "brain2_all.jsonl")

    # Use below if you wish to create a separate datasets for a given view
    # create_view_dataset(result_dir, result_dir, "axial", "brain2_axial.jsonl")

    print("Done!")


def get_image_files_for_dataset(input_dir, view="all"):
    """
    Get a list of all T1 PNG files for a given dataset directory and view.

    Args:
        input_dir (str): The directory path where the image files are located.
        view (str, optional): The desired view of the images. Defaults to "all".

    Returns:
        list: A list of image file paths.
    """
    image_files = [
        img
        for img in glob.glob(os.path.join(input_dir, "*.png"))
        if "SEGMENT" not in img
    ]
    if view == "axial":
        image_files = [img for img in image_files if "axial" in img]
    elif view == "sagittal":
        image_files = [img for img in image_files if "sagittal" in img]
    elif view == "coronal":
        image_files = [img for img in image_files if "coronal" in img]

    return image_files


def create_hf_dataset(image_files, output_dir, json_file_name="brain2.jsonl"):
    """
    Create a Hugging Face dataset from a list of image files.
    For more info see https://huggingface.co/docs/datasets/loading_datasets

    Args:
        image_files (list): List of image file paths.
        output_dir (str): Output directory for the dataset.
        json_file_name (str, optional): Name of the JSONL file. Defaults to "brain2.jsonl".
    """

    os.makedirs(output_dir, exist_ok=True)
    # Create a JSONL file for the Hugging Face dataset
    output_file = os.path.join(output_dir, json_file_name)
    with open(output_file, "w", encoding="utf-8") as jsonl_output:
        for i, image_file in enumerate(image_files):
            if i % 1000 == 0:
                print(f"Files remaining: {len(image_files) - i}")
            filename = os.path.basename(image_file)
            # Get the corresponding text file for the image
            txt_file = os.path.splitext(image_file)[0] + ".txt"
            # Read the text file with specified encoding
            with open(txt_file, "r", encoding="utf-8") as txt_input:
                labels = [label.strip() for label in txt_input.readlines()]

            # Write the image path and labels to the JSONL file
            json_line = {"file_name": filename, "text": labels}
            jsonl_output.write(json.dumps(json_line) + "\n")
            # move the image file to the output directory
            shutil.copy(image_file, output_dir)


def create_view_dataset(
    input_dir, output_dir, view="axial", json_file_name="brain2.jsonl"
):
    """
    Creates a hugging face dataset for a specific view of MRI images.

    Args:
        input_dir (str): The directory containing the input MRI images.
        output_dir (str): The directory where the dataset will be created.
        view (str, optional): The desired view of the MRI images. Defaults to "axial".
        json_file_name (str, optional): The name of the JSON file to store the dataset. 
                Defaults to "brain2.jsonl".

    Returns:
        None
    """
    image_files = get_image_files_for_dataset(input_dir, view)
    create_hf_dataset(image_files, output_dir, json_file_name)
    print(f"Created dataset for {view} view in {output_dir}")


def process_all(directory_list, result_dict, output_dir="slice_data"):
    """
    Save T1 slices with segmentation labels for all MRI scans in the given directory list.

    Args:
        directory_list (list): List of directories containing MRI scans.
        result_dict (dict): Dictionary to store the results.
        output_dir (str, optional): Output directory to save the processed data. 
            Defaults to "slice_data".
    """

    for i, d in enumerate(directory_list):
        print(f"Processing {d}... Remaining: {len(directory_list) - i}")
        path, sess_id = os.path.split(d)
        path, subj_id = os.path.split(path)
        scan_paths = [x for x in os.listdir(d) if x[0].isdigit()]
        scan_ids = [x.split("-")[0] for x in scan_paths]
        if not scan_ids:  # if empty
            continue

        for scan_id in scan_ids:
            print(f"Subject ID: {subj_id}, Session ID: {sess_id}, Scan ID: {scan_id}")
            search_pattern = os.path.join(d, f"*{scan_id}*/NIFTI/*.nii.gz")
            matching_files = glob.glob(search_pattern)

        if len(matching_files) == 0 or len(matching_files) > 2:
            print(
                "WARNING for ", d, ": ", len(matching_files), " matching files found!"
            )
            continue

        for f in matching_files:
            if "seg" in f:
                seg_path = f
            else:
                mri_path = f

        save_t1_slices_and_labels(
            mri_path, seg_path, output_dir, result_dict, subj_id, scan_id, True
        )


def create_dict_from_csv(csv_file):
    """
    Creates a dictionary from a CSV file that relates label indices to label names.

    Args:
        csv_file (str): The path to the CSV file from the slant T1 segmentation.

    Returns:
        dict: A dictionary where the keys are integers and the values are strings.
    """
    result_dict = {}

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip the header row (column labels)
        next(csvreader)
        for row in csvreader:
            key = int(row[1])
            value = row[0]
            result_dict[key] = value

    return result_dict


def save_t1_slices_and_labels(
    mri_file,
    seg_file,
    output_dir,
    label_dict,
    subject_id="",
    scan_id="",
    save_labels=False,
):
    """
    Save slices of MRI and corresponding segmentation labels as images.

    Note: size and DPI are set as global variables at the top of the script.

    Args:
        mri_file (str): Path to the MRI NIfTI file.
        seg_file (str): Path to the segmentation NIfTI file.
        output_dir (str): Directory to save the output images.
        label_dict (dict): Dictionary mapping label indices to label names.
        subject_id (str, optional): Subject ID. Defaults to ''.
        scan_id (str, optional): Scan ID. Defaults to ''.
        save_labels (bool, optional): Whether to save the labels as text files. Defaults to False.
    """
    # Load the MRI NIfTI file
    mri_img = nib.load(mri_file)
    seg_img = nib.load(seg_file)
    # Get the MRI data array
    mri_data = mri_img.get_fdata()
    seg_data = seg_img.get_fdata()
    labels = []
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set the desired output size
    output_size = OUTPUT_SIZE
    DPI = IMG_DPI
    # get the subject name to use for the file
    subject_name = f"cb2_{subject_id}_{scan_id}"

    #we will use the index of the view to determine how to rotate and display image
    _sagittal = 0
    _coronal = 1
    _axial = 2
    for view, view_label in enumerate(["sagittal", "coronal", "axial"]):
        # print(f"Number of slices for {view_label}: {mri_data.shape[view]} ")

        for i in range(mri_data.shape[view]):
            fig, ax = plt.subplots(
                figsize=(output_size[0] / DPI, output_size[1] / DPI),
                dpi=DPI,
                facecolor="black",
            )
            fig2, ax2 = plt.subplots(
                figsize=(output_size[0] / DPI, output_size[1] / DPI),
                dpi=DPI,
                facecolor="black",
            )

            if view == _sagittal:
                ax.imshow(np.rot90(mri_data[i, :, :], 3), cmap="gray", origin="lower")
                ax2.imshow(np.rot90(seg_data[i, :, :], 3), cmap="gray", origin="lower")
                slice_labels = np.unique(seg_data[i, :, :])
            elif view == _coronal:
                ax.imshow(np.rot90(mri_data[:, i, :]), cmap="gray", origin="lower")
                ax2.imshow(np.rot90(seg_data[:, i, :]), cmap="gray", origin="lower")
                slice_labels = np.unique(seg_data[:, i, :])
            elif view == _axial:
                ax.imshow(np.rot90(mri_data[:, :, i]), cmap="gray")
                ax2.imshow(np.rot90(seg_data[:, :, i]), cmap="gray", origin="lower")
                slice_labels = np.unique(seg_data[:, :, i])
            ax.axis("off")
            ax2.axis("off")
            labels = [int(x) for x in slice_labels[slice_labels > 0]]

            if len(labels) == 0:
                continue
            filename = os.path.join(
                output_dir, f"{subject_name}_{view_label}_{i:03d}.png"
            )
            fig.savefig(filename, dpi=fig.dpi, format="png")
            filename2 = os.path.join(
                output_dir, f"{subject_name}_{view_label}_{i:03d}_SEGMENT.png"
            )
            fig2.savefig(filename2, dpi=fig2.dpi, format="png")
            plt.close("all")

            # Save labels as text file
            if save_labels:
                string_labels = [label_dict[i] for i in labels]
                # print(subject_name, view, i, ','.join(string_labels))
                with open(filename.replace(".png", ".txt"), "w", encoding="utf-8") as f:
                    for label_line in string_labels:
                        f.write(f"{label_line}\n")
        fig.clear()
        fig2.clear()
        plt.close("all")

# UTILITIES to get list of directories and matching filenames assuming MASI 
# lab standard file structure
# <root>/<subject_id>/<session_id>/<scan_id>/NIFTI/*.nii.gz
def get_list_of_scan_dirs(path):
    """
    Retrieves a list of directories containing scan data.

    Args:
        path (str): The path to the root directory containing the scan data.

    Returns:
        list: A sorted list of directories containing scan data.
    """
    dirs_to_process = []
    first_level_dirs = [
        os.path.join(path, d)
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ]
    second_level_dirs = []
    for first_level_dir in first_level_dirs:
        subdirs = [
            os.path.join(first_level_dir, d)
            for d in os.listdir(first_level_dir)
            if os.path.isdir(os.path.join(first_level_dir, d))
        ]
        second_level_dirs.extend(subdirs)
    dirs_to_process = sorted(second_level_dirs)
    return dirs_to_process


def get_matching_filenames(dirs_to_process, pattern, verbose=False):
    """
    Retrieves a list of filenames that match the given pattern within the specified directories.

    Args:
        dirs_to_process (list): List of directories to search for matching files.
        pattern (str): Pattern to match filenames against.
        verbose (bool, optional): If True, prints additional information during processing. 
                Defaults to False.

    Returns:
        list: List of filenames that match the given pattern.
    """
    matching_files = []
    for d in dirs_to_process:
        if verbose:
            print(f"Processing {d}...")
        path, scan_id = os.path.split(d)
        path, subj_id = os.path.split(path)
        if verbose:
            print(f"Subject ID: {subj_id}, Scan ID: {scan_id}")
        search_pattern = os.path.join(d, pattern)
        matching_files += [x for x in glob.glob(search_pattern, recursive=True)]
    return matching_files


def reorient_files(filenames, verbose=False):
    """
    Reorients the given list of files using FSL's fslreorient2std tool.
    Learn more about orientation issues here:
    https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Orientation%20Explained

    Args:
        filenames (list): A list of file paths to be reoriented.
        verbose (bool, optional): If True, prints progress information. Defaults to False.
    """
    total = len(filenames)
    for i, f in enumerate(filenames):
        if verbose:
            print(f"Reorienting {f} ({i+1}/{total})")
        fslreorient2std(f, f)


# UTILITIES TO DISPLAY SLICES
def show_slices(slices, label, save=False):
    """
    Function to display row of image slices

    Parameters:
    slices (list): List of image slices to be displayed.
    label (str): A label of the brain segments contained in this slice.
    save (bool, optional): Flag indicating whether to save the figure as a PNG file. 
            Default is False.

    Usage note: Read up on imshow() to see how to customize the display.
    See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html for more info.
    Returns:
    None
    """

    fig, axes = plt.subplots(1, len(slices))
    axes[0].set_title(label, color="black", fontsize=20, fontweight="bold")
    for i, slice_img in enumerate(slices):
        axes[i].imshow(
            slice_img.T,
            cmap="gray",
            origin="lower",
        )
    if save:
        fig.savefig(f"{label}.png", bbox_inches="tight")
    plt.close(fig)


def show_mid_slice_from_all(filenames, save=False, include_seg=False):
    """
    Display the middle slice from each MRI file in the given list of filenames.

    Parameters:
    - filenames (list): A list of file paths to MRI files.
    - save (bool): Optional. If True, save the displayed slices as images. Default is False.
    - include_seg (bool): Optional. If True, include segmentation files in the display. 
            Default is False.
    """

    if not include_seg:
        filenames = [f for f in filenames if "slant" not in f]
    for f in filenames:
        path = os.path.split(f)[0]
        path, scan_id = os.path.split(path)
        path, subj_id = os.path.split(path)
        label = f"{subj_id.split('_')[0]}SLANT{scan_id}"
        mri = nib.load(f)
        mri_data = mri.get_fdata()
        x, y, z = [int(x / 2) for x in mri_data.shape]
        x_slice = mri_data[x, :, :]
        y_slice = mri_data[:, y, :]
        z_slice = mri_data[:, :, z]
        show_slices([x_slice, y_slice, z_slice], label, save)


if __name__ == "__main__":

    main()
