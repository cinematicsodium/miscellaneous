def underline_print(text):
    text = str(text)
    n = len(text)
    print()
    if "C:" in text:
        print("".ljust(125, "-"))
        print(text)
        print()
        return
    print(text)
    print("".ljust(n, "-"))
    print()

def award(Pathlib: object,serial_ind: int,serial_grp: int) -> bool:
    from dataclasses import dataclass
    from datetime import datetime
    from pprint import pprint
    import fitz
    import os
    
    date = datetime.today()
    today = date.strftime("%Y-%m-%d")
    revPath = "".join(i for i in reversed(str(Pathlib))).lower()
    n = revPath.index("\\")
    file_name = "".join(i for i in reversed(revPath[0:n]))
    path_name = str(Pathlib)
    x = "\n"

    def metadata_date(date_str):
        # D:20231006133323-06'00'
        if 'D:' not in date_str:
            return date_str
        date_part = date_str[2:10]
        time_part = date_str[10:16]
        date_time = datetime.strptime(date_part + time_part,'%Y%m%d%H%M%S')
        meta_date = date_time.strftime('%Y-%m-%d')
        return meta_date

    def rename_file(source, dest):
        try:
            directory, filename = os.path.split(source)
            new_path = os.path.join(directory, dest)
            os.rename(source, new_path)
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def amt_format(n):
        val = n.strip()
        if " " in val:
            val = val.split()[0]
        if " hrs" in val:
            val = val.replace("hrs",'')
        if " hours" in val:
            val = val.replace("hours",'')
        if '.' in val:
            val = val.split('.')[0]
        if '.' in val:
            val = val.split('.')[0]
        if "$" in val:
            val = val.replace("$",'')
        if "," in val:
            val = val.replace(",",'')
        if '"' in val:
            val = val.replace('"','')
        if val.isdigit():
            val = int(val)
            return val
        return n

    def sort_print_list(text):
        if isinstance(text,list):
            print("Count: ",len(text),"\n")
            text.sort()
            for field in text:
                key = field[0]
                val = field[1]
                keychars = len(key)
                if keychars > 32:
                    x = keychars - 32
                    y = keychars // 2
                    key = str(key[:y] + "." * x + key[y + x :])
                if " " in val and len(val.split()) > 25:
                    val = str(len(val.split())) + " words"
                print(key.ljust(36),val)
        elif isinstance(text,str):
            print(text)
        print("\n")

    def add_date_received(Pathlib: object) -> None:
        nonlocal today
        with fitz.open(Pathlib) as doc:
            for page in doc:
                date_xref = None
                fields = page.widgets()
                for field in fields:
                    key = field.field_name
                    key = key.strip().lower()
                    if key == "date received":
                        date_xref = field.xref
                        break
                if date_xref is not None:
                    date_field = page.load_widget(date_xref)
                    date_field.field_value = today
                    date_field.update()
                    doc.saveIncr()
                    return

    def classify_award() -> str:
        nonlocal file_name,path_name
        award = None

        skip = ['pending_','test_','template_']
        for i in skip:
            if i in file_name.lower():
                return False

        ind_class = ['indiv','indv','-ind-']
        for i in ind_class:
            if i in file_name:
                award = 'IND'

        grp_class = ['grp','group']
        for j in grp_class:
            if j in file_name:
                award = 'GRP'

        if award is None:
            underline_print(path_name)
            while True:
                valid_input = ('i','g','x')
                class_input = input('Classify award [i] [g] [x]: ').strip().lower()
                if class_input not in valid_input:
                    continue
                elif class_input == 'i':
                    award = 'IND'
                elif class_input == 'g':
                    award = 'GRP'
                elif class_input == 'x':
                    msg = 'UNABLE TO CLASSIFY AWARD FILE'
                    print(''.ljust(len(msg),'#'),x,msg)
                    print(''.ljust(len(msg),'#'))
                    return
                break
        # underline_print(path_name)
        return award

    def match_org(form_field_org_list):
        if len(form_field_org_list) == 0:
            return None
        orgAAA = ['ORG-AAA-001', 'ORG-AAA-002', 'ORG-AAA-003', 'ORG-AAA-004', 'ORG-AAA-005']
        orgBBB = ['ORG-BBB-001', 'ORG-BBB-002', 'ORG-BBB-003', 'ORG-BBB-004', 'ORG-BBB-005']
        orgCCC = ['ORG-CCC-001', 'ORG-CCC-002', 'ORG-CCC-003', 'ORG-CCC-004', 'ORG-CCC-005']
        orgDDD = ['ORG-DDD-001', 'ORG-DDD-002', 'ORG-DDD-003', 'ORG-DDD-004', 'ORG-DDD-005']
        orgEEE = ['ORG-EEE-001', 'ORG-EEE-002', 'ORG-EEE-003', 'ORG-EEE-004', 'ORG-EEE-005']
        orgFFF = ['ORG-FFF-001', 'ORG-FFF-002', 'ORG-FFF-003', 'ORG-FFF-004', 'ORG-FFF-005']
        orgGGG = ['ORG-GGG-001', 'ORG-GGG-002', 'ORG-GGG-003', 'ORG-GGG-004', 'ORG-GGG-005']
        orgHHH = ['ORG-HHH-001', 'ORG-HHH-002', 'ORG-HHH-003', 'ORG-HHH-004', 'ORG-HHH-005']
        orgIII = ['ORG-III-001', 'ORG-III-002', 'ORG-III-003', 'ORG-III-004', 'ORG-III-005']
        orgJJJ = ['ORG-JJJ-001', 'ORG-JJJ-002', 'ORG-JJJ-003', 'ORG-JJJ-004', 'ORG-JJJ-005']
        orgKKK = ['ORG-KKK-001', 'ORG-KKK-002', 'ORG-KKK-003', 'ORG-KKK-004', 'ORG-KKK-005']
        orgLLL = ['ORG-LLL-001', 'ORG-LLL-002', 'ORG-LLL-003', 'ORG-LLL-004', 'ORG-LLL-005']
        orgMMM = ['ORG-MMM-001', 'ORG-MMM-002', 'ORG-MMM-003', 'ORG-MMM-004', 'ORG-MMM-005']
        orgNNN = ['ORG-NNN-001', 'ORG-NNN-002', 'ORG-NNN-003', 'ORG-NNN-004', 'ORG-NNN-005']
        orgOOO = ['ORG-OOO-001', 'ORG-OOO-002', 'ORG-OOO-003', 'ORG-OOO-004', 'ORG-OOO-005']
        orgPPP = ['ORG-PPP-001', 'ORG-PPP-002', 'ORG-PPP-003', 'ORG-PPP-004', 'ORG-PPP-005']
        orgQQQ = ['ORG-QQQ-001', 'ORG-QQQ-002', 'ORG-QQQ-003', 'ORG-QQQ-004', 'ORG-QQQ-005']
        orgRRR = ['ORG-RRR-001', 'ORG-RRR-002', 'ORG-RRR-003', 'ORG-RRR-004', 'ORG-RRR-005']
        orgSSS = ['ORG-SSS-001', 'ORG-SSS-002', 'ORG-SSS-003', 'ORG-SSS-004', 'ORG-SSS-005']
        orgTTT = ['ORG-TTT-001', 'ORG-TTT-002', 'ORG-TTT-003', 'ORG-TTT-004', 'ORG-TTT-005']
        orgs =  [orgAAA,orgBBB,orgCCC,orgDDD,orgEEE,orgFFF,orgGGG,orgHHH,orgIII,orgJJJ,orgKKK,orgLLL,orgMMM,orgNNN,orgOOO,orgPPP,orgQQQ,orgRRR,orgSSS,orgTTT]
        for org in orgs:
            office=org[0]
            for div in org:
                for form_field_org in form_field_org_list:
                    if div in form_field_org.upper():return office
        return form_field_org_list

    def name_format(name: str) -> str:
        if all(i not in name for i in (",",".")) and len(name.split()) == 2:
            last_first = name.split()[1] + "," + name.split()[0]
            return last_first
        elif len(name.strip().split()) == 3 and 1 <= len(name.split()[1]) <= 2:
            last_first = name.split()[2] + "," + name.split()[0]
            return last_first
        return name

    def grp_doc_pg_count(Pathlib):
        with fitz.open(Pathlib) as doc:
            page_count = 0
            n = 0
            for page in doc:
                n += 1
            if n == 3:
                page_count = 7
            elif n == 4:
                page_count = 14
            elif n == 5:
                page_count = 21
            return page_count

    def grpAward(Pathlib: object,page_count: int,serial: int) -> bool:
        nonlocal today

        if page_count == 0:
            return False

        @dataclass
        class Award:
            id = f"24-GRP-{str(serial).zfill(3)}"
            date = today
            category = "GRP"
            type = None
            org = None
            nominator = None
            justification = None
            justCount = None
            nominee = None
            money: int = 0
            time: int = 0
            value_str = None
            extent_str = None
            value: int = None
            extent: int = None

            def __str__(self) -> str:
                return f"{self.id}\t{self.date}\t\t{self.nominee}\t{self.category}\t{self.type}\t{self.money}\t{self.time}\t{self.nominator}\t{self.org}\t\t{self.justification}\n"

            def print_vals(self):
                underline_print("Award Values:")
                for key,val in self.__dict__.items():
                    if (
                        val is not None
                        and " " in str(val)
                        and len(str(val).split(" ")) > 50
                    ):
                        print(str(key+':').title().ljust(16),str(len(str(val).split(" "))) + " words")
                        continue
                    elif 'val' in key or 'ext' in key and val is None:
                        continue
                    print(key.ljust(16),val)

        award = Award()

        x01 = ["employee name_2","award amount","time off hours"]
        x02 = ["employee name_3","award amount_2","time off hours_2"]
        x03 = ["employee name_4","award amount_3","time off hours_3"]
        x04 = ["employee name_5","award amount_4","time off hours_4"]
        x05 = ["employee name_6","award amount_5","time off hours_5"]
        x06 = ["employee name_7","award amount_6","time off hours_6"]
        x07 = ["employee name_8","award amount_7","time off hours_7"]
        grp7 = [x01,x02,x03,x04,x05,x06,x07]

        y01 = ["employee name_2","award amount","time off hours"]
        y02 = ["employee name_3","award amount_2","time off hours_2"]
        y03 = ["employee name_4","award amount_3","time off hours_3"]
        y04 = ["employee name_5","award amount_4","time off hours_4"]
        y05 = ["employee name_6","award amount_5","time off hours_5"]
        y06 = ["employee name_7","award amount_6","time off hours_6"]
        y07 = ["employee name_8","award amount_7","time off hours_7"]
        y08 = ["employee name_9","award amount_8","time off hours_8"]
        y09 = ["employee name_10","award amount_9","time off hours_9"]
        y10 = ["employee name_11","award amount_10","time off hours_10"]
        y11 = ["employee name_12","award amount_11","time off hours_11"]
        y12 = ["employee name_13","award amount_12","time off hours_12"]
        y13 = ["employee name_14","award amount_13","time off hours_13"]
        y14 = ["employee name_15","award amount_14","time off hours_14"]
        grp14 = [y01,y02,y03,y04,y05,y06,y07,y08,y09,y10,y11,y12,y13,y14]

        z01 = ["employee name_1","award amount","time off hours"]
        z02 = ["employee name_3","award amount_2","time off hours_2"]
        z03 = ["employee name_4","award amount_3","time off hours_3"]
        z04 = ["employee name_5","award amount_4","time off hours_4"]
        z05 = ["employee name_6","award amount_5","time off hours_5"]
        z06 = ["employee name_7","award amount_6","time off hours_6"]
        z07 = ["employee name_8","award amount_7","time off hours_7"]
        z08 = ["employee name_9","award amount_8","time off hours_8"]
        z09 = ["employee name_10","award amount_9","time off hours_9"]
        z10 = ["employee name_11","award amount_10","time off hours_10"]
        z11 = ["employee name_12","award amount_11","time off hours_11"]
        z12 = ["employee name_13","award amount_12","time off hours_12"]
        z13 = ["employee name_14","award amount_13","time off hours_13"]
        z14 = ["employee name_15","award amount_14","time off hours_14"]
        z15 = ["employee name_15","award amount_15","time off hours_15"]
        z16 = ["employee name_16","award amount_16","time off hours_16"]
        z17 = ["employee name_17","award amount_10","time off hours_10"]
        z18 = ["employee name_12","award amount_11","time off hours_11"]
        z19 = ["employee name_13","award amount_12","time off hours_12"]
        z20 = ["employee name_14","award amount_13","time off hours_13"]
        z21 = ["employee name_15","award amount_14","time off hours_14"]
        grp21 = [z01,z02,z03,z04,z05,z06,z07,z08,z09,z10,z11,z12,z13,z14,z15,z16,z17,z18,z19,z20,z21,]

        with fitz.open(Pathlib) as doc:
            xls_lines = []
            nominee_iter_count: int = 0
            count_nominee_fields = []
            processed_nominees = []
            val_list = ["moderate","high","exceptional"]
            ext_list = ["limited","extended","general"]
            award_fields = []
            all_fields = []
            metadata = []

            metaitems = doc.metadata.items()
            for key,val in metaitems:
                if val is None or key is None or val.isspace() or val == "":
                    continue
                elif key == 'modDate':
                    award.date = metadata_date(val)
                kv = [key,val]
                metadata.append(kv)

            nominees = []
            final_pg: int = 0
            if page_count == 7:
                nominees = grp7
                final_pg = 2
            elif page_count == 14:
                nominees = grp14
                final_pg = 3
            elif page_count == 21:
                nominees = grp21
                final_pg = 4
            else:
                underline_print("Unable to determine GRP document type.")
                return False

            for page in doc:
                fields = page.widgets()
                for field in fields:
                    key = field.field_name
                    key = key.strip().lower()
                    val = field.field_value
                    val = val.strip()
                    if val is None or key is None or val.isspace() or val == "":
                        continue
                    kv = [key,val]
                    all_fields.append(kv)
                    if "employee name" in key:
                        if page.number == 0 or page.number == final_pg:
                            continue
                        count_nominee_fields.append(key)

            for nominee in nominees:
                nominee_iter_count += 1
                if nominee_iter_count > len(count_nominee_fields) + 1:
                    break

                nom_name = nominee[0]
                nom_money = nominee[1]
                nom_time = nominee[2]

                if nom_name not in count_nominee_fields:
                    continue
                else:
                    sas_list = ["special service or act","time off award","undefined","hours_2"]
                    ots_list = ["on the spot award","hours"]
                    nom_list = ["please print","nominators name"]
                    just_list = ["extent of application","extent of application limited extended or general"]
                    org_list = ["org_2","organization_3","org_4"]
                    org_hold = []

                    for page in doc:
                        fields = page.widgets()
                        for field in fields:
                            key = field.field_name
                            key = key.strip().lower()
                            val = field.field_value
                            val = val.strip()
                            if val is None or key is None or val.isspace() or val == "":
                                continue
                            kv = [key,val]

                            if page.number == 0:
                                if award.type is None:
                                    if key in sas_list:
                                        award.type = "SAS"
                                        award_fields.append(kv)
                                    elif key in ots_list:
                                        award.type = "OTS"
                                        award_fields.append(kv)
                                elif award.nominator is None and key in nom_list:
                                    award.nominator = name_format(val.title())
                                    award_fields.append(kv)
                                elif award.org is None and key in org_list:
                                    org_hold.append(val)
                                    award_fields.append(kv)

                            elif page != 0:
                                if (
                                    award.justification is None 
                                    and key in just_list):
                                    just: str = (
                                        val.strip()
                                        .replace("  "," ")
                                        .replace("\r","    ")
                                        .replace("\n","    ")
                                        .replace("\t","    ")
                                        .encode("utf-8")
                                        .decode("ascii",errors="ignore")
                                    )
                                    award.justification = just
                                    award.justCount = (
                                        str(len(just.strip().split())) + " words"
                                    )
                                    award_fields.append([key,award.justCount])
                                elif (
                                    award.value is None
                                    and key in val_list
                                    and val.lower() == "on"
                                ):
                                    award.value = val_list.index(key)
                                    award.value_str = key.capitalize()
                                elif (
                                    award.extent is None
                                    and key in ext_list
                                    and val.lower() == "on"
                                ):
                                    award.extent = ext_list.index(key)
                                    award.extent_str = key.capitalize()
                                elif page.number == final_pg and "employee name" in key:
                                    continue

                                elif page_count == 21 and nominee == nominees[13]:
                                    if page.number == 2:
                                        if key == nom_name:
                                            award.nominee = name_format(val)
                                            award_fields.append(kv)
                                        elif key == nom_money:
                                            val = amt_format(val)
                                            award.money = val
                                            award_fields.append(kv)
                                        elif key == nom_time:
                                            val = amt_format(val)
                                            award.time = val
                                            award_fields.append(kv)
                                    continue
                                elif page_count == 21 and nominee == nominees[14]:
                                    if page.number == 3:
                                        if key == nom_name:
                                            award.nominee = name_format(val)
                                            award_fields.append(kv)
                                        elif key == nom_money:
                                            val = amt_format(val)
                                            award.money = val
                                            award_fields.append(kv)
                                        elif key == nom_time:
                                            val = amt_format(val)
                                            award.time = val
                                            award_fields.append(kv)
                                    continue

                                elif key == nom_name:
                                    val = name_format(val)
                                    award.nominee = val
                                    award_fields.append(kv)
                                elif key == nom_money:
                                    val = amt_format(val)
                                    award.money = val
                                    award_fields.append(kv)
                                elif key == nom_time:
                                    val = amt_format(val)
                                    award.time = val
                                    award_fields.append(kv)

                if award.org is None:
                    award.org = match_org(org_hold)
                if isinstance(award.org,list) and len(award.org) > 1:
                    print(x,x)
                    for n, i in enumerate(award.org):
                        print(str(n).zfill(2),i)
                    print(x,'Enter or Select Award Org')
                    select_org = input('>>> ').strip().lower()
                    if select_org.isdigit() and select_org in range(len(award.org)):
                        award.org = award.org[select_org]
                    elif '.' in select_org:
                        award.org = 'NA-' + select_org


                temp_type = award.type
                if temp_type is None and all(
                    x is not None for x in (award.nominee,award.money,award.time)
                ):
                    award.type = "SAS"

                award_items = [
                    award.id,
                    award.date,
                    award.nominee,
                    award.category,
                    award.type,
                    award.money,
                    award.time,
                    award.nominator,
                    award.org,
                    award.justCount,
                ]
                if None in award_items:
                    underline_print(path_name)
                    print("Award Value(s) == None")
                    award.print_vals()
                    return False

                elif (
                    (award.money == 0 and award.time == 0)
                    or not isinstance(award.money,int)
                    and not isinstance(award.time,int)
                ):
                    underline_print(path_name)
                    underline_print("See Monetary/Time Value(s)")
                    print("Monetary".ljust(16),award.money,type(award.money))
                    print("Time:".ljust(16),award.time,type(award.time),x)
                    return False

                elif all(
                    i is not None
                    for i in (
                        award.value,
                        award.value_str,
                        award.extent,
                        award.extent_str,
                    )
                ):
                    money_matrix = [
                        [500,      1000,      3000],    # moderate
                        [1000,     3000,      6000],    # high
                        [3000,     6000,      10000],   # exceptional
                    ]   # limited    extended    general
                    max_money: int = money_matrix[award.value][award.extent]
                    time_matrix = [
                        [9,        18,        27], # moderate
                        [18,       27,        36], # high
                        [27,       36,        40], # exceptional
                    ]   # ltd       ext'd       gen.
                    max_time: int = time_matrix[award.value][award.extent]
                    total_percent: float = (award.money / max_money) + (
                        award.time / max_time
                    )
                    percent_str = format(total_percent,".0%")

                    if total_percent > 1:
                        underline_print(path_name)
                        underline_print("Award Value(s) Exceed Max Amount Allowable")
                        print("AwardValue:".ljust(16),award.value_str.capitalize())
                        print("AwardExtent:".ljust(16),award.extent_str.capitalize(),
                              x,x)
                        print("Nominee:".ljust(16),award.nominee.title(),
                              x)
                        print(
                            "Monetary:".ljust(16),str("$" + str(award.money)).ljust(12),
                            "Max Allowed: ",str("$" + str(max_money)).ljust(12),
                            "Percent of Max: ",format(award.money / max_money,".0%"),
                        )
                        print(
                            "Time:".ljust(16),str(str(award.time) + " hrs").ljust(12),
                            "Max Allowed: ",str(str(max_time) + " hrs").ljust(12),
                            "Percent of Max: ",format(award.time / max_time,".0%"),x,
                        )
                        print(
                            "Total Percent:".ljust(16),percent_str," (Must be less than or equal to 100%)",x,
                        )
                        return False

                xls_lines.append(str(award))
                nominee_vals = [award.nominee,award.money,award.time]
                processed_nominees.append(nominee_vals)

            if len(processed_nominees) != len(count_nominee_fields):
                underline_print(path_name)
                underline_print("Verify Number of Nominees")
                print("Number of Nominees Detected:".ljust(32),len(count_nominee_fields))
                print("Number of Nominees Found:".ljust(32),len(processed_nominees),
                      x)
                print(count_nominee_fields)
                underline_print("Award Fields:")
                sort_print_list(award_fields)
                # underline_print('All Fields:')
                # sort_print_list(all_fields)
                return False

            # award_str = f'{"Award ID:".ljust(16)}{award.id} \n{"Nominator:".ljust(16)}{award.nominator} \n{"Funding Org:".ljust(16)}{award.org} \n{"Date Received:".ljust(16)}{award.date} \n{"Category:".ljust(16)}{award.category} \n{"Type:".ljust(16)}{award.type} \n{"Justification:".ljust(16)}{award.justCount} \n'
            # print(award_str)
            # processed_nominees.sort()
            # for i in processed_nominees:
            #     nom_name: str
            #     nom_money: int
            #     nom_time: int
            #     nom_name,nom_money,nom_time = i[0].title(),i[1],i[2]
            #     if i == processed_nominees[0]:
            #         print(f'Nominees & \n{"Award Amt(s):".ljust(16)}{nom_name.ljust(24)}${str(nom_money).ljust(8)}{nom_time} hours')
            #         print(f'{"".ljust(16)}{"".ljust(41,"-")}')
            #         continue
            #     print(f'{"".ljust(16)}{nom_name.ljust(24)}${str(nom_money).ljust(8)}{nom_time} hours')
            #     print(f'{"".ljust(16)}{"".ljust(41,"-")}')
            # print(x)
            # with open("output.txt","a") as f:
            #     for i in xls_lines:
            #         f.write(i)
            return True

    def indAward(Pathlib: object,serial: int) -> bool:
        nonlocal today

        with fitz.open(Pathlib) as doc:
            award_id = f"24-IND-{str(serial).zfill(3)}"
            award_date = today
            award_category = "IND"
            award_type = None
            award_nominee = None
            award_money: int = 0
            award_time: int = 0
            award_nominator: str = None
            award_org = None
            award_just = None
            award_justCount: str = None
            val_list = ["moderate","high","exceptional"]
            ext_list = ["limited","extended","general"]
            value_str = None
            extent_str = None
            value: int = None
            extent: int = None

            nominee = "employee name"
            sasBtn = "special service or act"
            sasMoney = ["amount","undefined"]
            sasTime = ["hours","hours_2"]
            otsMoney = "the spot"
            otsTime = "hours"
            nominator = ["please print","nominators name"]
            org = ["org_6","org_4","org","organization_2","organization_5"]
            justif = "extent"
            org_hold = []

            award_fields = []
            all_fields = []
            metadata = []

            metaitems = doc.metadata.items()
            for key,val in metaitems:
                key = key
                val = val
                if val is None or val.isspace() or val == "":
                    continue
                elif key == 'modDate':
                    award_date = metadata_date(val)
                kv = [key,val]
                metadata.append(kv)

            for page in doc:
                fields = page.widgets()
                for field in fields:
                    key = field.field_name
                    key = key.strip().lower()
                    val = field.field_value
                    val = val.strip()
                    if val is None or val.isspace() or val == "":
                        continue
                    kv = [key,val]
                    all_fields.append(kv)

                    if val is not None and len(str(val)) > 100 or justif in key:
                        just = (
                            val.strip()
                            .replace("  "," ")
                            .replace("\\r","")
                            .replace("\r","")
                            .replace("\n","")
                            .replace("\t","")
                        )
                        award_just = [val]
                        award_justCount = str(len(just.split())) + " words"
                        award_fields.append([key,award_justCount])

                    elif val is None or val.isspace() or val == "":
                        continue
                    elif key in val_list and val.lower() == "on":
                        value = val_list.index(key)
                        value_str = key.capitalize()
                    elif key in ext_list and val.lower() == "on":
                        extent = ext_list.index(key)
                        extent_str = key.capitalize()
                    elif key == nominee:
                        award_fields.append(kv)
                        award_nominee = name_format(val)
                    elif key == sasBtn and val == "on":
                        award_type = "SAS"
                        award_fields.append(kv)
                    elif otsMoney in key:
                        award_money = amt_format(val)
                        award_type = "OTS"
                        award_fields.append(kv)
                    elif key == otsTime:
                        award_time = amt_format(val)
                        award_type = "OTS"
                        award_fields.append(kv)
                    elif key in nominator:
                        award_fields.append(kv)
                        award_nominator = name_format(val)
                    elif key in sasMoney:
                        award_money = amt_format(val)
                        award_type = "SAS"
                        award_fields.append(kv)
                    elif key in org:
                        award_fields.append(kv)
                        org_hold.append(val.upper())
                    elif key in sasTime:
                        award_time = amt_format(val)
                        award_type = "SAS"
                        award_fields.append(kv)
                    elif key == 'date received':
                        award_date = val

            if len(org_hold) >= 1:
                award_org = match_org(org_hold)

            award_dict: dict = {
                "ID": award_id,
                "Date": award_date,
                "Name": award_nominee,
                "Category": award_category,
                "Type": award_type,
                "Monetary": award_money,
                "Time": award_time,
                "Nominator": award_nominator,
                "Org": award_org,
                "Justif": award_just,
            }

            if None in award_dict.values():
                underline_print(path_name)
                err_msg = "Award Value(s) == None"
                underline_print(err_msg)
                for k,v in award_dict.items():
                    print(str(str(k) + ":").ljust(16),v)
                print()
                return False

            elif all(i is not None for i in (value,value_str,extent,extent_str)):
                money_matrix = [
                    [500,      1000,      3000], # moderate
                    [1000,     3000,      6000], # high
                    [3000,     6000,      10000],# exceptional
                ]   # limited   #extended   #general
                max_money: int = money_matrix[value][extent]
                time_matrix = [
                    [9,        18,        27], # moderate
                    [18,       27,        36], # high
                    [27,       36,        40], # exceptional
                ]   # limited   #extended   #general
                max_time: int = time_matrix[value][extent]
                amt_percent: float = (award_money / max_money) + (award_time / max_time)
                percent_str = format(amt_percent,".0%")
                if amt_percent > 1:
                    underline_print(path_name)
                    underline_print("Award Value(s) Exceed Max Amount Allowable")
                    print("AwardValue:".ljust(16),value_str.capitalize())
                    print("AwardExtent:".ljust(16),extent_str.capitalize(),
                          x)
                    print("Nominee:".ljust(16),award_nominee.title(),
                          x)

                    print(
                        "Monetary:".ljust(16),str("$" + str(award_money)).ljust(12),
                        "Max Allowed:",str("$" + str(max_money)).ljust(12),
                        "Percent of Max:",format(award_money / max_money,".0%"),
                    )
                    print(
                        "Time:".ljust(16),str(str(award_time) + " hrs").ljust(12),
                        "Max Allowed:",str(str(max_time) + " hrs").ljust(12),
                        "Percent of Max:",format(award_time / max_time,".0%"),x,
                    )
                    print(
                        "Total Percent:".ljust(16),percent_str," (Must be less than or equal to 100%)",x,
                    )
                    return False

            elif (award_money == 0 and award_time == 0) or not all(
                isinstance(i,int) for i in (award_money,award_time)
            ):
                underline_print(path_name)
                underline_print("See Award Value(s)")
                print("Monetary".ljust(16),award_money)
                print("Time:".ljust(16),award_time,x)
                for k,v in award_dict.items():
                    print(str(str(k) + ":").ljust(16),v)
                print()
                return False

            award_repr = f"{award_id}\t{award_date}\t\t{award_nominee}\t{award_category}\t{award_type}\t{award_money}\t{award_time}\t{award_nominator}\t{award_org}\t\t{award_just}\n"
            # with open("output.txt","a") as f:
            #     f.write(award_repr)

            # print(
            #     x,
            #     "Award ID:".ljust(16),award_id,x,
            #     "Nominator:".ljust(16),award_nominator,x,
            #     "Funding Org:".ljust(16),award_org,x,
            #     "Date Received:".ljust(16),award_date,x,
            #     "Category:".ljust(16),award_category,x,
            #     "Type:".ljust(16),award_type,x,
            #     "Justification:".ljust(16),award_justCount,)
            # print(
            #     x,
            #     "Nominee &",x,"Award Amt(s):".ljust(16),
            #         award_nominee.ljust(24),
            #         "$",str(award_money).ljust(8),
            #         award_time," hours",
            # )
            # print("".ljust(16),"".ljust(50,"-"))
            return True

    category = classify_award()
    if category == False:
        return False

    elif category == "IND":
        if indAward(Pathlib,serial_ind) == True:
            # add_date_received(Pathlib)
            return "IND"

    elif category == "GRP":
        page_count: int = grp_doc_pg_count(Pathlib)
        if grpAward(Pathlib,page_count,serial_grp) == True:
            # add_date_received(Pathlib)
            return "GRP"


if __name__ == "__main__":
    pass
