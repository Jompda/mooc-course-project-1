# Project 1
[Instructions](https://cybersecuritybase.mooc.fi/module-3.1). Project based on MOOC CSRF task. 

## Accounts:
```
bob:squarepants
alice:redqueen
patrick:asteroid
```

- https://owasp.org/Top10/
- https://owasp.org/www-project-top-ten/2017/

## Vulnerabilities

- [X] A01:2021-Broken access control
  - "Access control enforces policy such that users cannot act outside of their intended permissions." https://owasp.org/Top10/A01_2021-Broken_Access_Control/
    - "Unohda" laittaa login requirement johki viewiin,

- [ ] A02:2021-Cryptographic Failures (kryptografia kusee tai jtn)
  - "Shifting up one position to #2, previously known as Sensitive Data Exposure, which is more of a broad symptom rather than a root cause, the focus is on failures related to cryptography (or lack thereof)" https://owasp.org/Top10/A02_2021-Cryptographic_Failures/
    - lack thereof, voisko olla hashaamattomia saliksia databases -> käykö vulnerability?

- [X] A03:2021-Injection (SQL ja Cross-Site Scripting)
  - "User-supplied data is not validated, filtered, or sanitized by the application." https://owasp.org/Top10/A03_2021-Injection/
    - SQL injektio: kaiva vaikka joku salis tietokannasta

- [X] A07:2021-Identification and Authentication Failures
  - Permits brute force or other automated attacks. https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
    - Jätä login bruteforcelle alttiiks.
    - hackpassword tiedosto tuotu, TODO siel

- [X] A09:2021-Security Logging and Monitoring Failures
  - "Without logging and monitoring, breaches cannot be detected"

- [X] CSRF
  - "Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on a web application in which they’re currently authenticated" https://owasp.org/www-community/attacks/csrf
    - Jätä CSRF token pois jostain formista.

