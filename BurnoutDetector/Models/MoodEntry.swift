import Foundation

/// Represents a single mood check-in entry
struct MoodEntry: Codable, Identifiable {
    let id: UUID
    let date: Date
    let mood: MoodLevel
    let note: String?

    init(id: UUID = UUID(), date: Date = Date(), mood: MoodLevel, note: String? = nil) {
        self.id = id
        self.date = date
        self.mood = mood
        self.note = note
    }
}

enum MoodLevel: Int, Codable, CaseIterable {
    case great = 5
    case okay = 4
    case flat = 3
    case stressed = 2
    case exhausted = 1

    var label: String {
        switch self {
        case .great: return "Great"
        case .okay: return "Okay"
        case .flat: return "Flat"
        case .stressed: return "Stressed"
        case .exhausted: return "Exhausted"
        }
    }

    var emoji: String {
        switch self {
        case .great: return "😄"
        case .okay: return "🙂"
        case .flat: return "😐"
        case .stressed: return "😣"
        case .exhausted: return "😩"
        }
    }

    /// Normalized score from 0.0 (worst) to 1.0 (best)
    var normalizedScore: Double {
        return Double(self.rawValue - 1) / 4.0
    }
}
