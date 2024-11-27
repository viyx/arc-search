### Basic usage:
```bash
# single file
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
```

```bash
# all files in two directories
python main.py -d ./data/arc/evaluation/ ./data/arc/training/ -l info
```

```bash
# run 8 processes
python main.py -p 8 -d ./data/arc/evaluation/
```