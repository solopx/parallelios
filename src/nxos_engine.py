from engine_core import (
    VendorAdapter,
    process_single_device as _process_single_device,
    transfer_and_verify_all as _transfer_and_verify_all,
)

FILESYSTEM = "bootflash:"


def _validate_os(show_ver, ip, log):
    if "NX-OS" not in show_ver:
        log(f"Device '{ip}' is not a NX-OS device. This module supports only NX-OS.", "error")
        raise Exception("IOS device detected — use IOS module")


def _no_enable(conn, use_enable, enable_secret, log):
    pass


def _handle_copy_prompts(conn, output):
    for _ in range(4):
        if "overwrite" in output.lower():
            output += conn.send_command_timing("yes\n", read_timeout=0)
        elif any(x in output for x in ["vrf", "Address", "filename", "confirm", "over"]):
            output += conn.send_command_timing("\n", read_timeout=0)
    return output


NXOS_ADAPTER = VendorAdapter(
    device_type="cisco_nxos",
    filesystem=FILESYSTEM,
    supports_enable=False,
    auth_error_suffix="check username/password.",
    validate_os=_validate_os,
    verify_cmd=lambda filename: f"show file {FILESYSTEM}{filename} md5sum",
    copy_cmd=lambda tftp_ip, filename: f"copy tftp://{tftp_ip}/{filename} {FILESYSTEM}{filename}",
    handle_copy_prompts=_handle_copy_prompts,
    handle_enable=_no_enable,
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
        NXOS_ADAPTER,
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
