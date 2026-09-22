# Put the rebuilt project on GitHub

Complete the hardware tests and replace placeholders before making the
repository public.

## First local backup

From the extracted `ALERTA_Rebuild` folder:

```bash
git init
git add .
git commit -m "Initial reproducible ALERTA rebuild"
```

This first commit already protects tracked code from ordinary accidental
deletion.

## Create and connect the GitHub repository

1. Create a new empty repository named `ALERTA` in your GitHub account.
2. Do not add another README or `.gitignore` on GitHub.
3. Copy the HTTPS repository URL and run:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ALERTA.git
git push -u origin main
```

## Everyday safe workflow

```bash
git status
git add .
git commit -m "Describe the tested change"
git push
```

Commit after every tested sensor or ML milestone. Never commit phone numbers,
API keys, participant identities or identifiable health data.

## Before adding the link to a portfolio

- [ ] Replace `YOUR_USERNAME` and all phone-number placeholders.
- [ ] Keep GSM alerts disabled in the public default configuration.
- [ ] Add clear prototype photographs that you own.
- [ ] Record exactly which functions have been physically tested.
- [ ] Keep all synthetic-performance claims labelled as synthetic.
- [ ] Do not claim clinical validation.
- [ ] Add the final repository URL beside the ALERTA project entry.

