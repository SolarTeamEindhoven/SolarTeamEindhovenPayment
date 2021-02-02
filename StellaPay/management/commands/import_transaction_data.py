import csv
import os

from django.core.management import BaseCommand

from StellaPay import models
from StellaPay.models import Transaction, Product, Customer


class Command(BaseCommand):
    help = "Import transaction data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('file', help="the CSV file to import", type=str)

    def handle(self, *args, **options):

        file_path = options['file']

        # Check if the specified file actually exists
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.stderr.write(f"The file {file_path} does not exit or is not a file!")
            return

        # Check if it is a CSV file
        if not os.path.splitext(file_path)[1] == ".csv":
            self.stderr.write(f"The specified file {file_path} is not a CSV file!")
            return

        self.stdout.write(f"Importing transactions from {os.path.basename(file_path)}...")

        # Open CSV and read every line
        with open(file_path, mode='r') as transaction_csv_file:
            csv_reader = csv.DictReader(transaction_csv_file)

            # Skip the header of the CSV file
            next(csv_reader, None)

            total_lines = 0

            # Keep references of foreign key objects
            # We need these to be able to add data to the database
            product_references = {}
            user_references = {}

            # Store rows that could not be imported and write them to a separate CSV
            not_imported_rows = []

            # Read all rows
            for row in csv_reader:

                total_lines += 1

                full_name = row['User']

                if " " in full_name:
                    first_name, last_name = full_name.split(" ", 1)
                else:
                    first_name, last_name = "", ""

                email_address = ""

                if row['Email'] is not None:
                    email_address = row['Email'].strip()

                date_time = ""

                if row['Date time'] is not None:
                    date_time = row['Date time'].strip()

                item = ""

                if row['Item bought'] is not None:
                    item = row['Item bought'].strip()

                transaction_price = ""

                if row['Price'] is not None:
                    transaction_price = row['Price'].strip()

                if email_address == "" and full_name == "":
                    self.stderr.write(f"Could not import row {row} because it had no user AND no email address!")
                    not_imported_rows.append(row)
                    continue

                if item == "":
                    self.stderr.write(f"Ignoring the following row (since it has no product): {row}")
                    not_imported_rows.append(row)
                    continue

                if transaction_price == "":
                    self.stderr.write(f"Ignoring the following row (since it has no price): {transaction_price}")
                    not_imported_rows.append(row)
                    continue

                # If we haven't loaded a reference to this product yet, we load it.
                if item not in product_references:
                    try:
                        product_references[item] = Product.objects.get(name=item)
                    except models.Product.DoesNotExist:
                        self.stderr.write(
                            f"Could not import this row because the product '{item}' does not exist.'")
                        not_imported_rows.append(row)  # Save this row because we failed to import it
                        continue

                # User did not provide an email address, let's see if we can find the email address.
                if email_address == "":
                    user_match = Customer.objects.filter(first_name=first_name, last_name=last_name).first()

                    if user_match is None:
                        self.stderr.write(f"Could not find an email address for the user: {full_name}")
                        not_imported_rows.append(row)
                        continue

                    email_address = user_match.email
                    self.stdout.write(f"Performed reverse lookup to match {full_name} to {email_address}.")

                # Load the users as a reference so we can use them as a foreign key
                if email_address not in user_references:
                    try:
                        user_references[email_address] = Customer.objects.get(email=email_address)
                    except models.Customer.DoesNotExist:
                        # We could not find the user by email, but maybe if we look for a name instead
                        user_match = Customer.objects.filter(first_name=first_name, last_name=last_name).first()

                        if user_match is None:
                            self.stderr.write(
                                f"Could not import the following row because I could find not a corresponding user: '{row}'")
                            not_imported_rows.append(row)  # Save this row because we failed to import it
                            continue

                        email_address = user_match.email
                        self.stdout.write(f"Performed reverse lookup to match {full_name} to {email_address}.")

                # Create object and store it in the database
                Transaction.objects.create(buyer=user_references[email_address], item_bought=product_references[item],
                                           price=float(transaction_price))

            # Provide feedback about how many were successfully imported and how many were not.
            self.stdout.write(
                f"Read {total_lines} lines and successfully imported {total_lines - len(not_imported_rows)} "
                f"({round(100 * ((total_lines - len(not_imported_rows)) / total_lines), 1)}%) lines.")

            # Check if we even have failed rows.
            if len(not_imported_rows) == 0:
                self.stdout.write(f"All lines were imported successfully!")
                return

            not_imported_rows_file = file_path.replace(".csv", "_not_imported.csv")

            # Write non-imported rows to a file
            with open(not_imported_rows_file, mode="w", newline='') as output_file:
                writer = csv.DictWriter(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                        fieldnames=["User", "Email", "Date time", "Item bought", "Price"])
                # Well, you know, write the header.
                writer.writeheader()

                # Write each row separately
                for failed_row in not_imported_rows:
                    writer.writerow(failed_row)

            self.stdout.write(f"Wrote remaining {len(not_imported_rows)} lines to {not_imported_rows_file}.")
