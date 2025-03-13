// swift-tools-version: 5.10
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Command",
    platforms: [
        .macOS("14.0"),
        .iOS("17.0"),
    ],
    products: [
        .library(
            name: "Command",
            targets: ["Command"]),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "Command"),
        .testTarget(
            name: "CommandTests",
            dependencies: ["Command"]),
    ]
)
