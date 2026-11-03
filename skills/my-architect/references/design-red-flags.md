# Design red flags

Screen every candidate against these before choosing. A red flag is a reason to revise or reject the shape. They come from John Ousterhout's *A Philosophy of Software Design*.

## Shallow module

A large interface that hides little complexity. Judge depth by how much capability and policy sit behind the public interface compared with the size of that interface. Prefer a simple interface backed by substantial behavior.

A deep module is not a deep call chain. A deep call chain scatters understanding across layers. A deep module concentrates capability behind one interface.

Signs:

- Callers have to coordinate several methods to complete one operation.
- Public options expose internal stages or implementation choices.
- Learning the interface doesn't save the caller from learning the implementation.

## Information leakage

Several modules depend on the same internal decision. A representation, policy, or protocol detail appears in more than one place, so changing it takes coordinated edits.

Re-exporting transport or wire types on a public interface is leakage. Parse external data into domain types behind the interface, and keep storage schemas, framework objects, and protocol details private.

## Organized by execution order

Modules split by when things run (load, validate, transform, save) instead of by the knowledge they own. Each stage then repeats the same representation and its rules.

Group code by the domain knowledge it owns. Functions that run at different times can belong to one module when they protect the same decisions.

## Pass-through method

A method that forwards the same arguments to another method of the same shape. It adds a layer without hiding anything.

Remove it, or move the responsibility to the module that can complete the operation. Keep a forwarding layer only when it adds policy, adaptation, or a distinct abstraction.
