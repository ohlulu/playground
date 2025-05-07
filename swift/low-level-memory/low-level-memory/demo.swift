// main.swift

import Foundation

// --- Static functions vs. Instance methods ---

// Version 1: Static function
struct StaticHelper {
  static func process() {
    print("StaticHelper.process() called. Belongs to the type itself.")
  }
}

// Version 2: Instance method (struct)
class InstanceHelper {
  func process() {
    // The instance itself occupies memory space.
    // 'self' here refers to that instance.
    print("InstanceHelper.process() called. Belongs to an instance. Self: \(self)")
  }
}
//
//// --- Dispatch Mechanisms ---
//
//// Non-final class (default: dynamic dispatch)
//class NonFinalBaseClass {
//  func performAction() {
//    print("NonFinalBaseClass.performAction() called. Potential dynamic dispatch.")
//  }
//
//  func describe() {
//    print("Instance of NonFinalBaseClass")
//  }
//}
//
//class DerivedClass: NonFinalBaseClass {
//  override func performAction() {
//    print("DerivedClass.performAction() called. (Override) Potential dynamic dispatch.")
//  }
//
//  override func describe() {
//    print("Instance of DerivedClass")
//  }
//}
//
//// Final class (typically static dispatch)
//final class FinalClassHelper {
//  func performAction() {
//    print("FinalClassHelper.performAction() called. Likely static dispatch.")
//  }
//}
//
//// --- Code Storage ---
//// Regardless of whether it's a static function or an instance method,
//// the compiled machine instructions are stored in the executable's
//// Text Segment (or Code Segment). This cannot be directly "shown"
//// in Swift code but is how Swift (and many compiled languages) work.
//
//// --- Main execution block ---
//print("--- Demonstrating Static vs. Instance Methods ---")
//StaticHelper.process()  // Calling a static function
//
//let instanceHelper = InstanceHelper()
//instanceHelper.process()  // Calling an instance method
//
//print("\n--- Demonstrating Dispatch Mechanisms ---")
//
//// Struct instance method - Static dispatch
//let structInstance = InstanceHelper()
//structInstance.process()
//
//// Final class instance method - Static dispatch
//let finalClassInstance = FinalClassHelper()
//finalClassInstance.performAction()
//
//// Non-final class instance method - Dynamic dispatch
//// Reference of base type pointing to an instance of derived type
//let baseClassInstance: NonFinalBaseClass = DerivedClass()
//baseClassInstance.performAction()  // Will call DerivedClass's version
//baseClassInstance.describe()  // Will also call DerivedClass's version
//
//let directDerivedInstance = DerivedClass()
//directDerivedInstance.performAction()  // Directly calls DerivedClass's version
//
//let plainBaseInstance: NonFinalBaseClass = NonFinalBaseClass()
//plainBaseInstance.performAction()  // Calls NonFinalBaseClass's version
//
//print("\n--- Regarding Code Storage ---")
//print("All method (static and instance) instructions are stored in the Text Segment.")
//print("This demo shows their invocation, not their memory address in Text Segment.")

class Demo {
  func functionOne() {
    print("Function One from Demo called!")
  }

  func functionTwo() {
    print("Function Two from Demo called!")
  }
}
