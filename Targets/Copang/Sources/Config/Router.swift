//
//  Router.swift
//  Copang
//
//  Created by Teddy on 2023/07/18.
//  Copyright © 2023 tuist.io. All rights reserved.
//

import SwiftUI

class Router {
    static let shared = Router()

    public private(set) var routes = [Route]()

    fileprivate var onPush: ((Route) -> Void)?
    fileprivate var onPop: (() -> Void)?
    fileprivate var onPopTo: ((Route) -> Void)?
    fileprivate var onPopToRoot: (() -> Void)?

    private init() {
        let initialRoute = Route(
            path: AppConstants.initialPath,
            swipeBackEnabled: false,
            replace: false,
            clearStack: false,
            arg: nil,
            completionHandler: nil
        )
        routes.append(initialRoute)
    }

    var currentPath: RoutePath {
        routes.last!.path
    }

    func push(
        path: RoutePath,
        swipeBackEnabled: Bool = true,
        replace: Bool = false,
        clearStack: Bool = false,
        arg: ScreenArgProtocol? = nil,
        completionHandler: RouteCompletionHandler? = nil
    ) {
        closeUIComponents()

        let route = Route(
            path: path,
            swipeBackEnabled: swipeBackEnabled,
            replace: replace,
            clearStack: clearStack,
            arg: arg,
            completionHandler: completionHandler
        )

        if route.clearStack {
            routes.removeAll()
        } else if route.replace {
            routes.removeLast()
        }

        routes.append(route)
        onPush?(route)
    }

    func pop(result: ScreenResultProtocol? = nil) {
        guard routes.count >= 2 else { return }

        closeUIComponents()

        routes.last!.completionHandler?(result)
        routes.removeLast()
        onPop?()
    }

    func pop(
        to path: RoutePath,
        swipeBackEnabled: Bool = false,
        arg: ScreenArgProtocol? = nil
    ) {
        closeUIComponents()

        let route = Route(
            path: path,
            swipeBackEnabled: swipeBackEnabled,
            replace: false,
            clearStack: false,
            arg: arg,
            completionHandler: nil
        )

        routes.removeLast()
        routes.append(route)
        onPopTo?(route)
    }

    func popToRoot() {
        guard routes.count > 1 else { return }

        closeUIComponents()

        routes.removeSubrange(1 ..< routes.count)
        onPopToRoot?()
    }

    private func closeUIComponents() {
//    KeyboardHelper.shared.closeKeyboard()
//    BottomSheetHelper.shared.closeBottomSheet()
//    DialogHelper.shared.closeDialog()
    }
}

struct RootRouterView<Screen: View>: UIViewControllerRepresentable {
    private let router = Router.shared

    @ViewBuilder
    let routeMappingBuilder: (Route) -> Screen

    private func onRouteChanged(context: Context) {
        if let latestRoute = router.routes.last {
            context.coordinator.swipeBackEnabled = latestRoute.swipeBackEnabled
        }
    }

    func makeUIViewController(context: Context) -> UINavigationController {
        let navigation = UINavigationController()

        let initial = router.routes.first!
        navigation.pushViewController(
            UIHostingController(rootView: initial.buildConfiguredView()),
            animated: true
        )

        router.onPush = { routeOption in
            let view = routeMappingBuilder(routeOption)
            navigation.pushViewController(
                UIHostingController(rootView: view),
                animated: true,
                onComplete: {
                    if routeOption.clearStack {
                        let lastIndex = navigation.viewControllers.count - 1
                        navigation.viewControllers.removeSubrange(0 ..< lastIndex)
                    } else if routeOption.replace {
                        let secondLastIndex = navigation.viewControllers.count - 2
                        navigation.viewControllers.remove(at: secondLastIndex)
                    }
                    onRouteChanged(context: context)
                }
            )
        }

        router.onPop = {
            navigation.popViewController(
                animated: true,
                onComplete: {
                    onRouteChanged(context: context)
                }
            )
        }

        router.onPopTo = { routeOption in
            let view = routeMappingBuilder(routeOption)
            let insertIndex = max(navigation.viewControllers.count - 1, 0)
            navigation.viewControllers.insert(
                UIHostingController(rootView: view),
                at: insertIndex
            )
            navigation.popViewController(
                animated: true,
                onComplete: {
                    onRouteChanged(context: context)
                }
            )
        }

        router.onPopToRoot = {
            navigation.popToRootViewController(
                animated: true,
                onComplete: {
                    onRouteChanged(context: context)
                }
            )
        }

        navigation.delegate = context.coordinator
        navigation.interactivePopGestureRecognizer?.delegate = context.coordinator

        return navigation
    }

    func updateUIViewController(
        _ uiViewController: UINavigationController,
        context: Context
    ) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(swipeBackEnabled: false)
    }

    class Coordinator: NSObject, UINavigationControllerDelegate, UIGestureRecognizerDelegate {
        var swipeBackEnabled: Bool

        init(swipeBackEnabled: Bool) {
            self.swipeBackEnabled = swipeBackEnabled
        }

        func gestureRecognizerShouldBegin(_ gestureRecognizer: UIGestureRecognizer) -> Bool {
            swipeBackEnabled
        }

        public func gestureRecognizer(
            _ gestureRecognizer: UIGestureRecognizer,
            shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
        ) -> Bool {
            swipeBackEnabled
        }
    }
}

fileprivate extension UINavigationController {
    func pushViewController(
        _ viewController: UIViewController,
        animated: Bool,
        onComplete: @escaping () -> Void
    ) {
        pushViewController(viewController, animated: animated)

        if animated, let coordinator = transitionCoordinator {
            coordinator.animate(alongsideTransition: nil) { _ in
                onComplete()
            }
        } else {
            onComplete()
        }
    }

    func popViewController(
        animated: Bool,
        onComplete: @escaping () -> Void
    ) {
        popViewController(animated: animated)

        if animated, let coordinator = transitionCoordinator {
            coordinator.animate(alongsideTransition: nil) { _ in
                onComplete()
            }
        } else {
            onComplete()
        }
    }

    func popToRootViewController(
        animated: Bool,
        onComplete: @escaping () -> Void
    ) {
        popToRootViewController(animated: animated)

        if animated, let coordinator = transitionCoordinator {
            coordinator.animate(alongsideTransition: nil) { _ in
                onComplete()
            }
        } else {
            onComplete()
        }
    }
}
