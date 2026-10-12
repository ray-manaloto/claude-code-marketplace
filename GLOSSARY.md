# Marketplace research language

Research refreshes retain observations and qualify which observations can support
later comparisons. Failed attempts remain evidence without becoming accepted history.

## Language

**Refresh attempt**: One bounded attempt to obtain and compare current research observations.
_Avoid_: Successful run when its comparison has failed

**Raw snapshot**: Retained observations from a provider operation, before acceptance for comparison.
_Avoid_: Accepted baseline

**Accepted comparison baseline**: A retained compatible observation eligible to anchor a later comparison. An unverified empty observation cannot be such a baseline.
_Avoid_: Latest snapshot

**Query history**: Coverage observations associated with a compatible query identity, including explicit coverage warnings. This history is distinct from comparison-baseline eligibility.
_Avoid_: Attempt history

**Failed-attempt receipt**: Evidence of an unsuccessful refresh stage, its actual outcome and the retained prior acceptance state.
_Avoid_: Success receipt

**Borrowed runtime**: An existing execution environment owned outside this refresh workflow and used without modification.
_Avoid_: Managed refresh runtime

**Coverage warning**: An observation's unresolved completeness or validity, retained without certifying a content change.
_Avoid_: Accepted content change

**Comparison failure**: An attempt that cannot complete the comparison operation or verify its evidence.
_Avoid_: Empty result

**Attempt status**: The outcome of a refresh's processing and evidence checks, distinct from whether its observations qualify for content comparison.
_Avoid_: Comparison status

**Unavailable borrowed runtime**: A borrowed execution environment that fails the refresh's required identity or import checks.
_Avoid_: Provider outage
