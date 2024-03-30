from string import punctuation
import csv
import re

def extract_properties(input_text):
    """
    Extract all extractable properties, which follow the following format in the description:
        <property> <value>
    """
    properties_dict = {}

    for prop in all_properties:
        # Create a regular expression pattern for the current property
        pattern = re.compile(rf'\b{re.escape(prop)}\s*(\S+)\b', re.IGNORECASE)

        # Search for the pattern in the input text
        match = pattern.search(input_text)

        if match:
            # Store the match in the properties dictionary
            properties_dict[prop] = match.group(1)

            # Remove the found property and its value from the input text
            input_text = re.sub(rf'\b{re.escape(prop)}\s*{re.escape(properties_dict[prop])}\b', '', input_text, flags=re.IGNORECASE).strip()

    return properties_dict, input_text.strip().strip(punctuation)

def extract_diameter(description):
    """
    Extracts the diameter from the description, based on the keyword "DIA"
    Contains a helper function is_valid_diameter_value
    Note: references the unit_length list (update accordingly!)
    """
    def is_valid_diameter_value(word):
        """
        Checks if the extracted diameter value is valid (i.e. has a number and a valid unit measurement of length)
        """
        # Define a regex pattern for valid diameter values
        # first regex extracts mixed fractions
        diameter_pattern = re.compile(r'(?:\S+\s+)*?((?:\d+\s+)?\d+/\d+\s*(?:' + '|'.join(units_dia) + r'))',re.IGNORECASE)   # good for mixed or unmixed fractions
        match = diameter_pattern.search(word)
        if match:
            return match.group(1)
        else:
            # next regex captures whole numbers
            diameter_pattern = re.compile(r'(?:\S+\s+)*?(\d+\s*(?:'+'|'.join(units_dia)+r'))(?=\s|$)',re.IGNORECASE)
            match = diameter_pattern.search(word)
            if match:
                return match.group(1)        
        return None
        # return bool(match)
    
    # Use regex to find the diameter in the description
    dia_match = re.search(r'\bDIA\b', description, re.IGNORECASE)
    
    if dia_match:
        # Extract the substring before and after "DIA"
        before_dia, after_dia = description.split("DIA", 1)

        # Check if the word preceding "DIA" is a valid diameter value
        before_dia = is_valid_diameter_value(before_dia.strip())
        if before_dia is not None:
            remaining_text = re.sub(before_dia, ' ', description, 1, flags=re.IGNORECASE)
            remaining_text = re.sub(r'\bDIA\b', '', remaining_text, flags=re.IGNORECASE)
            # remaining_text = re.sub("DIA", '', remaining_text, 1, flags=re.IGNORECASE)
            return before_dia.strip(), remaining_text.strip().strip(punctuation)

        after_dia = is_valid_diameter_value(after_dia.strip())
        if after_dia is not None:
            remaining_text = re.sub(after_dia, ' ', description, 1, flags=re.IGNORECASE)
            remaining_text = re.sub(r'\bDIA\b', '', remaining_text, flags=re.IGNORECASE)
            # remaining_text = re.sub("DIA", '', remaining_text, 1, flags=re.IGNORECASE)
            return after_dia.strip(), remaining_text.strip().strip(punctuation)

    return None, description.strip().strip(punctuation)

def extract_units(input_string):      
    unit_pattern = '|'.join(re.escape(unit) for unit in unit_property_map.keys())
    all_matches = []
    
    # checks for proper and improper fractions (taken from diameter algo)
    matches = re.findall(r'(?:\S+\s+)*?((?:\d+\s+)?\d+/\d+\s*(' + unit_pattern + r'))', input_string, flags=re.IGNORECASE)
    for match in matches:
        all_matches.append(match)
        unit = match[1]
        prop = unit_property_map.get(unit.lower())
        if prop:
            input_string = re.sub(match[0], '', input_string, 1, flags=re.IGNORECASE)
    
    # checks for whole numbers and decimals
    pattern = f'(?:\S+\s+)*?(\d+(?:[-.]\d+)?\s*({unit_pattern}))(?:/[^\\s]+)?(?=\s|$)'
    # pattern = f'(?:\S+\s+)*?(\d+(?:\.\d+)?\s*({unit_pattern}))(?:/[^\\s]+)?(?=\s|$)'
    matches = re.findall(pattern, input_string, flags=re.IGNORECASE)

    for match in matches:
        all_matches.append(match)
        unit = match[1]
        prop = unit_property_map.get(unit.lower())
        if prop:
            input_string = re.sub(match[0], '', input_string, 1, flags=re.IGNORECASE)
    
    # remove remaining " X " which separate dimensions
    input_string = re.sub(r'\bX\b', '', input_string, flags=re.IGNORECASE)
    
    return all_matches, input_string.strip().strip(punctuation)

