from datetime import datetime
from pathlib import Path
import shutil
import fitz
import json
import os

# ==================
TESTING: bool = False
# ==================
PROCESSING_FOLDER: str = (
    r""
)
FY24_FOLDER: str = (
    r""
)
# PROCESSING_FOLDER: str = r'X:\03 - Benefits & Work Life Balance\TEAM A\AWARDS\SPECIAL ACT OR SERVICE AWARDS\FY 2024\Submitted Nomination Forms - SASA'
TEST_FOLDER: str = (
    r""
)
AWARD_SER_NUMS: str = (
    r""
)
UPDATE_AWARD_SER_NUMS: bool = True
PRINT_AWARD_DATA: bool = True
CREATE_XLS_ROWS: bool = True
INSERT_DATE: bool = True
RENAME_AND_MOVE: bool = True
MIN_PAGE_COUNT: int = 2
MAX_PAGE_COUNT: int = 5
FIRST_PAGE: int = 0
# ----------------------------------------------------------------------------------------------------
# SHARED AWARD TOOLS
# ----------------------------------------------------------------------------------------------------


def get_file_name(filePath: str) -> str:
    return os.path.basename(filePath)


def get_pdf_fields(pdf_file: str) -> dict:
    with fitz.open(pdf_file) as doc:
        page_count: int = doc.page_count
        last_page: int = page_count - 1
        pdf_fields: dict = {
            "first_page": {},
            "mid_pages": {},
            "last_page": {},
            "page_count": page_count,
        }
        if not (MIN_PAGE_COUNT <= page_count <= MAX_PAGE_COUNT):
            raise Exception(
                f"get_pdf_fields() error: \nPage Count: {page_count} (not in range {MIN_PAGE_COUNT}-{MAX_PAGE_COUNT})\n"
            )
        elif page_count == 2:
            pdf_fields["category"] = "IND"
        else:
            pdf_fields["category"] = "GRP"
        for page in doc:
            current_page: int = page.number
            for field in page.widgets():
                key: str = field.field_name.strip().lower()
                val: str = field.field_value.strip()
                if all(
                    [
                        val == str(val),
                        not str(val).isspace(),
                        val != "",
                        str(val).lower() != "off",
                    ]
                ):
                    if current_page == FIRST_PAGE:
                        pdf_fields["first_page"][key] = val
                    elif current_page == last_page:
                        pdf_fields["last_page"][key] = val
                    elif FIRST_PAGE < current_page < last_page:
                        pdf_fields["mid_pages"][key] = val

    def count_fields(fields: dict) -> int:
        if not isinstance(fields, dict):
            return 1
        count = 0
        for field in fields.values():
            count += count_fields(field)
        return count

    field_count = count_fields(pdf_fields)
    if field_count < 10:
        combined_items = (
            "\n\t".join(f"{k}: {str(v)}" for k, v in pdf_fields.items())
            if pdf_fields
            else None
        )
        field_err_0 = "get_pdf_fields() error:"
        field_err_1 = "Insufficient number of PDF fields."
        field_err_2 = f"Field Count: {field_count}"
        field_err_3 = f"Fields:\n\t{combined_items}"
        field_err_msg = "\n".join([field_err_0, field_err_1, field_err_2, field_err_3])
        raise Exception(field_err_msg + "\n")
    return pdf_fields


def xjustification(field_text: str) -> str:
    field_text: str = (
        field_text.strip()
        .encode("utf-8", errors="ignore")
        .decode("ascii", errors="ignore")
        .replace('"', "'")
    )
    return '"' + field_text + '"'


