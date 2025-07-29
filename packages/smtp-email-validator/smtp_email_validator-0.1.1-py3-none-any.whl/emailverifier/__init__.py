import re
import smtplib
import socket
import dns.resolver
import logging
from typing import Tuple, List
import time

class EmailVerifier:
    """
    Comprehensive email verification tool that checks:
    - Format validity
    - Domain existence
    - MX records
    - SMTP message receiving capability
    - Disposable email detection
    """
    
    def __init__(self, timeout: int = 10, max_retries: int = 2):
        """
        Initialize the verifier
        
        Args:
            timeout: Timeout in seconds for network operations
            max_retries: Maximum retry attempts for failed operations
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = self._setup_logger()
        
        # Standard SMTP ports to try (25, 587, 465)
        self.smtp_ports = [25, 587, 465]
        
        # Domain lists (could be loaded from files)
        self.disposable_domains = {
            'mailinator.com', 'tempmail.com', '10minutemail.com',
            'guerrillamail.com', 'throwawaymail.com', 'fakeinbox.com',
            'maildrop.cc', 'temp-mail.org', 'yopmail.com'
        }
        
        self.free_email_domains = {
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'protonmail.com', 'aol.com', 'mail.com',
            'zoho.com', 'yandex.com'
        }

    def _setup_logger(self) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger('EmailVerifier')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def verify_email(self, email: str) -> Tuple[bool, str]:
        """
        Main verification method
        
        Args:
            email: Email address to verify
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            email = email.strip().lower()
            self.logger.info(f"Verifying email: {email}")

            # 1. Validate email format
            if not self._validate_email_format(email):
                return False, "Invalid email format"

            # 2. Extract domain
            try:
                domain = email.split('@')[1]
            except IndexError:
                return False, "Invalid email format - missing domain"

            # 3. Check for disposable emails
            if self._is_disposable_email(domain):
                return False, "Disposable email detected"

            # 4. Verify domain and MX records
            mx_valid, mx_msg = self._verify_mx_records(domain)
            if not mx_valid:
                return False, mx_msg

            # 5. For free emails, MX check is sufficient
            if domain in self.free_email_domains:
                return True, "Verified free email (MX check only)"

            # 6. For business emails, perform full SMTP verification
            smtp_valid, smtp_msg = self._verify_smtp(email, domain)
            if smtp_valid:
                return True, "Verified business email"
            return False, f"Business email verification failed: {smtp_msg}"

        except Exception as e:
            self.logger.error(f"Verification error: {str(e)}")
            return False, f"Verification error: {str(e)}"

    def _validate_email_format(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
        return re.match(pattern, email) is not None

    def _is_disposable_email(self, domain: str) -> bool:
        """Check if domain is a known disposable email provider"""
        return domain in self.disposable_domains

    def _verify_mx_records(self, domain: str) -> Tuple[bool, str]:
        """Verify domain MX records exist"""
        for attempt in range(self.max_retries + 1):
            try:
                # Try with system DNS first
                try:
                    answers = dns.resolver.resolve(domain, 'MX')
                    if answers:
                        return True, "MX records found"
                except:
                    # Fallback to Google DNS
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google DNS
                    answers = resolver.resolve(domain, 'MX')
                    if answers:
                        return True, "MX records found"
                return False, "No MX records found"
                
            except dns.resolver.NXDOMAIN:
                return False, "Domain does not exist"
            except dns.resolver.NoNameservers:
                return False, "No nameservers found for domain"
            except dns.resolver.Timeout:
                if attempt == self.max_retries:
                    return False, "DNS lookup timed out"
                time.sleep(1)
            except Exception as e:
                return False, f"DNS error: {str(e)}"
        return False, "DNS lookup failed after retries"

    def _verify_smtp(self, email: str, domain: str) -> Tuple[bool, str]:
        """
        Verify email can receive messages via SMTP
        
        Args:
            email: Full email address
            domain: Email domain portion
            
        Returns:
            Tuple of (is_valid, message)
        """
        # Get mail servers to try (MX records or domain fallback)
        mail_servers = self._get_mail_servers(domain)
        if not mail_servers:
            return False, "No mail servers found"

        # Try each server and port combination
        for server in mail_servers:
            for port in self.smtp_ports:
                for attempt in range(self.max_retries + 1):
                    try:
                        with smtplib.SMTP(timeout=self.timeout) as conn:
                            self.logger.info(f"Trying {server}:{port} (attempt {attempt + 1})")
                            conn.connect(server, port)
                            
                            # SMTP conversation
                            conn.helo('example.com')
                            conn.mail('verify@example.com')
                            code, msg = conn.rcpt(email)
                            conn.quit()
                            
                            # Interpret response
                            if code == 250:
                                return True, f"Verified at {server}:{port}"
                            elif 500 <= code < 600:
                                return False, f"Server rejected recipient: {code} {msg.decode()}"
                            else:
                                return False, f"Temporary failure: {code} {msg.decode()}"
                                
                    except smtplib.SMTPResponseException as e:
                        return False, f"SMTP error {e.smtp_code}: {e.smtp_error.decode()}"
                    except (socket.timeout, ConnectionRefusedError, smtplib.SMTPConnectError):
                        if attempt == self.max_retries:
                            break  # Move to next server/port
                        time.sleep(1)
                    except Exception as e:
                        return False, f"Connection error: {str(e)}"
        
        return False, "All mail servers/ports unavailable"

    def _get_mail_servers(self, domain: str) -> List[str]:
        """Get list of mail servers for domain, sorted by priority"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [str(mx.exchange) for mx in sorted(mx_records, key=lambda x: x.preference)]
        except Exception:
            return [domain]  # Fallback to domain itself


if __name__ == "__main__":
    # Example usage
    verifier = EmailVerifier(timeout=8, max_retries=1)
    
    test_emails = [
        "nworahgabriel6@gmail.com",
        "invalid.email@format",
        "nonexistent@example.com",
        "test@mailinator.com",
        "valid@businessdomain.com",
        "test@yahoo.com",
        "contact@microsoft.com",
        "user@github.com"
    ]
    
    print("Email Verification Results")
    print("=" * 50)
    
    for email in test_emails:
        valid, message = verifier.verify_email(email)
        status = "✓ VALID" if valid else "✗ INVALID"
        print(f"\nEmail: {email}")
        print(f"Status: {status}")
        print(f"Details: {message}")
        print("-" * 50)