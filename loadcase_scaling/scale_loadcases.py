import re

def scale_loadcases(loadcases, scale_factor, lcid_not_to_change):
    # Define the regex pattern to match the loadcases
    pattern = re.compile(r'(\d+)\s+([^\d]+)\s+(.*)')

    scaled_loadcases = []

    for loadcase in loadcases:
        match = pattern.match(loadcase)
        if match:
            lcid, lcname, operations = match.groups()
            lcid = int(lcid)
            
            # Split the operations part into individual components
            components = re.split(r'(\s[+-]\s)', operations)
            scaled_operations = []

            for component in components:
                float_match = re.match(r'(\d*\.?\d+)\s+\((\d+)\)', component.strip())
                if float_match:
                    value, lc_id = float_match.groups()
                    lc_id = int(lc_id)
                    value = float(value)
                    if lc_id not in lcid_not_to_change:
                        value *= scale_factor
                    scaled_operations.append(f"{value} ({lc_id})")
                else:
                    scaled_operations.append(component)
            
            # Correcting the signs in the operations string
            scaled_operations_str = ''.join(scaled_operations)
            scaled_operations_str = re.sub(r'\+\s+\-', '- ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\-', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\+\s+\+', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\+', '- ', scaled_operations_str)

            scaled_loadcases.append(f"{lcid} {lcname} {scaled_operations_str}")
        else:
            scaled_loadcases.append(loadcase)

    return scaled_loadcases

# Example usage:
loadcases = [
    "1 LoadCase_A 1.5 (101) + 2.0 (102) - 3.0 (103)",
    "2 LoadCase_B 0.5 (104) + 1.0 (105)",
    "3 LoadCase_C 2.5 (106) - 1.5 (107) + 4.0 (108)",
    "4 LoadCase_D 1.0 (109)",
    "5 LoadCase_E 3.0 (110) + 2.5 (111) - 1.0 (112)"
]

lcid_not_to_change = [101]
scale_factor = 0.5

scaled_loadcases = scale_loadcases(loadcases, scale_factor, lcid_not_to_change)
for lc in scaled_loadcases:
    print(lc)
