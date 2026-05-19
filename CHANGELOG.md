# Changelog

## [1.0.0] - 2026-05-19

### Features

- Initial release: virtual AMS filament inventory manager for Bambulab A1
- Event-driven coordinator tracking spool sensor and print state
- Automatic weight deduction after each successful print
- Services: `register_spool`, `update_spool`, `remove_spool`
- Lovelace card with inline register/edit forms, inventory list, and active spool view
- Bilingual UI: English and Italian
- Auto-registration of the Lovelace card resource on setup
