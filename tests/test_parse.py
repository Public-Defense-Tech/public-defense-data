import pytest
from bs4 import BeautifulSoup

from src.parser import pre2017, post2017
from tests.outputs import output_13145235

# old correct output
#weird_defendant_cell_output = {'code': '20-2423CR-1', 'odyssey id': '13145235', 'name': 'The State of Texas vs. Garrett Mitchell Daniels', 'case type': 'Adult Misdemeanor', 'date filed': '06/09/2020', 'location': 'County Court at Law #1', 'party information': {'defendant': 'Daniels, Garrett Mitchell', 'sex': 'Male', 'race': '', 'date of birth': '04/18/1998', 'height': '', 'weight': '', 'defense attorney': '145 lbs', 'appointed or retained': 'Court Appointed', 'defense attorney phone number': 'Court Appointed', 'defendant address': '6300 Linne Rd, Seguin, TX 78155', 'SID': 'TX50762437', 'prosecuting attorney': 'Melissa Pulido', 'prosecuting attorney phone number': '', 'prosecuting attorney address': '712 S Stagecoach TRL, San Marcos, TX 78666', 'bondsman': '', 'bondsman address': ''}, 'charge information': [{'charges': 'ASSAULT CAUSES BODILY INJURY FAMILY MEMBER', 'statute': '22.01(a)(1)', 'level': 'Misdemeanor A', 'date': '05/05/2019'}], 'other events and hearings': [['06/09/2020', 'Complaint & Information (Open Case)'], ['06/11/2020', 'Order for Summons', '(Judicial Officer: Updegrove, Robert )'], ['06/11/2020', 'Summons', 'Daniels, Garrett Mitchell', 'Served', '06/11/2020'], ['11/17/2020', 'CANCELED', 'Arraignment', '(9:00 AM) (Judicial Officers Updegrove, Robert, Glickler, David)', 'Reset'], ['12/09/2020', 'Arraignment', '(9:00 AM) (Judicial Officers Updegrove, Robert, Glickler, David)', 'Result: Arraigned'], ['02/25/2021', 'Discovery Receipt'], ['02/26/2021', 'Certificate of Contact'], ['03/09/2021', 'CANCELED', 'Announcement', '(1:30 PM) (Judicial Officer Updegrove, Robert)', 'Reset', 'ARRG 12.09 REQ WOC'], ['04/29/2021', 'CANCELED', 'Announcement', '(8:30 AM) (Judicial Officer Updegrove, Robert)', 'Reset'], ['06/17/2021', 'CANCELED', 'Announcement', '(1:30 PM) (Judicial Officer Updegrove, Robert)', 'Reset'], ['06/25/2021', 'Discovery Receipt'], ['06/28/2021', 'Discovery Receipt'], ['08/16/2021', 'Discovery Receipt'], ['09/02/2021', 'CANCELED', 'Announcement', '(1:30 PM) (Judicial Officer Updegrove, Robert)', 'Court'], ['10/27/2021', 'Announcement', '(8:30 AM) (Judicial Officer Updegrove, Robert)']], 'dispositions': []}

def test_pre2017_parse():
    # Test correct parsing for html that has missing info from defendent table cell
    with open('tests/example_data/13145235.html', 'r') as f:
        incomplete_defendant_cell_html = BeautifulSoup(f, "html.parser", from_encoding="UTF-8")
    assert pre2017.parse(incomplete_defendant_cell_html, '13145235') == output_13145235()