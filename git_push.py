# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'D:\Projects\ThesisFormatCheck')

# Add remote
r = subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/JustinZhu5268/PekingThesisFormatCheck.git'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Add remote:", r.returncode, r.stderr if r.stderr else "OK")

# Add all files except data/
r = subprocess.run(['git', 'add', '-A', '--', ':!data/*', ':!docs/TEST_ARCHITECTURE_REPORT.md'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Add files:", r.returncode, r.stderr[:200] if r.stderr else "OK")

# Commit
r = subprocess.run(['git', 'commit', '-m', 'v0.9: 修复大标题样式问题（章标题编号字体+段落格式统一）'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Commit:", r.returncode)
if r.stdout:
    print("  ", r.stdout[:300])
if r.stderr and 'warning' not in r.stderr.lower():
    print("  err:", r.stderr[:200])

# Push
r = subprocess.run(['git', 'push', '-u', 'origin', 'master'], 
                   capture_output=True, text=True, encoding='utf-8')
print("Push:", r.returncode)
if r.stderr:
    print("  ", r.stderr[:500])
if r.stdout:
    print("  ", r.stdout[:200])
