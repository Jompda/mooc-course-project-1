LINK: https://github.com/Jompda/mooc-course-project-1
Using list OWASP Top 10 - 2021.
Installation instructions:
1. Install Python (https://www.python.org/).
2. Install Django (https://docs.djangoproject.com/en/5.1/topics/install/). On Arch install package "python-django".
3. Install dependencies by running "pip install django-axes dj_user_login_history".
5. Start server by running "python3 manage.py runserver".

- If you enable something like login_history, make sure to run "python3 manage.py migrate".

Accounts:
bob:squarepants
alice:redqueen
patrick:asteroid

In case of a locked account, run "python manage.py axes_reset"


FLAW 1:
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/config/settings.py#L100

Cross Site Request Forgery (CSRF) is a type of attack leveraging browser authentication. The idea is that if a browser holds authentication information to a service, like a cookie or HTTP login information, a malicious actor can then send requests to said service which the browser then automatically authenticates [1]. In the course project, the referenced form is pointing to a API end point which accepts a GET request which can easily be forged by having the following element in a website '<img src="DOMAIN/confirm/?sender=INSERT_SENDER_ID&receiver=INSERT_RECEIVER_ID&amount=INSERT_AMOUNT" />', tricking the browser to sending the malicious request. Note that forging POST requests isn't much harder and can even be sent with JavaScript [1].

To filter out such requests, frameworks have begun providing tokens unique to user and form. Should a request not have the correct token, it should be deemed as malicious and discarded [2]. Though this method still allows for a malicious website to extract the CSRF token from the form page with a simple XmlHttpRequest and include it in the final malicious request, effectively bypassing a token-based fix.


FLAW 2:
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/pages/views.py#L52

A03:2021-Injection, in this case SQL injection, occurs when unsanitized input from a client is passed to SQL queries, thus allowing to escape the original SQL statement and run statements arbitrarily [3]. The referenced code has this flaw because it passes user-supplied content (HTTP query parameters) directly to a vulnerable function (transfer) which doesn't do any kind of sanitizing on the parameters and just inserts them to the SQL query.

This flaw can be avoided by utilizing parameterization of queries. Besides this, a common way to prevent SQL injection is to use libraries that provide Object-Relational Mapping (ORM). Although, ORM injection [4] is also a thing. In other words, using external libraries to patch a vulnerability can sometimes increase the attack surface.


FLAW 3:
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/pages/views.py#L45

A01:2021-Broken Access Control occurs when a user is allowed to act outside their intended privileges [5]. In the referenced code the client provides the account IDs and amount for the transaction and the server just blindly trusts the information. In consequence, any authenticated user is able to confirm a transfer from any account to any account. For example, a malicious request could be as follows: "DOMAIN/confirm/?sender=INSERT_SENDER_ID&receiver=INSERT_RECEIVER_ID&amount=INSERT_AMOUNT".

In real world, such a simple flaw should never make it to production. To a developer's defense, with a large amount of API end-points, this could still happen. The flaw in question can be easily fixed by checking whether or not the user actually has privileges over the sender account on the server side. In the project code the fix has been achieved by relying on the "@login_required" decorator which populates "request.user" who is always the authenticated sender, and thus no broken access control.


FLAW 4:
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/config/settings.py#L70

A07:2021-Identification and Authentication Failures includes vulnerability to brute force attacks [6]. A brute force attack usually consists of testing common values at a rapid speed and it can be taken further by using mutations of said values [7]. Even exhaustive methods can be utilized with todays computing performance.

Such a flaw can be quite easily fixed by setting a hard limit on how many failed login attempts can occur within a certain amount of time, after which the IP address gets blocked for a while, and optionally the owner of the account in question gets notified. This method still leaves the account vulnerable to botnets executing the brute force attack because the requests come in from multiple IP-addresses. The solution is to lock the victim account to prevent further login attempts which is called "a lockout policy" [7].


FLAW 5:
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/config/settings.py#L30
https://github.com/Jompda/mooc-course-project-1/blob/0178fdb3aeee22d2ef4fb11db9a1b21a4fe33047/server/pages/views.py#L8

A09:2021-Security Logging and Monitoring Failures can be simplified to insufficient logging [8]. The course project only logs HTTP requests and they're just printed to STDOUT which doesn't even get stored anywhere. Due to this flawed design, tracing unintended behaviour of the system itself is near impossible and malicious activity such as money transfers or login attempts can go completely undetected.

Fixing this issue takes a bit more effort. All events such as HTTP requests, logins, money transfers, and account lockouts should be logged to a persistent medium such as a database or dedicated files in a clearly readable format, excluding private information ofcourse. In addition, the log should also be backed up in a separate physical location [8]. All this is to create a trail to track down activity, be it malicious or otherwise necessary.


References:
[1] https://owasp.org/www-community/attacks/csrf
[2] https://cybersecuritybase.mooc.fi/module-2.3/1-security#programming-exercise-csrf-prompt-by-pass
[3] https://owasp.org/www-community/attacks/SQL_Injection
[4] https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05.7-Testing_for_ORM_Injection.html
[5] https://owasp.org/Top10/A01_2021-Broken_Access_Control/
[6] https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
[7] https://owasp.org/www-community/attacks/Brute_force_attack
[8] https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/
