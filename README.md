# combicracker.py
A simple cracky python tool for cracking hashes by testing all combinations of input strings against target hashes with different (hard-coded for now) seperators.

Yes, there are plenty of similar and faster tools out there, but this works great for targeted, low volume hash cracking. And tbh, building this was quicker than relearning the intricacies of hashcat or john when performing cracking using combined inputs.

Have a hash where the input is likely a combination of a few pieces of data? This script will enumerates all possible ordered combinations of the input strings joined by the delimiters (`"", " ", "-", "_", ":", "|"`), including concatted input strings. For example, if your input strings are `A, B, C`, the script tries:
- 1-length permutations: A, B, C
- 2-length permutations: AB, AC, BA, BC, CA, CB
- 3-length permutations: ABC, ACB, BAC, BCA, CAB, CBA
- etc (including other delimiters)

# Usage

```
usage: combicracker.py [-h] --input-strings INPUT_STRINGS --hashes HASHES [--verbose]

                    ___.  .___    
  ____  ____   _____\_ |_ |__|   
_/ ___\/  _ \ /    \| __ \|  |   
\  \__(  <_> )  Y Y \ \_\ \  |   
 \_____\____/|__|_|__\____/__|   
_/ ___\_  __ \__  \_/ ___\|  |/ /
\  \___|  | \// __ \  \___|    <er
 \_____>__|  (______\_____|__|__\
              v1.1

Brute-force permutations of input strings to match given hashes (algo guessed from hash length).

options:
  -h, --help            show this help message and exit
  --input-strings INPUT_STRINGS
                        Path to file with candidate input strings (one per line)
  --hashes HASHES       Path to file with target hashes (one per line, lowercase hex)
  --verbose             Show each attempt with actual input + hash                                           
```