def xname(field_text: str) -> str:
    last_first: str = ""
    if " " in field_text:
        split_name = field_text.split()
        for i in split_name:
            if "(" in i and ")" in i or (i[0] == '"' == i[-1]):
                split_name.remove(i)  # i == 'NickName' or (NickName)
        if len(split_name) == 2:
            if "," in split_name[0]:  # [0,1] = Last, First
                last_first = field_text
            elif (
                "." not in field_text
            ):  # [0,1] = First Last  -  not F. Last  -  not First L.
                last_first = ", ".join([split_name[1], split_name[0]])
        elif all(
            [
                len(split_name) == 3,
                "," not in split_name[0],
                1 <= len(split_name[1]) < 3,
            ]
        ):  # [0,1,2] = First M. Last  -  not F. M. Last  -  not First Middle Last
            last_first = ", ".join([split_name[2], split_name[0]])
    return last_first.title() if last_first else field_text


def xnumerical(field_text: str) -> int:
    if "." in field_text:
        field_text = field_text.split(".")[0]
    digits: int = int("".join(i for i in field_text if str(i).isdigit()))
    return digits


def get_nominator_name(first_page_fields: dict[str, str | int]) -> str:
    for field_name, field_text in first_page_fields.items():
        if field_name in ["please print", "nominators name"]:
            return xname(field_text)
    return ""

def get_type(first_page_fields: dict[str, str | int], grp=False, ind=False) -> str:
    award_type: str = "SAS"
    for field_name in first_page_fields.keys():
        if grp and field_name in ["on the spot award", "hours"]:
            award_type = "OTS"
            break
        elif ind and "the spot" in field_name or "hours" in field_name:
            award_type = "OTS"
    return award_type


def get_justification(last_page: dict[str, str]) -> str:
    for field_name, field_text in last_page.items():
        if "extent" in field_name:
            return xjustification(field_text)


VALUE_CHOICES: list = ["moderate", "high", "exceptional"]
ENTENT_CHOICES: list = ["limited", "extended", "general"]


def get_value_and_extent(last_page: dict[str, str]) -> dict:
    value_and_extent: dict = {}
    for field_name, field_text in last_page.items():
        if field_name in VALUE_CHOICES:
            value_and_extent["Value"] = {
                "Text": str(field_name).capitalize(),
                "Index": VALUE_CHOICES.index(field_name),
            }
        elif field_name in ENTENT_CHOICES:
            value_and_extent["Extent"] = {
                "Text": str(field_name).capitalize(),
                "Index": ENTENT_CHOICES.index(field_name),
            }
    if not value_and_extent:
        for field_name, field_text in last_page.items():
            if "extent" in field_name:
                awardJustificationText: list = field_text.split(" ")
                for i in range(0, len(awardJustificationText), 8):
                    n = 0 if i < 36 else i - 36
                    sentence: str = " ".join(i for i in awardJustificationText[n:i])
                    val_ext_detected: list = [
                        [v, e]
                        for v in VALUE_CHOICES
                        for e in ENTENT_CHOICES
                        if v in sentence and e in sentence
                    ]
                    if val_ext_detected:
                        val_ext_found: list[str] = val_ext_detected[0]
                        for text in val_ext_found:
                            sentence = sentence.replace(
                                text, "<--" + text.upper() + "-->"
                            )
                        print("Value and Extent Detected:\n")
                        print(*val_ext_detected, "\n")
                        print("Sentence:\n>>> ", sentence, "\n")
                        print("Enter 1 to verify.")
                        sentence_verification: str = input(">>> ")
                        if sentence_verification == "":
                            return None
                        elif sentence_verification == str(1):
                            value_and_extent["Value"] = {
                                "Text": str(val_ext_found[0]).capitalize(),
                                "Index": VALUE_CHOICES.index(val_ext_found[0]),
                            }
                            value_and_extent["Extent"] = {
                                "Text": str(val_ext_found[1]).capitalize(),
                                "Index": ENTENT_CHOICES.index(val_ext_found[1]),
                            }
                            return value_and_extent
    return value_and_extent


MONEY_MATRIX = [
    [500, 1000, 3000],  # moderate
    [1000, 3000, 6000],  # high
    [3000, 6000, 10000],  # exceptional
]  # limited    extended    general
TIME_MATRIX = [
    [9, 18, 27],  # moderate
    [18, 27, 36],  # high
    [27, 36, 40],  # exceptional
]  # limited    extended    general


