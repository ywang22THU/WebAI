def fail_to_get_url(url, e) -> RuntimeError:
    return RuntimeError(f"Failed to get URL: {url}\n{e}")

def login_failed(url) -> RuntimeError:
    return RuntimeError(f"User failed to login in {url}")