import re

def scale_loadcases(loadcases, scale_factor, lcid_not_to_change):
    scaled_loadcases = []
    
    # This regex will match lines that start with 'comb' followed by a loadcase ID, 
    # a name enclosed in single quotes, and then the operations with numbers and parentheses.
    comb_pattern = re.compile(r"^comb\s+(\d+)\s+'([^']+)'\s+(.+)")
    
    for loadcase in loadcases:
        loadcase = loadcase.strip()  # Clean up whitespace

        # Look for the loadcases that start with 'comb'
        comb_match = comb_pattern.match(loadcase)
        if comb_match:
            lc_id, lc_name, operations = comb_match.groups()
            lc_id = int(lc_id)

            print(f"Processing loadcase {lc_id} with name {lc_name}")  # Debugging print

            # Split the operations part into individual components
            components = re.split(r'(\s[+-]\s)', operations)
            scaled_operations = []

            for component in components:
                # Look for the pattern of a number followed by an LCID in parentheses
                float_match = re.match(r'(\d*\.?\d+)\s+\((\d+)\)', component.strip())
                if float_match:
                    value, operation_lcid = float_match.groups()
                    operation_lcid = int(operation_lcid)
                    value = float(value)
                    if operation_lcid not in lcid_not_to_change:
                        value *= scale_factor
                    # Limit the decimal places to 3
                    scaled_operations.append(f"{value:.3f} ({operation_lcid})")
                else:
                    # Add non-matching components (such as the signs) back to the list unchanged
                    scaled_operations.append(component)
            
            # Rebuild the operations string and correct double signs
            scaled_operations_str = ''.join(scaled_operations)
            
            # Correct double signs like "+ -" or "- -"
            scaled_operations_str = re.sub(r'\+\s+\-', '- ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\-', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\+\s+\+', '+ ', scaled_operations_str)
            scaled_operations_str = re.sub(r'\-\s+\+', '- ', scaled_operations_str)

            # Append the scaled loadcase
            scaled_loadcases.append(f"comb {lc_id} '{lc_name}' {scaled_operations_str}\n")
        else:
            # If the line doesn't start with 'comb', keep it unchanged
            scaled_loadcases.append(loadcase + "\n")

    return scaled_loadcases

if __name__ == '__main__':
    infile = './test_cond_file.cond'
    outfile = './scaled_cond_file.cond'

    with open(infile, 'r') as f:
        loadcases = f.readlines()

    lcid_not_to_change = [103]
    scale_factor = 0.2

    # Process the loadcases and get the scaled versions
    scaled_loadcases = scale_loadcases(loadcases, scale_factor, lcid_not_to_change)
    
    # Write the scaled loadcases to a new file
    with open(outfile, 'w') as f:
        for lc in scaled_loadcases:
            f.write(lc)

    print(f"Scaled loadcases have been written to {outfile}")
