#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import re
import math
import sys
import time

def load_list_from_file(path):
    """Read non-empty stripped lines from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def guess_algorithms_from_hash(h):
    """Guess hash algorithms based on length and hex pattern."""
    h = h.lower()
    if not re.fullmatch(r"[0-9a-f]+", h):
        return []  # Not a valid hex digest
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
    """
    Calculate exact total number of hashing attempts:
    sum_over_r( permutations(n_strings, r) * n_separators * (sum of algos count per hash) )
    """
    total = 0
    for r in range(1, n_strings + 1):
        perms = math.perm(n_strings, r)
        # Total attempts for all hashes for this r length
        for thash, algos in hash_algos_map.items():
            total += perms * n_separators * len(algos)
    return total

def format_eta(seconds):
    """Format seconds as HH:MM:SS."""
    return time.strftime("%H:%M:%S", time.gmtime(seconds))

def main():
    parser = argparse.ArgumentParser(
        description="Brute-force permutations of input strings to match given hashes (algo guessed from hash length).")
    parser.add_argument("--input-strings", required=True,
                        help="Path to file with possible input strings (one per line)")
    parser.add_argument("--hashes", required=True,
                        help="Path to file with target hashes (one per line, lowercase hex)")
    parser.add_argument("--verbose", action="store_true",
                        help="Display all attempts with actual computed input")
    args = parser.parse_args()

    input_strings = load_list_from_file(args.input_strings)
    target_hashes = set(load_list_from_file(args.hashes))

    # Guess algorithms for each target hash
    hash_algo_map = {}
    for th in target_hashes:
        algos = guess_algorithms_from_hash(th)
        if not algos:
            print(f"[!] Could not guess algorithm for hash: {th}")
        else:
            hash_algo_map[th] = algos

    separators = ["", " ", "-", "_", ":", "|"]

    total_attempts = total_permutations(len(input_strings), len(separators), hash_algo_map)

    print(f"[+] Loaded {len(input_strings)} input strings")
    print(f"[+] Loaded {len(target_hashes)} target hashes")
    print(f"[+] Common separators to try: {separators}")
    print(f"[+] Estimated total hashing attempts: {total_attempts:,}")

    # Show detected algorithms always
    print("[+] Detected hash algorithms:")
    for hval, algos in hash_algo_map.items():
        print(f"    {hval} -> {', '.join(algos)}")

    attempt_counter = 0
    found_any = False
    start_time = time.time()

    # Brute-force search
    for r in range(1, len(input_strings) + 1):
        for combo in itertools.permutations(input_strings, r):
            for sep in separators:
                candidate = sep.join(combo)
                for thash, algos in hash_algo_map.items():
                    for algo in algos:
                        attempt_counter += 1
                        h = hashlib.new(algo)
                        h.update(candidate.encode())

                        if args.verbose:
                            print(f"[ATTEMPT {attempt_counter}/{total_attempts}] "
                                  f"Algorithm:{algo} | Separator='{sep}' | Input:'{candidate}' | Hash={h.hexdigest()}")
                        else:
                            elapsed = time.time() - start_time
                            percent = (attempt_counter / total_attempts) * 100
                            eta = (elapsed / attempt_counter) * (total_attempts - attempt_counter) if attempt_counter > 0 else 0
                            sys.stdout.write(f"\r[Progress] Attempt {attempt_counter}/{total_attempts} "
                                             f"({percent:.2f}%) | ETA: {format_eta(eta)}")
                            sys.stdout.flush()

                        if h.hexdigest() == thash:
                            if not args.verbose:
                                print()  # move to new line before match
                            print(f"[MATCH] Hash={thash} | Algo={algo} | Separator='{sep}' | Input:'{candidate}'")
                            found_any = True

    if not args.verbose:
        print()  # newline after progress display

    if not found_any:
        print("[-] No matches found.")

if __name__ == "__main__":
    main()
