//
//  ConditionalView.swift
//  Copang
//
//  Created by Teddy on 2023/07/15.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

/// 조건에 따라 뷰가 전환되어야 할 때 애니메이션을 넣기 편하게 하기 위해 만든 뷰.
/// 아래에 `.animation()` modifier를 달면 애니메이션을 넣을 수 있다.
/// `trueContent`, `falseContent` 모두 누락해도 상관없다.
struct ConditionalView<TrueContent: View, FalseContent: View>: View {
  let condition: Bool
  let trueContent: TrueContent?
  let falseContent: FalseContent?
  
  init(
    _ condition: Bool,
    @ViewBuilder trueContent: @escaping () -> TrueContent = { EmptyView() },
    @ViewBuilder falseContent: @escaping () -> FalseContent = { EmptyView() }
  ) {
    self.condition = condition
    self.trueContent = condition ? trueContent() : nil
    self.falseContent = condition ? nil : falseContent()
  }
  
  var body: some View {
    ZStack {
      if (condition) {
        trueContent
      } else {
        falseContent
      }
    }
  }
}
