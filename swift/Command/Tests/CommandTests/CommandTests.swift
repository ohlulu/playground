import Combine
import XCTest

@testable import Command

final class CommandTests: XCTestCase {
    private var cancellable = Set<AnyCancellable>()

    func test_command_serialExecute() {
        let sut = makeSUT()
        let command1 = CommandSpy()
        let command2 = CommandSpy()
        let command3 = CommandSpy()
        
        sut.execute(command1)
        sut.execute(command2)
        sut.execute(command3)
        
        // Initial state: Only the first command should have started executing
        XCTAssertEqual(command1.executed, true)
        XCTAssertEqual(command2.executed, false)
        XCTAssertEqual(command3.executed, false)
        
        // Complete the first command
        command1.complete(with: CartModel())
        
        // Now the second command should be executing
        XCTAssertEqual(command2.executed, true)
        XCTAssertEqual(command3.executed, false)
        
        // Complete the second command
        command2.complete(with: CartModel())
        
        // Now the third command should be executing
        XCTAssertEqual(command3.executed, true)
    }
    
    func test() {    
        let numbers = [1, 2, 3, 4]
        let publisher = numbers.publisher
        
        let a = DispatchSemaphore(value: 3)

        publisher
            .flatMap(maxPublishers: .max(1)) { value in
                Just(value) // 這裡模擬一個簡單的 Publisher
                    .delay(for: .seconds(1), scheduler: DispatchQueue.main) // 模擬延遲
                    .map { "Processed \($0)" }
            }
            .sink { completion in
                print("Completed: \(completion)")
            } receiveValue: { value in
                print(value)
            }
            .store(in: &cancellable)
    }
}

private extension CommandTests {
    func makeSUT() -> CartOperator {
        let sut = CartOperator()
        return sut
    }

    final class CommandSpy: Command {
        var executed = false
        private var subject = PassthroughSubject<CartModel, Error>()
        
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
}
