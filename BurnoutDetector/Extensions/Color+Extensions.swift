import SwiftUI

extension Color {
    /// Risk level colors
    static let burnoutGreen = Color.green
    static let burnoutYellow = Color.yellow
    static let burnoutRed = Color.red

    /// Get color for a burnout score
    static func forBurnoutScore(_ score: Double) -> Color {
        switch score {
        case 0..<40: return .burnoutGreen
        case 40..<70: return .burnoutYellow
        default: return .burnoutRed
        }
    }

    /// Get color for a mood level
    static func forMood(_ mood: MoodLevel) -> Color {
        switch mood {
        case .great: return .green
        case .okay: return .mint
        case .flat: return .yellow
        case .stressed: return .orange
        case .exhausted: return .red
        }
    }
}
