import os

# รายการไฟล์สำคัญที่ต้องรวมเข้าเป็น Knowledge
files_to_merge = [
    "NaMo_Forbidden_Core_v2.0.json",
    "README.md",
    "system.yaml",
    "docs/ARCHITECTURE.md",
    "docs/NamoNexus_Integration_Handbook.md",
]

output_filename = "NaMo_Integrated_Knowledge_Base.md"

with open(output_filename, "w", encoding="utf-8") as outfile:
    for filename in files_to_merge:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as infile:
                outfile.write("\n# Source: " + filename + "\n")
                outfile.write(infile.read())
                outfile.write("\n---\n")

print(f"รวมไฟล์เสร็จสิ้น: {output_filename}")
