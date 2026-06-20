import os
import re
import time
import queue
import threading
import ipaddress
from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from netmiko import logging, ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from concurrent.futures import ThreadPoolExecutor

# ==============================================================================
# GLOBALS AND FLAGS
# ==============================================================================

stop_event = threading.Event()
active_connections = {}
connections_lock = threading.Lock()

# ==============================================================================
# Logging Configuration
# ==============================================================================

netmiko_logger = logging.getLogger("netmiko")
netmiko_logger.setLevel(logging.DEBUG)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(PROJECT_ROOT, "copy-tftp-flash.log")
file_handler = logging.FileHandler(LOG_PATH, encoding="UTF-8")
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
netmiko_logger.addHandler(file_handler)

# ==============================================================================
# Validation of entered IP addresses
# ==============================================================================

def validate_ips(ip_string, multiple=False):
    if multiple:
        raw_list = [ip.strip() for ip in ip_string.split(",") if ip.strip()]
        valid_ips = []
        invalid_ips = []

        for ip in raw_list:
            try:
                ipaddress.IPv4Address(ip)
                valid_ips.append(ip)
            except ValueError:
                invalid_ips.append(ip)
        return valid_ips, invalid_ips
    else:
        try:
            ipaddress.IPv4Address(ip_string.strip())
            return True
        except ValueError:
            return False

# ==============================================================================
# MD5 hash extraction and exact comparison
# ==============================================================================

def extract_md5(text):
    match = re.search(r"\b[a-fA-F0-9]{32}\b", text)
    return match.group(0).lower() if match else None


def md5_matches(text, expected_md5):
    found_hash = extract_md5(text)
    return found_hash is not None and found_hash == expected_md5.strip().lower()

# ==============================================================================
# Available space verification
# ==============================================================================

def check_space(conn, filesystem, file_size_bytes, log_func):
    if file_size_bytes is None:
        log_func("File size not provided. Skipping free disk space verification.", "warning")
        return True

    log_func(f"Verifying available flash space at: {filesystem}...", "warning")

    output = conn.send_command_timing(f"dir {filesystem}", read_timeout=15)

    match = re.search(r"(\d+)\s+bytes\s+free", output)

    if not match:
        log_func(f"Could not determine free space on {filesystem}. Proceeding with copy.", "warning")
        return True

    free_bytes = int(match.group(1))
    free_mb = free_bytes / (1024 * 1024)
    file_mb = file_size_bytes / (1024 * 1024)

    if free_bytes > file_size_bytes:
        log_func(f"Free space: {free_mb:.1f} MB | File: {file_mb:.1f} MB — OK", "success")
        return True
    else:
        log_func(
            f"INSUFFICIENT SPACE! Available: {free_mb:.1f} MB | Required: {file_mb:.1f} MB",
            "error",
        )
        return False

# ==============================================================================
# Vendor adapter: the small set of points where IOS and NX-OS actually differ
# ==============================================================================

@dataclass
class VendorAdapter:
    device_type: str
    filesystem: str
    supports_enable: bool
    auth_error_suffix: str
    validate_os: Callable[[str, str, Callable], None]
    verify_cmd: Callable[[str], str]
    copy_cmd: Callable[[str, str], str]
    handle_copy_prompts: Callable[[object, str], str]
    handle_enable: Callable[[object, bool, str, Callable], None]

# ==============================================================================
# Shared per-device transfer + MD5 verification logic
# ==============================================================================

