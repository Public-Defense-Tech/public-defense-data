from sqlmodel import Session, create_engine, SQLModel
from datetime import date
import unittest
import parser.p_hays
import main


class OrchestratorTests(unittest.TestCase):

    def test_orchestrator_end_to_end(
        self,
        counties=["hays"],
        start_date="2024-01-01",
        end_date="2024-01-01",
        court_calendar_link_text=None,
        case_number=None,
        case_html_path=None,
        judicial_officers=None,
        ms_wait=None,
        parse_single_file=False,
    ):

        orchestrator_instance = main.Orchestrator(
            counties=counties,
            start_date=start_date,
            end_date=end_date,
            court_calendar_link_text=court_calendar_link_text,
            case_number=case_number,
            case_html_path=case_html_path,
            judicial_officers=judicial_officers,
            ms_wait=ms_wait,
            parse_single_file=parse_single_file,
        )
        orchestrator_instance.orchestrate()
