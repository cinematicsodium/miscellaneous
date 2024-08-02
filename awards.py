

from datetime import datetime
from pprint import pprint
from pathlib import Path
import shutil
import fitz
import json
import os

# ==================
TESTING: bool = False
UPDATE_AWARD_SER_NUMS: bool = True
PRINT_AWARD_DATA: bool = True
CREATE_XLS_ROWS: bool = True
INSERT_DATE: bool = True
RENAME_AND_MOVE: bool = True
# ==================
PROCESSING_FOLDER: str = (
    r"C:\Users\Processing Folder"
)
FY24_FOLDER: str = (
    r"C:\Users\FY24 Folder"
)
TEST_FOLDER: str = (
    r"C:\Users\Test Folder"
)
AWARD_SER_NUMS: str = (
    r"C:\Users\Serial Numbers"
)


# ----------------------------------------------------------------------------------------------------
# SHARED AWARD TOOLS
# ----------------------------------------------------------------------------------------------------


def get_file_name(filePath: str) -> str:
    return os.path.basename(filePath)

MIN_PAGE_COUNT: int = 2
MAX_PAGE_COUNT: int = 5
FIRST_PAGE: int = 0
def get_pdf_fields(pdf_file: str) -> dict:
    with fitz.open(pdf_file) as doc:
        page_count: int = doc.page_count
        last_page: int = page_count - 1
        pdf_fields: dict = {
            "first_page": {},
            "mid_pages": {},
            "last_page": {},
            "page_count": page_count,
            "file_name": os.path.basename(pdf_file)
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


def get_funding_org(
    first_page_fields: dict[str, str | int], grp=False, ind=False
) -> str:

    def collect_list_of_divs(first_page_fields: dict) -> list | None:
        divisions_fields: list = []
        for field_name, field_text in first_page_fields.items():
            if field_name in ["org_2", "organization_3", "org_4"] and grp is True:
                divisions_fields.append(str(field_text).upper())
            elif (
                field_name
                in ["org_6", "org_4", "org", "organization_2", "organization_5"]
                and ind is True
            ):
                divisions_fields.append(str(field_text).upper())
        return divisions_fields if divisions_fields else None

    def define_funding_org(divisions_fields: list) -> str | list | None:
        if None == divisions_fields:
            return None
        org_ZJR: list[str] = ['div_EPB', 'div_OAQ', 'div_LCK', 'div_SKG', 'div_PAK', 'div_HCV', 'div_JDU', 'div_HUA', 'div_KNA', 'div_ISV']
        org_QTB: list[str] = ['div_MOS', 'div_HGD', 'div_FMB', 'div_LIY', 'div_OMO', 'div_QKQ', 'div_QEK', 'div_ISR', 'div_VTB', 'div_BIP']
        org_OKJ: list[str] = ['div_MOT', 'div_IWR', 'div_KXL', 'div_MAI', 'div_SUJ', 'div_ZKA', 'div_UPK', 'div_ZVI', 'div_OVW', 'div_MBQ']
        org_FTD: list[str] = ['div_RCW', 'div_LYQ', 'div_TVE', 'div_DTS', 'div_PMI', 'div_ZRK', 'div_KKY', 'div_XJB', 'div_IFM', 'div_JXM']
        org_UJY: list[str] = ['div_KTP', 'div_ZHN', 'div_CBC', 'div_ELV', 'div_BRL', 'div_HCJ', 'div_VWX', 'div_FRH', 'div_RGM', 'div_QBH']
        org_TWT: list[str] = ['div_RCI', 'div_FND', 'div_DGP', 'div_RED', 'div_KRF', 'div_STZ', 'div_QJB', 'div_DKA', 'div_GRM', 'div_EGS']
        org_ACO: list[str] = ['div_VEL', 'div_HGX', 'div_HVY', 'div_EWZ', 'div_OBO', 'div_GQQ', 'div_EDI', 'div_TUO', 'div_PCM', 'div_YRF']
        org_DFB: list[str] = ['div_ABD', 'div_YVX', 'div_ZLT', 'div_TUA', 'div_PBM', 'div_MKR', 'div_QAF', 'div_RIU', 'div_JNH', 'div_UAD']
        org_LQA: list[str] = ['div_OZB', 'div_IAB', 'div_ZCA', 'div_LVN', 'div_UMB', 'div_VJR', 'div_AHF', 'div_PFG', 'div_IDL', 'div_UWZ']
        org_IXN: list[str] = ['div_CVY', 'div_JZQ', 'div_TFL', 'div_EIT', 'div_OED', 'div_LPK', 'div_JDR', 'div_FCL', 'div_WFQ', 'div_AKC']
        org_RCC: list[str] = ['div_NIW', 'div_FLA', 'div_UBL', 'div_UCR', 'div_MDF', 'div_XSF', 'div_JIQ', 'div_HQO', 'div_AZA', 'div_QZA']
        org_IPZ: list[str] = ['div_MGI', 'div_VZS', 'div_WBF', 'div_PEH', 'div_WZI', 'div_GEY', 'div_SNE', 'div_PPB', 'div_LKB', 'div_EXF']
        org_QAK: list[str] = ['div_RDK', 'div_SDN', 'div_BKC', 'div_AYF', 'div_YPG', 'div_NQR', 'div_QEK', 'div_FHD', 'div_CJR', 'div_SYQ']
        org_RHL: list[str] = ['div_YKW', 'div_PBX', 'div_AUE', 'div_WFP', 'div_TVG', 'div_JWR', 'div_MXQ', 'div_WSD', 'div_XAJ', 'div_WAK']
        org_LIY: list[str] = ['div_KJB', 'div_UID', 'div_LTB', 'div_HWN', 'div_KGN', 'div_TDI', 'div_FUK', 'div_PRN', 'div_GSZ', 'div_HQD']
        org_EGW: list[str] = ['div_SEY', 'div_LAO', 'div_BHN', 'div_LWL', 'div_NCC', 'div_GOU', 'div_HLT', 'div_HAD', 'div_HDE', 'div_ZJX']
        org_ZKB: list[str] = ['div_SYH', 'div_HST', 'div_FEO', 'div_PTR', 'div_QKV', 'div_SMY', 'div_IDU', 'div_QZB', 'div_BEM', 'div_QDG']
        org_WZJ: list[str] = ['div_EMS', 'div_WHU', 'div_HBH', 'div_PXD', 'div_IEG', 'div_ZCL', 'div_KXD', 'div_OUQ', 'div_UPI', 'div_JNI']
        org_ROY: list[str] = ['div_SSW', 'div_BVW', 'div_IUN', 'div_UBM', 'div_WCK', 'div_ZXJ', 'div_QMO', 'div_FEX', 'div_ROD', 'div_STZ']
        org_RCK: list[str] = ['div_UVD', 'div_IJN', 'div_LLN', 'div_EIG', 'div_XQB', 'div_GQW', 'div_SBN', 'div_TEY', 'div_KMM', 'div_NPG']
        orgs: list[str] = [org_ZJR, org_QTB, org_OKJ, org_FTD, org_UJY, org_TWT, org_ACO, org_DFB, org_LQA, org_IXN, org_RCC, org_IPZ, org_QAK, org_RHL, org_LIY, org_EGW, org_ZKB, org_WZJ, org_ROY, org_RCK]

        for div_field in divisions_fields:
            for org in orgs:
                main_div: str = org[0]
                for div in org:
                    if div.lower() in div_field.lower() or div.lower() == div_field.lower():
                        if main_div == "NA-MB":
                            return div
                        return main_div

    divisions_fields: list = collect_list_of_divs(first_page_fields)
    funding_org: str = define_funding_org(divisions_fields)
    if funding_org:
        return funding_org
    elif divisions_fields:
        print("Unable to Determine Funding Org.\n")
        print(f"Divisions Found: {', '.join(divisions_fields)}\n")
        manual_org_selection: str = input("Enter Selection:\n>>> NA-").strip().upper()
        print()
        if manual_org_selection == "":
            return None
        elif manual_org_selection in ["na", "nx"]:
            pass
        else:
            manual_org_selection = "NA-" + manual_org_selection
        return manual_org_selection


def get_type(first_page_fields: dict[str, str | int], grp=False, ind=False) -> str:
    if ind is True:
        sas_fields: list[str] = ['hours_2','time off award','special act or service','undefined',]
        for field_name in first_page_fields.keys():
            if field_name in sas_fields:
                return "SAS"
        return "OTS"
    elif grp is True:
        ots_fields: list[str] = ['on the spot','hours',]
        for field_name in first_page_fields.keys():
            if field_name in ots_fields:
                return "OTS"
        return "SAS"


def get_justification(last_page: dict[str, str]) -> str:
    for field_name, field_text in last_page.items():
        if "extent" in field_name:
            return xjustification(field_text)


VALUE_CHOICES: list = ["moderate", "high", "exceptional"]
EXTENT_CHOICES: list = ["limited", "extended", "general"]

def get_value_and_extent(last_page: dict[str, str]) -> dict:
    """
    Extracts value and extent information from the last page.

    Args:
    last_page (dict[str, str]): A dictionary containing the last page data.

    Returns:
    dict: A dictionary containing the extracted value and extent information.
    """
    value_extent_dict: dict = {}
    items = list(last_page.items())

    # Check if value or extent is directly present in the last page
    for field_name, field_text in items:
        if field_name in VALUE_CHOICES:
            value_extent_dict["Value"] = {
                "Text": field_name.capitalize(),
                "Index": VALUE_CHOICES.index(field_name),
            }
        elif field_name in EXTENT_CHOICES:
            value_extent_dict["Extent"] = {
                "Text": field_name.capitalize(),
                "Index": EXTENT_CHOICES.index(field_name),
            }

    # If not found, search in the text
    if not value_extent_dict:
        for field_name, field_text in items:
            if "extent" in field_name:
                award_justification_text: list = field_text.split(" ")
                for i in range(0, len(award_justification_text), 8):
                    n = 0 if i < 36 else i - 36
                    sentence: str = " ".join(award_justification_text[n:i])
                    val_ext_detected: list = [
                        [v, e]
                        for v in VALUE_CHOICES
                        for e in EXTENT_CHOICES
                        if v in sentence and e in sentence
                    ]
                    if val_ext_detected:
                        val_ext_found: list[str] = val_ext_detected
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
                            value_extent_dict["Value"] = {
                                "Text": val_ext_found.capitalize(),
                                "Index": VALUE_CHOICES.index(val_ext_found),
                            }
                            value_extent_dict["Extent"] = {
                                "Text": val_ext_found.capitalize(),
                                "Index": EXTENT_CHOICES.index(val_ext_found),
                            }
                            return value_extent_dict
    return value_extent_dict


from typing import List, Dict, Union

MONETARY_LIMITS = [
    [500, 1000, 3000],  # moderate
    [1000, 3000, 6000],  # high
    [3000, 6000, 10000],  # exceptional
]  # limited    extended    general

TIME_LIMITS = [
    [9, 18, 27],  # moderate
    [18, 27, 36],  # high
    [27, 36, 40],  # exceptional
]  # limited    extended    general

def validate_award_amounts(
    nominees: list[dict],
    val_and_ext_vals: dict,
    is_group: bool = False,
    is_individual: bool = False
) -> None:
    value_index: int = val_and_ext_vals["Value"]["Index"]
    extent_index: int = val_and_ext_vals["Extent"]["Index"]
    max_monetary: int = MONETARY_LIMITS[value_index][extent_index]
    max_hours: int = TIME_LIMITS[value_index][extent_index]

    def check_award_limits(name: str, monetary_award: int, time_award: int) -> Union[str, None]:
        monetary_percentage: float = monetary_award / max_monetary
        time_percentage: float = time_award / max_hours
        total_percentage = monetary_percentage + time_percentage
        if total_percentage > 1:
            return (
                f"Nominee:  {name}\n"
                f"Monetary: ${monetary_award} (Max: ${max_monetary})\n"
                f"Time:     {time_award} hours (Max: {max_hours} hours)\n"
                f"Combined: {total_percentage:.2%} (Max: 100%)"
            )
        return None

    if is_group:
        invalid_nominations: List[str] = []
        for nominee in nominees:
            result = check_award_limits(nominee["Name"], nominee["Monetary"], nominee["Hours"])
            if result:
                invalid_nominations.append(result)
        
        if invalid_nominations:
            error_message = (
                f"Error:\n"
                f"Award amounts exceed the maximum allowed based on the selected award value and extent.\n"
                f"Value:  {val_and_ext_vals['Value']['Text']}\n"
                f"Extent: {val_and_ext_vals['Extent']['Text']}\n"
                f"Nominees:\n\n\t" + "\n\n\t".join(invalid_nominations)
            )
            raise ValueError(error_message)

    elif is_individual:
        result = check_award_limits(nominees["Name"], nominees["Monetary"], nominees["Hours"])
        if result:
            error_message = (
                f"Error:\n"
                f"Award amounts exceed the maximum allowed based on the selected award value and extent.\n"
                f"Value:    {val_and_ext_vals['Value']['Text']}\n"
                f"Extent:   {val_and_ext_vals['Extent']['Text']}\n"
                f"{result}"
            )
            raise ValueError(error_message)

def get_shared_ind_grp_data(pdf_fields: dict[str, int | dict[str, str]]) -> dict:
    first_page_fields: dict = pdf_fields["first_page"]
    last_page_fields: dict = pdf_fields["last_page"]
    shared_data: dict = {
        "Funding Org": (
            get_funding_org(first_page_fields, grp=True)
            if pdf_fields["category"] == "GRP"
            else get_funding_org(first_page_fields, ind=True)
        ),
        "Nominator": get_nominator_name(first_page_fields),
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


XLS_TO_TXT = r"C:\Users\joseph.strong\OneDrive - US Department of Energy\Python\process_award_data\spreadsheet_rows.txt"


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
    with open(r"process_award_data\awards_output.txt", "a") as f:
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
    if str(pdf_fields["file_name"]).startswith("24-"):
        grp_award_data["Award ID"] = pdf_fields["file_name"].split(" ")[0]
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    grp_award_data.update(shared_ind_grp_data)
    grp_award_data["Category"] = "GRP"
    group_configuration = determine_grp_configuration(pdf_fields["page_count"])
    nominees = get_grp_nominees_names_and_award_amounts(
        group_configuration, mid_pages_fields
    )
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominees, value_and_extent, is_group=True)
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
    if str(pdf_fields["file_name"]).startswith("24-"):
        ind_award_data["Award ID"] = pdf_fields["file_name"].split(" ")[0]
    shared_ind_grp_data: dict = get_shared_ind_grp_data(pdf_fields)
    ind_award_data.update(shared_ind_grp_data)
    ind_award_data["Category"] = "IND"
    nominee_name_award_amounts: str = get_ind_name_amounts(first_page_fields)
    value_and_extent: dict = get_value_and_extent(last_page_fields)
    if value_and_extent:
        validate_award_amounts(nominee_name_award_amounts, value_and_extent, is_individual=True)
        ind_award_data["Value"] = value_and_extent["Value"]["Text"]
        ind_award_data["Extent"] = value_and_extent["Extent"]["Text"]
    ind_award_data["Nominee"] = nominee_name_award_amounts["Name"]
    ind_award_data["Monetary"] = nominee_name_award_amounts["Monetary"]
    ind_award_data["Hours"] = nominee_name_award_amounts["Hours"]
    ind_award_data["Date Received"] = determine_date_received(pdf_fields)
    return ind_award_data


def getSerialNums() -> dict[str:int]:
    with open(AWARD_SER_NUMS, "r") as f:
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
        folderPath: str = PROCESSING_FOLDER if not TESTING else TEST_FOLDER
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
                if not TESTING:
                    if INSERT_DATE:
                        insertDateReceived(str(awardFile), awardData)
                    newFileName: str = createNewFileName(awardData)
                    if RENAME_AND_MOVE:
                        newFilePath: str = renameAwardFile(awardFile, newFileName)
                        move_file(newFilePath)

            except Exception as e:
                print(f"\n{lineBreak}\n{fileName}\nError: {e}\n")
                notProcessed.append(fileName)
        if UPDATE_AWARD_SER_NUMS and not TESTING:
            updateSerialNums({"IND": indID, "GRP": grpID})
        if len(notProcessed) > 0:
            print(f"Not Processed ({len(notProcessed)}):")
            print("\n".join(notProcessed))
    except Exception as e:
        print(f"Error: {e}")

def testProcessIND(file: str) -> None:
    try:
        fields = get_pdf_fields(file)
        award = process_ind_award_data(pdf_fields=fields,ind_sn=1)
        with open('blank.txt','w') as file:
            pprint(award, stream=file)
    except Exception as e:
        print(e)
# ----------------------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    print()
    print("START".center(100, "-"))
    print()
    try:
        processFiles()
        # file = r"X:\filepath.pdf"
        # fields = get_pdf_fields(file)
        # award = process_ind_award_data(pdf_fields=fields,ind_sn=1)
        # with open('blank.txt','w') as file:
        #     pprint(award, stream=file)
    except Exception as e:
        print(e)
    print()
    print("END".center(100, "-"))
    print()
