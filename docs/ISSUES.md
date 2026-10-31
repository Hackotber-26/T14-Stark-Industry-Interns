# Starter issues

These are proposed issue cards, not claims that features already exist. Create one repository issue per card, applying the listed labels.

| # | Issue | Labels | Scope and acceptance criteria |
|---|---|---|---|
| 1 | Add a garbage verification module | `hacktoberfest` | Design an issue-type-specific measurement contract, add synthetic tests, and expose the new issue type without changing pothole results. Document limitations and required source images. |
| 2 | Add Tamil and Hindi explanations | `hacktoberfest`, `good first issue` | Add reviewed templates for every verdict, including duplicate and wrong-location variants; test interpolation and Unicode output. Preserve existing English and Kannada responses. |
| 3 | Capture photos with signed GPS metadata | `hacktoberfest` | Add an opt-in capture flow and a documented signing/verification design that identifies the trusted signer. Test altered metadata, missing permissions, and replay; explain the limits of trusting device GPS. |
| 4 | Evaluate an optional LoFTR scene matcher | `hacktoberfest` | Keep the current matcher as the default. Benchmark a local alternative on hard viewpoint and lighting pairs; report accuracy, latency, hardware needs, and licensing. |
| 5 | Add a contractor scorecard | `hacktoberfest` | Define a contractor field and aggregation rules, then show counts and verification rates with sample sizes. Test missing fields and avoid presenting simulated cases as real contractor performance. |
| 6 | Improve accessible PDF evidence reports | `hacktoberfest`, `good first issue` | Extend the report module with clear image captions and accessible reading order. Add a configurable Kannada font with a truthful fallback, and test missing images and long reasons. |
| 7 | Add a local container-compose setup | `hacktoberfest`, `good first issue` | Provide backend/frontend services with local volumes and a health check. Document CPU operation, optional weights, startup commands, and a successful five-case smoke run. |
| 8 | Add an offline mobile PWA shell | `hacktoberfest` | Cache the interface and clearly labelled demo assets. Show an explicit offline state, preserve draft selections where supported, and never present cached fixtures as fresh upload verification. Test narrow screens and reconnection. |
