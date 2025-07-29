import PackageDescription

let package = Package(
  name: "MyCoolServer",
  platforms: [
    .macOS(.v12)
  ],

  dependencies: [
    .package(url: "https://github.com/vapor/vapor.git", from: "4.50.0"),

    .package(url: "https://github.com/MaxDesiatov/XMLCoder.git", .exact("0.13.0")),

    .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0"),

    .package(url: "https://github.com/apple/swift-collections.git", from: "1.1.0"),

    .package(url: "github.com/apple/swift-nio", from: "2.41.0"),
    .package(url: "https://github.com/Quick/Nimble.git", from: "13.2.1"),

  ],

  targets: [
    .executableTarget(
      name: "App",
      dependencies: [

        .product(name: "Vapor", package: "vapor"),
        .product(name: "XMLCoder", package: "XMLCoder"),
        .product(name: "ArgumentParser", package: "swift-argument-parser"),
        .product(name: "Collections", package: "swift-collections"),
      ],
      swiftSettings: []
    ),

    .testTarget(
      name: "AppTests",
      dependencies: [
        .target(name: "App"),
        .product(name: "XCTVapor", package: "vapor"),
        .product(name: "Quick", package: "Quick"),
        .product(name: "Nimble", package: "Nimble"),
      ]
    ),
  ]
)
