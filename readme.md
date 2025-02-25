pyaleparser
=====

Yet another python library to read from and write to the ALE (Avid Log Exchange) format.

Development is ongoing an currently unstable.  But if you want to give it a shot, be my guest!

```python
from aleparser import Ale

ale = Ale.from_path("MU001.ale")

print(ale.heading)
print(ale.columns)
print(ale.events)

ale.to_path("MU001_processed.ale")
```