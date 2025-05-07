//
//  Copyright © 2025 Ohlulu. All rights reserved.
//

import SwiftUI

struct ContentView: View {
  var body: some View {
    NavigationStack {
      VStack {
        Image(systemName: "globe")
          .imageScale(.large)
          .foregroundStyle(.tint)
        Text("Hello, world!")

        NavigationLink("前往 SecondView") {
          SecondView()
        }
        .padding()
      }
      .padding()
    }
  }
}

#Preview {
  ContentView()
}
