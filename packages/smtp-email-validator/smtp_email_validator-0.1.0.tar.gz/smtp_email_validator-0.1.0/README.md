```markdown
# EmailVerifier 📧✅

**EmailVerifier** is a comprehensive Python utility to validate email addresses using:

- Regular expression format validation  
- Domain and MX record checks  
- SMTP verification for business domains  
- Detection of disposable email domains  

Ideal for applications where email accuracy is critical (e.g., signups, CRMs, fraud prevention).

---

## 🔧 Features

- ✅ Format validation via regex  
- 🌐 Domain existence and MX record checks  
- 📬 SMTP verification (for business domains)  
- 🛡️ Disposable email detection (e.g., mailinator, 10minutemail)  
- ⚙️ Configurable timeout and retry settings  

---

## 📦 Installation

```bash
pip install emailverifier
```

---

## 🚀 Usage

```python
from emailverifier import EmailVerifier

verifier = EmailVerifier(timeout=8, max_retries=1)

email = "example@businessdomain.com"
is_valid, message = verifier.verify_email(email)

print(f"Valid: {is_valid}, Reason: {message}")
```

---

## 🔍 Sample Output

```
Valid: True, Reason: Verified business email
```

or

```
Valid: False, Reason: Disposable email detected
```

---

## ⚙️ Configuration

```python
verifier = EmailVerifier(timeout=10, max_retries=3)
```

- `timeout`: Network operation timeout in seconds  
- `max_retries`: Number of retry attempts for DNS and SMTP checks  

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ✨ Contributing

Pull requests and suggestions are welcome! Open an issue or submit a PR via GitHub.

---

## 📫 Contact

**Author**: Nworah Chimzuruoke Gabriel  
**Email**: nworahgabriel6@gmail.com  
**GitHub**: [https://github.com/Nworah-Gabriel/emailverifier](https://github.com/Nworah-Gabriel/emailverifier)

---

## 🛠 Dependencies

- [dnspython](https://pypi.org/project/dnspython/) – DNS resolver used for MX lookups  
- Python 3.7+

---

## ❗ Disclaimer

SMTP verification may not work with all servers, as some may reject or throttle unknown connections.
```
