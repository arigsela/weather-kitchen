# CSRF Protection

## Why Weather Kitchen Is Not Vulnerable to CSRF

Cross-Site Request Forgery (CSRF) is an attack where a malicious site tricks a logged-in user's browser into making unintended requests to another site. It works by exploiting how browsers automatically attach cookies to requests.

**Weather Kitchen uses Bearer token authentication — not cookies.**

---

## How CSRF Works (and Why Cookies Are the Problem)

1. User logs in to `bank.com` — browser stores a session cookie
2. User visits `evil.com` — page has `<img src="https://bank.com/transfer?to=attacker&amount=1000">`
3. Browser sends the request to `bank.com` **and automatically includes the session cookie**
4. `bank.com` sees a valid session cookie and processes the transfer

The attack works because **browsers send cookies automatically** for any request to a matching domain, regardless of where the request originates.

---

## Why Bearer Tokens Prevent CSRF

Weather Kitchen authenticates requests using:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Browsers do NOT automatically attach `Authorization` headers** to cross-origin requests. The token must be explicitly included by JavaScript running on the page.

When `evil.com` tries to make a request to Weather Kitchen:
1. Browser sends the request — but without the `Authorization: Bearer` header
2. Weather Kitchen returns `401 Unauthorized` — no cookie to steal means no CSRF attack

---

## CORS as Defense-in-Depth

Even though CSRF doesn't apply to Bearer token auth, Weather Kitchen also configures CORS:

```python
CORSMiddleware(
    allow_origins=["https://app.yourdomain.com"],  # Only your frontend
    allow_credentials=False,                        # No cookies
)
```

This prevents unauthorized JavaScript on other origins from reading API responses, even if they somehow managed to attach a token.

---

## Summary

| Protection | Mechanism | Status |
|------------|-----------|--------|
| CSRF prevention | Bearer tokens (not cookies) | ✅ Not vulnerable |
| Cross-origin read protection | CORS `allow_origins` whitelist | ✅ Configured |
| Token theft prevention | Short-lived access tokens (15 min) | ✅ Mitigated |
| Token revocation | Refresh token rotation + blocklist | ✅ Implemented |

No CSRF tokens, `SameSite` cookie flags, or synchronizer patterns are needed because no cookies are used.
