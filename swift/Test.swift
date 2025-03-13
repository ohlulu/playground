import Foundation
import Combine

public protocol Command {
    var name: String { get }
    func execute(with cart: CartModel) -> AnyPublisher<CartModel, Error>
}

public struct CartModel {
    public init() {}
}

public final class CartOperator {
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
            .sink(receiveCompletion: { completion in
                print("receive completion \(completion)")
//                guard let self = self else { return }
//                if case let .failure(error) = completion {
//                    self.errorPublisher.send(error)
//                }
            }, receiveValue: { cart in
                print("receive value \(cart)")
//                self?.cartPublisher.send(cart)
            })
            .store(in: &cancellable)
    }
    
    public func execute(_ command: Command) {
        commandSubject.send(command)
    }
}

final class CommandSpy: Command {
    let name: String
    
    var executed = false
    private var subject = PassthroughSubject<CartModel, Error>()
    
    init(name: String) {
        self.name = name
    }
    
    func execute(with cart: CartModel) -> AnyPublisher<CartModel, any Error> {
        executed = true
        return subject.eraseToAnyPublisher()
    }
    
    func complete(with cart: CartModel) {
        subject.send(cart)
        subject.send(completion: .finished)
    }
    
    func fail(with error: Error) {
        subject.send(completion: .failure(error))
    }
}

print("--------------------------------")

let sut = CartOperator()

let command1 = CommandSpy(name: "command 1")
let command2 = CommandSpy(name: "command 2")
let command3 = CommandSpy(name: "command 3")

sut.execute(command1)
sut.execute(command2)
sut.execute(command3)

