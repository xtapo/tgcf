import ctypes
import os
import signal
import subprocess
import sys
import time

import streamlit as st

from tgcf.config import CONFIG, read_config, write_config
from tgcf.web_ui.password import check_password
from tgcf.web_ui.utils import hide_st, switch_theme

CONFIG = read_config()


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            process = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, 0, pid
            )
            if process != 0:
                ctypes.windll.kernel32.CloseHandle(process)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def kill_pid(pid: int):
    if pid <= 0:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception:
        pass


def termination():
    st.code("process terminated!")
    if os.path.exists("logs.txt"):
        try:
            if os.path.exists("old_logs.txt"):
                os.remove("old_logs.txt")
            os.rename("logs.txt", "old_logs.txt")
            with open("old_logs.txt", "r", encoding="utf-8", errors="ignore") as f:
                st.download_button(
                    "Download last logs", data=f.read(), file_name="tgcf_logs.txt"
                )
        except Exception:
            pass

    CONFIG = read_config()
    CONFIG.pid = 0
    write_config(CONFIG)
    st.button("Refresh page")


st.set_page_config(
    page_title="Run",
    page_icon="🏃",
)
hide_st(st)
switch_theme(st, CONFIG)
if check_password(st):
    with st.expander("Configure Run"):
        CONFIG.show_forwarded_from = st.checkbox(
            "Show 'Forwarded from'", value=CONFIG.show_forwarded_from
        )
        mode = st.radio("Choose mode", ["live", "past"], index=CONFIG.mode)
        if mode == "past":
            CONFIG.mode = 1
            st.warning(
                "Only User Account can be used in Past mode. Telegram does not allow bot account to go through history of a chat!"
            )
            CONFIG.past.delay = st.slider(
                "Delay in seconds", 0, 100, value=CONFIG.past.delay
            )
        else:
            CONFIG.mode = 0
            CONFIG.live.delete_sync = st.checkbox(
                "Sync when a message is deleted", value=CONFIG.live.delete_sync
            )

        if st.button("Save"):
            write_config(CONFIG)

    check = False

    if CONFIG.pid == 0:
        check = st.button("Run", type="primary")

    if CONFIG.pid != 0:
        st.warning(
            "You must click stop and then re-run tgcf to apply changes in config."
        )
        # check if process is running using pid
        if not is_pid_running(CONFIG.pid):
            st.code("The process has stopped.")
            CONFIG.pid = 0
            write_config(CONFIG)
            time.sleep(1)
            st.rerun()

        stop = st.button("Stop", type="primary")
        if stop:
            kill_pid(CONFIG.pid)
            termination()

    if check:
        with open("logs.txt", "w", encoding="utf-8") as logs:
            tgcf_bin = sys.executable.replace("python.exe", "tgcf.exe")
            cmd = (
                [tgcf_bin, "--loud", mode]
                if os.path.exists(tgcf_bin)
                else ["tgcf", "--loud", mode]
            )
            process = subprocess.Popen(
                cmd,
                stdout=logs,
                stderr=subprocess.STDOUT,
            )
        CONFIG.pid = process.pid
        write_config(CONFIG)
        time.sleep(2)
        st.rerun()

    try:
        lines = st.slider(
            "Lines of logs to show", min_value=100, max_value=1000, step=100
        )
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r", encoding="utf-8", errors="ignore") as file:
                content = file.readlines()
                st.code("".join(content[-lines:]))
        else:
            st.write("No present logs found")
    except Exception as err:
        st.write("No present logs found")
    st.button("Load more logs")