def validate_award_amounts(
    name_award_amts: list[dict],
    value_extent: dict[dict[str, str | int]],
    grp=False,
    ind=False,
) -> None:
    value_idx: int = value_extent["Value"]["Index"]
    extent_idx: int = value_extent["Extent"]["Index"]
    max_monetary: int = MONEY_MATRIX[value_idx][extent_idx]
    max_hours: int = TIME_MATRIX[value_idx][extent_idx]
    if grp is True:
        invalid_awards: list = []
        for nominee_fields in name_award_amts:
            name: str = nominee_fields["Name"]
            money_award: int = nominee_fields["Monetary"]
            time_award: int = nominee_fields["Hours"]
            money_percent: int = money_award / max_monetary
            time_percent: int = time_award / max_hours
            combined_percent = money_percent + time_percent
            within_limits: bool = combined_percent <= 100
            if not within_limits:
                a: str = f"Nominee:  {name}"
                b: str = f"Monetary: ${money_award}        (Max: ${max_monetary})"
                c: str = f"Time:     {time_award} hours    (Max: {max_hours} hours)"
                d: str = f"Combined: {combined_percent}%   (Max: 100%)"
                errNominee: str = "\n".join([a, b, c, d])
                invalid_awards.append(errNominee)
        if invalid_awards:
            a: str = "Error:"
            b: str = (
                "Award amounts exceed the maximum allowed based on the selected award value and extent."
            )
            c: str = f"Value:  {value_extent['Value']['Text']}"
            d: str = f"Extent: {value_extent['Extent']['Text']}"
            e: str = "Nominees:"
            f: str = "\n\n\t".join(invalid_awards)
            errGrp: str = (
                "\n".join(
                    [
                        a,
                        b,
                        c,
                        d,
                        e,
                    ]
                )
                + "\n"
            )
            raise Exception(errGrp)
    elif ind is True:
        ind_name: str = name_award_amts["Name"]
        money_award: int = name_award_amts["Monetary"]
        time_award: int = name_award_amts["Hours"]
        money_percent: int = money_award / max_monetary
        time_percent: int = time_award / max_hours
        combined_percent = money_percent + time_percent
        within_limits: bool = combined_percent <= 1
        if not within_limits:
            a: str = f"Error:"
            b: str = (
                f"Award amounts exceed the maximum allowed based on the selected award value and extent."
            )
            c: str = f"Value:    {value_extent['Value']['Text']}"
            d: str = f"Extent:   {value_extent['Extent']['Text']}"
            e: str = f"Nominee:  {ind_name}"
            f: str = f"Monetary: ${money_award}  (Max: ${max_monetary})"
            g: str = f"Time: {time_award} hours  (Max: {max_hours} hours)"
            errInd: str = "\n".join([a, b, e, c, d, f, g]) + "\n"
            raise Exception(errInd)


def get_shared_ind_grp_data(pdf_fields: dict[str, int | dict[str, str]]) -> dict:
    first_page_fields: dict = pdf_fields["first_page"]
    last_page_fields: dict = pdf_fields["last_page"]
    shared_data: dict = {
        "Funding Org": (
            get_funding_org(first_page_fields, grp=True)
            if pdf_fields["category"] == "GRP"
            else get_funding_org(first_page_fields, ind=True)
        ),
        "Nominator"
        "Justification": get_justification(last_page_fields),
        "Type": (
            get_type(first_page_fields, grp=True)
            if pdf_fields["category"] == "GRP"
            else get_type(first_page_fields, ind=True)
        ),
    }
    if None in shared_data.values():
        none_fields = [
            str("- " + field)
            for field in shared_data.keys()
            if shared_data[field] is None
        ]
        none_fields_err = "\n".join(none_fields)
        raise Exception(f"Error:\nMissing required fields:\n{none_fields_err}\n")
    return shared_data


