# XNAT Assessor Deletion Script

## Overview
This Python script is developed for use in my [current digital imaging deep learning lab at Vanderbilt](https://www.vanderbilt.edu/vise/tag/masi-lab/). Many in our lab as well as other groups use our cloud servers to run automated analysis of MRI images. One of the biggest issues is that due to the underlying [XNAT](https://www.xnat.org) implementation, any time an identifying label is changed the analysis is rerun and the older files remain on server but associated with no images. This script makes it easy to fix this either by deleting all assessors (the automated spiders that run the algorithms) before they change a label, or by searching for any already "orphaned" assessors and cleaning them up. This is a very time consuming process when done manually, but the automated script saves many hours per week and also reduces server resources (and costs) being wasted.

## Functionality
- **Delete Specific Assessors:** Allows deletion of all assessors from a list of subjects within specified projects.
- **Remove Orphaned Assessors:** Capable of identifying and deleting orphaned assessors that do not have proper subject or session labels.
- **Batch Processing:** Efficiently handles multiple assessors and subjects, ensuring a streamlined workflow for large datasets.

## Typical Usage
- To delete assessors from a list of subjects:
  ```
  python delete_assessors.py --projects CIBS_COPE CIBS_BRAIN2 --subjects VCP-002 VCP-003
  ```
- To delete assessors from a single subject:
  ```
  python delete_assessors.py --projects CIBS_COPE --subjects VCP-002
  ```
- To delete orphaned assessors:
  ```
  python delete_assessors.py --projects CIBS_COPE CIBS_BRAIN2
  ```

## Key Components
- **Command-Line Interface:** The script is accessed via a command-line interface, allowing for flexibility and ease of use in various computational environments.
- **Customizability:** Users can specify projects and subjects for which assessors need to be deleted, offering tailored functionality to meet different research needs.
- **Error Handling:** Incorporates error handling (such as ReadTimeout exceptions) to ensure robust performance even in cases of network issues.

## Requirements
- Python Environment
- Access to an XNAT server with appropriate permissions
- Required Python libraries: `requests`, `argparse`

## Author
Mike Phillips, MASI Lab, Vanderbilt University


---

## Script Outline: XNAT Assessor Deletion

1. **Introduction and Module-Level Docstring:**
   - The script begins with a module-level docstring detailing its purpose, typical usage, and author information. It sets the stage for its functionality in managing XNAT assessor objects.

2. **Import Statements:**
   - Essential modules and classes are imported at the start:
     - `my_utils`: Likely contains utility functions for XNAT interaction.
     - `ReadTimeout`: Exception handling from `requests.exceptions` for network issues.
     - `ArgumentParser`: From `argparse` module, to parse command-line arguments.

3. **Setting Default Projects:**
   - A constant variable `PROJECTS` is defined with default values `['CIBS_COPE', 'CIBS_BRAIN2']`, indicating the default projects to be included in the script's operations.

4. **XNAT Interface Initialization:**
   - The script initializes an XNAT interface instance using `my_utils.get_interface()`, which is crucial for the subsequent API interactions with XNAT.

5. **Function Definitions:**
   - `delete_assessor()`: A function that takes parameters `xnat`, `proj`, `subj`, `sess`, and `assr`. It is designed to delete a single assessor from XNAT, based on the provided identifiers.
   - `delete_assessors()`: This function likely takes a list of assessors and the XNAT interface instance, iterating through the list to delete each assessor.
   - `delete_all_assessors()`: A function for deleting all assessors associated with a given project and subject.
   - `delete_orphaned_assessors()`: This function is intended to delete assessors not associated with a valid session or subject within specified projects.

6. **Main Execution Block:**
   - The script uses an `ArgumentParser` instance to parse command-line arguments, allowing users to specify the projects (`--projects`) and subjects (`--subjects`) for which assessors should be deleted.
   - Based on the provided arguments, the script decides whether to delete specific assessors associated with given subjects or to delete orphaned assessors.
   - The script then executes the appropriate deletion function based on the parsed arguments.

7. **Conclusion:**
   - The script concludes with conditional statements that drive the deletion process, either targeting specific assessors or orphaned ones, based on the user's input from the command line.
