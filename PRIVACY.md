# Privacy & Ethics Notice

## Data Handling

The memory module stores:
- **Notes**: Your notes about meetings, conversations, decisions
- **People**: Contact info (name, company, role, email)
- **Projects**: Project names and descriptions
- **Events**: Event titles and dates
- **Decisions**: Decision records

## Ethical Considerations

### 1. Consent
- Only add people you have legitimate relationship with
- Don't store data about people who haven't consented

### 2. Purpose
- Use for personal knowledge management
- Don't use for surveillance or tracking without consent

### 3. Security
- Keep `evokb_memory.db` private
- Don't commit to git (already in .gitignore)

### 4. Accuracy
- Don't store speculative or unverified info as fact
- Mark uncertain information clearly

## GDPR Compliance (EU)

If you're subject to GDPR:
- Right to access: Users can query their data
- Right to delete: Implement data removal
- Data minimization: Only store necessary fields
- Purpose limitation: Use data only for stated purpose

## Best Practices

```python
# Good
store.add_person("John", company="Acme", role="CTO")

# Avoid
store.add_person("John", email="private@personal.com")  # Personal email?
store.add_person("John", notes="John is having marital issues")  # Sensitive
```

---

*EvoKB is a tool - use it responsibly.*
