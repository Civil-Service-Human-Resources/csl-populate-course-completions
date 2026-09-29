import json
import re

def parse_custom_string(s):
    """Recursively parses a single custom log string line into a dictionary."""
    s = s.strip()
    if not s:
        return None

    # Match the top-level class name and its inner body content
    match = re.match(r"^(\w+)\((.*)\)$", s, re.DOTALL)
    if not match:
        return s  # Return as a primitive string if it doesn't match ClassName(...)

    class_name = match.group(1)
    body = match.group(2)

    # Initialize the dictionary for this class level
    result = {"__type__": class_name}

    # Tokenise the key-value pairs while tracking matching parenthesis nesting
    pairs = []
    current_token = []
    paren_depth = 0

    for char in body:
        if char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1

        if char == "," and paren_depth == 0:
            pairs.append("".join(current_token).strip())
            current_token = []
        else:
            current_token.append(char)

    if current_token:
        pairs.append("".join(current_token).strip())

    # Map each tokenized pair into keys and values
    for pair in pairs:
        if "=" in pair:
            key, val = pair.split("=", 1)
            key = key.strip()
            val = val.strip()

            # Recursively parse nested classes like CourseCompletionMessage(...)
            if re.match(r"^\w+\(.*\)$", val, re.DOTALL):
                result[key] = parse_custom_string(val)
            else:
                # Convert numbers to integers, otherwise save as text string
                if val.isdigit():
                    result[key] = int(val)
                else:
                    result[key] = val

    return result


def process_log_file(input_filename, output_filename):
    """Reads lines from raw data file and writes a single JSON array to output file."""
    json_records = []

    # Open and process the raw file
    with open(input_filename, "r", encoding="utf-8") as file:
        for line in file:
            cleaned_line = line.strip()
            if cleaned_line:  # Skip empty lines
                parsed_data = parse_custom_string(cleaned_line)
                if parsed_data:
                    json_records.append(parsed_data)

    # Save the parsed structure as a valid JSON array
    with open(output_filename, "w", encoding="utf-8") as outfile:
        json.dump(json_records, outfile, indent=4)

    print(
        f"Successfully processed {len(json_records)} records. Saved to '{output_filename}'."
    )


# Run the script using your file names
if __name__ == "__main__":
    process_log_file("/input/rawData.txt", "/output/extracted_course_data.json")
