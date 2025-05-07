# Swift Memory and Function Dispatch Demo

This project demonstrates concepts related to function calls and memory management in Swift, as discussed in the article.
It covers:
- Static functions vs. Instance methods
- Dispatch mechanisms (Static vs. Dynamic)
- Conceptual location of method code (Text Segment)

## How to Compile and Run

1.  Save the code in `main.swift` into a file named `main.swift`.
2.  Open your terminal.
3.  Navigate to the directory where you saved `main.swift`.
4.  Compile the Swift code using the Swift compiler:
    ```sh
    swiftc main.swift -o demo
    ```
5.  Run the compiled executable:
    ```sh
    ./demo
    ```

## Code Explanation

-   **`StaticHelper.process()`**:
    -   This is a static function. It's called directly on the type (`StaticHelper`).
    -   It doesn't require an instance of `StaticHelper` to be created.
    -   No implicit `self` parameter is passed.
    -   Dispatch: Typically uses **static dispatch**.

-   **`InstanceHelper().process()`**:
    -   This is an instance method of a `struct`.
    -   An instance (`instanceHelper`) must be created first.
    -   An implicit `self` parameter (referring to `instanceHelper`) is passed to `process()`.
    -   Dispatch: For `structs`, instance methods usually use **static dispatch**.

-   **`FinalClassHelper().performAction()`**:
    -   This is an instance method of a `final class`.
    -   An instance (`finalClassInstance`) is created.
    -   Implicit `self` is passed.
    -   Dispatch: For `final` classes, instance methods can also use **static dispatch** because the compiler knows the method implementation cannot be overridden.

-   **`NonFinalBaseClass` and `DerivedClass`**:
    -   `NonFinalBaseClass` has an instance method `performAction()` and `describe()`.
    -   `DerivedClass` inherits from `NonFinalBaseClass` and overrides `performAction()` and `describe()`.
    -   When `baseClassInstance.performAction()` is called (where `baseClassInstance` is typed as `NonFinalBaseClass` but refers to a `DerivedClass` object), **dynamic dispatch** is used. The program determines at runtime which version of `performAction()` (the one in `NonFinalBaseClass` or `DerivedClass`) to execute.
    -   This is typically implemented using a vtable (virtual function table).

-   **Code Storage (Text Segment)**:
    -   The actual machine code instructions for all these methods (`StaticHelper.process`, `InstanceHelper.process`, `NonFinalBaseClass.performAction`, `DerivedClass.performAction`, `FinalClassHelper.performAction`) are stored in the **Text Segment** (or Code Segment) of the compiled executable.
    -   This segment is typically read-only.
    -   There's only one copy of the method's machine code, regardless of how many instances are created.
    -   The difference lies in how they are called (with or without `self`) and the dispatch mechanism used, not where the code itself is stored.

By running the `demo` executable, you will see print statements that indicate which functions are being called, illustrating the flow of execution and the effect of dynamic dispatch when using class inheritance. 