XLS_TO_TXT = r""


def writeXlsRows(award_data: dict) -> None:
    award_id = award_data["Award ID"]
    award_date = award_data["Date Received"]
    award_category = award_data["Category"]
    award_type = award_data["Type"]
    award_nominator = award_data["Nominator"]
    award_org = award_data["Funding Org"]
    award_just = award_data["Justification"]
    if award_data.get("Nominee"):  # IND
        award_nominee = award_data["Nominee"]
        award_money = award_data["Monetary"]
        award_time = award_data["Hours"]
        xls_row = f"{award_id}\t{award_date}\t\t{award_nominee}\t{award_category}\t{award_type}\t{award_money}\t{award_time}\t{award_nominator}\t{award_org}\t\t{award_just}\n"
        with open(XLS_TO_TXT, "a") as f:
            f.write(xls_row)
    elif award_data.get("Nominees"):  # GRP
        for nominee in award_data["Nominees"]:
            award_nominee = nominee["Name"]
            award_money = nominee["Monetary"]
            award_time = nominee["Hours"]
            xls_row = f"{award_id}\t{award_date}\t\t{award_nominee}\t{award_category}\t{award_type}\t{award_money}\t{award_time}\t{award_nominator}\t{award_org}\t\t{award_just}\n"
            with open(XLS_TO_TXT, "a") as f:
                f.write(xls_row)


def determine_date_received(pdf_fields: dict[str, int | dict[str, str]]) -> str:
    for k, v in pdf_fields["first_page"].items():
        if k == "date received" and v.lower() != "today":
            return v
    return datetime.now().strftime("%Y-%m-%d")


def insertDateReceived(filePath: str, award_data: dict) -> None:
    with fitz.open(filePath) as doc:
        for page in doc:
            for field in page.widgets():
                fkey: str = field.field_name.lower()
                fxrf: str = field.xref
                if fkey == "date received":
                    date = page.load_widget(fxrf)
                    date.field_value = award_data["Date Received"]
                    date.update()
                    doc.saveIncr()


