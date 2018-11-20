from pathlib import Path

def write_file(dirname, filename, data):
   p = Path(dirname)
   if not p.exists():
      p.mkdir()
   p = p / filename
   with open(str(p), 'w') as f:
      f.write(data)
