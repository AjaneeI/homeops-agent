# Security

HomeOps Agent is a prototype that currently uses simulated devices. It does not require real smart-home credentials for the deterministic public demo.

## Credential hygiene

- Do not commit `.env` files, provider keys, device credentials, private certificates, or local credential JSON.
- Keep example environment files free of usable secrets.
- Use least-privilege credentials for any future real-device integration.
- Treat any credential exposed in Git history, logs, screenshots, issues, or pull requests as compromised and rotate or revoke it before cleanup.

## Safety boundary

Real-device integrations should preserve the existing approval gates, failure handling, and human-in-the-loop controls. Door-lock and access changes must not be presented as autonomous production behavior.
