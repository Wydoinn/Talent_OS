# Source Inventory and Known Limitations

## Included

This source package contains the Angular frontend, four backend service directories, shared backend dependency list, launch scripts, license, and centralized documentation. The optional text-generation integration is configured through environment variables and does not contain a hard-coded vendor endpoint or deployment identifier.

## Deliberately excluded runtime and sample assets

- Candidate resume examples are not included. The `backend/ats_parser_checker/resumes/internal/` and `external/` directories are empty placeholders for configured source data.
- UI screenshots and generated demonstration material are not included.
- Local runtime weights and binary inference assets are not included. Provision required assets separately and configure their paths through environment variables.
- Populated `.env` files, local databases, caches, and generated files are not included.

## Missing source packages in the supplied archive

The uploaded source archive did not contain the following packages, although imports in the services reference them:

- `backend/orchestration/app/models/`
- `backend/ats_parser_checker/app/models/`

These are application source packages, not binary model weights. Their absence prevents a complete runtime or integration validation of the affected services. Restore the authoritative versions from the original project repository before building a deployable release. No replacement database models or schemas have been fabricated in this package.

The root `.gitignore` has been narrowed so that a generic `models/` ignore rule does not accidentally exclude nested application source packages in future commits.

## Validation notes

The Python sources can be syntax-checked with `python -m compileall -q backend`. Runtime behavior, migrations, model asset compatibility, third-party service connections, and full end-to-end workflows require the missing source packages and an environment configured with the required infrastructure and assets.
