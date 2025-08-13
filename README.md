# combicracker
A simple cracky python tool for cracking hashes by testing all combinations of input strings against target hashes with different (hard-coded for now) seperators.

```
python combicracker.py -h                                                       
usage: combicracker.py [-h] --input-strings INPUT_STRINGS --hashes HASHES [--verbose]

Brute-force permutations of input strings to match given hashes (algo guessed from hash length).

options:
  -h, --help            show this help message and exit
  --input-strings INPUT_STRINGS
                        Path to file with possible input strings (one per line)
  --hashes HASHES       Path to file with target hashes (one per line, lowercase hex)
  --verbose             Display all attempts
                                            
```
