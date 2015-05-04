android_resource_cleaner
========================

Use the script ot clean the unused values which reported by lint.
The command should be like:
```python
    python value_cleaner.py target_path [force]
```
Be care of the force option, when use it, values will be removed without any confirmation. The origin value files will be backup in path './backup_folder'. Be aware of that backup files will be replaced every time you run the script, and you may need run multiple times to assure that all the unused values has been cleaned.
