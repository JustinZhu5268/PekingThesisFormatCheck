# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'D:\Projects\ThesisFormatCheck')

# Add all files except data/
r = subprocess.run(['git', 'add', '-A', '--', ':!data/*', ':!docs/TEST_ARCHITECTURE_REPORT.md'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Add files:", r.returncode)

# Commit
r = subprocess.run(['git', 'commit', '-m', 'v0.91: 修复第七章自动编号字体（段落标记底层属性清洗）'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Commit:", r.returncode)
if r.stdout:
    print("  ", r.stdout[:300])

# Push
r = subprocess.run(['git', 'push', 'origin', 'master'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Push:", r.returncode)
if r.stdout:
    print("  ", r.stdout[:200])
