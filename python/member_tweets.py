#!/usr/bin/env python3
"""
Run all Python files contained in python/character_py sequentially.

Usage:
  python member_tweets.py

Logs are written to python/member_tweets.log next to this script.
"""
import os
import sys
import subprocess
import time
from datetime import datetime


def main():
    base_dir = os.path.dirname(__file__)
    target_dir = os.path.join(base_dir, 'character_py')

    if not os.path.isdir(target_dir):
        print(f"Target directory does not exist: {target_dir}")
        sys.exit(1)

    py_files = [f for f in os.listdir(target_dir) if f.endswith('.py') and not f.startswith('__')]
    py_files.sort()
    # delay between successive script runs (seconds)
    DELAY_SECONDS = 120  # 5 seconds

    log_path = os.path.join(base_dir, 'member_tweets.log')
    with open(log_path, 'a', encoding='utf-8') as logf:
        header = f"\n=== Run batch at {datetime.now().isoformat()} ===\n"
        logf.write(header)
        print(header, end='')

        overall_ok = True
        for fname in py_files:
            file_path = os.path.join(target_dir, fname)
            start_msg = f"--- Running: {fname} ---\n"
            print(start_msg, end='')
            logf.write(start_msg)

            proc = subprocess.run([sys.executable, file_path], capture_output=True, text=True)

            out = proc.stdout or ''
            err = proc.stderr or ''

            if out:
                logf.write('STDOUT:\n')
                logf.write(out)
                print(out, end='')
            if err:
                logf.write('STDERR:\n')
                logf.write(err)
                print(err, end='', file=sys.stderr)

            if proc.returncode != 0:
                # Retry failed script up to RETRY_MAX times with RETRY_DELAY seconds between attempts
                RETRY_MAX = 5
                RETRY_DELAY = 300  # 5 minutes
                attempt = 0
                failed = True
                # log initial failure
                fail_msg = f"*** {fname} exited with code {proc.returncode} (initial attempt) ***\n"
                logf.write(fail_msg)
                print(fail_msg, file=sys.stderr)

                while attempt < RETRY_MAX:
                    attempt += 1
                    retry_msg = f"Retrying {fname} in {RETRY_DELAY} seconds (attempt {attempt}/{RETRY_MAX})...\n"
                    logf.write(retry_msg)
                    print(retry_msg, end='')
                    time.sleep(RETRY_DELAY)

                    rproc = subprocess.run([sys.executable, file_path], capture_output=True, text=True)
                    rout = rproc.stdout or ''
                    rerr = rproc.stderr or ''
                    if rout:
                        logf.write('RETRY STDOUT:\n')
                        logf.write(rout)
                        print(rout, end='')
                    if rerr:
                        logf.write('RETRY STDERR:\n')
                        logf.write(rerr)
                        print(rerr, end='', file=sys.stderr)

                    if rproc.returncode == 0:
                        ok_retry = f"--- {fname} succeeded on retry attempt {attempt} ---\n"
                        logf.write(ok_retry)
                        print(ok_retry, end='')
                        failed = False
                        break
                    else:
                        retry_fail = f"*** {fname} retry attempt {attempt} exited with code {rproc.returncode} ***\n"
                        logf.write(retry_fail)
                        print(retry_fail, file=sys.stderr)

                if failed:
                    overall_ok = False
                    final_fail = f"*** {fname} failed after {RETRY_MAX} retries — aborting batch ***\n"
                    logf.write(final_fail)
                    print(final_fail, file=sys.stderr)
                    break
                # else: succeeded on retry, continue to next script
            else:
                ok_msg = f"--- {fname} finished OK ---\n"
                logf.write(ok_msg)
                print(ok_msg, end='')

            # wait between runs (only if continuing)
            if fname != py_files[-1]:
                wait_msg = f"Waiting {DELAY_SECONDS} seconds before next script...\n"
                logf.write(wait_msg)
                print(wait_msg, end='')
                time.sleep(DELAY_SECONDS)

        # If everything finished OK, run merger.py to aggregate JSONs
        if overall_ok:
            merger_path = os.path.join(base_dir, 'merger.py')
            if os.path.isfile(merger_path):
                run_msg = f"All scripts completed successfully — running merger: {os.path.basename(merger_path)}\n"
                print(run_msg, end='')
                logf.write(run_msg)
                mproc = subprocess.run([sys.executable, merger_path], capture_output=True, text=True)
                if mproc.stdout:
                    logf.write('MERGER STDOUT:\n')
                    logf.write(mproc.stdout)
                    print(mproc.stdout, end='')
                if mproc.stderr:
                    logf.write('MERGER STDERR:\n')
                    logf.write(mproc.stderr)
                    print(mproc.stderr, end='', file=sys.stderr)
                if mproc.returncode != 0:
                    overall_ok = False
                    err_msg = f"*** merger.py exited with code {mproc.returncode} ***\n"
                    logf.write(err_msg)
                    print(err_msg, file=sys.stderr)
                else:
                    ok_merger = f"--- merger.py finished OK ---\n"
                    logf.write(ok_merger)
                    print(ok_merger, end='')
                    # After successful merge, run embed.py to produce site data.json
                    embed_path = os.path.join(base_dir, 'embed.py')
                    if os.path.isfile(embed_path):
                        run_msg = f"Running embed: {os.path.basename(embed_path)}\n"
                        print(run_msg, end='')
                        logf.write(run_msg)
                        eproc = subprocess.run([sys.executable, embed_path], capture_output=True, text=True)
                        if eproc.stdout:
                            logf.write('EMBED STDOUT:\n')
                            logf.write(eproc.stdout)
                            print(eproc.stdout, end='')
                        if eproc.stderr:
                            logf.write('EMBED STDERR:\n')
                            logf.write(eproc.stderr)
                            print(eproc.stderr, end='', file=sys.stderr)
                        if eproc.returncode != 0:
                            overall_ok = False
                            err_msg = f"*** embed.py exited with code {eproc.returncode} ***\n"
                            logf.write(err_msg)
                            print(err_msg, file=sys.stderr)
                        else:
                            ok_embed = f"--- embed.py finished OK ---\n"
                            logf.write(ok_embed)
                            print(ok_embed, end='')
                    else:
                        miss_embed = f"embed.py not found at {embed_path}, skipping embed run.\n"
                        logf.write(miss_embed)
                        print(miss_embed, end='')
            else:
                miss_msg = f"merger.py not found at {merger_path}, skipping merge.\n"
                logf.write(miss_msg)
                print(miss_msg, end='')

        footer = f"=== Batch finished at {datetime.now().isoformat()} - overall_ok={overall_ok} ===\n"
        logf.write(footer)
        print(footer, end='')

    sys.exit(0 if overall_ok else 2)


if __name__ == '__main__':
    main()
