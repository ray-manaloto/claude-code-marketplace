# RF4: Publish the complete reusable refresh package

**What to build:** Make the accepted refresh runner, runtime safeguards, complete
offline tests, portable examples and lessons available from the existing Git
integration branch, with explicit local runtime/state selection.

**Blocked by:** Settled RF1, RF2, RF3a and RF3b implementation/review gates (complete).

**Status:** Implemented, independently reviewed and checked; Git publication pending.
This remains a local record, not a published tracker ticket.

- [x] Mechanical source/test transfer retains exact provenance.
- [x] Explicit configuration refuses unsafe state/runtime selection before side effects.
- [x] Complete imported suite and existing development/baseline gates pass.
- [x] Portable guide and generalized lessons retain scope and evidence limits.
- [x] Independent standards/specification review and actionable retro findings settle.
- [ ] Committed branch is pushed and its exact remote tip verified.

Implementation is one dependency-aware publication unit, with bounded reviews of
the transfer, new configuration boundary and delivery documentation. The approved
scope reuses the existing runner test seam. No external issue or readiness label
is created by this record.
