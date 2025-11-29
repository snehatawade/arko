import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from io import StringIO

SUPPORTED_DATE_FORMATS = [
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
]


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip column names so we can match them easily."""
    df.columns = (
        df.columns.str.lower().str.strip().str.replace(" ", "_").str.replace("__", "_")
    )
    return df


def _find_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    """Return the first column whose name contains any of the keywords."""
    for col in df.columns:
        for keyword in keywords:
            if keyword in col:
                return col
    return None


def _parse_amount(value: str) -> float:
    """Convert messy currency strings to float."""
    raw = str(value).strip()
    if not raw:
        raise ValueError("amount is empty")

    # Handle parentheses for negative values e.g. (1200)
    negative = False
    if raw.startswith("(") and raw.endswith(")"):
        negative = True
        raw = raw[1:-1]

    # Remove common currency symbols / text
    cleaned = (
        raw.replace(",", "")
        .replace("₹", "")
        .replace("$", "")
        .replace("rs", "")
        .replace("RS", "")
        .replace("inr", "")
        .strip()
    )

    # Remove trailing credit/debit markers if present
    cleaned = cleaned.replace("CR", "").replace("DR", "").strip()

    amount = float(cleaned)
    if negative:
        amount *= -1
    return amount


def _apply_transaction_type(amount: float, txn_type: Optional[str]) -> float:
    """Use the 'type' column to fix the sign if the data doesn't use +/-."""
    if not txn_type:
        return amount

    txn_type_lower = str(txn_type).strip().lower()
    if not txn_type_lower:
        return amount

    if "debit" in txn_type_lower and amount > 0:
        return -abs(amount)
    if "credit" in txn_type_lower and amount < 0:
        return abs(amount)
    return amount


def _parse_dataframe(df: pd.DataFrame) -> List[Dict]:
    df = _normalize_columns(df.copy())

    date_col = _find_column(df, ["date"])
    amount_col = _find_column(df, ["amount", "amt"])
    desc_col = _find_column(
        df,
        [
            "raw_description",
            "raw_desc",
            "raw_descr",
            "description",
            "desc",
            "merchant",
            "narration",
        ],
    )
    bank_col = _find_column(df, ["account", "bank", "card"])
    type_col = _find_column(df, ["type", "txn_type"])

    if not all([date_col, amount_col, desc_col]):
        available_cols = ", ".join(df.columns.tolist())
        raise ValueError(
            "File must contain date, amount, and description columns. "
            f"Found columns: {available_cols}"
        )

    transactions: List[Dict] = []

    for _, row in df.iterrows():
        try:
            date_value = row[date_col]
            if pd.isna(date_value):
                continue

            parsed_date = None
            try:
                parsed_date = pd.to_datetime(date_value)
            except Exception:
                for fmt in SUPPORTED_DATE_FORMATS:
                    try:
                        parsed_date = datetime.strptime(str(date_value), fmt)
                        break
                    except Exception:
                        continue
            if not parsed_date:
                continue

            amount_value = row[amount_col]
            if pd.isna(amount_value):
                continue
            amount = _parse_amount(amount_value)

            txn_type = row[type_col] if type_col and type_col in row else None
            amount = _apply_transaction_type(amount, txn_type)

            description_value = row[desc_col]
            if pd.isna(description_value):
                continue
            description = str(description_value).strip()
            if not description:
                continue

            bank_value = (
                row[bank_col] if bank_col and bank_col in row and not pd.isna(row[bank_col]) else None
            )
            bank_account = str(bank_value).strip() if bank_value else "Primary Account"

            transactions.append(
                {
                    "date": parsed_date,
                    "amount": amount,
                    "description": description,
                    "bank_account": bank_account,
                    "raw_text": str(row.to_dict()),
                }
            )
        except Exception as exc:
            print(f"Error parsing row: {exc}")
            continue

    if not transactions:
        raise ValueError("No valid transactions found in the file")

    return transactions


def parse_csv(file_content: str) -> List[Dict]:
    """Parse CSV bank statement (supports Indian bank formats)."""
    try:
        df = pd.read_csv(StringIO(file_content))
        return _parse_dataframe(df)
    except Exception as exc:
        raise ValueError(f"Error parsing CSV: {exc}")


def parse_excel(df: pd.DataFrame) -> List[Dict]:
    """Parse Excel bank statement DataFrame."""
    try:
        return _parse_dataframe(df)
    except Exception as exc:
        raise ValueError(f"Error parsing Excel file: {exc}")