def extract_color_name(input_string):
    """
    Extracts the colors based on common values found in the string
    """
    basic_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "white", "black", "gray", "brown", "pink", "grey"]

    # Remove leading and trailing whitespaces and convert to lowercase for case-insensitive matching
    normalized_input = input_string.strip().lower()

    # Construct a regular expression pattern for color matching
    pattern = re.compile(r'\b(?:light |dark )?(' + '|'.join(basic_colors) + r')\b')

    # Search for the color pattern in the input string
    match = pattern.search(normalized_input)

    if match:
        input_string = re.sub(match.group(0), '', input_string, 1, flags=re.IGNORECASE)
        return match.group(0), input_string
    else:
        return None, input_string

def extract_wire_type(input_string):
    """
    Extracts types of wires (e.g. THHN, THW-2, etc.)
    Update the wire_types list
    """
    wire_types_pattern = re.compile(r'\b(?:' + '|'.join(sorted(wire_types,reverse=True)) + r')\b', re.IGNORECASE)
    matches = wire_types_pattern.findall(input_string)
    for match in matches:
        # all_matches.append(match)
        input_string = re.sub(match, '', input_string, 1, flags=re.IGNORECASE)
            
    return matches, input_string.strip().strip(punctuation)

def extract_keywords(input_string):
    """
    Extracts unlabeled brands and other keywords in description
    (ex. brands: Panasonic, Phelps Dodge)
    Update the dictionary of lists keywords_known
    """
    
    for a_categ in keywords_known.keys():   # by the category, e.g. brand
        keywords_pattern = re.compile(r'\b(?:' + '|'.join(keywords_known[a_categ]) + r')\b', re.IGNORECASE)
        matches = keywords_pattern.findall(input_string)
        for match in matches:
            # all_matches.append(match)
            input_string = re.sub(match, '', input_string, 1, flags=re.IGNORECASE)
            
            # all_matches.append(match)
            prop = keywords_known_map.get(match.lower())
            if prop:
                input_string = re.sub(match, '', input_string, 1, flags=re.IGNORECASE)
            
    # TODO: double-check that variable "matches" is accurate (may return ALL but is not consistent with if prop: above)
    return matches, input_string.strip().strip(punctuation)

# Define a function to extract "type", "with_property", and clean the "info" column accordingly
def extract_with(input_string):
    # Extract "with_property"
    if ' WITH ' in input_string:
        with_start_index = info.index(' WITH ')
        with_property = info[with_start_index:].strip()
        # Remove "with_property" from "info"
        info = info[:with_start_index].strip()
    else:
        with_property = ''
    
    # Extract "type" (this example does not specifically parse "type" but gives a structure for potential extraction)
    # Assuming "type" could be more complex to extract, we'll leave this for specific case handling if needed

    # Update the row with cleaned "info" and extracted properties
    row['info'] = info
    row['with_property'] = with_property

    return row

# =================================
# DEFINING CONSTANTS HERE
# - populate unit_others with dict of property and its allowed units
# - populate units_dia with allowed units of diameter
# - populate wire_types with allowed types of wire (insulation)
# - populate keywords_known as dict with format: property=[<list_of_allowed_values>]. For ex., dict(wire_type=["male","female"], ...)
# =================================

