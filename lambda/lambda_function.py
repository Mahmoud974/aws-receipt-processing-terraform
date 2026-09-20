import json
import os
import urllib.parse
import uuid

import boto3

textract = boto3.client("textract")
dynamodb = boto3.resource("dynamodb")
ses = boto3.client("ses")

TABLE_NAME = os.environ["TABLE_NAME"]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]

table = dynamodb.Table(TABLE_NAME)


def extract_receipt_fields(textract_response):
    """Pull vendor / total / date out of a Textract AnalyzeExpense response."""
    vendor = None
    total = None
    receipt_date = None

    for document in textract_response.get("ExpenseDocuments", []):
        for field in document.get("SummaryFields", []):
            field_type = field.get("Type", {}).get("Text")
            value = field.get("ValueDetection", {}).get("Text")

            if not value:
                continue

            if field_type == "VENDOR_NAME" and vendor is None:
                vendor = value
            elif field_type == "TOTAL" and total is None:
                total = value
            elif field_type == "INVOICE_RECEIPT_DATE" and receipt_date is None:
                receipt_date = value

    return vendor or "UNKNOWN", total or "UNKNOWN", receipt_date or "UNKNOWN"


def process_receipt(bucket, key):
    print(f"Processing s3://{bucket}/{key}")

    try:
        response = textract.analyze_expense(
            Document={"S3Object": {"Bucket": bucket, "Name": key}}
        )
    except Exception as exc:  # noqa: BLE001 - want to log and keep going
        print(f"ERROR: Textract failed for {key}: {exc}")
        return False

    vendor, total, receipt_date = extract_receipt_fields(response)

    print(f"Vendor={vendor} Date={receipt_date} Total={total} File={key}")

    receipt_id = str(uuid.uuid4())

    try:
        table.put_item(
            Item={
                "receipt_id": receipt_id,
                "vendor": vendor,
                "total": total,
                "date": receipt_date,
                "file": key,
            }
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: DynamoDB write failed for {key}: {exc}")
        return False

    try:
        ses.send_email(
            Source=EMAIL_ADDRESS,
            Destination={"ToAddresses": [EMAIL_ADDRESS]},
            Message={
                "Subject": {"Data": "Nouveau reçu traité", "Charset": "UTF-8"},
                "Body": {
                    "Text": {
                        "Data": (
                            "Reçu traité avec succès\n\n"
                            f"Vendeur : {vendor}\n"
                            f"Date : {receipt_date}\n"
                            f"Total : {total}\n"
                            f"Fichier : {key}\n"
                        ),
                        "Charset": "UTF-8",
                    }
                },
            },
        )
    except Exception as exc:  # noqa: BLE001 - email failure shouldn't fail the whole run
        print(f"WARNING: SES send failed for {key}: {exc}")

    print(f"Saved receipt {receipt_id} for {key}")
    return True


def lambda_handler(event, context):
    results = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        ok = process_receipt(bucket, key)
        results.append({"file": key, "success": ok})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Receipt processing complete", "results": results}),
    }
