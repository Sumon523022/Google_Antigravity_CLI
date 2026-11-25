import os
import shutil
import subprocess
import sys
import time


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"


def banner():
    os.system("clear" if os.name != "nt" else "cls")
    art = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗
║   {Colors.MAGENTA}✦ {Colors.WHITE}GOOGLE ANTIGRAVITY CLI {Colors.CYAN}• {Colors.YELLOW}TERMUX AUTO INSTALLER {Colors.MAGENTA}✦{Colors.CYAN}         ║
║      {Colors.DIM}{Colors.WHITE}Unique Edition  |  Auto-Setup  |  Auto-Launch{Colors.CYAN}           ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(art)


def step_header(step_num, title):
    print(
        f"\n{Colors.BLUE}{Colors.BOLD}╭─ STEP {step_num}: {Colors.CYAN}{title} {Colors.BLUE}{'─' * max(1, 44 - len(title))}╮{Colors.RESET}"
    )


def step_footer():
    print(f"{Colors.BLUE}╰{'─' * 60}╯{Colors.RESET}")


def spinner_wait(label, duration=1.0):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time:
        frame = frames[idx % len(frames)]
        print(
            f"\r  {Colors.MAGENTA}{frame}{Colors.RESET} {Colors.WHITE}{label}{Colors.RESET}",
            end="",
            flush=True,
        )
        time.sleep(0.08)
        idx += 1
    print(f"\r  {Colors.GREEN}✔{Colors.RESET} {Colors.WHITE}{label}{Colors.RESET}      ")


def run_cmd(cmd, check=True):
    print(f"  {Colors.YELLOW}▶ CMD:{Colors.RESET} {Colors.DIM}{cmd}{Colors.RESET}")
    result = subprocess.run(cmd, shell=True, text=True)
    if check and result.returncode != 0:
        print(f"  {Colors.RED}✖ Command failed (exit {result.returncode}): {cmd}{Colors.RESET}")
        sys.exit(1)
    return result.returncode == 0


def ensure_packages():
    step_header(1, "Checking Required Packages")
    required_pkgs = ["curl", "git", "nano"]
    spinner_wait("Scanning Termux environment for curl, git, nano...", 0.9)
    missing = [pkg for pkg in required_pkgs if shutil.which(pkg) is None]

    if missing:
        print(f"  {Colors.YELLOW}! Missing:{Colors.RESET} {', '.join(missing)}")
        run_cmd("pkg update -y && pkg upgrade -y", check=False)
        run_cmd(f"pkg install {' '.join(missing)} -y")
        print(f"  {Colors.GREEN}✔ Installed missing packages successfully!{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}✔ All required packages (curl, git, nano) are ready.{Colors.RESET}")
    step_footer()


def install_antigravity():
    step_header(2, "Installing Antigravity CLI")
    agy_bin = os.path.expanduser("~/.local/bin/agy")
    spinner_wait("Checking existing Antigravity binary...", 0.8)

    if os.path.exists(agy_bin):
        print(f"  {Colors.CYAN}ℹ Already installed at:{Colors.RESET} {agy_bin}")
        print(f"  {Colors.GREEN}✔ Skipping fresh download (auto-updates in background).{Colors.RESET}")
    else:
        run_cmd("curl -fsSL https://antigravity.google/cli/install.sh | bash")
        print(f"  {Colors.GREEN}✔ Antigravity CLI installation step completed!{Colors.RESET}")
    step_footer()


def configure_path():
    step_header(3, "Configuring PATH Environment")
    home = os.path.expanduser("~")
    bashrc_path = os.path.join(home, ".bashrc")
    local_bin = os.path.join(home, ".local", "bin")
    export_line = 'export PATH="$HOME/.local/bin:$PATH"'

    spinner_wait("Checking ~/.bashrc and environment PATH...", 0.7)

    existing_content = ""
    if os.path.exists(bashrc_path):
        with open(bashrc_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    if export_line not in existing_content:
        with open(bashrc_path, "a", encoding="utf-8") as f:
            f.write(f"\n{export_line}\n")
        print(f"  {Colors.GREEN}✔ Added ~/.local/bin to ~/.bashrc{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}✔ ~/.local/bin is already configured in ~/.bashrc{Colors.RESET}")

    current_path = os.environ.get("PATH", "")
    if local_bin not in current_path.split(":"):
        os.environ["PATH"] = f"{local_bin}:{current_path}"
        print(f"  {Colors.CYAN}ℹ Active session PATH updated.{Colors.RESET}")
    step_footer()


def verify_and_launch():
    step_header(4, "Verifying & Auto-Launching")
    spinner_wait("Locating `agy` executable...", 0.7)
    agy_path = shutil.which("agy")

    if agy_path:
        print(f"  {Colors.GREEN}✔ Binary found:{Colors.RESET} {Colors.WHITE}{agy_path}{Colors.RESET}")
        run_cmd("agy --version", check=False)
        step_footer()

        print(
            f"\n{Colors.GREEN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗\n"
            f"║    ★ SETUP COMPLETE! Launching Google Antigravity CLI... ★   ║\n"
            f"╚══════════════════════════════════════════════════════════════╝{Colors.RESET}\n"
        )
        spinner_wait("Starting Antigravity CLI...", 1.0)
        # সরাসরি বর্তমান টার্মিনাল সেশনে agy চালু করবে
        os.execvp(agy_path, ["agy"])
    else:
        print(f"  {Colors.RED}✖ `agy` not found in PATH yet.{Colors.RESET}")
        print(
            f"  {Colors.YELLOW}Tip:{Colors.RESET} Native Termux (ARM64) may hit Android kernel/glibc limits\n"
            f"       with the official script. Try `proot-distro` or a patched build."
        )
        step_footer()


def main():
    banner()
    ensure_packages()
    install_antigravity()
    configure_path()
    verify_and_launch()


if __name__ == "__main__":
    main()
