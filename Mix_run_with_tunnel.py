import subprocess
import threading
import time
import re
import socket
import sys
from app import socketio, app

# ANSI color codes
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
    "END": "\033[0m",
}

def print_color(text, color):
    """To print colored text"""
    print(f"{COLORS[color]}{text}{COLORS['END']}")

def print_banner():
    """Display server startup banner"""
    banner = f"""
{COLORS['BLUE']}{COLORS['BOLD']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                🚀 Video Conferencing Server                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{COLORS['END']}
"""
    print(banner)

def get_local_ip():
    """Find local network IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_flask_app():
    """Run Flask server"""
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_cloudflared_tunnel():
    """Run Cloudflare Tunnel and extract URL"""
    try:
        # run cloudflared tunnel
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://0.0.0.0:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # pattern to search for URL
        url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

        # read process output
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # only search for and print URL
                url_match = url_pattern.search(output)
                if url_match:
                    cloudflare_url = url_match.group()
                    local_ip = get_local_ip()
                    
                    # display nicely formatted output
                    print_banner()
                    
                    print_color("Server started successfully!", "GREEN")
                    print()
                    
                    print_color("🌐 Cloudflare Tunnel URL:", "BOLD")
                    print_color(f"   {cloudflare_url}", "BLUE")
                    print()
                    
                    print_color("👨‍💼 Admin page:", "BOLD")
                    print_color(f"   {cloudflare_url}/admin/room1", "BLUE")
                    print()
                    
                    print_color("💻 Local URL:", "BOLD")
                    print_color(f"   http://localhost:5000", "YELLOW")
                    print()
                    
                    print_color("📡 Local Network URL:", "BOLD")
                    print_color(f"   http://{local_ip}:5000", "YELLOW")
                    print()
                    
                    print_color("📱 Mobile Testing:", "BOLD")
                    print_color(f"   http://{local_ip}:5000", "YELLOW")
                    print_color("   (Same WiFi network required)", "BOLD")
                    print()
                    
                    print_color("=" * 60, "BLUE")
                    print_color("Press Ctrl+C to stop the server...", "BOLD")
                    print_color("=" * 60, "BLUE")
                    break

        # keep process running
        process.wait()

    except Exception as e:
        print_color(f"Error: while running cloudflared: {e}", "RED")

if __name__ == '__main__':
    # Run Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Wait a little for Flask server to start
    time.sleep(3)

    # Run Cloudflare Tunnel
    tunnel_thread = threading.Thread(target=run_cloudflared_tunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()

    try:
        # Keep main thread active
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_color("\nShutting down server...", "RED")
        sys.exit(0)