# Read the input CSV file
# input_file_path = 'data_cleanup_physical-inventory/fresh-0304/physical_inventory_checkpoint0304_consmat-electrical_csv.csv' 
# output_file_path = 'data_cleanup_physical-inventory/fresh-0304/modified_consmat_electrical_csv.csv' 
# input_file_path = 'data_cleanup_physical-inventory/fresh-0304/physical_inventory_checkpoint0304_consmat_csv.csv' 
# output_file_path = 'data_cleanup_physical-inventory/fresh-0304/modified_consmat_csv_03-06.csv' 
# input_file_path = 'data_cleanup_physical-inventory/physical_inventory_joined_checkpoint-full.csv'  
# output_file_path = 'data_cleanup_physical-inventory/modified_sample.csv' 
# ? Original values
input_file_path = 'masterlist_03-08/masterlist_orig_0308_csv.csv' 
output_file_path = 'masterlist_03-08/masterlist_extracted_0308_csv.csv' 
# ? Modified for personal assignment
input_file_path = 'masterlist_03-27/masterlist_raw_categories_csv.csv' 
output_file_path = 'masterlist_03-27/masterlist_categories_extracted_csv.csv'
# categ_assigned = ['CON14', 'CON17', 'CON26', 'CON35', 'FWK18', 'FWK30', 'FWK31', 'LFO12', 'SPR11', 'SPR32', 'SPR44', 'SPR49', 'SPR53', 'SPR61', 'SPR65', 'SUP13', 'SUP17']


 
all_properties = ["P/N", "SN", "model", "brand", "grade","no.","sch"]

# important lists / constants
units_others = [{
    "prop": "weight",
    "unit": ["kg","kg/s","kgs","kilo","kilos","lbs","ton","tons","gram","grams","g","lbs/ft.","lbs/ft","lb","lb.","lbs","lbs."]
},{
    "prop": "cross-sectional area",
    "unit": ["mm sq","mm sq."]
},{
    "prop": "volume",
    "unit": ["cu. ft.","ml","litre","liter","liters","litres"]
},{
    "prop": "length",
    "unit": ["mm","m","in","ft","ml","cm","ft","ft.","meters","mtrs"]
},{
    "prop": "current",
    "unit": ["a","amp","amps","ampere"]
},{
    "prop": "voltage rating",
    "unit": ["v","kv","vdc","vac","v vdc","v vac"]
},{
    "prop": "power rating",
    "unit": ["w","watt","watts"]
},{
    "prop": "apparent power rating",
    "unit": ["va","kva"]
},{
    "prop": "horsepower",
    "unit": ["hp"]
},{
    "prop": "angle",
    "unit": ["deg"]
},{
    "prop": "frequency",
    "unit": ["rad/s","hz","hertz"]
},{
    "prop": "color temperature",
    "unit": ["k"]
},{
    "prop": "capacitance",
    "unit": ["f","mf","uf","pf"]
},{
    "prop": "inductance",
    "unit": ["h","mh","uh","ph"]
},{
    "prop": "conductors",
    "unit": ["c"]
},{
    "prop": "pins",
    "unit": ["pin","pins","prong","prongs"]
},{
    "prop": "phase",
    "unit": ["phase"]
},{
    "prop": "pole",
    "unit": ["p","pole","poles"]
},{
    "prop": "hole",
    "unit": ["hole","holes","-hole","-holes"]
},{
    "prop": "force",
    "unit": ["kn"]
},{
    "prop": "gang",
    "unit": ["gang","-gang"]
},{
    "prop": "teeth",
    "unit": ["teeth","-teeth"]
},{
    "prop": "spline",
    "unit": ["spline"]
}]

# note: conductors unit "C" may also be Coulomb (charge)
units_dia = ["mm","cm","m","in"]      # for diameter
wire_types = [
    "THHN", "THWN", "XHHW", "USE", "UF", "NM", "MC", "TECK", "BX",
    "RHW", "RW90", "THW", "PV", "FPL", "SER", "SEU", "USE-2", "MTW", "XLP",
    "SJOOW", "SOOW", "THW-2", "LSZH"
]
keywords_known = dict(
    brand=["Panasonic", "Phelps Dodge", "TELEMICANIQUE","Mcgill","Penn-union","Exoweld",
           "Kumweld","Firefly","Philips","Moldex"],    
)
keywords_known_map = {a_value.lower(): a_categ for a_categ in keywords_known.keys() for a_value in sorted(keywords_known[a_categ],reverse=True)}

