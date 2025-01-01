## Installation

```
pip install find-frame-tv
```

## Usage
### Command line
```bash
find-frame-tv
My Frame: 192.168.1.102 (manufacturer: Samsung Electronics, serial: xxxxxxxxxx)
```

### Python
```py
from find_frame_tv import find_tvs

tvs = find_tvs()
print(tv.ip, tv.friendly_name)
```
