import re
import os

def process_sidebar_links(line):
    """Process a line from sidebar.md to convert spaces to hyphens and lowercase in parentheses"""
    if not line.startswith('1.'):
        return line
    
    # Find content within parentheses
    matches = re.findall(r'\((.*?)\)', line)
    if not matches:
        return line
    
    # Get the last parentheses content
    original_text = matches[-1]
    # Process the text: replace spaces with hyphens and convert to lowercase
    processed_text = original_text.replace(' ', '-').lower()
    
    # Replace the original text with processed text
    return line.replace(original_text, processed_text)

def extract_md_filenames(sidebar_content):
    """Extract markdown filenames from sidebar content"""
    filenames = []
    for line in sidebar_content:
        if line.startswith('1.'):
            # Find the last parentheses content
            matches = re.findall(r'\((.*?)\)', line)
            if matches:
                filename = matches[-1]
                # Remove '#docs/' prefix if exists
                if filename.startswith('#docs/'):
                    filename = filename[6:]  # Remove '#docs/'
                filenames.append(filename + '.md')
    return filenames

def create_md_files(filenames):
    """Create markdown files in docs directory if they don't exist"""
    # Create docs directory if it doesn't exist
    if not os.path.exists('docs'):
        os.makedirs('docs')
    
    # Create files
    for filename in filenames:
        filepath = os.path.join('docs', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('')
            print(f"Created file: {filepath}")
        else:
            print(f"File already exists: {filepath}")

def main():
    # Read the sidebar file
    with open('sidebar.md', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Process the links
    processed_lines = [process_sidebar_links(line) for line in lines]
    
    # Write processed content back to sidebar.md
    with open('sidebar.md', 'w', encoding='utf-8') as file:
        file.writelines(processed_lines)
    
    # Extract filenames and create MD files
    filenames = extract_md_filenames(processed_lines)
    create_md_files(filenames)
    
    print("Processing completed!")

if __name__ == "__main__":
    main() 