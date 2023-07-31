//
//  Route.swift
//  Copang
//
//  Created by Teddy on 2023/07/18.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

typealias RouteCompletionHandler = (ScreenResultProtocol?) -> ()

class Route {
  let path: RoutePath
  let swipeBackEnabled: Bool
  let replace: Bool
  let clearStack: Bool
  let arg: ScreenArgProtocol?
  let completionHandler: RouteCompletionHandler?
  
  init(
    path: RoutePath,
    swipeBackEnabled: Bool,
    replace: Bool,
    clearStack: Bool,
    arg: ScreenArgProtocol?,
    completionHandler: RouteCompletionHandler?
  ) {
    self.path = path
    self.swipeBackEnabled = swipeBackEnabled
    self.replace = replace
    self.clearStack = clearStack
    self.arg = arg
    self.completionHandler = completionHandler
  }
  
  @ViewBuilder
  private func routeOptionConfigured(for view: some View) -> some View {
    view
      .navigationBarHidden(true)
  }
  
  @ViewBuilder
  func buildConfiguredView() -> some View {
    routeOptionConfigured(
      for: self.path.buildScreenView(arg: self.arg)
    )
  }
}
