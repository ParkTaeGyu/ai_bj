//
//  ViewDidLoadModifier.swift
//  Copang
//
//  Created by Teddy on 2023/07/15.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

extension View {
  func onLoad(perform action: (() async -> Void)? = nil) -> some View {
    modifier(ViewDidLoadModifier(perform: action))
  }
}

struct ViewDidLoadModifier: ViewModifier {
  @State private var didLoad = false
  private let task: (() async -> Void)?
  
  init(perform task: (() async -> Void)? = nil) {
    self.task = task
  }
  
  func body(content: Content) -> some View {
    content.onAppear {
      Task {
        if didLoad == false {
          didLoad = true
          await task?()
        }
      }
    }
  }
}

