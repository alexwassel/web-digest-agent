
import re

def sanitize_topic(topic: str) -> str:
    t = re.sub(r"[\r\n\t]", " ", topic).strip()
    t = re.sub(r"[<>`$]", "", t)
    return t[:200]
