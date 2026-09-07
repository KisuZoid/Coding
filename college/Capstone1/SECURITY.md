# Security Policy — AutoInspect-X

## Reporting a vulnerability

This is an academic capstone project without a public security contact. Report
suspected vulnerabilities privately to the project maintainer. Do not open a
public issue containing exploit details.

## Secrets

Never commit API keys, tokens, passwords, private certificates, cloud
credentials, or service-account files.

- Real values live in `.env`, which is git-ignored.
- Only `.env.example` is tracked, and it contains variable names with empty or
  clearly non-secret placeholder values.
- If a secret is committed, treat it as compromised: rotate it first, then
  remove it from history.

## Database access

The connected Supabase account contains a project belonging to a different
product, **Physios Plus CRM V3** (`nykalxhmbupsarhicrtd`). No code, script, or
agent in this repository may read from or write to it. AutoInspect-X currently
has no database.

Resolve the correct project from `SUPABASE_URL` in `.env`, never from memory.

## Uploaded images

Vehicle photographs may contain number plates, faces, location metadata, and
other personal data. When image handling is implemented:

- validate file type and size at the boundary;
- strip EXIF location data unless it is required and the user consented;
- do not log raw image content or full file paths containing user identifiers;
- define a retention period before storing anything.

## Model artefacts

Never commit trained checkpoints. Load model artefacts from a configured path or
registry, never from a hard-coded location, and never execute a model file
downloaded from an unverified source.

## Dependencies

Verify the exact package before installing when a name is ambiguous. Pin
versions for anything used in a reproducible experiment.