# wire_types = [
#     "THHN", "THWN", "XHHW", "USE", "UF", "NM", "AC", "MC", "TECK", "BX",
#     "RHW", "RW90", "THW", "PV", "FPL", "SER", "SEU", "USE-2", "MTW", "XLP",
#     "SJOOW", "SOOW", "THW-2", "PVC", "LSZH"
# ]

unit_property_map = {unit: unit_info["prop"] for unit_info in units_others for unit in sorted(unit_info["unit"],reverse=True)}
# note: sorted the units in reverse to prioritize longer units
units_others_list = [a_prop["prop"] for a_prop in units_others]
print(units_others_list)


# =============================
#      PROGRAM BEGINS HERE
# =============================

# ? encoding: utf-8 or latin-1
with open(input_file_path, 'r', encoding='latin-1') as input_file, open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:    
    # Create CSV reader and writer objects
    csv_reader = csv.DictReader(input_file)
    new_columns = ['info', 'color', 'configuration','style','size','diameter', 'wire type']  # ! add 'dimensions' when extraction fixed
    
    # TODO 03-08-2024: add 3 columns
    
    # csv_columns = csv_reader.fieldnames[:csv_reader.fieldnames.index('Description') + 1] + new_columns + all_properties + csv_reader.fieldnames[csv_reader.fieldnames.index('Description') + 1:]
    csv_columns = ['extracted'] + csv_reader.fieldnames + new_columns + all_properties + units_others_list
    csv_writer = csv.DictWriter(output_file, fieldnames=csv_columns)
    
    # Write the header to the output file
    csv_writer.writeheader()

    # Iterate through each row and update 'fresh' column
    for row in csv_reader:
        # ! Important: check if assigned row is active, otherwise skip
        # if row["Product Group Code"] not in categ_assigned:
        #     continue
        # ? temporary comment: if description 2 already contains the keyword from Description column, splice! 
        # if(row["Item Category"].lower() in row["Description"].strip().lower()):
        #     total_descr = row["Description"].replace(row["Item Category"],"",1).strip().strip(punctuation)
        # else:
        #     total_descr = row["Description"]
        total_descr = row["Item Category"].strip().strip(punctuation)
        # total_descr = row["Description"].strip().strip(punctuation)
        
        # replace all colons AND commas AND semicolons AND periods with spaces
        total_descr = total_descr.replace(": "," ")
        total_descr = total_descr.replace(","," ")
        total_descr = total_descr.replace(". "," ")
        total_descr = total_descr.replace(";"," ")
        total_descr = total_descr.replace("("," ")
        total_descr = total_descr.replace(")"," ")
            
        # ! extract the properties
        result_properties, total_descr = extract_properties(total_descr)
        for prop, value in result_properties.items():
            # row[prop] = value
            try:
                if(row[prop] is not None or row[prop]!=''):
                    row[prop] += ", " + value
            except KeyError:
                row[prop] = value
        
        # ! extracting the diameter
        result_dia, total_descr = extract_diameter(total_descr)
        if result_dia is not None:
            row["diameter"] = result_dia
        
        # ! extracting the units
        # TODO: double check function; may accidentally truncate extra text?
        result_units, total_descr = extract_units(total_descr)
        # print(result_units)
        if result_units is not None:
            # print("found some")
            for match in result_units:
                unit = match[1]
                prop = unit_property_map.get(unit.lower())
                # print("prop:",prop,"and match:",match[0])
                if prop:
                    # check if there already is a property, so we just append the value
                    try:
                        if(row[prop] is not None or row[prop]!=''):
                            if(prop=='length'):
                                row[prop] += " X " + match[0]
                            else:
                                row[prop] += ", " + match[0]
                    except KeyError:
                        row[prop] = match[0]
        
        # ! extracting the color
        result_color, total_descr = extract_color_name(total_descr)
        if result_color is not None:
            row["color"] = result_color
        
        # ! extracting the wire type
        result_wire_type, total_descr = extract_wire_type(total_descr)
        if result_wire_type is not None:
            row["wire type"] = ", ".join(result_wire_type)
        
        # ! extracting keywords (e.g. brands)
        result_keywords, total_descr = extract_keywords(total_descr)
        if result_keywords is not None:
            for match in result_keywords:
                prop = keywords_known_map.get(match.lower())
                # print("Hit a match,",prop)
                if prop:
                    # check if there already is a property, so we just append the value
                    try:
                        if(row[prop] is not None or row[prop]!=''):
                            row[prop] += ", " + match
                    except KeyError:
                        row[prop] = match
        
        # TODO: extract all properties and combine cells!
        # configuration_props = ['current', 'voltage rating', 'power rating', 'apparent power rating', 'horsepower', 'angle', 'frequency', 'color temperature', 'capacitance', 'inductance', 'conductors', 'pins', 'phase', 'pole','hole','force','gang','grade','no.']
        configuration_props = [a_prop for a_prop in units_others_list if a_prop not in ("weight","volume","length")]
        configuration_values = []
        for a_prop in configuration_props:
            try:
                if a_prop=="grade" and row[a_prop] not in [None,""]:
                    configuration_values.append("GRADE")
                    configuration_values.append(row[a_prop])
                elif a_prop=="no." and row[a_prop] not in [None,""]:
                    configuration_values.append("No.")
                    configuration_values.append(row[a_prop])
                else:
                    configuration_values.append(row[a_prop])
            except:
                pass
        
        # ! additional: extract remaining words from the description which have a numerical value
        # TODO: fill in the code snippet below
        
        # combine all configuration values to one tab
        row['configuration'] = " ".join(configuration_values)
        # row['configuration'] = ['weight', 'cross-sectional area', 'length', 'current', 'voltage rating', 'power rating', 'apparent power rating', 'horsepower', 'angle', 'frequency', 'color temperature', 'capacitance', 'inductance', 'conductors', 'pins', 'phase', 'pole']

        size_props = ['weight','length','diameter']
        size_values = []
        for a_prop in size_props:
            try:
                size_values.append(row[a_prop])
                if (a_prop=='diameter'):
                    size_values.append("DIA")
            except:
                pass
            
        row['size'] = " X ".join(size_values)
        
        # ---------------------
        # ---------------------
        # ---------------------
        
        # paste the remaining text under info
        row["info"] = total_descr
        # check whether data was fully extracted or not
        if row["info"]==row["Item Category"]:
            row["extracted"] = "Y"
        else:
            row["extracted"] = ""
        # finally, write the row in CSV
        
        csv_writer.writerow(row)

    

