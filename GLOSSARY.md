# Marketplace research domain

The marketplace exposes one shared research behavior through host-specific
interfaces. These terms keep research evidence and coverage distinct from
the route used to obtain it.

## Language

**Research operation**:
A typed research request and corresponding result for one named action, such
as GitHub issue search or Context7 documentation query. An operation is not
a host-specific plugin command.

**Research plan**:
The declared capabilities, corpora, source standards, freshness, limits and
fallback rules that a research run must satisfy.

**Provider**:
A named external service or tool that supplies a research operation, such as
Exa or Context7. A provider is not necessarily an independent upstream.

**Route**:
The concrete access path used for an operation, including a primary endpoint
or a fallback. Distinct routes can reach the same corpus or upstream.

**Upstream**:
The publisher or independently originating source of material returned by a
route. Two routes do not create two upstreams when they surface the same source.

**Corpus**:
The underlying collection of material searched by a route. Providers can
share a corpus even when their APIs and response formats differ.

**Artifact**:
An immutable captured response or source item retained with its provenance
to support a research result or claim.

**Coverage verdict**:
The plan-level judgment of whether the required capabilities and source
independence were met. It is separate from a process exit or route status.

**Host adapter**:
A thin host-specific registration and invocation surface for the shared core.
It does not define independent research semantics.
