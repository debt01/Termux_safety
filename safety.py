# DOn;t try to copy my tool.!
#!/data/data/com.termux/files/usr/bin/python3
import os
import sys
import re
import shutil
import subprocess
from pathlib import Path

# ======================
#  CONFIGURATION
# ======================
SAFEBOX_ROOT = Path.home() / "safebox"
ALLOWED_COMMANDS = ["git", "python", "bash", "ls", "cd", "pwd", "pip", "tree", 
                   "cmatrix", "bat", "node", "npm", "wget", "curl", "nano", "vim"]
DANGEROUS_PATTERNS = [
    r"rm\s+-rf", r":\(\)\{:\|:\&\};:", r"chmod\s+[0-7]{3,4}",
    r"(wget|curl)\s+.?\s\|\s*sh", r"dd\s+if=.?of=.", r"(su|sudo)\b",
    r"/data/data/com.termux/files/home", r";", r"&&", r"\|\|",
    r"mv\s+.*\s+/", r"cat\s+>/", r">\s*/", r"echo\s+.?\s+>",
    r"chown\b", r"tar\s+.*\s+-(x|f)", r"\.\/", r"sh\s+.*\.sh"
]

# ======================
#  CORE SAFEBOX CLASS
# ======================
class SafeBox:
    def __init__(self):
        self.current_dir = SAFEBOX_ROOT
        self.setup_environment()
        self.show_welcome()

    def setup_environment(self):
        """Initialize the sandbox directories"""
        os.makedirs(SAFEBOX_ROOT, exist_ok=True)
        os.makedirs(SAFEBOX_ROOT / "bin", exist_ok=True)
        os.makedirs(SAFEBOX_ROOT / "home", exist_ok=True)
        os.makedirs(SAFEBOX_ROOT / "tmp", exist_ok=True)

        # Create symlinks for allowed commands
        for cmd in ALLOWED_COMMANDS:
            cmd_path = shutil.which(cmd)
            if cmd_path:
                dest = SAFEBOX_ROOT / "bin" / cmd
                if not dest.exists():
                    os.symlink(cmd_path, dest)

        # Create basic .bashrc
        bashrc = SAFEBOX_ROOT / "home" / ".bashrc"
        if not bashrc.exists():
            with open(bashrc, 'w') as f:
                f.write("echo 'Welcome to SafeBox environment'\n")

    def is_command_allowed(self, cmd):
        """Check if command is safe"""
        # First check if command is in allowed list
        base_cmd = cmd.split()[0]
        if base_cmd not in ALLOWED_COMMANDS:
            return False
            
        # Then check for dangerous patterns
        return not any(re.search(pattern, cmd, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS)

    def execute_safe(self, cmd):
        """Run command with safety checks"""
        try:
            # Create restricted environment
            env = os.environ.copy()
            env["PATH"] = f"{SAFEBOX_ROOT}/bin"
            env["HOME"] = str(SAFEBOX_ROOT / "home")
            env["TMPDIR"] = str(SAFEBOX_ROOT / "tmp")

            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=self.current_dir,
                executable="/bin/bash",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()

            if stdout: print(stdout, end='')
            if stderr: print(f"\033[91m{stderr}\033[0m", end='', file=sys.stderr)

        except Exception as e:
            print(f"\033[91mError: {str(e)}\033[0m")

    def change_directory(self, new_dir):
        """Safe directory navigation"""
        try:
            target = (self.current_dir / new_dir).resolve()

            if str(target).startswith(str(SAFEBOX_ROOT)):
                if target.is_dir():
                    self.current_dir = target
                    print(f"\033[94mCurrent dir: {self.current_dir}\033[0m")
                else:
                    print(f"\033[91mDirectory not found: {new_dir}\033[0m")
            else:
                print("\033[91mError: Cannot leave SafeBox environment!\033[0m")
        except Exception as e:
            print(f"\033[91mError: {str(e)}\033[0m")

    def show_welcome(self):
        """Display welcome message"""
        print(f"""
\033[1;36m
▓█████▄  ██▀███   ▄▄▄       ██▓███   ██▓ ███▄ ▄███▓
▒██▀ ██▌▓██ ▒ ██▒▒████▄    ▓██░  ██▒▓██▒▓██▒▀█▀ ██▒
░██   █▌▓██ ░▄█ ▒▒██  ▀█▄  ▓██░ ██▓▒▒██▒▓██    ▓██░
░▓█▄   ▌▒██▀▀█▄  ░██▄▄▄▄██ ▒██▄█▓▒ ▒░██░▒██    ▒██ 
░▒████▓ ░██▓ ▒██▒ ▓█   ▓██▒▒██▒ ░  ░░██░▒██▒   ░██▒
 ▒▒▓  ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒▓▒░ ░  ░░▓  ░ ▒░   ░  ░
 ░ ▒  ▒   ░▒ ░ ▒░  ▒   ▒▒ ░░▒ ░      ▒ ░░  ░      ░
 ░ ░  ░   ░░   ░   ░   ▒   ░░        ▒ ░░      ░   
   ░       ░           ░  ░          ░         ░   
\033[0m
        \033[1;33mTermux SafeBox v1.2\033[0m
        \033[1;32mSafe Environment Activated\033[0m
        \033[1;32mDeveloped by Debt01\033[0m
        Current sandbox: {SAFEBOX_ROOT}
        Type 'help' for commands, 'exit' to quit
        """)

    def show_help(self):
        """Display help menu"""
        print("""
\033[1;35mSAFEBOX COMMANDS:\033[0m
  \033[1;32mcd <dir>\033[0m      - Change directory (within SafeBox)
  \033[1;32m<command>\033[0m     - Execute allowed commands directly
  \033[1;32mhelp\033[0m         - Show this help
  \033[1;32mexit\033[0m         - Leave SafeBox

\033[1;35mALLOWED TOOLS:\033[0m
  """ + ", ".join(ALLOWED_COMMANDS) + """

\033[1;31mBLOCKED ACTIONS:\033[0m
  • File deletion commands (rm, shred)
  • Permission changes (chmod, chown)
  • System commands (sudo, su)
  • Pipe-to-shell patterns
  • Fork bombs and other exploits
  • Access to real Termux filesystem
        """)

    def start(self):
        """Main interactive shell"""
        while True:
            try:
                prompt = f"\033[1;32m[SAFE]\033[0m \033[94m{self.current_dir}\033[0m $ "
                user_input = input(prompt).strip()

                if not user_input:
                    continue
                elif user_input.lower() == "exit":
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                elif user_input.startswith("cd "):
                    self.change_directory(user_input[3:])
                else:
                    if self.is_command_allowed(user_input):
                        self.execute_safe(user_input)
                    else:
                        print("\033[91mBLOCKED: Potentially dangerous command or not allowed!\033[0m")

            except KeyboardInterrupt:
                print("\n\033[93mType 'exit' to quit\033[0m")
            except Exception as e:
                print(f"\033[91mFatal error: {str(e)}\033[0m")

# ======================
#  MAIN EXECUTION
# ======================
if __name__ == "__main__":
    try:
        safebox = SafeBox()
        safebox.start()
        print("\033[1;32m[+] SafeBox session ended. Your system is safe.\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Critical error: {str(e)}\033[0m")
        sys.exit(1)
