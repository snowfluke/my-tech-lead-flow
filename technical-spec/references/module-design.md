# Module Design

The design lens that `technical-spec`, `api-spec`, and `tech-lead-setups` apply
when they shape modules, operations, and file patterns. The ideas come from
John Ousterhout (deep modules, "design it twice") and Michael Feathers (seams).

## Vocabulary

Use these words, and only these, when a spec talks about design. Mixed words
("component", "service", "boundary") make two specs describe one thing in two
ways.

| Term | Meaning |
| --- | --- |
| Module | Anything with an interface and an implementation. A function, a class, a package, or a slice across tiers. Size does not matter. |
| Interface | Everything a caller must know to use the module correctly: types, and also invariants, call order, errors, required configuration, and cost. More than a type signature. |
| Implementation | The code inside the module. |
| Depth | How much behaviour a caller gets per unit of interface it must learn. A deep module hides a lot behind a small interface. A shallow module's interface is almost as complex as its code. |
| Seam | The place where behaviour can change without editing that place. A module's interface sits at a seam. Where to put the seam is its own decision. |
| Adapter | A concrete thing that fills a seam by satisfying its interface. The word names a role, not a size. |
| Port | An interface defined at a seam so that more than one adapter can fill it. |

Depth pays twice. Callers get more capability for less to learn. Maintainers
get locality: a change, a bug, or a test lands in one place.

## Checks

- **Delete it.** Imagine the module gone. If the complexity disappears with it, the module was a pass-through. If the complexity reappears in every caller, the module earns its place.
- **Test at the interface.** Callers and tests cross the same seam. A test that must reach past the interface points to a module with the wrong shape.
- **Count the adapters.** One adapter is a guess about the future, and a seam for it is only indirection. Two adapters, usually production and test, make the seam real.
- **Keep internal seams internal.** A deep module may split its code into small swappable parts for its own tests. Those parts do not belong in the interface.

## Dependency categories

Classify every dependency that crosses a module or a service. The category
decides where the seam goes and how tests stand in for the dependency.

| Category | Example | Seam and test strategy |
| --- | --- | --- |
| In-process | Pure computation, in-memory state | No seam. Test the module directly through its interface. |
| Local stand-in | A database with an embedded or in-memory twin | Seam stays inside the module. Tests run the stand-in. |
| Remote, owned | Your own service over HTTP, gRPC, or a queue | Define a port. Production uses a network adapter. Tests use an in-memory adapter. The logic stays in one deep module. |
| Remote, third party | A payment or messaging provider | Define a port. Production uses the provider's client. Tests use a fake adapter. |

When a module becomes deeper, write tests at its new interface and delete the
old tests of the shallow parts. Tests describe behaviour, so an internal
refactor must not break them.

## Design it twice

The first interface you think of is rarely the best. For the one or two
interfaces that matter most (most callers, or hardest to change later), draft
several different ones before the spec fixes one.

1. **Frame the problem.** Write down what any interface must satisfy: its constraints, its dependencies with their categories, and a rough sketch to make them concrete. Show it to the user.
2. **Draft three or more designs, each under a different constraint.** Run the drafts in parallel fresh contexts if the harness has them, otherwise one after another.
   - The smallest interface: one to three entry points, most behaviour per entry point.
   - The most flexible interface: many use cases and extension points.
   - The easiest common case: the usual call is trivial.
   - Ports and adapters, when dependencies cross a seam.
3. **Describe each design the same way:** the interface (types, invariants, order, errors), one caller's usage, what it hides, how it handles dependencies, and where its depth is thin.
4. **Compare and recommend.** Compare the designs by depth, locality, and seam placement. Recommend one, or a mix of two, and say why. Let the user choose before the spec fixes the shape.
