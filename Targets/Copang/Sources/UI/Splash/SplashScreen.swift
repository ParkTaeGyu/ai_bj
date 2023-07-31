//
//  SplashScreen.swift
//  Copang
//
//  Created by Teddy on 2023/07/18.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

struct SplashScreen: View {
    var body: some View {
        contentView
            .onLoad {
                DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                    Router.shared.push(path: .main)
                }
            }
    }
}

extension SplashScreen {
    var contentView: some View {
        Image(systemName: "figure.walk")
    }
}
