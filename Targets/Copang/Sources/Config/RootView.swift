//
//  RootView.swift
//  Copang
//
//  Created by Teddy on 2023/07/14.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

struct RootView: View {
  @State private var isAppInitialized = false
  
  var body: some View {
    ConditionalView(
      isAppInitialized,
      trueContent: {
        RouteConfiguredView()
      }
    )
    .onLoad {
      await initializeApp()
    }
  }
  
  private func initializeApp() async {
    DispatchQueue.main.async {
      isAppInitialized = true
    }
  }
}

fileprivate struct RouteConfiguredView: View {
  var body: some View {
    RootRouterView { routeOption in
      routeOption.buildConfiguredView()
    }
  }
}