def format_and_save(fileName: str, award_data: dict) -> str:
    award_data: dict = dict(award_data)
    k_len = max([len(k) for k in award_data.keys()])
    award_data["Justification"] = (
        str(len(award_data["Justification"].split())) + " words"
    )
    if award_data["Category"] == "IND":
        award_data["Monetary"] = "$" + str(award_data["Monetary"])
        award_data["Hours"] = str(award_data["Hours"]) + " hours"
        award_data["Nominee"] = (
            f"{award_data['Nominee']}    {award_data['Monetary']}    {award_data['Hours']}"
        )
        del award_data["Monetary"]
        del award_data["Hours"]
    elif award_data["Category"] == "GRP":
        nominees = award_data["Nominees"]
        award_data["Nominees"] = format_grp_nominees(nominees)
    res: str = (
        fileName
        + '\n\n'
        + "\n".join(f"{(k + ':').ljust(k_len + 2)} {v}" for k, v in award_data.items())
        + '\n'
        + "." * 50 
        + '\n\n'
    )
    with open(r""
        f.write(res)
    return res


def createNewFileName(award_data: dict) -> str:
    id: str = award_data["Award ID"]
    org: str = award_data["Funding Org"]
    nominee: str = (
        award_data["Nominee"]
        if award_data.get("Nominee")
        else str(len(award_data["Nominees"])) + " nominees"
    )
    date: str = award_data["Date Received"]
    return " - ".join(
        [
            id,
            org,
            nominee,
            date,
        ]
    )


def renameAwardFile(filePath: str, new_file_name: str) -> None:
    try:
        directory: str = os.path.dirname(filePath) + "\\"
        old_file_name: str = os.path.basename(filePath)
        new_path = directory + new_file_name + ".pdf"
        os.rename(filePath, new_path)
        return new_path
    except FileNotFoundError:
        print(f"{filePath} not found.")
    except Exception as e:
        print(f"Error occurred while renaming file: {e}")


# ----------------------------------------------------------------------------------------------------
# GRP FUNCTIONS
# ----------------------------------------------------------------------------------------------------


def determine_grp_configuration(page_count: int) -> list[list]:
    all_configs_nom_i1 = ("employee name_3", "award amount_2", "time off hours_2")
    all_configs_nom_i2 = ("employee name_4", "award amount_3", "time off hours_3")
    all_configs_nom_i3 = ("employee name_5", "award amount_4", "time off hours_4")
    all_configs_nom_i4 = ("employee name_6", "award amount_5", "time off hours_5")
    all_configs_nom_i5 = ("employee name_7", "award amount_6", "time off hours_6")
    all_configs_nom_i6 = ("employee name_8", "award amount_7", "time off hours_7")
    all_grp_configuration_duplicates: list = [
        all_configs_nom_i1,
        all_configs_nom_i2,
        all_configs_nom_i3,
        all_configs_nom_i4,
        all_configs_nom_i5,
        all_configs_nom_i6,
    ]

    nom_i7 = ("employee name_9", "award amount_8", "time off hours_8")
    nom_i8 = ("employee name_10", "award amount_9", "time off hours_9")
    nom_i9 = ("employee name_11", "award amount_10", "time off hours_10")
    nom_i10 = ("employee name_12", "award amount_11", "time off hours_11")
    nom_i11 = ("employee name_13", "award amount_12", "time off hours_12")
    nom_i12 = ("employee name_14", "award amount_13", "time off hours_13")
    nom_i13 = ("employee name_15", "award amount_14", "time off hours_14")
    max14_max21_duplicates: list = [
        nom_i7,
        nom_i8,
        nom_i9,
        nom_i10,
        nom_i11,
        nom_i12,
        nom_i13,
    ]

    max7_config: list = [
        ("employee name_2", "award amount", "time off hours")
    ] + all_grp_configuration_duplicates

    max14_config: list = max7_config + max14_max21_duplicates

    max21_config: list = (
        [("employee name_1", "award amount", "time off hours")]
        + all_grp_configuration_duplicates
        + max14_max21_duplicates
        + [("employee name_15", "award amount_15", "time off hours_15")]
        + [("employee name_16", "award amount_16", "time off hours_16")]
        + [("employee name_17", "award amount_10", "time off hours_10")]
        + max14_config[10:]
    )

    if page_count == 3:
        return max7_config
    elif page_count == 4:
        return max14_config
    elif page_count == 5:
        return max21_config


def get_grp_nominees_names_and_award_amounts(
    grp_nominees_fields: list[list], mid_page_fields: dict
) -> list[dict]:
    nominees_detected: list = []
    nominees_processed: list = []
    no_award_amounts_found: list = []

    for nominee_fields in grp_nominees_fields:
        nominee_name_field: str = nominee_fields[0]
        monetary_field: str = nominee_fields[1]
        hours_field: str = nominee_fields[2]
        current_nominee: dict = {"Name": None, "Monetary": 0, "Hours": 0}

        for field_name, field_text in mid_page_fields.items():
            if "employee name" in field_name and field_text not in nominees_detected:
                nominees_detected.append(field_text)
            current_nominee["Name"] = (
                xname(field_text)
                if current_nominee["Name"] is None and field_name == nominee_name_field
                else current_nominee["Name"]
            )
            current_nominee["Monetary"] = (
                xnumerical(field_text)
                if field_name == monetary_field
                else current_nominee["Monetary"]
            )
            current_nominee["Hours"] = (
                xnumerical(field_text)
                if field_name == hours_field
                else current_nominee["Hours"]
            )

        if current_nominee["Name"] is not None:
            if current_nominee["Monetary"] == 0 and current_nominee["Hours"] == 0:
                if len(grp_nominees_fields) == 21 and nominee_fields in (
                    grp_nominees_fields[13],
                    grp_nominees_fields[14],
                ):
                    continue
                no_award_amounts_found.append(
                    ", ".join(f"{k}: {v}" for k, v in current_nominee.items())
                )
            nominees_processed.append(current_nominee)
    if len(nominees_detected) == 0 or len(nominees_processed) == 0:
        return None
    elif len(nominees_detected) > len(nominees_processed):
        join_detected = "\n\t".join(i for i in nominees_detected)
        join_processed = "\n\t".join(i for i in nominees_processed)
        det_pro_err_0 = "Error:"
        det_pro_err_1 = (
            "Number of nominees detected does not match number of nominees processed\n"
        )
        det_pro_err_2 = f"Detected: {len(nominees_detected)}\n\t{join_detected}\n"
        det_pro_err_3 = f"Processed {len(nominees_processed)}\n\t{join_processed}\n"
        det_pro_err_msg = (
            "\n".join(
                [
                    det_pro_err_0,
                    det_pro_err_1,
                    det_pro_err_2,
                    det_pro_err_3,
                ]
            )
            + "\n"
        )
        raise Exception(det_pro_err_msg)
    elif no_award_amounts_found:
        join_no_award = "\n\t".join(str(i) for i in no_award_amounts_found)
        raise Exception(f"Error: No award amounts found.\n\t{join_no_award}\n")
    return nominees_processed


def format_grp_nominees(nominees: list[dict[str, str]]) -> str:
    max_name_len = max([len(nominee["Name"]) for nominee in nominees]) + 5
    max_monetary_len = max([len(str(nominee["Monetary"])) for nominee in nominees]) + 5
    return "\n    " + "\n    ".join(
        f"{(nominee['Name']+':').ljust(max_name_len)}${str(nominee['Monetary']).ljust(max_monetary_len)}{nominee['Hours']} hours"
        for nominee in nominees
    )


def process_grp_award_data(pdf_fields: dict, grp_sn: int) -> dict:
    last_page_fields: dict = pdf_fields["last_page"]
    mid_pages_fields = pdf_fields["mid_pages"]
    grp_award_data: dict = {
        "Award ID": "24-GRP-" + str(grp_sn).zfill(3),
    }
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    grp_award_data.update(shared_ind_grp_data)
    grp_award_data["Category"] = "GRP"
    group_configuration = determine_grp_configuration(pdf_fields["page_count"])
    nominees = get_grp_nominees_names_and_award_amounts(
        group_configuration, mid_pages_fields
    )
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominees, value_and_extent, grp=True)
        grp_award_data["Value"] = value_and_extent["Value"]["Text"]
        grp_award_data["Extent"] = value_and_extent["Extent"]["Text"]
    grp_award_data["Nominees"] = nominees
    grp_award_data["Date Received"] = determine_date_received(pdf_fields)
    return grp_award_data


