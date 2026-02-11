# gunicorn.conf.py
import socket

def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    We patch the socket module here to force IPv4 (AF_INET)
    and ignore IPv6 (AF_INET6) to prevent 30s timeouts on Render.
    """
    try:
        original_getaddrinfo = socket.getaddrinfo

        def new_getaddrinfo(*args, **kwargs):
            res = original_getaddrinfo(*args, **kwargs)
            # Filter out any IPv6 results
            return [r for r in res if r[0] == socket.AF_INET]

        socket.getaddrinfo = new_getaddrinfo
        worker.log.info("IPv4 Force Patch Applied successfully.")
    except Exception as e:
        worker.log.warning(f"IPv4 Patch failed: {e}")