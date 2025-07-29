# ReqLint

Quickly lint your python files to detect if you're using requests library without specifying a timeout value

## Quick Start
* `pip install py-reqlint`
```python
from reqlint import ReqLint

with open('your_file.py', 'r') as f:
    code = f.read()

for issue in ReqLint(code).lint():
    print(issue)
```
```
