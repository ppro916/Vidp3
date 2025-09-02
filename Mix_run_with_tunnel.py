import subprocess
import threading
import time
import re
import socket
import sys
from app import socketio, app

# ANSI रंग कोड
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
    """रंगीत टेक्स्ट प्रिंट करण्यासाठी"""
    print(f"{COLORS[color]}{text}{COLORS['END']}")

def print_banner():
    """सर्व्हर स्टार्टअप बॅनर प्रदर्शित करा"""
    banner = f"""
{COLORS['BLUE']}{COLORS['BOLD']}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                🚀 व्हिडिओ कॉन्फरन्सिंग सर्व्हर                    ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{COLORS['END']}
"""
    print(banner)

def get_local_ip():
    """लोकल नेटवर्क IP पत्ता शोधण्यासाठी"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_flask_app():
    """Flask सर्व्हर चालवण्यासाठी"""
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_cloudflared_tunnel():
    """Cloudflare Tunnel चालवण्यासाठी आणि URL extract करण्यासाठी"""
    try:
        # cloudflared tunnel चालवा
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://0.0.0.0:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # URL शोधण्यासाठी pattern
        url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

        # प्रक्रियेचे output वाचा
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # फक्त URL शोधा आणि प्रिंट करा
                url_match = url_pattern.search(output)
                if url_match:
                    cloudflare_url = url_match.group()
                    local_ip = get_local_ip()
                    
                    # सुंदर आउटपुट प्रदर्शित करा
                    print_banner()
                    
                    print_color("सर्व्हर यशस्वीरित्या सुरू झाला आहे!", "GREEN")
                    print()
                    
                    print_color("🌐 क्लाउडफ्लेअर टनेल URL:", "BOLD")
                    print_color(f"   {cloudflare_url}", "BLUE")
                    print()
                    
                    print_color("👨‍💼 प्रशासन पान:", "BOLD")
                    print_color(f"   {cloudflare_url}/admin/room1", "BLUE")
                    print()
                    
                    print_color("💻 स्थानिक URL:", "BOLD")
                    print_color(f"   http://localhost:5000", "YELLOW")
                    print()
                    
                    print_color("📡 लोकल नेटवर्क URL:", "BOLD")
                    print_color(f"   http://{local_ip}:5000", "YELLOW")
                    print()
                    
                    print_color("📱 मोबाइल टेस्टिंग:", "BOLD")
                    print_color(f"   http://{local_ip}:5000", "YELLOW")
                    print_color("   (समान WiFi नेटवर्क आवश्यक)", "BOLD")
                    print()
                    
                    print_color("=" * 60, "BLUE")
                    print_color("सर्व्हर बंद करण्यासाठी Ctrl+C दाबा...", "BOLD")
                    print_color("=" * 60, "BLUE")
                    break

        # प्रक्रिया चालू ठेवा
        process.wait()

    except Exception as e:
        print_color(f"त्रुटी: cloudflared चालवताना: {e}", "RED")

if __name__ == '__main__':
    # Flask सर्व्हर स्वतंत्र thread मध्ये चालवा
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # थोडा वेळ थांबा Flask सर्व्हर सुरू होण्यासाठी
    time.sleep(3)

    # Cloudflare Tunnel चालवा
    tunnel_thread = threading.Thread(target=run_cloudflared_tunnel)
    tunnel_thread.daemon = True
    tunnel_thread.start()

    try:
        # मुख्य thread ला सक्रिय ठेवा
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_color("\nसर्व्हर बंद करत आहे...", "RED")
        sys.exit(0)
