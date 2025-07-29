from datetime import datetime

from peewee import fn, NodeList, SQL

from dialer.configs import logger
from dialer.configs.settings import BATCH_SIZE, OPTOUT_AFTER_FAILED_WEEKS

from .crud_ops import CRUD
from .models import CustomerRecord, Language

log = logger.get_logger()


class DbWork:
    """
    Prepares and processes any DB tasks
    """
    def __init__(self):
        self.crud = CRUD()

    def get(self, dialer_name):
        """
        Extract records
        """
        now = f"{datetime.now().strftime('%Y-%m-%d %H')}:00:00"

        filters = (
            (
                (CustomerRecord.run_on == now) |
                (CustomerRecord.retry_on == now) |
                (CustomerRecord.run_on.is_null(True))
            )
            &
            (CustomerRecord.dialer_name == dialer_name)
            &
            (CustomerRecord.failed_weeks < OPTOUT_AFTER_FAILED_WEEKS)
        )

        columns_to_select = (
            CustomerRecord.id,
            CustomerRecord.phone_number,
            CustomerRecord.campaign_type,
            CustomerRecord.training_level,
            Language.name.alias('customer_language_name'),
            CustomerRecord.run_on,
            CustomerRecord.retry_on
        )

        return self.crud.read(
            CustomerRecord,
            filters,
            columns_to_select,
            Language
        )

    def initial_update(self, record_id, retry_on, run_on):
        """
        On calling number, set retry_on and run_on 1 & 7 days from now
        """
        retry_on_interval = NodeList((SQL('INTERVAL'), 1, SQL('DAY')))
        filters = (CustomerRecord.id == record_id)

        if retry_on and retry_on < run_on:
            update_values = {
                'retry_on': fn.date_add(
                    CustomerRecord.retry_on,
                    retry_on_interval
                ),
                'updated_on': datetime.now()
            }

            records = self.crud.update(
                CustomerRecord,
                filters,
                **update_values
            )
            return print(f"{records} record/s updated")

        run_on_interval = NodeList((SQL('INTERVAL'), 7, SQL('DAY')))
        update_values = {
            'retry_on': fn.date_add(CustomerRecord.run_on, retry_on_interval),
            'run_on': fn.date_add(CustomerRecord.run_on, run_on_interval),
            'updated_on': datetime.now()
        }

        records = self.crud.update(
            CustomerRecord,
            filters,
            **update_values
        )
        return print(f"{records} record/s updated")

    def final_update(self, my_number, my_dialer, date_or_status="successful"):
        """
        On reading asterisk log file, update record basing on
        whether call was successful
        """
        if date_or_status == "successful":
            filters = (
                (CustomerRecord.phone_number == my_number) &
                (CustomerRecord.dialer_name == my_dialer) &
                (CustomerRecord.retry_on != None )
            )
            update_values = {
                'retry_on': None,
                'training_level': CustomerRecord.training_level + 1,
                'failed_weeks': 0,
                'updated_on': datetime.now()
                }

            records = self.crud.update(
                CustomerRecord,
                filters,
                **update_values
            )
            return print(f"{records} record/s updated")

        elif(date_or_status == "Failed"):
            filters = (
                (CustomerRecord.phone_number == my_number) &
                (CustomerRecord.dialer_name == my_dialer) &
                (CustomerRecord.retry_on >= CustomerRecord.run_on)
            )
            update_values = {
                'retry_on': None,
                'training_level': CustomerRecord.training_level + 1,
                'failed_weeks': CustomerRecord.failed_weeks + 1,
                'updated_on': datetime.now()
                }

            updated = self.crud.update(
                CustomerRecord,
                filters,
                **update_values
            )

            if updated > 0:
                log.info(
                    f"{my_number} moved to next module after a week of failure"
                )

            return print(f"{updated} records updated")

        elif(date_or_status == "OptOut"):
            filters = (
                (CustomerRecord.phone_number == my_number) &
                (CustomerRecord.dialer_name == my_dialer)
            )
            update_values = {
                'retry_on': None,
                'failed_weeks': OPTOUT_AFTER_FAILED_WEEKS,
                'updated_on': datetime.now()
                }

            updated = self.crud.update(
                CustomerRecord,
                filters,
                **update_values
            )

            if updated > 0:
                log.info(
                    f"{my_number} opted out of the training"
                )

            return print(f"{updated} records updated")

        else:
            filters = (
                (CustomerRecord.phone_number == my_number) &
                (CustomerRecord.dialer_name == my_dialer)
            )
            update_values = {
                'run_on': date_or_status,
                'training_level': 1,
                'updated_on': datetime.now()
                }

            records = self.crud.update(
                CustomerRecord,
                filters,
                **update_values
            )
            return print(f"{records} record/s updated")

    def insert(self, data):
        """
        Bulk upload numbers into DB
        """
        if not isinstance(data, list):
            log.error("Expected a list, rectify or give up")
            raise ValueError("Expected a list, rectify or give up")

        for row in data:
            row["customer_language_id"] = self.crud.read_or_create(
                Language,
                **{'name': row["customer_language_id"]}
            )

        records = self.crud.bulk_insert(
            CustomerRecord,
            data,
            BATCH_SIZE
        )
        return f"SUCCESSFUL <br>: {records} records added"
