### Frappe NPO

Frappe Non Profit Organization

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app frappe_npo
```

### Documentation

A user guide (for staff, not developers) lives in [`frappe_npo/docs/user-guide`](frappe_npo/docs/user-guide/README.md).
It covers membership, donations, grants, volunteers, chapters, certifications,
beneficiaries, cases, field operations, services, disbursements and reporting.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/frappe_npo
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

agpl-3.0
