import subprocess
import threading
import time
import re
import socket
import sys
from app import socketio, app


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

                    print("\n" + "=" * 60)
                    print("सर्व्हर यशस्वीरित्या सुरू झाला आहे!")
                    print("=" * 60)
                    print(f"🌐 Cloudflare Tunnel URL: {cloudflare_url}")
                    print(f"👨‍💼 Cloudflare Tunnel Admin URL: {cloudflare_url}/admin/room1")
                    print(f"💻 Localhost URL: http://localhost:5000")
                    print(f"📡 LAN URL: http://{local_ip}:5000")
                    print(f"📱 Mobile testing: http://{local_ip}:5000 (समान WiFi आवश्यक)")
                    print("=" * 60)
                    print("\nसर्व्हर बंद करण्यासाठी Ctrl+C दाबा...")
                    print("=" * 60 + "\n")
                    break

        # प्रक्रिया चालू ठेवा
        process.wait()

    except Exception as e:
        print(f"त्रुटी: cloudflared चालवताना: {e}")


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
        print("\nसर्व्हर बंद करत आहे...")
        sys.exit(0)
