# TestCloak

A simple test repository demonstrating PII masking using [DocPivot](https://github.com/hernamesbarbara/docpivot) and [CloakPivot](https://github.com/hernamesbarbara/cloakpivot) together.

## Overview

This project provides a command-line tool that:
- Reads PDF documents using Docling
- Identifies personally identifiable information (PII)
- Masks sensitive data using CloakPivot
- Exports both masked and unmasked versions as markdown files

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Usage

### Basic Usage (Default Redaction)
```bash
python pii-cloak mask --infile data/pdf/email.pdf --output-format markdown --outdir data/md/
```

### With Replacement Strategy
```bash
python pii-cloak mask --infile data/pdf/email.pdf --output-format markdown --outdir data/md/ --strategy replace
```

### Available Strategies
- `redact` (default): Replaces PII with static placeholders like `[NAME]`, `[EMAIL]`, `[DATE]`
- `replace`: Replaces PII with masked characters (currently uses asterisks)

## Example Output

The script processes PDF documents and produces masked and unmasked versions. Here's the same email shown with different masking strategies:

### Unmasked Document

```markdown
---------- Forwarded message ----------

From: Cameron MacIntyre <cameron@example.com>

Date: Tuesday, September 2 2025 at 12:19 PM EDT

Subject: Re: FYI emailing with from inness robins

To: Julian Margaret <jmargaret@company.com>

Hi Julian,

I'd definitely like to meet Inness if you think she'd be open to meeting! Thanks so so much for pounding the pavement so much for me here.

Best,

Cameron

PS - here are the remaining 3 birthdays you asked for :)

| surname   | first name   | birthdate   |
|-----------|--------------|-------------|
| White     | Johnson      | 1958-04-21  |
| Borden    | Ashley       | 1944-12-22  |
| Green     | Marjorie     | 1958-04-21  |
```

### Masked Document (Redact Strategy)

```markdown
# Masked Document (Strategy: redact)

**Entities Found:** 11
**Entities Masked:** 11

---------- Forwarded message ----------

From: [NAME] <[EMAIL]>

Date: [DATE] at [DATE]

Subject: Re: FYI emailing with from inness robins

To: [NAME] <[EMAIL]>

Hi [NAME],

I'd definitely like to meet Inness if you think she'd be open to meeting! Thanks so so much for pounding the pavement so much for me here.

Best,

Cameron

PS - here are the remaining [DATE] you asked for :)

| surname   | first name   | birthdate   |
|-----------|--------------|-------------|
| White     | Johnson      | [DATE]      |
| Borden    | Ashley       | [DATE]      |
| Green     | Marjorie     | [DATE]      |
```

### Masked Document (Replace Strategy)

```markdown
# Masked Document (Strategy: replace)

**Entities Found:** 11
**Entities Masked:** 11

---------- Forwarded message ----------

From: ***************** <*******************>

Date: ************************* at ************

Subject: Re: FYI emailing with from inness robins

To: *************** <*********************>

Hi ******,

I'd definitely like to meet Inness if you think she'd be open to meeting! Thanks so so much for pounding the pavement so much for me here.

Best,

Cameron

PS - here are the remaining *********** you asked for :)

| surname   | first name   | birthdate        |
|-----------|--------------|------------------|
| White     | Johnson      | **********       |
| Borden    | Ashley       | **********       |
| Green     | Marjorie     | **********       |
```

## What Gets Masked

The tool automatically detects and masks:
- 📧 Email addresses → `[EMAIL]`
- 👤 Person names → `[NAME]`
- 📅 Dates and times → `[DATE]`
- 📱 Phone numbers → `[PHONE]`
- 💳 Credit card numbers → `[CARD-****]`
- 🏠 Locations → `[LOCATION]`
- And more...

## Output Files

The script generates three files per strategy:

### Default (Redact) Strategy:
- `{filename}.unmasked.md` - Original content in markdown format
- `{filename}.masked.md` - Content with PII replaced by placeholders
- `{filename}.cloakmap.json` - Detailed mapping of all masked entities

### Replace Strategy:
- `{filename}.unmasked.md` - Original content in markdown format (same as above)
- `{filename}.masked.replace.md` - Content with PII replaced by asterisks
- `{filename}.cloakmap.replace.json` - Detailed mapping with replacement metadata

## Dependencies

- [Docling](https://github.com/DS4SD/docling) - PDF to structured document conversion
- [DocPivot](https://github.com/hernamesbarbara/docpivot) - Document processing pipeline
- [CloakPivot](https://github.com/hernamesbarbara/cloakpivot) - PII detection and masking
- [Presidio](https://github.com/microsoft/presidio) - PII detection engine (via CloakPivot)

## Known Limitations

- The `replace` strategy currently uses asterisks instead of realistic fake data due to a limitation in the CloakPivot/Presidio integration. Future versions may support realistic fake data generation using libraries like Faker.

## License

This is a test repository for demonstration purposes.