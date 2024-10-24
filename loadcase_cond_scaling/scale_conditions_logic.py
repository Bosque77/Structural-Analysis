import re

def scale_loadcases(loadcases, scale_factor, lcid_not_to_change):
    scaled_loadcases = []
    
    # This regex matches lines that start with 'comb' followed by an ID, a name in single quotes, and operations
    comb_pattern = re.compile(r"^comb\s+(\d+)\s+'([^']+)'\s+(.+)")
    
    for loadcase in loadcases:
        loadcase = loadcase.strip()  # Clean up whitespace

        # Match lines starting with 'comb'
        comb_match = comb_pattern.match(loadcase)
        if comb_match:
            lc_id, lc_name, operations = comb_match.groups()
            lc_id = int(lc_id)

            print(f"Processing loadcase {lc_id} with name {lc_name}")  # Debugging print

            # Match all terms (operator, value, lcid)
            terms = re.findall(r'([+-]?)\s*(\d*\.?\d+)\s*\((\d+)\)', operations)

            scaled_operations = []

            for idx, term in enumerate(terms):
                operator, value, operation_lcid = term
                operation_lcid = int(operation_lcid)
                value = float(value)
                if operation_lcid not in lcid_not_to_change:
                    value *= scale_factor
                # Limit the decimal places to 3
                # For the first term, omit the operator if it's missing
                if idx == 0 and not operator.strip():
                    scaled_operations.append(f"{value:.3f} ({operation_lcid})")
                else:
                    if not operator.strip():
                        operator = '+'
                    scaled_operations.append(f"{operator} {value:.3f} ({operation_lcid})")

            # Rebuild the operations string
            scaled_operations_str = ' '.join(scaled_operations)

            # Append the scaled loadcase
            scaled_loadcases.append(f"comb {lc_id} '{lc_name}' {scaled_operations_str}\n")
        else:
            # Keep non-matching lines unchanged
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
