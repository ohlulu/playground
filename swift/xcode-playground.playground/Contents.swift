import UIKit

func makePromotionSetting(_ setting: SettingData, file: StaticString = #file, line: UInt = #line)
  throws -> SettingsPromotions
{
  let decoder = JSONDecoder()
  decoder.keyDecodingStrategy = .convertFromSnakeCase

  var jsonString = "{"
  if let orderGiftExclude = setting.orderGiftExclude {
    let row = """
      "order_gift_exclude_credit_and_point" : \(orderGiftExclude.isEmpty ? "\"\"" : orderGiftExclude), 
      """
    jsonString.append(row)
  }
  if let orderGiftThreshold = setting.orderGiftThreshold {
    let row = """
      "order_gift_threshold_mode" : "\(orderGiftThreshold)", 
      """
    jsonString.append(row)
  }
  if let categoryThreshold = setting.categoryThreshold {
    let row = """
      "category_item_gift_threshold_mode" : "\(categoryThreshold)"
      """
    jsonString.append(row)
  }
  jsonString.append("}")

  let jsonData = jsonString.data(using: .utf8) ?? Data()
  return try decoder.decode(SettingsPromotions.self, from: jsonData)
}