# ----------------------------------------------------------------------------------------------------
#  IND FUNCTIONS
# ----------------------------------------------------------------------------------------------------


def get_ind_name_amounts(first_page_fields: dict) -> str:
    ind_name_amounts: dict = {
        "Name": None,
        "Monetary": 0,
        "Hours": 0,
    }
    for field_name, field_text in first_page_fields.items():
        if ind_name_amounts["Name"] is None and field_name == "employee name":
            ind_name_amounts["Name"] = xname(field_text)

        elif (
            ind_name_amounts["Monetary"] == 0
            and field_name in ["amount", "undefined"]
            or "the spot" in field_name
        ):
            ind_name_amounts["Monetary"] = xnumerical(field_text)

        elif ind_name_amounts["Hours"] == 0 and "hours" in field_name:
            ind_name_amounts["Hours"] = xnumerical(field_text)
    ind_name_amounts_str = "\t".join(f"{k}: {v}" for k, v in ind_name_amounts.items())
    if ind_name_amounts["Monetary"] == 0 == ind_name_amounts["Hours"]:
        raise Exception(f"No award amount found.\n{ind_name_amounts_str}\n")
    elif ind_name_amounts["Name"] is None:
        raise Exception("Unable to determine IND award nominee")
    return ind_name_amounts


