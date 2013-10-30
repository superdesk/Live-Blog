import os

uiDir = '/home/mihaigociu/Work/workspace/Ally-Py/plugins-ui'

init_files = [os.path.join(root, file) for (root, dirs, files) in os.walk(uiDir)
        for file in files if file=='__init__.py']

for file in init_files:
    print(file)
    os.remove(file)
