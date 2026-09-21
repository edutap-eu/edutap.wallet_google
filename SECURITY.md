# Security Policy

## Reporting a vulnerability

**Use the "Report a vulnerability" button on the Security tab of this
repository.** It opens a private advisory that only the maintainers can see, so
the issue stays confidential while it is being fixed.

A GitHub account is required for that form — creating one is free. If you cannot
or do not want to use GitHub, write to **security@edutap.eu**.

> **That address is a mailing list and is not encrypted.** Anything you send to
> it is readable by whoever operates the mail infrastructure along the way. Do
> not put exploit details, credentials or personal data in that mail. Use it to
> ask for another channel, and we will arrange one.

Please do not open a public issue for a suspected vulnerability. A public issue
is a disclosure, and it happens before anyone has had a chance to react.

## What happens next

We will confirm that your report arrived and tell you what we think of it. We do
this as quickly as we can manage.

**We do not promise a deadline.** eduTAP is open source, maintained by people
with other duties; a fixed response time would be a promise we could not keep
reliably, and a broken promise is worse than none. What we do commit to is that
a report will not be ignored, and that you will hear from us rather than be left
guessing.

## Supported versions

| Version | Supported |
|---|---|
| 3.0.0b2 (latest pre-release) | ✅ |
| everything older | ❌ |

**There is no stable release yet.** The current line is a pre-release: it is published so that it can be used and reviewed, and its interfaces may still change between versions. Supported means the newest pre-release, not a guarantee of stability.

There are no maintenance branches. A fix goes into the current development line
and is released from there; there is no backport to an earlier version. If you
depend on an older release, the answer to a security problem will be to move
forward.