print("Processing completed. Results saved to:", output_file_path)
# print("Trying to extract de")

# print(extract_dimensions("20MM X 4FT X 8FT 450 BHN"))
# print(extract_dimensions("6MM X 4 500 BHN"))
# print(extract_dimensions("38 X 4FT X 8FT 500 BHN"))
# print(extract_dimensions("ANCHOR PLATE 100MM X 310MM X 12MM x 5MM"))
# print(extract_dimensions("ANCHOR BOLT A307 X 500MM L + 100MM BEND  100MM THREAD WITH 2 NUTS AND 1 FLAT WASHER"))
# # print(extract_dimensions_chat("20MM X 4FT X 8FT 450 BHN"))
# print(extract_dimensions_chat("6MM X 4 500 BHN"))
# print(extract_dimensions_chat("38 X 4FT X 8FT 500 BHN"))
# print(extract_dimensions_chat("ANCHOR PLATE 100MM X 310MM X 12MM x 5MM"))
# print(extract_dimensions_chat("ANCHOR BOLT A307 DIA 20MM WITH 2 NUTS AND 1 FLAT WASHER"))
# print(extract_dimensions_chat("ANCHOR BOLT A307 20MM DIA X 500MM L + 100MM BEND  100MM THREAD WITH 2 NUTS AND 1 FLAT WASHER"))
# print(extract_properties("CLUTCH MASTER ASSY P/N 8-97024293-0"))
# print(extract_properties("LAMP P/N 1092629700 hello SN Ilove234 hi"))
# print(extract_properties("FLOODLIGHT ASSY P/N 1092629700"))
# print(extract_properties("BULB P/N 1092805900"))


