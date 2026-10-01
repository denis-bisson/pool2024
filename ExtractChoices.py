import os
import sys

def process_choice_files(folder_path: str, choices: list[str]) -> None:
    """
    Scans a folder for .txt files, checks each line against a choices list,
    and prints the filename along with the 0-based match indices (or -1).
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory '{folder_path}' does not exist.")
        return

    # 1. Get list of files ending with .txt
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]

    # 2. Iterate through each file
    for filename in sorted(txt_files):
        file_path = os.path.join(folder_path, filename)
        
        # 3. Initialize tracking strings
        choices_made = ""
        choices_done = ""
        
        indices = []
        
        # 4. Read the lines of text from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            for line in lines:
                clean_line = line.strip()
                
                # 5. Find position in choices (-1 if not found)
                if clean_line in choices:
                    pos = choices.index(clean_line)
                else:
                    pos = -1
                
                indices.append(str(pos))

        # 6 & 7. Format indices with commas
        choices_made = ",".join(indices)
        choices_done = choices_made

        # 8. Output filename without extension + choices_done value
        filename_without_ext = os.path.splitext(filename)[0]
        print(f"{filename_without_ext}: {choices_done}")

# Example usage:
# choices_list = ["Option A", "Option B", "Option C"]
# process_choice_files("./data_folder", choices_list)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_excel.py <folder_path>")
        sys.exit(1)

