import SwiftUI

struct SecondView: View {
  var body: some View {
    VStack {
      Text("這裡是第二個視圖！")
        .navigationTitle("Second View")  // Optional: Add a title

      // Add two new buttons
      Button("Call StaticHelper.process()") {
        StaticHelper.process()
      }
      .padding()

      Button("Call InstanceHelper().process()") {
        InstanceHelper().process()
      }
      .padding()
    }
  }
}

#Preview {
  // To preview SecondView within a navigation context if needed
  // NavigationStack {
  SecondView()
  // }
}


