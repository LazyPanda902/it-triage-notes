# Privacy Policy

## Data Collection

This tool is a local command-line application. It does not collect, transmit, or share any data with external services or third parties.

## Local Storage Only

All notes you create are stored exclusively on your local machine in a JSON Lines file. No data is sent over the network.

## Sample Data

The test suite includes sample incident data for testing purposes:

- "Azure login fail" — sample Azure/authentication incident
- "M365 license issue" — sample Microsoft 365 incident
- "Disk alert" — sample monitoring incident

These are used for automated tests only and are not persisted beyond test execution.

## User Information

The only user-related information stored is what you explicitly record in your notes. The tool does not:

- Track your identity
- Log your activity
- Collect usage statistics
- Record timestamps beyond note creation/update times
- Store IP addresses or device information
- Require authentication or account creation

## Data Retention

You have full control over your data. Delete notes at any time using the `delete` command. Your notes are only retained as long as you maintain your local notes database file.

## Third-Party Services

This tool does not integrate with or depend on any third-party services. All processing is local and offline.

## Privacy Recommendations

1. **Anonymize incident data**: Do not store real names, email addresses, or phone numbers
2. **Avoid sensitive details**: Summarize security issues without technical details
3. **File permissions**: Restrict your notes database file to your user only
4. **Backups**: Apply the same privacy controls to any backups of your notes

For privacy questions, contact the maintainers.
