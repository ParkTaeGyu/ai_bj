//
//  RoutePath.swift
//  Copang
//
//  Created by Teddy on 2023/07/18.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

enum RoutePath: String, Hashable {
    case splash = "/splash"
    case main = "/main"
    case menu = "/menu"
    case search = "/search"
    case home = "/home"
    case profile = "/profile"
    case cart = "/cart"

    @ViewBuilder
    func buildScreenView(arg: ScreenArgProtocol?) -> some View {
        switch self {
        case .splash: SplashScreen()
        case .main: MainScreen()
        case .menu: MenuScreen()
        case .search: SearchScreen()
        case .home: HomeScreen()
        case .profile: ProfileScreen()
        case .cart: CartScreen()
        }
    }
}