def process_single_device(
    adapter,
    ip,
    tftp_ip,
    ios_filename,
    md5_hash,
    username,
    password,
    enable_secret,
    use_enable,
    file_size,
    log_callback,
    results_queue,
    transfer_timeout,
):
    if stop_event.is_set():
        results_queue.put((ip, "failed", "Interrupted by user"))
        return

    outcome = "failed"
    failure_reason = "Unknown error"
    display_id = ip
    fatal_errors = ["%Error", "Timed out", "Invalid", "refused", "not found"]

    def log(msg, tag="info"):
        formatted_log = f"[{display_id}] {msg}"
        if tag == "error":
            netmiko_logger.error(formatted_log)
        elif tag == "warning":
            netmiko_logger.warning(formatted_log)
        else:
            netmiko_logger.info(formatted_log)
        log_callback(display_id, msg, tag)

    def extract_error_line(text):
        for line in text.splitlines():
            if any(e in line for e in fatal_errors):
                return line.strip()
        return "Unidentified TFTP Error"

    try:
        device = {
            "device_type": adapter.device_type,
            "host": ip,
            "username": username,
            "password": password,
            "global_delay_factor": 1,
        }
        if adapter.supports_enable:
            device["secret"] = enable_secret if enable_secret else None

        conn = ConnectHandler(**device)
        with connections_lock:
            active_connections[ip] = conn

        show_ver = conn.send_command_timing("show version", read_timeout=10)
        adapter.validate_os(show_ver, ip, log)

        adapter.handle_enable(conn, use_enable, enable_secret, log)

        full_prompt = conn.find_prompt()
        display_id = full_prompt.replace("#", "").replace(">", "").strip()

        log(f"Connecting to... '{ip}'", "device")
        log(f"Checking for file '{ios_filename}' on '{display_id}'...", "warning")
        md5_start_timestamp = datetime.now().strftime("%H:%M:%S")
        log(f"{md5_start_timestamp} - Calculating MD5 hash on device — this can take a few minutes for large files...", "warning")

        res = conn.send_command_timing(adapter.verify_cmd(ios_filename), read_timeout=0)

        md5_check_timestamp = datetime.now().strftime("%H:%M:%S")
        md5_matches_locally = False
        if md5_matches(res, md5_hash):
            md5_matches_locally = True
            outcome = "skipped"
            log(f"{md5_check_timestamp} - Local MD5 hash matches. Skipping file copy for '{display_id}'.", "success")
        else:
            log(f"{md5_check_timestamp} - File not found or MD5 hash mismatch. Proceeding with copy for '{display_id}'", "device")

        if not md5_matches_locally and not stop_event.is_set():

            if not check_space(conn, adapter.filesystem, file_size, log):
                raise Exception("Insufficient space on device")

            start_timestamp = datetime.now().strftime("%H:%M:%S")
            log(f"{start_timestamp} - Starting TFTP transfer for '{display_id}'...", "warning")

            output = conn.send_command_timing(adapter.copy_cmd(tftp_ip, ios_filename), read_timeout=0)
            log(f"Transfer operation in progress (Waiting for {transfer_timeout // 60} min)...", "warning")

            output = adapter.handle_copy_prompts(conn, output)

            if any(e in output for e in fatal_errors):
                error_line = extract_error_line(output)
                raise Exception(error_line)

            start_time = time.time()
            copy_finished = False
            accumulated = output
            silence_count = 0

            while time.time() - start_time < transfer_timeout:
                if stop_event.is_set():
                    raise Exception("Cancelled by user")

                chunk = conn.read_channel()

                if chunk:
                    accumulated += chunk
                    silence_count = 0

                    if any(e in accumulated for e in fatal_errors):
                        error_line = extract_error_line(accumulated)
                        raise Exception(error_line)

                    if "#" in chunk or ">" in chunk:
                        copy_finished = True
                        break
                else:
                    silence_count += 1

                    if silence_count >= 10:
                        try:
                            prompt = conn.find_prompt()
                            if "#" in prompt or ">" in prompt:
                                copy_finished = True
                                break
                        except Exception:
                            pass
                        silence_count = 0

                time.sleep(1)

            if not copy_finished:
                timeout_timestamp = datetime.now().strftime("%H:%M:%S")
                log(f"{timeout_timestamp} - Timeout reached during copy", "error")
                raise Exception(f"Copy timed out after {transfer_timeout // 60} min")

            log("Checking integrity of copied file...", "warning")
            md5_start_timestamp = datetime.now().strftime("%H:%M:%S")
            log(f"{md5_start_timestamp} - Calculating MD5 hash on device — this can take a few minutes for large files...", "warning")
            res_final = conn.send_command_timing(
                adapter.verify_cmd(ios_filename), read_timeout=0, last_read=15.0
            )

            if md5_matches(res_final, md5_hash):
                outcome = "copied"
                log("Copy complete and MD5 verified successfully!", "success")
            else:
                outcome = "failed"
                failure_reason = "MD5 hash mismatch after copy"
                log("ERROR! Copy failed! MD5 hash does not match!", "error")

            end_timestamp = datetime.now().strftime("%H:%M:%S")
            log(f"Transfer completed at {end_timestamp}", "success")

        conn.disconnect()

    except NetmikoTimeoutException as e:
        timestamp = datetime.now().strftime("%H:%M:%S")
        first_line = str(e).splitlines()[0]
        outcome = "failed"
        failure_reason = first_line
        log(f"{timestamp} - ERROR {first_line}", "error")

    except NetmikoAuthenticationException:
        timestamp = datetime.now().strftime("%H:%M:%S")
        outcome = "failed"
        failure_reason = f"Authentication failed for {ip} — {adapter.auth_error_suffix}"
        log(f"{timestamp} - ERROR Authentication failed for {ip} — {adapter.auth_error_suffix}", "error")

    except Exception as e:
        with connections_lock:
            conn_to_close = active_connections.get(ip)
        if conn_to_close:
            try:
                conn_to_close.disconnect()
            except Exception:
                pass

        timestamp = datetime.now().strftime("%H:%M:%S")
        outcome = "failed"
        if stop_event.is_set():
            msg = f"{timestamp} - INTERRUPTED"
            failure_reason = "Interrupted by user"
        else:
            msg = f"{timestamp} - ERROR {str(e)}"
            failure_reason = str(e)

        log(msg, "error")

    finally:
        with connections_lock:
            active_connections.pop(ip, None)
            results_queue.put((display_id, outcome, failure_reason))

# ==============================================================================
# Parallel transfer orchestration (shared between engines)
# ==============================================================================

def transfer_and_verify_all(
    process_func,
    tftp_ip,
    ios_filename,
    md5_hash,
    devices,
    username,
    password,
    enable_secret,
    use_enable,
    file_size,
    log_callback,
    on_complete,
    max_workers,
    transfer_timeout,
):
    stop_event.clear()
    total = len(devices)
    success_count = 0
    results_queue = queue.Queue()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_func,
                ip,
                tftp_ip,
                ios_filename,
                md5_hash,
                username,
                password,
                enable_secret,
                use_enable,
                file_size,
                log_callback,
                results_queue,
                transfer_timeout,
            )
            for ip in devices
        ]
        for future in futures:
            future.result()

    details = []
    while not results_queue.empty():
        display_id, outcome, failure_reason = results_queue.get()
        details.append((display_id, outcome, failure_reason))
        if outcome != "failed":
            success_count += 1

    on_complete(success_count, total, details)
