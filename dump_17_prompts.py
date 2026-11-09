# -*- coding: utf-8 -*-
import os
import sys
import master_thumbnail_prompt_engine as m

sys.stdout.reconfigure(encoding="utf-8")

output_lines = []
for i, cfg in enumerate(m.CATEGORY_CONFIGS, 1):
    prompt, _ = m.build_master_thumbnail_prompt(category_id=cfg["id"])
    block = f"================================================================================\n"
    block += f"CATEGORY {i:02d}: {cfg['id'].upper()} ({cfg['model_side'].upper()} SIDE MODEL)\n"
    block += f"INSTRUMENT: {cfg['instrument']}\n"
    block += f"3D TEXT: \"{cfg['hook_title']}\" | \"{cfg['hook_sub']}\"\n"
    block += f"--------------------------------------------------------------------------------\n"
    block += f"{prompt}\n"
    block += f"================================================================================\n\n"
    output_lines.append(block)

all_text = "".join(output_lines)
with open("all_17_category_prompts.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"Successfully generated all {len(m.CATEGORY_CONFIGS)} category prompts in all_17_category_prompts.txt")

