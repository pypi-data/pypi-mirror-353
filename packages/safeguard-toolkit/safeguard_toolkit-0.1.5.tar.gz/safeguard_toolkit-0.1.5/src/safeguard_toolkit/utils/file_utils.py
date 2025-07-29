import os, re
from typing import List, Dict
import requests
import math, ast

PYPI_API_URL = "https://pypi.org/pypi/{package}/json"

def fetch_pypi_metadata(package_name, cache):
    if package_name in cache:
        return cache[package_name]
    try:
        resp = requests.get(PYPI_API_URL.format(package=package_name), timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            cache[package_name] = data
            return data
    except Exception:
        pass
    return None


def read_lines_from_file(file_path: str) -> List[str]:
    """
    Reads a file and returns the lines as a list.
    Ignores decoding errors gracefully.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except Exception as e:
        raise IOError(f"Failed to read {file_path}: {e}")


def get_files_by_extension(base_path: str, extensions: List[str]) -> List[str]:
    """
    Recursively collect all files under base_path with specified extensions.

    Args:
        base_path (str): Base directory to search.
        extensions (List[str]): List of file extensions to include (e.g. ['.py', '.json']).

    Returns:
        List[str]: List of matching file paths.
    """
    exts = set(ext.lower() for ext in extensions)
    matched_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            file_lower = file.lower()
            if file_lower == ".env":
                matched_files.append(os.path.join(root, file))
                continue
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in exts:
                matched_files.append(os.path.join(root, file))
    return matched_files

def scan_lines_with_regex(lines: List[str], regex_patterns: Dict[str, str], whitelist: List[str]) -> List[dict]:
    findings = []
    seen_lines = set()  

    for lineno, line in enumerate(lines, 1):
        if any(w in line for w in whitelist):
            continue

        matched_labels = []
        for label, pattern in regex_patterns.items():
            if re.search(pattern, line):
                matched_labels.append(label)

        if matched_labels:
            key = (lineno, line.strip())
            if key not in seen_lines:
                seen_lines.add(key)
                labels_str = ", ".join(matched_labels)
                findings.append({
                    "level": "HIGH",
                    "types": matched_labels,  
                    "line": lineno,
                    "message": f"{labels_str} detected",
                    "content": line.strip()
                })

    return findings

def calculate_entropy(data: str) -> float:
    """
    Calculate the Shannon entropy of a string.
    """
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    for char in set(data):
        p_x = data.count(char) / length
        entropy -= p_x * math.log2(p_x)
    return entropy


def scan_lines_with_entropy(lines: List[str], whitelist: List[str],threshold) -> List[str]:
    """
    Scan lines for high-entropy strings.
    Returns warnings for lines above threshold.
    """
    findings = []

    for lineno, line in enumerate(lines, 1):
        if any(w in line for w in whitelist):
            continue
        entropy = calculate_entropy(line)
        if entropy > threshold:
            findings.append(f"[MEDIUM] High entropy at line {lineno}: {line.strip()} (Entropy: {entropy:.2f})")
    return findings


RISKY_CONFIGS = {
    "DEBUG": ["true", "1", "yes", "on"],
    "ALLOW_ALL_HOSTS": ["true", "1", "yes", "*"],
    "CORS_ALLOW_ALL_ORIGINS": ["true", "1", "yes", "*"],
    "SECRET_KEY": None,
    "DATABASE_URL": ["", "localhost", "127.0.0.1", "sqlite://", "sqlite:///:memory:"],
    "API_KEY": None,
    "PASSWORD": None,
    "TOKEN": None,
    "AWS_SECRET_ACCESS_KEY": None,
    "AWS_ACCESS_KEY_ID": None,
    "GCP_API_KEY": None,
    "AZURE_CLIENT_SECRET": None,
    "AZURE_STORAGE_KEY": None,
    "SLACK_TOKEN": None,
    "GITHUB_TOKEN": None,
    "GITLAB_TOKEN": None,
    "OPENAI_API_KEY": None,
    "ANTHROPIC_API_KEY": None,
    "COHERE_API_KEY": None,
    "HUGGINGFACE_API_KEY": None,
    "REPLICATE_API_TOKEN": None,
    "MISTRAL_API_KEY": None,
    "TOGETHER_API_KEY": None,
    "GROQ_API_KEY": None,
    "PERPLEXITY_API_KEY": None,
    "GEMINI_API_KEY": None,
    "DEEPINFRA_API_KEY": None,
    "LLM": None,
    "LLM_API_KEY": None,
    "LLM_SECRET": None,
    "LLM_TOKEN": None,
    "MODEL": None,
    "MODEL_NAME": None,
    "MODEL_PATH": None,
    "MODEL_URL": None,
    "PRIVATE_KEY": None,
    "CLIENT_SECRET": None,
    "CLIENT_ID": None,
    "ACCESS_TOKEN": None,
    "REFRESH_TOKEN": None,
}

SECRET_PATTERNS = [
    re.compile(r"(?i)apikey|api_key|api-key|secret|token|password|passwd|passphrase|access[_-]?key|auth[_-]?token"),
    re.compile(r"(?i)private[_-]?key|privatekey|private-key|secret[_-]?key|secretkey"),
    re.compile(r"(?i)client[_-]?secret|clientsecret"),
    re.compile(r"(?i)bearer[_-]?token|bearer_token"),
    re.compile(r"(?i)auth[_-]?secret|authsecret"),
    re.compile(r"(?i)jwt|jwt_token"),
    re.compile(r"(?i)session[_-]?token|sessiontoken"),
    re.compile(r"(?i)oauth[_-]?token|oauth_token"),
    re.compile(r"(?i)refresh[_-]?token|refreshtoken"),
    re.compile(r"(?i)password[_-]?hash|passwordhash"),
    re.compile(r"(?i)db[_-]?password|dbpassword"),
    re.compile(r"(?i)smtp[_-]?password|smtppassword"),
    re.compile(r"(?i)encryption[_-]?key|encryptionkey"),
    re.compile(r"(?i)private[_ ]?pem"),
    re.compile(r"(?i)rsa[_-]?private[_-]?key"),
    re.compile(r"(?i)ssh[_-]?key"),
    re.compile(r"(?i)pgp[_-]?private[_-]?key"),
    re.compile(r"(?i)openai[_-]?api[_-]?key"),
    re.compile(r"(?i)anthropic[_-]?api[_-]?key"),
    re.compile(r"(?i)cohere[_-]?api[_-]?key"),
    re.compile(r"(?i)huggingface[_-]?api[_-]?key"),
    re.compile(r"(?i)replicate[_-]?api[_-]?token"),
    re.compile(r"(?i)mistral[_-]?api[_-]?key"),
    re.compile(r"(?i)together[_-]?api[_-]?key"),
    re.compile(r"(?i)groq[_-]?api[_-]?key"),
    re.compile(r"(?i)perplexity[_-]?api[_-]?key"),
    re.compile(r"(?i)gemini[_-]?api[_-]?key"),
    re.compile(r"(?i)deepinfra[_-]?api[_-]?key"),
    re.compile(r"(?i)vertex[_-]?ai[_-]?key"),
    re.compile(r"(?i)llm[_-]?(api[_-]?key|secret|token)"),
    re.compile(r"(?i)model[_-]?(api[_-]?key|secret|token)"),
    re.compile(r"(?i)service[_-]?account[_-]?key"),
    re.compile(r"(?i)firebase[_-]?api[_-]?key"),
    re.compile(r"(?i)slack[_-]?token"),
    re.compile(r"(?i)github[_-]?token"),
    re.compile(r"(?i)gitlab[_-]?token"),
    re.compile(r"(?i)azure[_-]?(client[_-]?secret|storage[_-]?key|sas[_-]?token)"),
    re.compile(r"(?i)gcp[_-]?api[_-]?key"),
    re.compile(r"(?i)heroku[_-]?api[_-]?key"),
    re.compile(r"(?i)stripe[_-]?(api[_-]?key|secret)"),
    re.compile(r"(?i)mailgun[_-]?api[_-]?key"),
    re.compile(r"(?i)sendgrid[_-]?api[_-]?key"),
    re.compile(r"(?i)twilio[_-]?api[_-]?key"),
    re.compile(r"(?i)salesforce[_-]?oauth[_-]?token"),
    re.compile(r"(?i)database[_-]?url"),
    re.compile(r"(?i)basic[_-]?auth"),
    re.compile(r"(?i)access[_-]?token"),
    re.compile(r"(?i)refresh[_-]?token"),
    re.compile(r"(?i)client[_-]?id"),
    re.compile(r"(?i)client[_-]?key"),
    re.compile(r"(?i)consumer[_-]?key"),
    re.compile(r"(?i)consumer[_-]?secret"),
    re.compile(r"(?i)app[_-]?secret"),
    re.compile(r"(?i)app[_-]?key"),
    re.compile(r"(?i)session[_-]?id"),
    re.compile(r"(?i)session[_-]?key"),
    re.compile(r"(?i)authorization"),
    re.compile(r"(?i)bearer"),
]

REGEX_PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws(.{0,20})?(secret|key)['\"]?\s*[:=]\s*['\"][0-9a-zA-Z\/+]{40}['\"]",
    "AWS Session Token": r"(?i)aws(.{0,20})?(session|token)['\"]?\s*[:=]\s*['\"][A-Za-z0-9\/+=]{16,}['\"]",
    "Generic API Key": r"(?i)(api|token|key)['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
    "Password": r"(?i)(pass|password|pwd)['\"]?\s*[:=]\s*['\"].{6,}['\"]",
    "JWT": r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Google OAuth Access Token": r"ya29\.[0-9A-Za-z\-_]+",
    "Slack Token": r"xox[baprs]-([0-9a-zA-Z]{10,48})?",
    "Heroku API Key": r"(?i)heroku(.{0,20})?['\"]?\s*[:=]\s*['\"][0-9a-fA-F]{32}['\"]",
    "Stripe API Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Stripe Restricted Key": r"rk_live_[0-9a-zA-Z]{24}",
    "Mailgun API Key": r"key-[0-9a-zA-Z]{32}",
    "SendGrid API Key": r"SG\.[0-9A-Za-z\-_]{22,66}",
    "Twilio API Key": r"SK[0-9a-fA-F]{32}",
    "Private Key": r"-----BEGIN (RSA|DSA|EC|PGP|OPENSSH|PRIVATE) PRIVATE KEY-----",
    "SSH (DSA) Private Key": r"-----BEGIN DSA PRIVATE KEY-----",
    "SSH (EC) Private Key": r"-----BEGIN EC PRIVATE KEY-----",
    "SSH (OPENSSH) Private Key": r"-----BEGIN OPENSSH PRIVATE KEY-----",
    "SSH (RSA) Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "PGP Private Key Block": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    "Facebook Access Token": r"EAACEdEose0cBA[0-9A-Za-z]+",
    "GitHub Token": r"ghp_[0-9A-Za-z]{36}",
    "GitHub App Token": r"ghu_[0-9A-Za-z]{36}",
    "GitLab Token": r"glpat-[0-9A-Za-z\-]{20,}",
    "Bitbucket Token": r"x-token-auth:[0-9a-zA-Z\-_=]+",
    "Azure Storage Key": r"(?i)azure(.{0,20})?(account|key)['\"]?\s*[:=]\s*['\"][A-Za-z0-9+\/=]{88}['\"]",
    "Azure SAS Token": r"sv=201[0-9]-[0-9]{2}-[0-9]{2}&ss=[a-z]&srt=[a-z]&sp=[a-z]+&se=[0-9T:.Z]+&st=[0-9T:.Z]+&spr=https?&sig=[A-Za-z0-9%]+",
    "Salesforce OAuth Token": r"00D[A-Za-z0-9]{12,15}![A-Za-z0-9]{60,80}",
    "Database URL": r"(?i)(postgres|mysql|mongodb|redis|mssql|oracle|sqlite)://[^ \n]+",
    "Basic Auth in URL": r"https?:\/\/[^\/\s:]+:[^\/\s@]+@[^\/\s]+",
    "RSA Private Key": r"-----BEGIN RSA PRIVATE KEY-----",
    "DSA Private Key": r"-----BEGIN DSA PRIVATE KEY-----",
    "EC Private Key": r"-----BEGIN EC PRIVATE KEY-----",
    "PKCS8 Private Key": r"-----BEGIN PRIVATE KEY-----",
    "JSON Web Token": r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
    "API Secret": r"(?i)(api|secret|client|private)[-_]?(key|secret)?['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
    "Client Secret": r"(?i)client(.{0,20})?secret['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
    "Client ID": r"(?i)client(.{0,20})?id['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
    "Access Token": r"(?i)access(.{0,20})?token['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]",
    "Refresh Token": r"(?i)refresh(.{0,20})?token['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-\.]{8,}['\"]",
    "OpenAI API Key": r"sk-[A-Za-z0-9]{32,}",
    "Anthropic API Key": r"sk-ant-[A-Za-z0-9\-_]{36,}",
    "Cohere API Key": r"cohere-apikey-[a-zA-Z0-9]{64}",
    "Google Vertex AI Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "HuggingFace API Key": r"hf_[A-Za-z0-9]{36,}",
    "Replicate API Token": r"r8_[A-Za-z0-9]{32,}",
    "Mistral API Key": r"mistral-[A-Za-z0-9\-_]{32,}",
    "OpenRouter API Key": r"or-[A-Za-z0-9\-_]{32,}",
    "Together AI API Key": r"together-[A-Za-z0-9\-_]{32,}",
    "Groq API Key": r"gsk_[A-Za-z0-9]{32,}",
    "Perplexity API Key": r"pplx-[A-Za-z0-9\-_]{32,}",
    "Gemini API Key": r"gsk_[A-Za-z0-9]{32,}",
    "DeepInfra API Key": r"di_[A-Za-z0-9]{32,}",
    "OpenAI (legacy) API Key": r"openai-[A-Za-z0-9\-_]{32,}",
    "Password": r'password\s*[:=]\s*["\']?[\w@#$%^&*]{6,}["\']?',
    "API Key": r'[A-Za-z0-9]{16,}',
}
