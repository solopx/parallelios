import time
from netmiko.exceptions import ReadTimeout

from engine_core import (
    VendorAdapter,
    process_single_device as _process_single_device,
    transfer_and_verify_all as _transfer_and_verify_all,
)


def _validate_os(show_ver, ip, log):
    if "NX-OS" in show_ver:
        log(f"Device '{ip}' is a NX-OS device. Select 'Cisco NX-OS' module in the UI.", "error")
        raise Exception("NX-OS device detected — switch to NX-OS module")


def _handle_enable(conn, use_enable, enable_secret, log):
    if use_enable:
        if enable_secret:
            try:
                conn.enable()
            except (ValueError, ReadTimeout):
                log("Error: Enable password is incorrect.", "error")
                raise Exception("Enable password incorrect")
        else:
            log("Error: Please provide the enable password", "error")
            raise Exception("Enable pass missing")
    else:
        if not conn.check_enable_mode():
            try:
                conn.write_channel("enable\n")
                time.sleep(1)
                output = conn.read_channel()
                if "Password" in output:
                    log("Error: The switch requires an enable password, but the option is unchecked.", "error")
                    raise Exception("Insufficient privileges (enable password required)")
            except Exception:
                log("Error: Could not obtain write privileges (#).", "error")
                raise Exception("Privileged access denied")


def _handle_copy_prompts(conn, output):
    for _ in range(3):
        if any(x in output for x in ["Address", "filename", "confirm", "over"]):
            output += conn.send_command_timing("\n", read_timeout=0)
    return output


IOS_ADAPTER = VendorAdapter(
    device_type="cisco_ios",
    filesystem="flash:",
    supports_enable=True,
    auth_error_suffix="check username/password/enable secret.",
    validate_os=_validate_os,
    verify_cmd=lambda filename: f"verify /md5 flash:/{filename}",
    copy_cmd=lambda tftp_ip, filename: f"copy tftp://{tftp_ip}/{filename} flash:/{filename}",
    handle_copy_prompts=_handle_copy_prompts,
    handle_enable=_handle_enable,
)


def process_single_device(
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
    _process_single_device(
        IOS_ADAPTER,
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


def transfer_and_verify_all(
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
    _transfer_and_verify_all(
        process_single_device,
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
    )
