//
//  Copyright © 2024 Ohlulu. All rights reserved.
//

import Combine
import Foundation

public protocol Command {
    func execute(with cart: CartModel) -> AnyPublisher<CartModel, Error>
}

public struct CartModel {
    // Add your cart properties here
    public init() {}
}

/// 負責一台購物車的所有操作，包括執行各種命令如新增商品、套用顧客資訊和優惠等。
public final class CartOperator: Identifiable {
    public let cartPublisher: CurrentValueSubject<CartModel, Never>
    public let errorPublisher = PassthroughSubject<Error, Never>()
    
    // Command input stream
    private let commandSubject = PassthroughSubject<Command, Never>()
    private let cart = CartModel()
    private var cancellable = Set<AnyCancellable>()
    
    public init() {
        cartPublisher = CurrentValueSubject(cart)
        
        // Setup command processing pipeline
        commandSubject
            .flatMap(maxPublishers: .max(1)) { [weak self] command -> AnyPublisher<CartModel, Error> in
                guard let self = self else {
                    return Fail(error: NSError(domain: "CartOperator", code: 1, userInfo: [NSLocalizedDescriptionKey: "CartOperator deallocated"]))
                        .eraseToAnyPublisher()
                }
                
                // Execute the command
                return command.execute(with: self.cart)
            }
            .sink(receiveCompletion: { [weak self] completion in
                guard let self = self else { return }
                if case let .failure(error) = completion {
                    self.errorPublisher.send(error)
                }
            }, receiveValue: { [weak self] cart in
                self?.cartPublisher.send(cart)
            })
            .store(in: &cancellable)
    }
    
    public func execute(_ command: Command) {
        commandSubject.send(command)
    }
}
