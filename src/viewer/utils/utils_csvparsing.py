from dataclasses import dataclass, asdict
from typing import Optional, Dict, Callable, List, Union
import pandas as pd
import re
import numpy as np

# ------------------------------
# Data classes
# ------------------------------

@dataclass
class CSVIssue:
    row: int
    column: str
    value: object
    reason: str
    mrid: Optional[object] = None

@dataclass
class CsvFieldGate:
    ok: bool
    missing: List[str]
    present: List[str]
    extra: List[str]
    file_ok: bool
    note: str

@dataclass
class CsvValidationReport:
    file_ok: bool
    columns_ok: bool
    missing_cols: List[str]
    present_cols: List[str]
    extra_cols: List[str]
    issues: List[CSVIssue]           # row-level details
    ok: bool                         # columns_ok AND no issues
    rows: int

# ------------------------------
# Column validators registry
# ------------------------------

COLUMN_VALIDATORS: Dict[str, Callable[[pd.DataFrame, str, str], List[CSVIssue]]] = {}

def register_csv_column(name: str) -> Callable[[Callable[[pd.DataFrame, str, str], List[CSVIssue]]], Callable[[pd.DataFrame, str, str], List[CSVIssue]]]:
    def deco(fn: Callable[[pd.DataFrame, str, str], List[CSVIssue]]) -> Callable[[pd.DataFrame, str, str], List[CSVIssue]]:
        COLUMN_VALIDATORS[name] = fn
        return fn
    return deco

# ------------------------------
# Helpers
# ------------------------------

def issues_from_mask(df: pd.DataFrame, column: str, badmask: pd.Series, reason: str, mrid_col: str) -> List[CSVIssue]:
    dftmp = df.copy()
    if mrid_col not in dftmp.columns:
        dftmp[mrid_col] = None
    
    idx = dftmp.index[badmask.fillna(False)]
    
    mrids: pd.Series = df.loc[idx, mrid_col]
    values: pd.Series = df.loc[idx, column]
    
    return [
        CSVIssue(
            row=int(i),
            column=column,
            value=values.loc[i],
            reason=reason,
            mrid=(mrids.loc[i])
        )
        for i in idx
    ]

# ------------------------------
# Validators
# ------------------------------

def v_int(df: pd.DataFrame, col: str, *, ge: Optional[int] = None, le: Optional[int] = None) -> List[CSVIssue]:
    s: pd.Series = df[col]
    bad = ~s.dropna().astype(str).str.fullmatch(r"-?\d+")
    issues: List[CSVIssue] = issues_from_mask(df, col, bad.reindex(df.index, fill_value=False), "not an integer", mrid_col="MRID")
    if ge is not None:
        issues += issues_from_mask(df, col, s < ge, f"< {ge}", mrid_col="MRID")
    if le is not None:
        issues += issues_from_mask(df, col, s > le, f"> {le}", mrid_col="MRID")
    return issues

def v_float(df: pd.DataFrame, col: str, *, ge: Optional[float] = None, le: Optional[float] = None) -> List[CSVIssue]:
    s: pd.Series = df[col]
    try:
        x: pd.Series = pd.to_numeric(s, errors="coerce")
    except Exception:
        x = pd.Series(np.nan, index=s.index)
    issues: List[CSVIssue] = issues_from_mask(df, col, x.isna() & s.notna(), "not a float", mrid_col="MRID")
    if ge is not None:
        issues += issues_from_mask(df, col, x < ge, f"< {ge}", mrid_col="MRID")
    if le is not None:
        issues += issues_from_mask(df, col, x > le, f"> {le}", mrid_col="MRID")
    return issues

def v_enum(df: pd.DataFrame, col: str, *, values: List[Union[str, int]]) -> List[CSVIssue]:
    s: pd.Series = df[col].astype(str)
    values_as_strs: List[str] = [str(val) for val in values]
    bad: pd.Series = ~s.isin(values_as_strs)
    return issues_from_mask(df, col, bad, f"not in {values}", mrid_col="MRID")

def v_regex(df: pd.DataFrame, col: str, *, pattern: str) -> List[CSVIssue]:
    pat = re.compile(pattern)
    s: pd.Series = df[col].astype(str)
    bad: pd.Series = ~s.str.match(pat)
    return issues_from_mask(df, col, bad, f"regex mismatch: {pattern}", mrid_col="MRID")

def v_nonempty(df: pd.DataFrame, col: str) -> List[CSVIssue]:
    s: pd.Series = df[col]
    bad: pd.Series = s.isna() | (s.astype(str).str.len() == 0)
    return issues_from_mask(df, col, bad, "empty", mrid_col="MRID")

# ------------------------------
# Specific column validators
# ------------------------------

@register_csv_column("MRID")
def _validate_mrid(df: pd.DataFrame, col: str, mrid_col: str) -> List[CSVIssue]:
    out: List[CSVIssue] = []
    out += v_nonempty(df, col)
    dup_mask: pd.Series = df[col].duplicated(keep=False)
    out += issues_from_mask(df, col, dup_mask, "duplicate MRID", mrid_col)
    return out

@register_csv_column("Age")
def _validate_age(df: pd.DataFrame, col: str, mrid_col: str) -> List[CSVIssue]:
    return v_int(df, col, ge=0, le=120)

@register_csv_column("Sex")
def _validate_sex(df: pd.DataFrame, col: str, mrid_col: str) -> List[CSVIssue]:
    return v_enum(df, col, values=["M","F"])

@register_csv_column("IsCN")
def _validate_iscn(df: pd.DataFrame, col: str, mrid_col: str) -> List[CSVIssue]:
    return v_enum(df, col, values=[0, 1])

@register_csv_column("Batch")
def _validate_batch(df: pd.DataFrame, col: str, mrid_col: str) -> List[CSVIssue]:
    return v_nonempty(df, col)

# ------------------------------
# CSV validation
# ------------------------------

def validate_csv(csv_path: str, required_cols: List[str], mrid_col: str = "MRID") -> CsvValidationReport:
    import os
    if not (csv_path and os.path.isfile(csv_path)):
        return CsvValidationReport(
            file_ok=False,
            columns_ok=False,
            missing_cols=required_cols,
            present_cols=[],
            extra_cols=[],
            issues=[],
            ok=False,
            rows=0
        )

    df: pd.DataFrame = pd.read_csv(csv_path)
    cols: List[str] = list(df.columns)
    missing: List[str] = [c for c in required_cols if c not in cols]
    present: List[str] = [c for c in required_cols if c in cols]
    extra: List[str]   = [c for c in cols if c not in required_cols]

    columns_ok: bool = len(missing) == 0
    issues: List[CSVIssue] = []

    if columns_ok:
        # Run registered validators for present columns
        for col in present:
            if col in COLUMN_VALIDATORS:
                issues.extend(COLUMN_VALIDATORS[col](df, col, mrid_col))
        # Optionally validate extra columns that have validators
        for col in df.columns:
            if (col not in present) and (col in COLUMN_VALIDATORS):
                issues.extend(COLUMN_VALIDATORS[col](df, col, mrid_col))

    ok: bool = columns_ok and (len(issues) == 0)

    return CsvValidationReport(
        file_ok=True,
        columns_ok=columns_ok,
        missing_cols=missing,
        present_cols=present,
        extra_cols=extra,
        issues=issues,
        ok=ok,
        rows=len(df)
    )
