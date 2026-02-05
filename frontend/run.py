import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


def main() -> None:
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000

    server = ThreadingHTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
