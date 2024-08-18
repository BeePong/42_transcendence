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

