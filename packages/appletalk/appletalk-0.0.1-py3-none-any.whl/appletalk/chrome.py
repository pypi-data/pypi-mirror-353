try:
    from . import __init__
except:
    import __init__


def get_active_tab_url() -> str:
    script = '''
    tell application "Google Chrome"
        if not (exists window 1) then return ""
        set theUrl to URL of active tab of front window
        return theUrl
    end tell
    '''
    return __init__.run_applescript(script)
def get_active_tab_title() -> str:
    script = '''
    tell application "Google Chrome"
        if not (exists window 1) then return ""
        set theTitle to title of active tab of front window
        return theTitle
    end tell
    '''
    return __init__.run_applescript(script)
def open_url(url: str) -> None:
    script = f'''
    tell application "Google Chrome"
        if not (exists window 1) then make new window
        tell window 1
            make new tab with properties {{URL:"{url}"}}
        end tell
        activate
    end tell
    '''
    __init__.run_applescript(script)

if __name__ == "__main__":
    print(get_active_tab_url())
    print(get_active_tab_title())
    open_url("https://www.example.com")