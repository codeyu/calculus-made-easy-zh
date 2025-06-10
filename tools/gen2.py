import re

def process_sidebar_lines():
    """Process sidebar.md and return modified lines"""
    modified_lines = []
    
    with open('sidebar.md', 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('1.'):
                # Replace '1.' with '  *'
                new_line = '  *' + line[2:]
                
                # Remove '#'
                new_line = new_line.replace('#', '')
                
                # Find the last parentheses content and add .md
                matches = re.findall(r'\((.*?)\)', new_line)
                if matches:
                    last_match = matches[-1]
                    new_line = new_line.replace(last_match, last_match + '.md')
                
                modified_lines.append(new_line)
    
    return modified_lines

def update_summary_file(modified_lines):
    """Update SUMMARY.md with modified lines starting from line 6"""
    # Read existing SUMMARY.md content
    try:
        with open('SUMMARY.md', 'r', encoding='utf-8') as file:
            summary_lines = file.readlines()
    except FileNotFoundError:
        summary_lines = []
    
    # If SUMMARY.md has less than 6 lines, pad it with empty lines
    while len(summary_lines) < 6:
        summary_lines.append('\n')
    
    # Insert modified lines at position 6
    summary_lines[6:6] = modified_lines
    
    # Write back to SUMMARY.md
    with open('SUMMARY.md', 'w', encoding='utf-8') as file:
        file.writelines(summary_lines)

def main():
    # Process sidebar.md and get modified lines
    modified_lines = process_sidebar_lines()
    
    # Update SUMMARY.md with the modified lines
    update_summary_file(modified_lines)
    
    print("SUMMARY.md has been updated successfully!")

if __name__ == "__main__":
    main()
