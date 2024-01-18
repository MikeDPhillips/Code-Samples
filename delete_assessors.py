# -*- coding: utf-8 -*-
"""Delete assessor objects from XNAT sessions or delete orphaned assessors that are not 
        associated with a session or subject.
    @author: Mike Phillips, MASI Lab, Vanderbilt University

    Args:
        --projects: All projects you wish to include in the search. Default is CIBS_COPE and CIBS_BRAIN2
        --subjects: All subjects you wish to include in the search. If None, then delete only orphaned assessors.

    Typical usage:
        To delete all assessors from a matching subject list:
            python delete_assessors.py --projects CIBS_COPE CIBS_BRAIN2 --subjects VCP-002 VCP-003
        To delete all assessors from a single subject:
            python delete_assessors.py --projects CIBS_COPE --subjects VCP-002
        To delete all orphaned assessors that do not have proper subject or session labels:
            python delete_assessors.py --projects CIBS_COPE CIBS_BRAIN2
"""

import my_utils
from requests.exceptions import ReadTimeout
from argparse import ArgumentParser

#Defaults if not changed by arg parser
PROJECTS = ['CIBS_COPE', 'CIBS_BRAIN2']
xnat = my_utils.get_interface()


def delete_assessor(xnat, proj, subj, sess, assr):
    """Delete a single assessor from XNAT.

    Parameters
    ----------
    xnat : pyxnat.Interface
        XNAT interface
    proj : str
        Project ID
    subj : str
        Subject ID
    sess : str
        Session ID
    assr : str
        Assessor ID
    """
    try:
        selected = xnat.select_assessor(proj, subj, sess, assr)
        if selected.exists():
            selected.delete(True)
            return True
        return False
    except ReadTimeout:
        print("ReadTimeout error. Trying again.")
        delete_assessor(xnat, proj, subj, sess, assr)


def delete_assessors(xnat, assessors_to_delete):
    count = 0
    total_length = len(assessors_to_delete)
    if total_length == 0:
        print("No assessors to delete.")
        return
    
    for s in assessors_to_delete:
        count += 1
        print(f"Working on #{count}. {total_length-count} remaining.")
        if delete_assessor(xnat, 
                           s['project_id'], 
                           s['subject_label'], 
                           s['session_label'], 
                           s['label']):           
            print(f"Deleted {s['label']}")
        else:
            print(f"Failed to delete {s['label']}")

    

def delete_all_assessors(xnat, proj, subject):
    """Delete all assessors for the given project and subject.

    Parameters
    ----------
    xnat : pyxnat.Interface
        XNAT interface
    projects : str
        Project containing given subject
    subject_list : str
        Subject to delete assessors for
    """

    assessors = xnat.list_project_assessors(proj)
    assessors_to_delete = [a for a in assessors if a['subject_label'] == subject]
    delete_assessors(xnat, assessors_to_delete)
    
    
def delete_orphaned_assessors(xnat, projects):
    """Delete assessors that are not associated with a session or subject.

    Parameters
    ----------
    xnat : pyxnat.Interface
        XNAT interface
    projects : list of str
        List of projects to check
    subject_list : list of str, optional
        List of subjects to check. If None, all subjects will be checked.
    """
    for proj in projects:
        assessors = xnat.list_project_assessors(proj)
        # Find all assessors who have a subject_label or session_label that does not 
        # match the appropriate label.
        subj_delete = [a for a in assessors if a['subject_label']
                    != a['label'].split('-x-')[1]]
        sess_delete = [a for a in assessors if a['session_label']
                    != a['label'].split('-x-')[2]]
        assessors_to_delete = subj_delete + sess_delete
        delete_assessors(xnat, assessors_to_delete)

 
if __name__ == '__main__':
   
    parser = ArgumentParser(description='Delete matching subjects assessors from XNAT or orphaned assessors')
    parser.add_argument('-p', '--projects', nargs='+', help='List of projects to check')
    parser.add_argument('-s', '--subjects', nargs='+', help='List of subjects to check')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
    
    args = parser.parse_args()
    if args.projects:
        PROJECTS = args.projects
    if args.subjects:
        SUBJECTS = args.subjects
    else:
        SUBJECTS = None
        
    if SUBJECTS:
        print(f"Deleting assessors from {PROJECTS} for subjects {SUBJECTS}")
    else:
        print(f"Deleting orphaned assessors from {PROJECTS}")
        delete_orphaned_assessors(xnat, PROJECTS)


