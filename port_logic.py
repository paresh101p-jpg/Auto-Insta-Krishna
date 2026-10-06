import os
import re

with open('e:/Paresh/Auto Post/Auto-Insta-Pooja/main.py', 'r', encoding='utf-8') as f:
    pooja_code = f.read()

with open('e:/Paresh/Auto Post/Auto-Insta-Krishna/main.py', 'r', encoding='utf-8') as f:
    krishna_code = f.read()

# Extract Krishna's generate_caption
krishna_caption_match = re.search(r'def generate_caption\(media_path\):.*?(?=def get_ig_account_id\(\):)', krishna_code, re.DOTALL)
krishna_caption = krishna_caption_match.group(0)

# Replace in Pooja's code
new_krishna_code = re.sub(r'def generate_caption\(media_path\):.*?(?=def get_ig_account_id\(\):)', krishna_caption, pooja_code, flags=re.DOTALL)

# Replace Page ID
new_krishna_code = new_krishna_code.replace('FB_PAGE_ID = "1313997728621727"', 'FB_PAGE_ID = "1808917602588221"')

# Replace Repo URL
new_krishna_code = new_krishna_code.replace('Auto-Insta-Pooja', 'Auto-Insta-Krishna')

with open('e:/Paresh/Auto Post/Auto-Insta-Krishna/main.py', 'w', encoding='utf-8') as f:
    f.write(new_krishna_code)

print('Successfully ported Pooja logic to Krishna!')