def process_ind_award_data(pdf_fields: dict, ind_sn: int) -> str:
    first_page_fields: dict = pdf_fields["first_page"]
    last_page_fields: dict = pdf_fields["last_page"]
    ind_award_data: dict = {
        "Award ID": "24-IND-" + str(ind_sn).zfill(3),
    }
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    ind_award_data.update(shared_ind_grp_data)
    ind_award_data["Category"] = "IND"
    nominee_name_award_amounts: str = get_ind_name_amounts(first_page_fields)
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominee_name_award_amounts, value_and_extent, ind=True)
        ind_award_data["Value"] = value_and_extent["Value"]["Text"]
        ind_award_data["Extent"] = value_and_extent["Extent"]["Text"]
    ind_award_data["Nominee"] = nominee_name_award_amounts["Name"]
    ind_award_data["Monetary"] = nominee_name_award_amounts["Monetary"]
    ind_award_data["Hours"] = nominee_name_award_amounts["Hours"]
    ind_award_data["Date Received"] = determine_date_received(pdf_fields)
    return ind_award_data


def getSerialNums() -> dict[str:int]:
    with open(AWARD_SER_NUMS, "r""
        jsonSerNums: json[str:int] = json.load(f)
        serialNums: dict[str:int] = {
            "IND": jsonSerNums["IND"],
            "GRP": jsonSerNums["GRP"],
        }
        return serialNums


def updateSerialNums(serialNums: dict[str:int]) -> None:
    with open(AWARD_SER_NUMS, "w") as f:
        json.dump(serialNums, f, indent=4)


def move_file(filePath: str) -> None:
    shutil.move(filePath, FY24_FOLDER)


def processFiles() -> None:
    try:
        serialNums: dict[str:int] = getSerialNums()
        indID: int = serialNums["IND"]
        grpID: int = serialNums["GRP"]
        notProcessed: list[str] = []
        folderPath: str = PROCESSING_FOLDER
        if TESTING:
            folderPath = TEST_FOLDER
        awardFiles: Path = Path(folderPath).rglob("*pdf")
        for awardFile in awardFiles:
            fileName: str = get_file_name(awardFile)
            nameLen: int = len(fileName)
            lineBreak: str = "".ljust(nameLen, "-")
            try:
                pdfFields: dict = get_pdf_fields(awardFile)
                awardCategory: str = pdfFields["category"]
                if awardCategory == "GRP":
                    awardData = process_grp_award_data(pdfFields, grpID)
                    grpID += 1
                else:
                    awardData = process_ind_award_data(pdfFields, indID)
                    indID += 1
                if PRINT_AWARD_DATA:
                    formattedData: str = format_and_save(fileName,awardData)
                    print(formattedData)
                if CREATE_XLS_ROWS:
                    writeXlsRows(awardData)
                if INSERT_DATE:
                    insertDateReceived(str(awardFile), awardData)
                newFileName: str = createNewFileName(awardData)
                if RENAME_AND_MOVE:
                    newFilePath: str = renameAwardFile(awardFile, newFileName)
                    move_file(newFilePath)

            except Exception as e:
                print(f"\n{lineBreak}\n{fileName}\nError: {e}\n")
                notProcessed.append(fileName)
        if UPDATE_AWARD_SER_NUMS:
            updateSerialNums({"IND": indID, "GRP": grpID})
        if len(notProcessed) > 0:
            print(f"Not Processed ({len(notProcessed)}):")
            print("\n".join(notProcessed))
    except Exception as e:
        print(f"Error: {e}")


# ----------------------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    print()
    print("START".center(100, "-"))
    print()
    try:
        processFiles()
    except Exception as e:
        print(e)
    print()
    print("END".center(100, "-"))
    print()
