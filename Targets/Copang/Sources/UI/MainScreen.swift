//
//  MainScreen.swift
//  Copang
//
//  Created by Teddy on 2023/07/18.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

struct MainScreen: View {
    var body: some View {
        TabView {
            MenuScreen()
                .tabItem {
                    Image(systemName: "contextualmenu.and.cursorarrow")
                }

            SearchScreen()
                .tabItem {
                    Image(systemName: "magnifyingglass")
                }

            HomeScreen()
                .tabItem {
                    Image(systemName: "house")
                }

            ProfileScreen()
                .tabItem {
                    Image(systemName: "person")
                }

            CartScreen()
                .tabItem {
                    Image(systemName: "cart")
                }
        }
    }
}
