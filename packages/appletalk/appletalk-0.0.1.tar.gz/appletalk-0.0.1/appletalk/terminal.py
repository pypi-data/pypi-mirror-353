try:
    from . import __init__
except:
    import __init__

def run_command(command: str, visible: bool = True):
    if visible:
        script = f'''
        tell application "Terminal"
            activate
            do script "{command}"
        end tell
        '''
    else:
        # run hidden via `do shell script`
        script = f'''set homeContents to do shell script "{command}"
                    display dialog homeContents'''
    
    __init__.run_applescript(script)
def capture_command_output(command: str) -> str:
    script = f'''set homeContents to do shell script "{command}"
                    display dialog homeContents'''
    
    __init__.run_applescript(script)
if __name__ == "__main__":
    run_command("echo 'Hello, World!'", visible=True)
    run_command("echo 'This is hidden'", visible=False)
    run_command("ls -l", visible=True)
    run_command("pwd", visible=False)