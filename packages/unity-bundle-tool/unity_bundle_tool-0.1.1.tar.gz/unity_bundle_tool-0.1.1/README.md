# Unity Bundle Tool

A powerful, user-friendly command-line tool to extract and repack Unity asset bundles. Built with Python and UnityPy.

**Developer:** [minhmc2007](https://github.com/minhmc2007)

---

## Installation

Install the tool directly from PyPI:

\`\`\`bash
pip install unity-bundle-tool
\`\`\`

## Usage

Once installed, you can use the \`ubt\` command from your terminal.

### Extract a Bundle

\`\`\`bash
ubt extract path/to/your/asset.bundle path/to/output_folder/
\`\`\`

### Repack a Bundle

After modifying files, repack them into a new bundle:

\`\`\`bash
ubt repack path/to/output_folder/ path/to/new_repacked.bundle
\`\`\`

## License

This project is licensed under the MIT License.
