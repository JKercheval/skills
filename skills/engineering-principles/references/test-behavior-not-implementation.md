# Test behavior, not implementation

A test should call the code the way its users do and check the result they observe against a literal expected value.

**The check:** would this test still pass if every function it imports returned nothing? If so, it can't catch a defect. Rewrite the assertion or delete the test.

**Tests that fail that check:**
- **Weak assertions:** none at all, or only "is not None", "is truthy", "didn't raise", "length > 0".
- **Mock-only assertions:** only checking that a mock was or wasn't called.
- **Self-referential assertions:** the expected value comes from the code under test, like `assert f(x) == f(x)`.
- **Constant pins:** restating a constant, config default, or prompt string, like `assert MAX_RETRIES == 3`. These don't test behavior, and they break when someone legitimately changes the value.
- **Fixture checks:** asserting on data the test itself built, while the code under test never runs.

**The fix:** call the code with a concrete input and assert the literal output or the observable effect, like `assert slugify("Hello, World!") == "hello-world"`.
- For "nothing happens" cases, also assert that something does happen for a contrasting input in the same test.
- For a constant, test the behavior that uses it.
- For a mock, assert on what it received or the state after the call, not just that it was called.
- If no meaningful assertion exists, delete the test.
