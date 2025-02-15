import json, argparse, os, xxhash
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv
from datetime import datetime as dt
import logging
import psycopg2
from psycopg2 import sql

class Updater():
    def __init__(self, county = "hays"):
        self.county = county.lower()
        self.case_json_cleaned_folder_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", self.county, "case_json_cleaned"
        )
        self.processed_path = os.path.join(self.case_json_cleaned_folder_path)
        
        # open or create a output directory for a log and successfully processed data
        if os.path.exists(self.case_json_cleaned_folder_path) and \
            not os.path.exists(self.processed_path): 
            os.makedirs(self.processed_path)
        self.logger = self.configure_logger()

    def configure_logger(self):
        logger = logging.getLogger(name=f"updater: pid: {os.getpid()}")
        
        # Set up basic configuration for the logging system
        logging.basicConfig(level=logging.INFO)

        updater_log_path = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
        now = dt.now()
        # Format it as "DD-MM-YYYY - HH:MM"
        formatted_date_time = now.strftime("%d-%m-%Y-%H.%M")
        updater_log_name = formatted_date_time + '_updater_logger_log.txt'

        file_handler = logging.FileHandler(os.path.join(updater_log_path, updater_log_name))
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    #Below is some quick code from chatgpt that might give a way of converting the json to tables.
    #TODO: We should remember to work in versioning of different times parsed.

    def load_db_env(self, file_path='src/updater/.env'):
        #Create a local environment field called 'env.env' with your credentials
        env_path = os.path.abspath(file_path)
        load_dotenv(file_path)
        DB_PARAMS = {
            "dbname": os.getenv("PGDATABASE"),
            "user": os.getenv("PGUSER"),
            "password": os.getenv("PGPASSWORD"),
            "host": os.getenv("PGHOST"),
            "port": os.getenv("PGPORT"),
        }
        # Debugging: Print loaded values (except password)
        print("Connecting to this Postgres DB:", {k: v for k, v in DB_PARAMS.items() if k != "password"})        
        return DB_PARAMS

    def create_tables(self, cursor):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS case_metadata (
                id SERIAL PRIMARY KEY,
                county TEXT,
                cause_number TEXT,
                earliest_charge_date DATE,
                has_evidence_of_representation BOOLEAN,
                good_motions TEXT
            )""",
"""
            CREATE TABLE IF NOT EXISTS related_cases (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                related_case TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS parse_metadata (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                parsing_date DATE,
                html_hash TEXT,
                cause_number_hashed TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS defendants (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                name TEXT,
                sex TEXT,
                race TEXT,
                date_of_birth TEXT,
                height TEXT,
                weight TEXT,
                address TEXT,
                sid TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS defense_attorneys (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                name TEXT,
                phone TEXT,
                appointed_retained TEXT,
                attorney_hash TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS state_information (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                prosecuting_attorney TEXT,
                prosecuting_attorney_phone TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS charges (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                charge_id INTEGER,
                charge_level TEXT,
                original_charge TEXT,
                statute TEXT,
                is_primary_charge BOOLEAN,
                charge_date DATE,
                charge_name TEXT,
                uccs_code TEXT,
                charge_desc TEXT,
                offense_category_desc TEXT,
                offense_type_desc TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS dispositions (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                date DATE,
                event TEXT,
                judicial_officer TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS disposition_details (
                id SERIAL PRIMARY KEY,
                disposition_id INTEGER REFERENCES dispositions(id),
                charge TEXT,
                outcome TEXT
            )""",
            """
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                case_id INTEGER REFERENCES case_metadata(id),
                date DATE,
                event TEXT,
                details TEXT
            )"""
        ]
        for query in queries:
            cursor.execute(query)

    # Load JSON data
    def get_jsons(self, folder_path=None):
        folder_path = folder_path if folder_path else self.case_json_cleaned_folder_path
        json_files = [f for f in os.listdir(folder_path)]
        return json_files

    def insert_case(self, cursor, case_data):
        cursor.execute(
            """
            INSERT INTO case_metadata (county, cause_number, earliest_charge_date, has_evidence_of_representation, good_motions)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id""",
            (
                case_data["County"],
                case_data["CauseNumber"],
                case_data["EarliestChargeDate"],
                case_data["HasEvidenceOfRepresentation"],
                case_data["GoodMotions"],
            )
        )
        return cursor.fetchone()[0]

    def insert_related_cases(self, cursor, case_id, related_cases):
        if related_cases:
            for related_case in related_cases:
                cursor.execute("INSERT INTO related_cases (case_id, related_case) VALUES (%s, %s)", (case_id, related_case))

    def insert_defendant(self, cursor, case_id, defendant_data):
        if defendant_data:
            cursor.execute(
                """
                INSERT INTO defendants (case_id, name, sex, race, date_of_birth, height, weight, address, sid) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    case_id,
                    defendant_data["DefendantName"],
                    defendant_data["Sex"],
                    defendant_data["Race"],
                    defendant_data["DateOfBirth"],
                    defendant_data["Height"],
                    defendant_data["Weight"],
                    defendant_data["DefendantAddress"],
                    defendant_data["SID"],
                )
            )

    def insert_defense_attorney(self, cursor, case_id, defense_attorney_data):
        if defense_attorney_data:
            cursor.execute(
                """
                INSERT INTO defense_attorneys (case_id, name, phone, appointed_retained, attorney_hash) 
                VALUES (%s, %s, %s, %s, %s)""",
                (
                    case_id,
                    defense_attorney_data["DefenseAttorney"],
                    defense_attorney_data["DefenseAttorneyPhoneNumber"],
                    defense_attorney_data["AppointedOrRetained"],
                    defense_attorney_data["DefenseAttorneyHash"],
                )
            )

    def insert_charges(self, cursor, case_id, charges):
        if charges:
            for charge in charges:
                cursor.execute(
                    """INSERT INTO charges (case_id, charge_id, charge_level, original_charge, 
                    statute, is_primary_charge, charge_date, charge_name, uccs_code, charge_desc,
                    offense_category_desc, offense_type_desc)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        case_id, 
                        charge["ChargeId"],
                        charge["ChargeLevel"], 
                        charge["OrignalCharge"], 
                        charge["Statute"],
                        charge["IsPrimaryCharge"],
                        charge["ChargeDate"],
                        charge["charge_name"],
                        charge["uccs_code"],
                        charge["charge_desc"],
                        charge["offense_category_desc"],
                        charge["offense_type_desc"],
                    )
                )

    def insert_dispositions(self, cursor, case_id, dispositions):
        if dispositions:
            for disposition in dispositions:
                cursor.execute(
                    "INSERT INTO dispositions (case_id, date, event, judicial_officer) VALUES (%s, %s, %s, %s) RETURNING id",
                    (case_id, disposition["date"], disposition["event"], disposition["judicial officer"])
                )
                disposition_id = cursor.fetchone()[0]
                for detail in disposition["details"]:
                    cursor.execute(
                        "INSERT INTO disposition_details (disposition_id, charge, outcome) VALUES (%s, %s, %s)",
                        (disposition_id, detail["charge"], detail["outcome"])
                    )

    def insert_events(self, cursor, case_id, events):
        if events:
            for event in events:
                cursor.execute(
                    "INSERT INTO events (case_id, date, event, details) VALUES (%s, %s, %s, %s)",
                    (case_id, event[0], event[1], " ".join(event[2:]))
                )

    def update(self):
        DB_PARAMS = self.load_db_env()
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        self.create_tables(cursor)
        json_files = self.get_jsons()
        for json_file in json_files:
            self.logger.info(f"Updating the database with this json file: {json_file}")
            json_file_path = self.case_json_cleaned_folder_path + "/" + json_file
            # Need to have a system here that will query to see if the case table has a
            # file with a matching hash or a matching cause number to create different versions.
            with open(json_file_path, "r") as file:
                data = json.load(file)
                case_id = self.insert_case(cursor, data['CaseMetadata'])
                self.insert_related_cases(cursor, case_id, data['CaseMetadata'].get("RelatedCases", []))
                self.insert_defendant(cursor, case_id, data["DefendantInformation"])
                self.insert_defense_attorney(cursor, case_id, data["DefenseAttorneyInformation"])
                self.insert_charges(cursor, case_id, data["ChargeInformation"])
                self.insert_dispositions(cursor, case_id, data["DispositionInformation"])
                self.insert_events(cursor, case_id, data["EventsAndHearings"])
            
        conn.commit()
        cursor.close()
        conn.close()

if __name__ == '__main__':
    Updater().update()
