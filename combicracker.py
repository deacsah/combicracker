#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import re
import math
import sys
import time

# ANSI colors
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"

# ASCII banner (displayed in -h output)
banner = r"""
                    ___.  .___    
  ____  ____   _____\_ |_ |__|   
_/ ___\/  _ \ /    \| __ \|  |   
\  \__(  <_> )  Y Y \ \_\ \  |   
 \_____\____/|__|_|__\____/__|   
  ________________   ____ |  | __
_/ ___\_  __ \__  \_/ ___\|  |/ /
\  \___|  | \// __ \  \___|    <er
 \_____>__|  (______\_____|__|__\
              v1.1
"""

def load_list_from_file(path):
    """Read non-empty stripped lines from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def guess_algorithms_from_hash(h):
    """Guess hash algorithms based on length and hex pattern."""
    h = h.lower()
    if not re.fullmatch(r"[0-9a-f]+", h):
        return []
    length = len(h)
    guesses = {
        32: ["md5"],
        40: ["sha1"],
        56: ["sha224"],
        64: ["sha256", "sha3_256", "blake2s"],
        96: ["sha384", "sha3_384", "blake2b"],
        128: ["sha512", "sha3_512"],
    }
    return guesses.get(length, [])

def total_permutations(n_strings, n_separators, hash_algos_map):
    """Calculate total number of hashing attempts."""
    total = 0
    for r in range(1, n_strings + 1):
        perms = math.perm(n_strings, r)
        for thash, algos in hash_algos_map.items():
            total += perms * n_separators * len(algos)
    return total

def main():
    parser = argparse.ArgumentParser(
        description=banner + "\nBrute-force permutations of input strings to match given hashes "
                             "(algo guessed from hash length).",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input-strings", required=True,
                        help="Path to file with candidate input strings (one per line)")
    parser.add_argument("--hashes", required=True,
                        help="Path to file with target hashes (one per line, lowercase hex)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show each attempt with actual input + hash")
    args = parser.parse_args()

    # Load inputs & hashes
    input_strings = load_list_from_file(args.input_strings)
    target_hashes = set(load_list_from_file(args.hashes))

    # Guess algorithms
    hash_algo_map = {}
    for th in target_hashes:
        algos = guess_algorithms_from_hash(th)
        if not algos:
            print(f"{YELLOW}[!] Could not guess algorithm for hash:{RESET} {th}")
        else:
            hash_algo_map[th] = algos

    separators = ["", " ", "-", "_", ":", "|"]

    total_attempts = total_permutations(len(input_strings), len(separators), hash_algo_map)

    print(f"{BLUE}[+] Loaded {len(input_strings)} input strings{RESET}")
    print(f"{BLUE}[+] Loaded {len(target_hashes)} target hashes{RESET}")
    print(f"{BLUE}[+] Common separators to try:{RESET} {separators}")
    print(f"{BLUE}[+] Estimated total hashing attempts:{RESET} {total_attempts:,}")
    print(f"{BLUE}[+] Detected hash algorithms:{RESET}")
    for hval, algos in hash_algo_map.items():
        print(f"    {CYAN}{hval}{RESET} -> {', '.join(algos)}")

    attempt_counter = 0
    found_any = False
    found_hashes = set()
    start_time = time.time()
    stop_flag = False

    # Brute-force loop
    for r in range(1, len(input_strings) + 1):
        if stop_flag: break
        for combo in itertools.permutations(input_strings, r):
            if stop_flag: break
            for sep in separators:
                if stop_flag: break
                candidate = sep.join(combo)
                for thash, algos in hash_algo_map.items():
                    if thash in found_hashes:
                        continue
                    for algo in algos:
                        attempt_counter += 1
                        h = hashlib.new(algo)
                        h.update(candidate.encode())
                        digest = h.hexdigest()

                        if args.verbose:
                            print(f"{YELLOW}[ATTEMPT {attempt_counter}/{total_attempts}]{RESET} "
                                  f"Algorithm:{CYAN}{algo}{RESET} | Separator='{sep}' "
                                  f"| Input:{GREEN}'{candidate}'{RESET} | Hash={digest}")
                        else:
                            elapsed = time.time() - start_time
                            percent = (attempt_counter / total_attempts) * 100
                            remaining = 0
                            if attempt_counter > 0:
                                remaining = (elapsed / attempt_counter) * (total_attempts - attempt_counter)
                            elapsed_str = time.strftime("%H:%M", time.gmtime(elapsed))
                            remaining_str = time.strftime("%H:%M", time.gmtime(remaining))
                            sys.stdout.write(
                                f"\r{CYAN}[Progress]{RESET} Attempt {attempt_counter}/{total_attempts} "
                                f"({percent:.2f}%) | Elapsed: {elapsed_str} | Remaining: {remaining_str}"
                            )
                            sys.stdout.flush()

                        if digest == thash:
                            if not args.verbose:
                                print()
                            print(f"{GREEN}[MATCH]{RESET} Hash={CYAN}{thash}{RESET} | Algo={CYAN}{algo}{RESET} "
                                  f"| Separator='{sep}' | Input:{GREEN}'{candidate}'{RESET}")
                            found_any = True
                            found_hashes.add(thash)
                            if found_hashes == target_hashes:
                                stop_flag = True
                            break
                    if stop_flag:
                        break

    if not args.verbose and not stop_flag:
        print()

    if not found_any:
        print(f"{RED}[-] No matches found.{RESET}")
    elif stop_flag:
        print(f"{GREEN}[+] All hashes found.{RESET}")

if __name__ == "__main__":
    main()
